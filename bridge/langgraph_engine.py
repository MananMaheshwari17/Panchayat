"""
Panchayat Bridge — LangGraph Engine
=====================================
The core agentic workflow manager. Implements a StateGraph that:
1. Receives the player's policy action
2. For each AI candidate: uses Gemini + tools to generate an in-character reaction
3. Updates voter sentiments and election forecast

Rate-limit aware: adds delays between Gemini calls to stay within free-tier limits.
Uses gemini-2.5-flash-lite (10 RPM, 20 RPD) as the primary model.
"""

import os
import sys
import time
from typing import TypedDict
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
try:
    from langchain.agents import create_react_agent
except ImportError:
    from langgraph.prebuilt import create_react_agent

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from bridge.ai_prompts import (
    get_candidate_system_prompt,
    get_candidate_info,
    get_all_candidate_ids,
    build_reaction_prompt,
)
from bridge.tools_langchain import get_all_tools
from data.ideology_engine import (
    load_candidates,
    get_candidate_ideologies,
    rank_candidates_for_voter,
    simulate_election_result,
    compute_ideology_distance,
)
from data.voter_profiles import VOTER_PROFILES, calculate_reaction

# Load environment
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

# ─── Rate Limit Config ──────────────────────────────────────────────────────
# gemini-2.5-flash-lite: 10 RPM = 1 request per 6 seconds
# We add a 7-second delay between calls to be safe
RATE_LIMIT_DELAY = 7  # seconds between Gemini API calls


# ─── Game State ──────────────────────────────────────────────────────────────

class GameState:
    """Mutable game state that persists across turns."""

    def __init__(self):
        self.turn_number = 0
        self.voter_sentiments = {
            vid: vp.base_happiness for vid, vp in VOTER_PROFILES.items()
        }
        self.candidate_scores = {
            cid: 50.0 for cid in get_all_candidate_ids()
        }
        self.history = []

    def to_dict(self):
        return {
            "turn": self.turn_number,
            "voter_sentiments": dict(self.voter_sentiments),
            "candidate_scores": dict(self.candidate_scores),
        }


# ─── LangGraph Agent Factory ────────────────────────────────────────────────

def _get_model_name() -> str:
    """Get the best available model from env, with fallback chain."""
    return os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")


def create_candidate_agent(candidate_id: str):
    """
    Create a LangGraph ReAct agent for a specific candidate.
    Uses gemini-3.1-flash-lite for speed + rate limit friendliness.
    """
    model_name = _get_model_name()
    system_prompt = get_candidate_system_prompt(candidate_id)

    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.8,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_retries=3,
        request_timeout=30,
    )

    tools = get_all_tools()

    agent = create_react_agent(
        llm,
        tools,
        prompt=system_prompt,
    )

    return agent


def run_candidate_reaction(candidate_id: str, player_action: str, callback=None) -> str:
    """
    Run a single candidate's reaction using ReAct agent.
    Includes rate-limit delay and error handling with retry.
    """
    max_retries = 2

    for attempt in range(max_retries):
        try:
            agent = create_candidate_agent(candidate_id)
            user_prompt = build_reaction_prompt(candidate_id, player_action)

            result = agent.invoke({
                "messages": [HumanMessage(content=user_prompt)]
            })

            # Extract final response
            messages = result.get("messages", [])
            for msg in reversed(messages):
                if hasattr(msg, "content") and msg.content and not getattr(msg, "tool_calls", None):
                    return msg.content

            return "[No response generated]"

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                # Rate limited — wait and retry
                wait_time = RATE_LIMIT_DELAY * (attempt + 2)
                if callback:
                    callback(f"Rate limited, waiting {wait_time}s...")
                time.sleep(wait_time)
            elif attempt < max_retries - 1:
                time.sleep(RATE_LIMIT_DELAY)
            else:
                return f"[Error after {max_retries} attempts: {error_msg[:150]}]"

    return "[Failed to get response]"


