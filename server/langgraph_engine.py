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
import random
import os
import sys
import time
from typing import TypedDict
from dotenv import load_dotenv
from data.manifesto_bank import get_available_manifestos , claim_manifesto

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
try:
    from langchain.agents import create_react_agent
except ImportError:
    from langgraph.prebuilt import create_react_agent


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)



# 2. Look for the .env specifically in the server/ folder
env_path = os.path.join(SCRIPT_DIR, ".env")
load_dotenv(env_path)

ID_TO_GROUP = {
    0: "Farmers",
    1: "Students",
    2: "Tech Workers",
    3: "Laborers",
    4: "Youth"
}

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
    """Game state that fetches live data from MongoDB Atlas."""

    def __init__(self):

        mongo_uri = os.getenv("MONGO_URI")
        if not mongo_uri:
            raise ValueError("MONGO_URI not found in .env file!")

        self.client = MongoClient(mongo_uri)
        self.db = self.client.panchayat_db
        self.turn_number = 0
        self.history = []

    def fetch_latest_shares(self):
        """Pull the current voter shares from the Cloud."""
        return list(self.db.voter_shares.find())

    def get_world_summary(self) -> str:
        """
        Fetches Names and Roles from DB to build a narrative context for Gemini.
        """
        # Fetch candidate info once to avoid multiple DB calls in the loop
        candidate_docs = list(self.db.candidates.find())
        candidate_map = {c['id']: c for c in candidate_docs}
        
        shares = self.fetch_latest_shares()
        
        summary = f"--- CURRENT ELECTION STATUS (Turn {self.turn_number}) ---\n"
        
        for g_id, g_name in ID_TO_GROUP.items():
            summary += f"\nVoter Group: {g_name} (Total Weight: 20% of population)\n"
            
            # Filter shares belonging to this specific group
            group_data = [s for s in shares if s["group_id"] == g_id]
            
            for data in group_data:
                c_id = data['candidate_id']
                info = candidate_map.get(c_id, {"name": f"Unknown({c_id})", "role": "npc"})
                
                # Tag the player so the AI knows who its human rival is
                role_tag = "[YOU - THE HUMAN PLAYER]" if info.get('role') == "player" else "[AI OPPONENT]"
                
                summary += f"  - {info['name']} {role_tag}: {data['share']:.2f}%\n"
        
        return summary

    def to_dict(self):
        """Used for JSON logging/history."""
        return {
            "turn": self.turn_number,
            "shares": self.fetch_latest_shares(),
            "history_length": len(self.history)
        }


# ─── LangGraph Agent Factory ────────────────────────────────────────────────

def _get_model_name() -> str:
    """Get the best available model from env, with fallback chain."""
    return os.getenv("GEMINI_FLASH_MODEL", "gemini-2.5-flash")


def create_candidate_agent(candidate_id: int):
    """
    Creates a ReAct agent by fetching the archetype and persona 
    from MongoDB Atlas for a specific candidate ID.
    """
    # 1. Connect to Mongo to find the candidate's personality "DNA"
    from pymongo import MongoClient

    mongo_uri = os.getenv("MONGO_URI")

    client = MongoClient(mongo_uri)
    db = client.panchayat_db
    
    # 2. Fetch the specific candidate data
    candidate_data = db.candidates.find_one({"id": candidate_id})
    
    if not candidate_data:
        raise ValueError(f"Candidate with ID {candidate_id} not found in MongoDB!")

    # 3. Use the 'archetype' field to get the specific System Prompt
    # (e.g., 'dharma_rakshak' or 'vikas_purush')
    archetype = candidate_data.get('archetype', 'jan_neta')
    system_prompt = get_candidate_system_prompt(archetype)

    model_name = _get_model_name()
    
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.8,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_retries=3,
        request_timeout=30,
    )

    # 4. Get the tools (which now hit your FastAPI -> Mongo bridge)
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
    Simulates one full round. NPCs pick randomly from the bank 
    to test the frontend connection without API costs.
    """
    game_state.turn_number += 1
    
    # 1. Get NPC list from DB
    ai_candidates = list(game_state.db.candidates.find({"role": "npc"}))
    turn_log = []

    # Phase 1: NPC Mock Simulation
    for cand in ai_candidates:
        cid = cand['id']
        name = cand['name']
        
        # Get what's left in the bank
        available = get_available_manifestos()
        
        if available:
            # --- RANDOM SELECTION FOR TESTING ---
            chosen_manifesto = random.choice(available)
            
            # Execute the shift via the FastAPI tool
            claim_and_deploy_manifesto(
                manifesto_id=chosen_manifesto['id'], 
                candidate_id=cid
            )
            
            # Log specific details for the frontend to display
            turn_log.append({
                "candidate": name, 
                "action": f"Deployed: {chosen_manifesto['title']}",
                "target_group": chosen_manifesto['target_group_id']
            })

    # Phase 2: Final State Fetch
    # We pull from DB to get the results of the "Waterfall Math"
    updated_shares = game_state.fetch_latest_shares()
    candidate_names = {c['id']: c['name'] for c in game_state.db.candidates.find()}
    
    # Phase 3: Format Forecast for React
    final_forecast = {}
    for share in updated_shares:
        c_name = candidate_names.get(share['candidate_id'], "Unknown")
        final_forecast[c_name] = final_forecast.get(c_name, 0) + share['share']

    return {
        "turn": game_state.turn_number,
        "player_action": player_action,
        "log": turn_log,
        "election_forecast": {n: round(v, 2) for n, v in final_forecast.items()},
        "game_state": "Sync Complete"
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
    from pymongo import MongoClient
    print("🚀 STARTING FULL SYSTEM TEST...")
    
    # 1. Initialize Game State
    try:
        gs = GameState()
        print("✅ Connected to MongoDB Atlas")
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        sys.exit(1)

    # 2. Define a Player Action
    # This is what the AI candidates will react to.
    player_move = "I am promising 50% reservation in local tech jobs for village youth."
    
    print(f"\n--- Turn 1 Test ---")
    print(f"Player Action: {player_move}")
    print("--------------------------------------------------")

    def status_callback(msg):
        print(f"  > {msg}")

    # 3. Run the Full Turn
    # This triggers: Fetch DB -> Prompt AI -> AI Tool calls Bridge -> Bridge updates DB -> Return
    results = run_full_turn(player_move, gs, callback=status_callback)

    print("\n--- TEST RESULTS ---")
    print(f"Turn Number: {results['turn']}")
    
    print("\n💬 Candidate Reactions:")
    for cid, data in results['candidate_reactions'].items():
        print(f"[{data['name']}]: {data['reaction'][:100]}...")

    print("\n📊 New Election Forecast (Should have changed from 20% each):")
    for name, score in results['election_forecast'].items():
        print(f" - {name}: {score}%")

    print("\n✅ Test Complete. Check your MongoDB Atlas browser to see the 'Waterfall' shifts!")
