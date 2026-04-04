import os
from pymongo import MongoClient
from dotenv import load_dotenv
from data.manifesto_bank import MANIFESTO_BANK

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

def restart_game_state():
    # 1. Clear Collections
    db.candidates.delete_many({})
    db.voter_groups.delete_many({})
    db.voter_shares.delete_many({})

    # 2. Setup 5 Candidates with Roles and Archetypes
    candidates = [
        {"id": 0, "name": "Vikas Purush", "role": "npc", "archetype": "vikas_purush", "manifesto_settled": False, "coins": 200, "shield_active": True, "weakness_desc": get_weakness_desc("vikas_purush")},
        {"id": 1, "name": "Dharma Rakshak", "role": "npc", "archetype": "dharma_rakshak", "manifesto_settled": False, "coins": 200, "shield_active": True, "weakness_desc": get_weakness_desc("dharma_rakshak")},
        {"id": 2, "name": "Jan Neta", "role": "npc", "archetype": "jan_neta", "manifesto_settled": False, "coins": 200, "shield_active": True, "weakness_desc": get_weakness_desc("jan_neta")},
        {"id": 3, "name": "Mukti Devi", "role": "npc", "archetype": "mukti_devi", "manifesto_settled": False, "coins": 200, "shield_active": True, "weakness_desc": get_weakness_desc("mukti_devi")},
        {"id": 4, "name": "Player", "role": "player", "archetype": "player", "manifesto_settled": False, "coins": 200, "shield_active": True, "weakness_desc": get_weakness_desc("player")},
    ]
    db.candidates.insert_many(candidates)

    # 3. Setup 5 Voter Groups
    group_names = ["Farmers", "Students", "Tech Workers", "Laborers", "Youth"]
    db.voter_groups.insert_many([
        {"id": i, "name": name, "total_weight": 20.0} 
        for i, name in enumerate(group_names)
    ])

    # 4. Setup Initial Shares (4% per candidate per group)
    initial_shares = []
    for g_id in range(5):
        for c_id in range(5):
            initial_shares.append({
                "group_id": g_id,
                "candidate_id": c_id,
                "share": 4.0 
            })
    db.voter_shares.insert_many(initial_shares)
    
    # 5. Reset Manifesto Bank
    for m in MANIFESTO_BANK:
        m["used_by"] = None

    print("✅ Database Reset: Data initialized with Roles and Archetypes.")

if __name__ == "__main__":
    restart_game_state()