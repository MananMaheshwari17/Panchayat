using SpacetimeDB;
using System;
using System.Collections.Generic;
using System.Linq;

namespace SpacetimeDB.Modules.Panchayat
{
    // 1. Table for the 5 Candidates
    [Table(Public = true)]
    public partial struct Candidate
    {
        [PrimaryKey]
        public uint CandidateId;
        public string Name;
        public float TotalPopularity;
    }

    // 2. Table for the 5 Voter Groups
    [Table(Public = true)]
    public partial struct VoterGroup
    {
        [PrimaryKey]
        public uint GroupId;
        public string Name;
        public float PopulationWeight;
    }

    // 3. Table for the 20% Initial Share Distribution
    [Table(Public = true)]
    public partial struct VoterShare
    {
        [PrimaryKey]
        public string CombinedId; // e.g., "0_1"
        public uint GroupId;
        public uint CandidateId;
        public float SharePercent;
    }

    public static partial class Module
    {
        [Reducer(ReducerKind.Init)]
        public static void Init(ReducerContext ctx)
        {
            string[] names = { "Students", "Farmers", "Tech", "Labor", "Youth" };
            
            for (uint i = 0; i < 5; i++)
            {
                // 1. Create the Group (20% of total population each)
                ctx.Db.VoterGroup.Insert(new VoterGroup { 
                    GroupId = i, 
                    Name = names[i], 
                    PopulationWeight = 0.20f 
                });
                
                for (uint c = 0; c < 5; c++)
                {
                    // 2. Initial Global Share: (20% group total / 5 candidates) = 4% each
                    ctx.Db.VoterShare.Insert(new VoterShare { 
                        CombinedId = i + "_" + c, 
                        GroupId = i, 
                        CandidateId = c, 
                        SharePercent = 4.0f 
                    });
                }
            }

            for (uint c = 0; c < 5; c++)
            {
                // 3. Create the Candidate (Starting at 20% Total Popularity)
                ctx.Db.Candidate.Insert(new Candidate { 
                    CandidateId = c, 
                    Name = "Leader " + c, 
                    TotalPopularity = 20.0f 
                });
            }

            Log.Info("Panchayat initialized: 5 groups, 5 candidates, 4% global share per slot.");
        }

        [Reducer]
        public static void ShiftVoterShare(ReducerContext ctx, uint targetCandidateId, uint groupId, float gainAmount)
        {
            // 1. Get all 5 records for this specific group
            var shares = ctx.Db.VoterShare.Iter().Where(s => s.GroupId == groupId).ToList();
            
            var winner = shares.FirstOrDefault(s => s.CandidateId == targetCandidateId);
            var opponents = shares.Where(s => s.CandidateId != targetCandidateId).ToList();

            // 2. Safety check: How much can we actually steal from opponents?
            float totalOpponentPool = opponents.Sum(o => o.SharePercent);
            float actualGain = Math.Min(gainAmount, totalOpponentPool);
            float debtToCollect = actualGain;

            // 3. Update the Winner
            ctx.Db.VoterShare.Delete(winner); // Remove old row
            var updatedWinner = winner;
            updatedWinner.SharePercent += actualGain;
            ctx.Db.VoterShare.Insert(updatedWinner); // Insert modified row

            // 4. Zero-Sum Redistribution (Take from opponents)
            while (debtToCollect > 0.001f)
            {
                var eligibleOpponents = opponents.Where(o => o.SharePercent > 0).ToList();
                if (eligibleOpponents.Count == 0) break;

                float takePerOpponent = debtToCollect / eligibleOpponents.Count;

                foreach (var opp in eligibleOpponents)
                {
                    float amountToTake = Math.Min(opp.SharePercent, takePerOpponent);
                    
                    ctx.Db.VoterShare.Delete(opp);
                    var updatedOpp = opp;
                    updatedOpp.SharePercent -= amountToTake;
                    ctx.Db.VoterShare.Insert(updatedOpp);
                    
                    debtToCollect -= amountToTake;
                }
            }

            // 5. Sync the Leaderboard
            SyncPopularity(ctx);
        }

        private static void SyncPopularity(ReducerContext ctx)
        {
            foreach (var candidate in ctx.Db.Candidate.Iter().ToList())
            {
                float newTotal = ctx.Db.VoterShare.Iter()
                    .Where(s => s.CandidateId == candidate.CandidateId)
                    .Sum(s => s.SharePercent);
                
                ctx.Db.Candidate.Delete(candidate);
                var updatedCandidate = candidate;
                updatedCandidate.TotalPopularity = newTotal;
                ctx.Db.Candidate.Insert(updatedCandidate);
            }
        }


    }
}