def run_full_turn(player_action: str, game_state: GameState, callback=None) -> dict:
    """
    Run a complete game turn with rate-limit awareness.
    callback(status_message) is called with progress updates.
    """
    game_state.turn_number += 1
    candidate_ids = get_all_candidate_ids()
    candidate_reactions = {}

    # Phase 1: Get reactions from all 4 candidates (with delays)
    for i, cid in enumerate(candidate_ids):
        info = get_candidate_info(cid)

        if callback:
            callback(f"{info['emoji']} {info['name']} is thinking... ({i+1}/4)")

        reaction = run_candidate_reaction(cid, player_action, callback)
        candidate_reactions[cid] = {
            "name": info["name"],
            "archetype": info["archetype"],
            "emoji": info["emoji"],
            "reaction": reaction,
        }

        # Rate limit delay between candidates (skip after last)
        if i < len(candidate_ids) - 1:
            if callback:
                callback(f"Cooling down ({RATE_LIMIT_DELAY}s rate limit)...")
            time.sleep(RATE_LIMIT_DELAY)

    # Phase 2: Update voter sentiments
    category = _detect_category(player_action)
    sentiment_changes = {}

    for vid, vp in VOTER_PROFILES.items():
        reaction_result = calculate_reaction(vid, {
            "category": category,
            "direction": 1,
            "magnitude": 0.6,
            "description": player_action,
        })
        old = game_state.voter_sentiments[vid]
        shift = reaction_result["sentiment_shift"]
        new = max(0, min(100, old + shift))
        game_state.voter_sentiments[vid] = new
        sentiment_changes[vid] = {
            "name": vp.name_en,
            "emoji": vp.emoji,
            "old": round(old, 1),
            "new": round(new, 1),
            "shift": round(shift, 1),
            "narrative": reaction_result["narrative"],
        }

    # Phase 3: Recalculate election forecast
    candidate_ideologies = get_candidate_ideologies()
    mock_sentiments = {}
    for vid, vp in VOTER_PROFILES.items():
        sentiments = {}
        current_happiness = game_state.voter_sentiments[vid]
        for cid in candidate_ids:
            sim = compute_ideology_distance(vp.ideology_alignment, candidate_ideologies[cid])
            sentiments[cid] = sim * current_happiness
        sentiments["player"] = current_happiness * 0.85
        mock_sentiments[vid] = sentiments

    voter_pops = {vid: vp.population_pct for vid, vp in VOTER_PROFILES.items()}
    election = simulate_election_result(mock_sentiments, voter_pops)

    game_state.history.append({
        "turn": game_state.turn_number,
        "action": player_action,
        "reactions": {k: v["reaction"] for k, v in candidate_reactions.items()},
    })

    return {
        "turn": game_state.turn_number,
        "player_action": player_action,
        "candidate_reactions": candidate_reactions,
        "sentiment_changes": sentiment_changes,
        "election_forecast": election,
        "game_state": game_state.to_dict(),
    }


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _detect_category(action: str) -> str:
    """Simple keyword-based category detection."""
    action_lower = action.lower()
    categories = {
        "msp": "msp_guarantee", "farm": "msp_guarantee",
        "agri": "crop_insurance", "crop": "crop_insurance",
        "irrig": "water_irrigation", "water": "water_irrigation",
        "land": "land_rights",
        "tech": "technology_access", "digital": "technology_access",
        "5g": "technology_access", "app": "technology_access",
        "startup": "employment", "job": "employment", "employ": "employment",
        "tax": "gst_tax_reform", "gst": "gst_tax_reform",
        "business": "easy_credit_loans", "loan": "easy_credit_loans",
        "health": "healthcare_maternal", "hospital": "healthcare_maternal",
        "education": "education_skills", "school": "education_children",
        "pension": "pension_security", "salary": "pay_commission",
        "women": "safety_security", "safety": "safety_security",
        "shg": "shg_microfinance",
        "welfare": "subsidies_loans", "subsid": "subsidies_loans",
        "ration": "nutrition_food_security", "food": "nutrition_food_security",
        "mnrega": "subsidies_loans", "work": "employment",
        "reform": "governance_transparency", "corrupt": "governance_transparency",
        "blockchain": "governance_transparency", "transparen": "governance_transparency",
    }
    for keyword, cat in categories.items():
        if keyword in action_lower:
            return cat
    return "governance_transparency"


# ─── Quick Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("Testing LangGraph Engine")
    print("=" * 50)
    api_key = os.getenv("GOOGLE_API_KEY", "")
    print(f"API Key: {'...'+api_key[-6:] if api_key else 'NOT SET!'}")
    print(f"Model: {_get_model_name()}")
    print(f"Candidates: {get_all_candidate_ids()}")
    print(f"Rate limit delay: {RATE_LIMIT_DELAY}s between calls")

    print("\n--- Single candidate test ---")
    print("Calling Gemini API (may take 10-20s)...")

    def print_status(msg):
        print(f"  [{msg}]")

    reaction = run_candidate_reaction(
        "dharma_rakshak",
        "Increase MSP by 50% for all crops",
        callback=print_status,
    )
    print(f"\n🕉️ Dharma Rakshak says:\n{reaction}")
