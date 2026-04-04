from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import os
import random
from dotenv import load_dotenv
from pydantic import BaseModel
from data.manifesto_bank import get_available_manifestos, claim_manifesto, get_all_manifestos
from server.init_db import restart_game_state

load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGO_URI"))
db = client.panchayat_db

class ManifestoRequest(BaseModel):
    candidate_id: int
    group_id: int
    shift_amount: float

@app.post("/api/apply-manifesto")
async def apply_manifesto(req: ManifestoRequest):
    # 1. Fetch current shares for this specific group
    shares_cursor = list(db.voter_shares.find({"group_id": req.group_id}))
    
    # NEW: Safety check to prevent 500 errors
    if not shares_cursor:
        raise HTTPException(status_code=404, detail=f"Group ID {req.group_id} not found in DB.")

    shares_dict = {s["candidate_id"]: s["share"] for s in shares_cursor}

    target_id = req.candidate_id
    total_to_redistribute = req.shift_amount

    # 2. Apply Gain to Target (Cap at 20%)
    old_target_share = shares_dict[target_id]
    new_target_share = min(20.0, old_target_share + total_to_redistribute)
    actual_increase = new_target_share - old_target_share
    shares_dict[target_id] = new_target_share

    # 3. Waterfall Redistribution from Opponents
    # We need to take 'actual_increase' from others
    debt = actual_increase
    opponents = [c_id for c_id in shares_dict if c_id != target_id]

    while debt > 0.001 and opponents:
        share_per_opponent = debt / len(opponents)
        new_opponents_list = []
        
        for opp_id in opponents:
            reduction = min(shares_dict[opp_id], share_per_opponent)
            shares_dict[opp_id] -= reduction
            debt -= reduction
            
            # If this opponent still has juice, keep them for next round of debt
            if shares_dict[opp_id] > 0:
                new_opponents_list.append(opp_id)
        
        opponents = new_opponents_list

    # 4. Bulk Update MongoDB
    for c_id, final_share in shares_dict.items():
        db.voter_shares.update_one(
            {"group_id": req.group_id, "candidate_id": c_id},
            {"$set": {"share": round(final_share, 4)}}
        )

    return {"status": "success", "group": req.group_id, "new_shares": {str(k): v for k, v in shares_dict.items()}}

@app.get("/api/total-standing")
async def get_standing():
    # Sums up all shares across all groups for each candidate
    pipeline = [
        {"$group": {"_id": "$candidate_id", "total_support": {"$sum": "$share"}}}
    ]
    results = list(db.voter_shares.aggregate(pipeline))
    return results

@app.get("/api/all-shares")
async def get_all_shares():
    # Returns all shares with group_id and candidate_id
    shares = list(db.voter_shares.find({}, {"_id": 0}))
    return shares


# In server/main.py
@app.post("/api/play-turn")
async def play_game_turn(data: dict):
    # 'data' will be {"action": "I promise free water"} from React
    player_action = data.get("action", "Generic Campaigning")
    
    # Initialize connection
    gs = GameState()
    
    # Run the round
    result = run_full_turn(player_action, gs)
    
    return result


@app.get("/api/manifesto-bank")
async def get_bank():
    # This calls your helper function and returns the list as JSON
    return get_available_manifestos()

@app.get("/api/all-manifestos")
async def get_all_bank():
    return get_all_manifestos()

@app.post("/api/restart-game")
async def restart_game():
    # Call the database reset logic from init_db
    restart_game_state()
    return {"status": "success", "message": "Game reset to starting state."}

@app.post("/api/end-turn")
async def end_turn():
    # Iterate through NPCs 0 to 3
    actions = []
    
    for npc_id in range(4):
        available = get_available_manifestos()
        if not available:
            break
        chosen = random.choice(available)
        claimed = claim_manifesto(chosen["id"], npc_id)
        if not claimed:
            continue
            
        # Apply waterfall mechanics for the NPC precisely as apply_manifesto does
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
            "candidate_id": npc_id,
            "manifesto_id": claimed["id"],
            "title": claimed["title"],
            "group_id": group_id,
            "shift_amount": shift_amount
        })
        
    return {"status": "success", "npc_actions": actions}