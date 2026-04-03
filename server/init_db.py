import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.panchayat_db

def restart_game_state():
    # 1. Clear Collections
    db.candidates.delete_many({})
    db.voter_groups.delete_many({})
    db.voter_shares.delete_many({})

    # 2. Setup 5 Candidates with Roles and Archetypes
    # These archetypes MUST match your 'bridge/ai_prompts.py' keys
    candidates = [
        {"id": 0, "name": "Vikas Purush", "role": "npc", "archetype": "vikas_purush", "manifesto_settled": False},
        {"id": 1, "name": "Dharma Rakshak", "role": "npc", "archetype": "dharma_rakshak", "manifesto_settled": False},
        {"id": 2, "name": "Jan Neta", "role": "npc", "archetype": "jan_neta", "manifesto_settled": False},
        {"id": 3, "name": "Mukti Devi", "role": "npc", "archetype": "mukti_devi", "manifesto_settled": False},
        {"id": 4, "name": "Player", "role": "player", "archetype": "player", "manifesto_settled": False},
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
    
    print("✅ Database Reset: Data initialized with Roles and Archetypes.")

if __name__ == "__main__":
    restart_game_state()