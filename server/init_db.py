import os
from pymongo import MongoClient
from dotenv import load_dotenv
from data.manifesto_bank import MANIFESTO_BANK
import time

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path, override=True)
client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=10000)
db = client.panchayat_db

import json
import random

with open("data/weaknesses.json", "r") as f:
    ALL_WEAKNESSES = json.load(f)

def get_weakness_desc(archetype):
    wks = ALL_WEAKNESSES.get(archetype, [])
    if not wks: return ""
    return random.choice(wks)["description"]

def restart_game_state(session_id: str):
    # 1. Clear Collections for this session only
    db.candidates.delete_many({"session_id": session_id})
    db.voter_groups.delete_many({"session_id": session_id})
    db.voter_shares.delete_many({"session_id": session_id})
    db.manifestos.delete_many({"session_id": session_id})
    db.sessions.delete_many({"session_id": session_id})

    # 2. Setup 5 Candidates with Roles and Archetypes
    candidates = [
        {"session_id": session_id, "id": 0, "name": "Vikas Purush", "role": "npc", "archetype": "vikas_purush", "manifesto_settled": False, "coins": 300, "shield_active": True, "weakness_desc": get_weakness_desc("vikas_purush"), "voice_id": "76erronSBRzQKnz10Li9", "has_watermark": False, "pending_deepfake_defense": None},
        {"session_id": session_id, "id": 1, "name": "Dharma Rakshak", "role": "npc", "archetype": "dharma_rakshak", "manifesto_settled": False, "coins": 300, "shield_active": True, "weakness_desc": get_weakness_desc("dharma_rakshak"), "voice_id": "76erronSBRzQKnz10Li9", "has_watermark": False, "pending_deepfake_defense": None},
        {"session_id": session_id, "id": 2, "name": "Jan Neta", "role": "npc", "archetype": "jan_neta", "manifesto_settled": False, "coins": 300, "shield_active": True, "weakness_desc": get_weakness_desc("jan_neta"), "voice_id": "K2Byg54sHB1oHegvENtI", "has_watermark": False, "pending_deepfake_defense": None},
        {"session_id": session_id, "id": 3, "name": "Mukti Devi", "role": "npc", "archetype": "mukti_devi", "manifesto_settled": False, "coins": 300, "shield_active": True, "weakness_desc": get_weakness_desc("mukti_devi"), "voice_id": "K2Byg54sHB1oHegvENtI", "has_watermark": False, "pending_deepfake_defense": None},
        {"session_id": session_id, "id": 4, "name": "Player", "role": "player", "archetype": "player", "manifesto_settled": False, "coins": 300, "shield_active": True, "weakness_desc": get_weakness_desc("player"), "voice_id": "76erronSBRzQKnz10Li9", "has_watermark": False, "pending_deepfake_defense": None},
    ]
    db.candidates.insert_many(candidates)

    # 3. Setup 5 Voter Groups
    group_names = ["Farmers", "Students", "Tech Workers", "Laborers", "Youth"]
    db.voter_groups.insert_many([
        {"session_id": session_id, "id": i, "name": name, "total_weight": 20.0} 
        for i, name in enumerate(group_names)
    ])

    # 4. Setup Initial Shares (4% per candidate per group)
    initial_shares = []
    for g_id in range(5):
        for c_id in range(5):
            initial_shares.append({
                "session_id": session_id,
                "group_id": g_id,
                "candidate_id": c_id,
                "share": 4.0 
            })
    db.voter_shares.insert_many(initial_shares)
    
    # 5. Initialize Manifesto Bank for this session
    session_manifestos = []
    for m in MANIFESTO_BANK:
        m_copy = m.copy()
        m_copy["session_id"] = session_id
        m_copy["used_by"] = None
        session_manifestos.append(m_copy)
    db.manifestos.insert_many(session_manifestos)

    # 6. Initialize Session Tracking
    db.sessions.update_one(
        {"session_id": session_id},
        {"$set": {"last_activity": time.time()}},
        upsert=True
    )

    print(f"✅ Database Session Initialized: {session_id}")

if __name__ == "__main__":
    restart_game_state()