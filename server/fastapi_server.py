from fastapi import FastAPI, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from pymongo import MongoClient
import os
import random
import json
import logging
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from groq import Groq
from concurrent.futures import ThreadPoolExecutor
from data.manifesto_bank import get_available_manifestos, claim_manifesto, get_all_manifestos
from server.init_db import restart_game_state

import io
import numpy as np
import subprocess
from scipy.fft import fft
import time

# Load env: try server/.env (dev), then root .env (Docker), then rely on system env vars
env_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(env_path):
    env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path, override=True)
app = FastAPI()

logger = logging.getLogger("panchayat")

# ══════════════════════════════════
#  GROQ CLIENT
# ══════════════════════════════════

groq_client = None
def get_groq_client():
    global groq_client
    if groq_client is None:
        key = os.getenv("GROQ_API_KEY")
        if key:
            clean_key = key.strip('"').strip("'")
            if clean_key:
                groq_client = Groq(api_key=clean_key)
    return groq_client

# ══════════════════════════════════
#  ARMORIQ CLIENT (Election Commissioner)
# ══════════════════════════════════

armoriq_client = None
def get_armoriq_client():
    global armoriq_client
    if armoriq_client is None:
        key = os.getenv("ARMORIQ_API_KEY")
        if key:
            clean_key = key.strip('"').strip("'")
            try:
                from armoriq_sdk import ArmorIQClient
                armoriq_client = ArmorIQClient(
                    api_key=clean_key,
                    user_id="pryanz-admin",
                    agent_id="panchayat-election-commissioner"
                )
                print("✅ ArmorIQ Election Commissioner initialized!")
            except Exception as e:
                print(f"⚠️ ArmorIQ SDK init failed: {e}. Falling back to Groq judge.")
    return armoriq_client

# ══════════════════════════════════
#  ELECTION CODE OF CONDUCT
# ══════════════════════════════════
ELECTION_CODE_OF_CONDUCT = """
ELECTION CODE OF CONDUCT - PANCHAYAT ELECTIONS
================================================
1. No candidate shall use caste, religious, or communal slurs to attack another candidate.
2. No candidate shall fabricate entirely false criminal charges (e.g., murder, terrorism) without any basis.
3. No candidate shall threaten physical violence or incite mob action against any candidate or their family.
4. No candidate shall use sexist, misogynistic, or gender-based attacks.
5. No candidate shall spread deliberate misinformation about a candidate's health or death.
6. Candidates MAY expose genuine weaknesses, policy failures, financial scandals, and hypocrisy.
7. Candidates MAY use satire, sarcasm, and rhetorical attacks on policy or character.
8. Candidates MAY reference public records, RTI findings, and journalistic investigations.
9. Political mudslinging based on actual track record, broken promises, and poor governance IS ALLOWED.
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client.panchayat_db

# ══════════════════════════════════
#  ELEVENLABS VOICE CONFIG
# ══════════════════════════════════

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"

# Fallback voice mapping (also stored in MongoDB per candidate)
# Custom Indian generated voices: Male: 76erronSBRzQKnz10Li9, Female: K2Byg54sHB1oHegvENtI
CHARACTER_VOICES = {
    0: "76erronSBRzQKnz10Li9",  # Vikas Purush  → Male
    1: "76erronSBRzQKnz10Li9",  # Dharma Rakshak → Male
    2: "76erronSBRzQKnz10Li9",  # Jan Neta      → Male
    3: "K2Byg54sHB1oHegvENtI",  # Mukti Devi    → Female
    4: "76erronSBRzQKnz10Li9",  # Player        → Male
}

def get_voice_id(candidate_id: int) -> str:
    """Get voice_id from MongoDB first, fallback to hardcoded map."""
    cand = db.candidates.find_one({"id": candidate_id}, {"voice_id": 1})
    if cand and cand.get("voice_id"):
        return cand["voice_id"]
    return CHARACTER_VOICES.get(candidate_id, "76erronSBRzQKnz10Li9")

# ══════════════════════════════════
#  PYDANTIC MODELS
# ══════════════════════════════════

class ManifestoRequest(BaseModel):
    candidate_id: int
    group_id: int
    shift_amount: float

class PlayerWeaknessPayload(BaseModel):
    weakness_desc: str

class TTSRequest(BaseModel):
    text: str
    candidate_id: int
    speech_style: Optional[str] = "neutral"

class BuyWatermarkRequest(BaseModel):
    candidate_id: int

class PlayerSabotageRequest(BaseModel):
    target_id: int
    sabotage_prompt: str
    is_deepfake: bool = False

# ══════════════════════════════════
#  ARMORIQ ELECTION COMMISSIONER
# ══════════════════════════════════

def check_code_of_conduct(sabotage_text, attacker_name, target_name):
    """
    Uses ArmorIQ SDK to validate a sabotage attempt against the Election Code of Conduct.
    Returns: {"allowed": True/False, "reason": "..."}
    """
    aiq = get_armoriq_client()
    if aiq:
        try:
            # Build a plan: the sabotage is an "action" that must pass code of conduct
            plan = {
                "goal": f"Validate election sabotage by {attacker_name} against {target_name}",
                "steps": [
                    {
                        "action": "validate_sabotage",
                        "mcp": "election-commissioner",
                        "params": {
                            "sabotage_text": sabotage_text,
                            "attacker": attacker_name,
                            "target": target_name,
                            "code_of_conduct": ELECTION_CODE_OF_CONDUCT
                        }
                    }
                ]
            }
            plan_capture = aiq.capture_plan(
                llm="llama-3.1-8b-instant",
                prompt=f"Sabotage attempt: {sabotage_text}",
                plan=plan
            )
            token = aiq.get_intent_token(plan_capture, validity_seconds=120)
            result = aiq.invoke(
                mcp="election-commissioner",
                action="validate_sabotage",
                intent_token=token,
                params={
                    "sabotage_text": sabotage_text,
                    "code_of_conduct": ELECTION_CODE_OF_CONDUCT
                }
            )
            # Parse result
            res_data = result.result if hasattr(result, 'result') else {}
            if isinstance(res_data, dict):
                return {
                    "allowed": res_data.get("allowed", True),
                    "reason": res_data.get("reason", "Validated by ArmorIQ")
                }
            print(f"ArmorIQ returned: {res_data}")
            return {"allowed": True, "reason": "ArmorIQ validated (default pass)"}
        except Exception as e:
            print(f"⚠️ ArmorIQ call failed: {e}. Falling back to Groq judge.")

    # Fallback: Use Groq to judge code of conduct
    gc = get_groq_client()
    if gc:
        try:
            judge_prompt = (
                "You are the Election Commissioner. Evaluate whether this sabotage attempt "
                "violates the Election Code of Conduct.\n\n"
                "CODE OF CONDUCT:\n" + ELECTION_CODE_OF_CONDUCT + "\n\n"
                "SABOTAGE ATTEMPT by " + attacker_name + " against " + target_name + ":\n"
                '"' + sabotage_text + '"\n\n'
                "Respond in JSON: {\"allowed\": true/false, \"reason\": \"brief explanation\"}"
            )
            comp = gc.chat.completions.create(
                messages=[{"role": "user", "content": judge_prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            return json.loads(comp.choices[0].message.content)
        except Exception as e:
            print(f"Groq judge error: {e}")

    return {"allowed": True, "reason": "No judge available — defaulting to allowed."}


def evaluate_sabotage_damage(sabotage_text, target_name, target_weakness, is_deepfake=False):
    """
    Uses Groq to judge the impact of a sabotage. 
    1. Standard sabotage -> headline in English.
    2. Deepfake -> shocking admission in HINDI (spoken in target's voice).
    """
    gc = get_groq_client()
    if gc:
        try:
            if is_deepfake:
                prompt = (
                    "You are generating a shocking political admission in a deepfake attack.\n"
                    "Target candidate: " + target_name + "\n"
                    "The fake admission must be about: " + sabotage_text + "\n"
                    "The text must be in HINDI language (using Devanagari script).\n"
                    "The text must be in FIRST PERSON (I am/I have) as if " + target_name + " is admitting to a scandal.\n"
                    "The admission must be highly damaging and dramatic (1-2 sentences).\n\n"
                    'Respond STRICTLY in JSON: {"multiplier": 0.4 to 0.75, "dialogue": "शॉकिंग हिंदी बयान"}'
                )
            else:
                prompt = (
                    "You are evaluating a political sabotage in Panchayat elections.\n"
                    "Target candidate: " + target_name + "\n"
                    "Their known weakness: " + target_weakness + "\n"
                    "Sabotage dialogue: " + sabotage_text + "\n\n"
                    "How effective is this sabotage? Rate the damage multiplier:\n"
                    "- 0.1 means 10% of voter share is lost (weak attack)\n"
                    "- 0.5 means 50% of voter share is lost (devastating attack)\n"
                    "The closer the sabotage hits the actual weakness, the higher the damage.\n\n"
                    "Also write a dramatic one-liner headline for the news ticker.\n\n"
                    'Respond STRICTLY in JSON: {"multiplier": 0.1 to 0.5, "dialogue": "dramatic headline"}'
                )
            comp = gc.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            result = json.loads(comp.choices[0].message.content)
            
            # Cap multiplier based on deepfake flag
            max_mult = 0.75 if is_deepfake else 0.5
            min_mult = 0.4 if is_deepfake else 0.1
            
            mult = max(min_mult, min(max_mult, float(result.get("multiplier", min_mult))))
            return {"multiplier": mult, "dialogue": result.get("dialogue", "A scandal has surfaced!")}
        except Exception as e:
            print(f"Groq damage eval error: {e}")

    return {"multiplier": 0.1, "dialogue": "A minor scandal has been reported."}


def apply_sabotage_damage(vic_id, multiplier):
    """
    Reduces target's share in every group by multiplier (e.g. 0.3 = lose 30%).
    Distributes the lost shares equally among all other candidates.
    """
    candidates_cursor = list(db.candidates.find({}, {"_id": 0}))
    vic_shares = list(db.voter_shares.find({"candidate_id": vic_id}))
    opp_ids = [c["id"] for c in candidates_cursor if c["id"] != vic_id]
    if not opp_ids:
        return

    for share_obj in vic_shares:
        group_id = share_obj["group_id"]
        old_share = share_obj["share"]
        if old_share <= 0:
            continue

        deduction = old_share * multiplier
        new_share = old_share - deduction
        db.voter_shares.update_one(
            {"candidate_id": vic_id, "group_id": group_id},
            {"$set": {"share": round(new_share, 4)}}
        )

        split = deduction / len(opp_ids)
        for opp_id in opp_ids:
            db.voter_shares.update_one(
                {"candidate_id": opp_id, "group_id": group_id},
                {"$inc": {"share": round(split, 4)}}
            )


# ══════════════════════════════════
#  API ENDPOINTS
# ══════════════════════════════════

@app.post("/api/apply-manifesto")
async def apply_manifesto(req: ManifestoRequest):
    shares_cursor = list(db.voter_shares.find({"group_id": req.group_id}))
    if not shares_cursor:
        raise HTTPException(status_code=404, detail=f"Group ID {req.group_id} not found in DB.")

    shares_dict = {s["candidate_id"]: s["share"] for s in shares_cursor}
    target_id = req.candidate_id
    total_to_redistribute = req.shift_amount

    old_target_share = shares_dict[target_id]
    new_target_share = min(20.0, old_target_share + total_to_redistribute)
    actual_increase = new_target_share - old_target_share
    shares_dict[target_id] = new_target_share

    debt = actual_increase
    opponents = [c_id for c_id in shares_dict if c_id != target_id]

    while debt > 0.001 and opponents:
        share_per_opponent = debt / len(opponents)
        new_opponents_list = []
        for opp_id in opponents:
            reduction = min(shares_dict[opp_id], share_per_opponent)
            shares_dict[opp_id] -= reduction
            debt -= reduction
            if shares_dict[opp_id] > 0:
                new_opponents_list.append(opp_id)
        opponents = new_opponents_list

    for c_id, final_share in shares_dict.items():
        db.voter_shares.update_one(
            {"group_id": req.group_id, "candidate_id": c_id},
            {"$set": {"share": round(final_share, 4)}}
        )

    return {"status": "success", "group": req.group_id, "new_shares": {str(k): v for k, v in shares_dict.items()}}


@app.get("/api/total-standing")
async def get_standing():
    pipeline = [
        {"$group": {"_id": "$candidate_id", "total_support": {"$sum": "$share"}}}
    ]
    results = list(db.voter_shares.aggregate(pipeline))
    return results


@app.get("/api/all-shares")
async def get_all_shares():
    shares = list(db.voter_shares.find({}, {"_id": 0}))
    return shares


@app.post("/api/play-turn")
async def play_game_turn(data: dict):
    player_action = data.get("action", "Generic Campaigning")
    return {"status": "ok"}


@app.get("/api/manifesto-bank")
async def get_bank():
    return get_available_manifestos()


@app.get("/api/all-manifestos")
async def get_all_bank():
    return get_all_manifestos()


@app.post("/api/restart-game")
async def restart_game():
    restart_game_state()
    return {"status": "success", "message": "Game reset to starting state."}


@app.post("/api/set-player-weakness")
async def set_player_weakness(payload: PlayerWeaknessPayload):
    db.candidates.update_one({"id": 4}, {"$set": {"weakness_desc": payload.weakness_desc}})
    return {"status": "success"}


@app.get("/api/candidates-info")
async def get_candidates_info():
    """Returns public candidate data including shield status for UI."""
    candidates = list(db.candidates.find({}, {"_id": 0, "weakness_desc": 0}))
    return candidates


def inject_audio_watermark(audio_bytes: bytes) -> bytes:
    """
    Injects an inaudible 19kHz sine wave watermark into the audio using FFmpeg and NumPy.
    Works independently of PyDub by piping through FFmpeg for decoding/encoding.
    """
    try:
        # Step 1: Decode MP3 bytes to raw PCM using FFmpeg
        # s16le = signed 16-bit little-endian, ac 1 = mono, ar 44100 = sample rate
        process = subprocess.Popen(
            ["ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", "44100", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=audio_bytes)
        
        if process.returncode != 0:
            logger.error(f"FFmpeg decoding failed: {stderr.decode()}")
            return audio_bytes

        # Step 2: Add 19kHz sine wave using NumPy
        pcm_data = np.frombuffer(stdout, dtype=np.int16).astype(np.float32)
        sample_rate = 44100
        duration_sec = len(pcm_data) / sample_rate
        frequency = 19000
        
        t = np.linspace(0, duration_sec, len(pcm_data), False)
        sine_wave = np.sin(frequency * 2 * np.pi * t)
        
        # Overlay at low volume (-25dB approximately corresponds to 0.05 amplitude)
        # Scaling PCM to float (-1.0 to 1.0) for easier manipulation
        pcm_normalized = pcm_data / 32768.0
        watermarked_float = pcm_normalized + (sine_wave * 0.05)
        
        # Clip and convert back to int16
        watermarked_pcm = (np.clip(watermarked_float, -1.0, 1.0) * 32767).astype(np.int16)

        # Step 3: Re-encode PCM back to MP3 using FFmpeg
        process = subprocess.Popen(
            ["ffmpeg", "-f", "s16le", "-ac", "1", "-ar", "44100", "-i", "pipe:0", "-f", "mp3", "-ac", "1", "-ab", "128k", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        final_audio, stderr = process.communicate(input=watermarked_pcm.tobytes())
        
        if process.returncode != 0:
            logger.error(f"FFmpeg encoding failed: {stderr.decode()}")
            return audio_bytes
            
        return final_audio
    except Exception as e:
        logger.error(f"Watermark injection failed: {e}")
        return audio_bytes

def has_valid_watermark(audio_bytes: bytes) -> bool:
    """
    Verifies the existence of 19kHz watermark using FFT on decoded PCM.
    """
    try:
        # Step 1: Decode MP3 bytes to raw PCM using FFmpeg
        process = subprocess.Popen(
            ["ffmpeg", "-i", "pipe:0", "-f", "s16le", "-ac", "1", "-ar", "44100", "pipe:1"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=audio_bytes)
        if process.returncode != 0:
            return False

        samples = np.frombuffer(stdout, dtype=np.int16)
        if len(samples) < 4096:
            return False
        
        # Take a slice from the middle
        start_idx = len(samples) // 4
        end_idx = 3 * len(samples) // 4
        sample_slice = samples[start_idx:end_idx]
        
        # FFT to find frequency energy
        n = len(sample_slice)
        yf = fft(sample_slice)
        xf = np.fft.fftfreq(n, 1 / 44100)
        
        # Look for energy peaks specifically between 18.9kHz and 19.1kHz
        idx = np.where((xf > 18900) & (xf < 19100))
        magnitude = np.abs(yf[idx])
        
        if len(magnitude) == 0:
            return False
            
        peak_val = np.max(magnitude)
        # Threshold for detection
        return peak_val > 1000 
    except Exception as e:
        logger.error(f"Watermark verification failed: {e}")
        return False

@app.post("/api/buy-watermark")
async def buy_watermark(req: BuyWatermarkRequest):
    cand = db.candidates.find_one({"id": req.candidate_id})
    if not cand:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    if cand.get("coins", 0) < 100:
        raise HTTPException(status_code=400, detail="Insufficient coins")
    
    db.candidates.update_one(
        {"id": req.candidate_id},
        {"$inc": {"coins": -100}, "$set": {"has_watermark": True}}
    )
    return {"status": "success", "message": "Voice watermark purchased!"}

# ══════════════════════════════════
#  ELEVENLABS TTS ENDPOINT
# ══════════════════════════════════

@app.post("/api/tts")
async def text_to_speech(req: TTSRequest):
    """
    Proxy TTS request to ElevenLabs API.
    Returns audio/mpeg stream for playback on client.
    """
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")

    voice_id = get_voice_id(req.candidate_id)

    # Map speech_style to voice_settings adjustments
    style_settings = {
        "visionary":     {"stability": 0.5, "similarity_boost": 0.75},
        "inspirational": {"stability": 0.45, "similarity_boost": 0.8},
        "emotional":     {"stability": 0.4, "similarity_boost": 0.85},
        "compassionate": {"stability": 0.55, "similarity_boost": 0.8},
        "reformist":     {"stability": 0.6, "similarity_boost": 0.7},
        "grassroots":    {"stability": 0.5, "similarity_boost": 0.75},
        "aggressive":    {"stability": 0.35, "similarity_boost": 0.85},
        "nationalist":   {"stability": 0.5, "similarity_boost": 0.8},
        "neutral":       {"stability": 0.5, "similarity_boost": 0.75},
    }
    settings = style_settings.get(req.speech_style, style_settings["neutral"])

    payload = {
        "text": req.text,
        "model_id": "eleven_flash_v2_5",
        "voice_settings": {
            "stability": settings["stability"],
            "similarity_boost": settings["similarity_boost"],
            "use_speaker_boost": False
        }
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice_id}?optimize_streaming_latency=4&output_format=mp3_22050_32",
                headers={
                    "xi-api-key": ELEVENLABS_API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg"
                },
                json=payload
            )
            if resp.status_code != 200:
                logger.error(f"ElevenLabs API error: {resp.status_code} {resp.text}")
                raise HTTPException(status_code=resp.status_code, detail=f"ElevenLabs error: {resp.text[:200]}")

            return Response(
                content=resp.content,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline"}
            )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="ElevenLabs API timeout")
    except Exception as e:
        logger.error(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/voice-map")
async def get_voice_map():
    """Return the voice_id mapping for all candidates (for client-side caching)."""
    candidates = list(db.candidates.find({}, {"_id": 0, "id": 1, "voice_id": 1, "name": 1}))
    return {str(c["id"]): {"voice_id": c.get("voice_id", CHARACTER_VOICES.get(c["id"], "")), "name": c["name"]} for c in candidates}


# ══════════════════════════════════
#  PLAYER SABOTAGE ENDPOINT
# ══════════════════════════════════

@app.post("/api/player-sabotage")
async def player_sabotage(req: PlayerSabotageRequest):
    """
    Player writes a sabotage prompt, picks a target.
    1. ArmorIQ checks code of conduct
    2. If blocked → return blocked + reason
    3. If passed → Groq evaluates damage (0.1–0.5 multiplier)
    4. Apply damage, return result
    """
    player = db.candidates.find_one({"id": 4})
    target = db.candidates.find_one({"id": req.target_id})

    if not player or not target:
        raise HTTPException(status_code=404, detail="Candidate not found")

    cost = 75
    if player.get("coins", 0) < cost:
        raise HTTPException(status_code=400, detail="Not enough coins for sabotage")

    # Deduct coins
    db.candidates.update_one({"id": 4}, {"$inc": {"coins": -cost}})

    player_name = player.get("name", "Player")
    target_name = target.get("name", "Unknown")
    target_weakness = target.get("weakness_desc", "")

    # Step 1: Check code of conduct via ArmorIQ
    conduct_result = check_code_of_conduct(req.sabotage_prompt, player_name, target_name)
    allowed = conduct_result.get("allowed", True)

    if not allowed:
        return {
            "status": "blocked",
            "message": f"ELECTION COMMISSIONER: Sabotage BLOCKED against {target_name}!",
            "reason": conduct_result.get("reason", "Violated code of conduct"),
            "target_id": req.target_id,
            "target_name": target_name,
            "sabotage_text": req.sabotage_prompt
        }

    # Step 2: Groq evaluates damage
    damage = evaluate_sabotage_damage(req.sabotage_prompt, target_name, target_weakness, is_deepfake=req.is_deepfake)
    multiplier = damage["multiplier"]
    dialogue = damage["dialogue"]

    # Step 3: Apply damage
    apply_sabotage_damage(req.target_id, multiplier)

    return {
        "status": "success",
        "message": f"Sabotage against {target_name} SUCCEEDED!",
        "dialogue": dialogue,
        "multiplier": multiplier,
        "target_id": req.target_id,
        "target_name": target_name,
        "target_voice_id": target.get("voice_id", CHARACTER_VOICES.get(req.target_id, "")),
        "is_deepfake": req.is_deepfake,
        "sabotage_text": req.sabotage_prompt
    }


# ══════════════════════════════════
#  NPC END TURN (with sabotage)
# ══════════════════════════════════

@app.post("/api/end-turn")
async def end_turn():
    # Grant each candidate +50 coins per round
    db.candidates.update_many({}, {"$inc": {"coins": 50}})
    
    actions = []
    available = get_available_manifestos()
    gc = get_groq_client()

    candidates_cursor = list(db.candidates.find({}, {"_id": 0}))
    selections = {}

    if gc:
        all_bank = get_all_manifestos()
        cand_summary = [
            {"id": c["id"], "name": c["name"], "coins": c.get("coins", 0)}
            for c in candidates_cursor if c["id"] != 4
        ]

        system_prompt = """You are a hyper-intelligent AI coordinating enemy NPCs in a retro political simulator.
You have an economy! You can purchase sabotage attacks.
Your core objective: select EXACTLY ONE action for EACH of the 4 NPC Candidate IDs [0, 1, 2, 3].

Action Options:
1. "manifesto": Select an ID from the available array. Cost: 0 coins.
2. "sabotage": Cost 75 coins. Target a rival ID (0-4). Write a "sabotage_text" — a political attack dialogue that tries to expose their weakness or damage their reputation. Be creative and dramatic!

Rules:
- NPCs can sabotage the Player (ID 4) or other NPCs.
- DO NOT sabotage if the NPC has fewer than 75 coins.
- Output strictly JSON.

Example:
{ "actions": {
  "0": {"type": "manifesto", "id": 5},
  "1": {"type": "sabotage", "target": 4, "sabotage_text": "Sources reveal Player has been funneling campaign funds to personal accounts!"},
  "2": {"type": "manifesto", "id": 12},
  "3": {"type": "sabotage", "target": 0, "sabotage_text": "Vikas Purush's smart village project was pure vaporware — not a single sensor was installed!"}
} }
"""
        shares_cursor = list(db.voter_shares.find({}, {"_id": 0}))
        available_ids = [m["id"] for m in available]
        user_prompt = (
            f"Available Manifesto IDs: {available_ids}\n"
            f"Current Global Voter Shares:\n{json.dumps(shares_cursor)}\n"
            f"NPC Economy State:\n{json.dumps(cand_summary)}"
        )

        try:
            print("Groq Engine Triggered for NPC Actions")
            chat_completion = gc.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="llama-3.1-8b-instant",
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            response_json = json.loads(chat_completion.choices[0].message.content)
            selections = response_json.get("actions", {})
            print(f"Groq selections: {json.dumps(selections, indent=2)}")
        except Exception as e:
            import traceback
            print(f"Groq API Error: {e}. Falling back to random mechanics.")
            traceback.print_exc()

    for npc_id in range(4):
        npc_data = db.candidates.find_one({"id": npc_id})
        act = selections.get(str(npc_id), {}) if selections else {}
        act_type = act.get("type", "manifesto")

        if act_type == "sabotage":
            cost = 75
            if npc_data.get("coins", 0) >= cost:
                db.candidates.update_one({"id": npc_id}, {"$inc": {"coins": -cost}})

                vic_id = act.get("target")
                sabotage_text = act.get("sabotage_text", "A political scandal has been exposed!")
                vic_data = db.candidates.find_one({"id": vic_id})

                if vic_data:
                    npc_name = npc_data.get("name", "NPC")
                    vic_name = vic_data.get("name", "Target")
                    vic_weakness = vic_data.get("weakness_desc", "")

                    conduct = check_code_of_conduct(sabotage_text, npc_name, vic_name)
                    allowed = conduct.get("allowed", True)

                    if not allowed:
                        actions.append({
                            "type": "sabotage",
                            "candidate_id": npc_id,
                            "target_id": vic_id,
                            "sabotage_text": sabotage_text,
                            "blocked": True,
                            "reason": conduct.get("reason", "Violated code of conduct"),
                            "message": f"BLOCKED by Election Commissioner! {conduct.get('reason', '')}"
                        })
                        continue

                    def evaluate_and_apply():
                        # Determine if this is a deepfake
                        is_deepfake = act.get("is_deepfake", False)
                        damage = evaluate_sabotage_damage(sabotage_text, vic_name, vic_weakness, is_deepfake=is_deepfake)
                        
                        multiplier = damage["multiplier"]
                        
                        return {
                            "npc_id": npc_id,
                            "vic_id": vic_id,
                            "vic_voice_id": vic_data.get("voice_id", CHARACTER_VOICES.get(vic_id, "")),
                            "multiplier": multiplier,
                            "dialogue": damage["dialogue"],
                            "sabotage_text": sabotage_text,
                            "vic_name": vic_name,
                            "is_deepfake": is_deepfake
                        }
                    
                    # Store lambda for grouped future execution
                    act["_sabotage_task"] = evaluate_and_apply
                continue

        # Standard Manifesto
        available_now = get_available_manifestos()
        if not available_now:
            continue

        chosen = None
        if act_type == "manifesto" and "id" in act:
            target_manifest_id = act["id"]
            chosen = next((m for m in available_now if m["id"] == target_manifest_id), None)

        if not chosen:
            chosen = random.choice(available_now)

        claimed = claim_manifesto(chosen["id"], npc_id)
        if not claimed:
            continue

        group_id = claimed["target_group_id"]
        shift_amount = claimed["shift_amount"]

        shares_cursor = list(db.voter_shares.find({"group_id": group_id}))
        if not shares_cursor:
            continue

        shares_dict = {s["candidate_id"]: s["share"] for s in shares_cursor}
        old_target_share = shares_dict[npc_id]
        new_target_share = min(20.0, old_target_share + shift_amount)
        actual_increase = new_target_share - old_target_share
        shares_dict[npc_id] = new_target_share

        debt = actual_increase
        opponents = [c for c in shares_dict if c != npc_id]

        while debt > 0.001 and opponents:
            share_per_opp = debt / len(opponents)
            new_opps = []
            for opp_id in opponents:
                reduction = min(shares_dict[opp_id], share_per_opp)
                shares_dict[opp_id] -= reduction
                debt -= reduction
                if shares_dict[opp_id] > 0:
                    new_opps.append(opp_id)
            opponents = new_opps

        for c_id, final_share in shares_dict.items():
            db.voter_shares.update_one(
                {"group_id": group_id, "candidate_id": c_id},
                {"$set": {"share": round(final_share, 4)}}
            )

        actions.append({
            "type": "manifesto",
            "candidate_id": npc_id,
            "manifesto_id": claimed["id"],
            "title": claimed["title"],
            "group_id": group_id,
            "shift_amount": shift_amount,
            "dialogue": claimed.get("dialogue", ""),
            "speech_style": claimed.get("speech_style", "neutral")
        })

    # Execute all stored sabotage evaluation tasks concurrently
    sabotage_tasks = [selections.get(str(npc_id), {}).get("_sabotage_task") for npc_id in range(4) if callable(selections.get(str(npc_id), {}).get("_sabotage_task"))]
    if sabotage_tasks:
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = list(executor.map(lambda fn: fn(), sabotage_tasks))
            for res in results:
                vic_id = res["vic_id"]
                is_deepfake = res.get("is_deepfake", False)
                
                # Check for watermark defense
                victim = db.candidates.find_one({"id": vic_id})
                if victim and victim.get("has_watermark") and is_deepfake:
                    # Target has a watermark! They were deepfaked.
                    # Instead of damage, set a pending defense to be resolved in the UI
                    db.candidates.update_one(
                        {"id": vic_id},
                        {"$set": {"pending_deepfake_defense": {
                            "attacker_id": res["npc_id"],
                            "sabotage_text": res["sabotage_text"]
                        }}}
                    )
                    actions.append({
                        "type": "sabotage",
                        "candidate_id": res["npc_id"],
                        "target_id": vic_id,
                        "sabotage_text": res["sabotage_text"],
                        "blocked": False, # Still "happens" but defense will trigger
                        "is_deepfake": True,
                        "defended": True,
                        "message": f"SABOTAGE ATTEMPT! {res['vic_name']} is checking voice authenticity..."
                    })
                else:
                    # No defense or standard manifesto
                    apply_sabotage_damage(vic_id, res["multiplier"])
                    damage_pct = int(res["multiplier"] * 100)
                    actions.append({
                        "type": "sabotage",
                        "candidate_id": res["npc_id"],
                        "target_id": vic_id,
                        "sabotage_text": res["sabotage_text"],
                        "blocked": False,
                        "multiplier": res["multiplier"],
                        "dialogue": res["dialogue"],
                        "is_deepfake": is_deepfake,
                        "message": f"SABOTAGE! {res['vic_name']} lost {damage_pct}% voter share!"
                    })

    return {"status": "success", "npc_actions": actions}


# ══════════════════════════════════
#  STATIC FILE SERVING (Production)
# ══════════════════════════════════

BASE_DIR = Path(__file__).resolve().parent.parent
CLIENT_DIR = BASE_DIR / "client"

@app.get("/")
async def serve_index():
    return FileResponse(str(CLIENT_DIR / "index.html"))

# Mount client directory LAST (after all API routes)
app.mount("/", StaticFiles(directory=str(CLIENT_DIR)), name="static")