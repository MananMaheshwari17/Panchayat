"""
Panchayat — Ideology Engine
============================
Mathematical scoring engine for ideology distance calculations,
policy impact computation, candidate ranking, and election simulation.

Uses cosine similarity on 8-axis ideology vectors to determine alignment
between candidates, voters, and policies.
"""

import math
import json
import os
from typing import Dict, List, Tuple, Optional

# ─── Constants ───────────────────────────────────────────────────────────────

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
IDEOLOGY_AXES = [
    "economy", "social_progress", "environment", "technology",
    "defense", "welfare", "governance_reform", "cultural_identity"
]


# ─── Core Math Functions ─────────────────────────────────────────────────────

def compute_ideology_distance(scores_a: Dict[str, int], scores_b: Dict[str, int]) -> float:
    """
    Compute cosine similarity between two ideology score vectors.

    Returns a value between 0.0 (completely opposite) and 1.0 (perfectly aligned).
    Uses the 8-axis ideology model defined in candidates.json.

    Args:
        scores_a: Dict of axis_id → score (0-100) for entity A
        scores_b: Dict of axis_id → score (0-100) for entity B

    Returns:
        Float between 0.0 (opposite) and 1.0 (aligned)
    """
    vec_a = [scores_a.get(axis, 50) for axis in IDEOLOGY_AXES]
    vec_b = [scores_b.get(axis, 50) for axis in IDEOLOGY_AXES]

    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a ** 2 for a in vec_a))
    magnitude_b = math.sqrt(sum(b ** 2 for b in vec_b))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    similarity = dot_product / (magnitude_a * magnitude_b)
    return round(max(0.0, min(1.0, similarity)), 4)


def compute_euclidean_distance(scores_a: Dict[str, int], scores_b: Dict[str, int]) -> float:
    """
    Compute normalized Euclidean distance between two ideology vectors.

    Returns a value between 0.0 (identical) and 1.0 (maximally distant).
    Useful for "how different are these two positions?" calculations.
    """
    vec_a = [scores_a.get(axis, 50) for axis in IDEOLOGY_AXES]
    vec_b = [scores_b.get(axis, 50) for axis in IDEOLOGY_AXES]

    squared_diff = sum((a - b) ** 2 for a, b in zip(vec_a, vec_b))
    # Max possible distance: sqrt(8 * 100^2) = sqrt(80000) ≈ 282.84
    max_distance = math.sqrt(len(IDEOLOGY_AXES) * (100 ** 2))
    normalized = math.sqrt(squared_diff) / max_distance

    return round(normalized, 4)


def compute_policy_impact(
    policy_ideology_impact: Dict[str, int],
    voter_ideology: Dict[str, int],
    voter_issue_weights: Dict[str, float],
    policy_category: str
) -> Dict:
    """
    Calculate how a specific policy impacts a voter group's sentiment.

    The calculation considers:
    1. How much does this policy shift ideology in a direction the voter likes?
    2. How important is this policy's category to the voter?

    Args:
        policy_ideology_impact: Dict of axis → shift amount (e.g., +15 or -10)
        voter_ideology: The voter group's ideology alignment scores
        voter_issue_weights: The voter group's issue importance weights
        policy_category: Category of the policy (agriculture, technology, etc.)

    Returns:
        Dict with alignment_score, category_relevance, net_impact, and sentiment_shift
    """
    # Step 1: Calculate alignment of policy shift with voter preferences
    # Positive shift on an axis the voter scores HIGH on = good
    # Positive shift on an axis the voter scores LOW on = can be bad
    alignment_score = 0.0
    for axis, shift in policy_ideology_impact.items():
        if axis not in IDEOLOGY_AXES:
            continue
        voter_preference = voter_ideology.get(axis, 50)

        # If voter wants HIGH and policy pushes HIGH → positive
        # If voter wants LOW and policy pushes HIGH → negative
        # Normalize voter preference: 0-100 → -1 to +1
        voter_direction = (voter_preference - 50) / 50.0
        policy_direction = shift / 25.0  # Normalize shift (max is ±25)

        alignment_score += voter_direction * policy_direction

    alignment_score = alignment_score / len(IDEOLOGY_AXES)  # Average

    # Step 2: Find category relevance
    category_relevance = 0.0
    for issue, weight in voter_issue_weights.items():
        if policy_category.lower() in issue.lower() or issue.lower() in policy_category.lower():
            category_relevance = max(category_relevance, weight)

    if category_relevance == 0.0:
        category_relevance = 0.05  # Minimum baseline interest

    # Step 3: Compute net impact
    # Net = alignment * relevance * 100 (scale to -30 to +30 range)
    net_impact = alignment_score * category_relevance * 100
    sentiment_shift = max(-30.0, min(30.0, net_impact))

    return {
        "alignment_score": round(alignment_score, 4),
        "category_relevance": round(category_relevance, 4),
        "net_impact": round(net_impact, 4),
        "sentiment_shift": round(sentiment_shift, 2),
        "direction": "positive" if sentiment_shift > 2 else ("negative" if sentiment_shift < -2 else "neutral"),
    }


def rank_candidates_for_voter(
    voter_ideology: Dict[str, int],
    candidate_ideologies: Dict[str, Dict[str, int]]
) -> List[Tuple[str, float]]:
    """
    Rank candidates by ideology alignment with a voter group.

    Args:
        voter_ideology: The voter group's ideology scores
        candidate_ideologies: Dict of candidate_id → ideology_scores

    Returns:
        List of (candidate_id, similarity_score) tuples, sorted descending
    """
    rankings = []
    for cid, c_ideology in candidate_ideologies.items():
        similarity = compute_ideology_distance(voter_ideology, c_ideology)
        rankings.append((cid, similarity))

    rankings.sort(key=lambda x: x[1], reverse=True)
    return rankings


def simulate_election_result(
    voter_sentiments: Dict[str, Dict[str, float]],
    voter_populations: Dict[str, float]
) -> Dict:
    """
    Simulate election results based on current voter sentiments toward each candidate.

    Args:
        voter_sentiments: Dict of voter_group_id → Dict of candidate_id → happiness (0-100)
        voter_populations: Dict of voter_group_id → population proportion (sums to 1.0)

    Returns:
        Dict with vote_share per candidate, winner, and breakdown
    """
    candidate_ids = set()
    for sentiments in voter_sentiments.values():
        candidate_ids.update(sentiments.keys())

    # Calculate weighted vote share
    vote_shares: Dict[str, float] = {cid: 0.0 for cid in candidate_ids}

    breakdown = {}
    for voter_id, sentiments in voter_sentiments.items():
        pop = voter_populations.get(voter_id, 0.0)
        if pop == 0 or not sentiments:
            continue

        # Softmax-style voting: higher sentiment → exponentially more likely to vote for that candidate
        total_exp = sum(math.exp(s / 20.0) for s in sentiments.values())
        voter_breakdown = {}

        for cid, sentiment in sentiments.items():
            vote_pct = (math.exp(sentiment / 20.0) / total_exp) * pop
            vote_shares[cid] += vote_pct
            voter_breakdown[cid] = round(vote_pct / pop * 100, 1) if pop > 0 else 0

        breakdown[voter_id] = voter_breakdown

    # Normalize to percentages
    total_votes = sum(vote_shares.values())
    if total_votes > 0:
        vote_shares = {cid: round(v / total_votes * 100, 2) for cid, v in vote_shares.items()}

    # Sort by vote share
    sorted_results = sorted(vote_shares.items(), key=lambda x: x[1], reverse=True)
    winner = sorted_results[0][0] if sorted_results else "unknown"

    return {
        "winner": winner,
        "vote_shares": dict(sorted_results),
        "voter_breakdown": breakdown,
        "margin": round(sorted_results[0][1] - sorted_results[1][1], 2) if len(sorted_results) > 1 else 100.0,
    }


# ─── Data Loading Helpers ────────────────────────────────────────────────────

def load_candidates() -> Dict:
    """Load candidates.json and return the parsed data."""
    path = os.path.join(DATA_DIR, "candidates.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_scenarios() -> Dict:
    """Load scenarios.json and return the parsed data."""
    path = os.path.join(DATA_DIR, "scenarios.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_manifestos() -> Dict:
    """Load manifestos.json and return the parsed data."""
    path = os.path.join(DATA_DIR, "manifestos.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_weaknesses() -> Dict:
    """Load weaknesses.json and return the parsed data."""
    path = os.path.join(DATA_DIR, "weaknesses.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_dialogues() -> Dict:
    """Load dialogues.json and return the parsed data."""
    path = os.path.join(DATA_DIR, "dialogues.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_candidate_ideologies() -> Dict[str, Dict[str, int]]:
    """Extract ideology_scores for all candidates."""
    data = load_candidates()
    return {c["id"]: c["ideology_scores"] for c in data["candidates"]}


# ─── Quick Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("PANCHAYAT — Ideology Engine Test")
    print("=" * 60)

    # Load data
    candidates = load_candidates()
    candidate_ideologies = get_candidate_ideologies()

    # Import voter profiles
    from data.voter_profiles import VOTER_PROFILES

    # Test 1: Candidate-Candidate distances
    print("\n📊 Candidate Ideology Distances (Cosine Similarity):")
    c_ids = list(candidate_ideologies.keys())
    for i in range(len(c_ids)):
        for j in range(i + 1, len(c_ids)):
            sim = compute_ideology_distance(
                candidate_ideologies[c_ids[i]],
                candidate_ideologies[c_ids[j]]
            )
            print(f"   {c_ids[i]} ↔ {c_ids[j]}: {sim:.4f}")

    # Test 2: Rank candidates for each voter group
    print("\n🗳️ Candidate Rankings per Voter Group:")
    for vid, vp in VOTER_PROFILES.items():
        rankings = rank_candidates_for_voter(vp.ideology_alignment, candidate_ideologies)
        print(f"\n   {vp.emoji} {vp.name_en}:")
        for rank, (cid, score) in enumerate(rankings, 1):
            print(f"      #{rank} {cid}: {score:.4f}")

    # Test 3: Simulate an election
    print("\n🏆 Mock Election Simulation:")
    mock_sentiments = {}
    for vid, vp in VOTER_PROFILES.items():
        sentiments = {}
        for cid in c_ids:
            sim = compute_ideology_distance(vp.ideology_alignment, candidate_ideologies[cid])
            sentiments[cid] = sim * 100  # Scale to 0-100
        mock_sentiments[vid] = sentiments

    voter_pops = {vid: vp.population_pct for vid, vp in VOTER_PROFILES.items()}
    result = simulate_election_result(mock_sentiments, voter_pops)

    print(f"   Winner: {result['winner']}")
    print(f"   Margin: {result['margin']}%")
    for cid, share in result["vote_shares"].items():
        print(f"   {cid}: {share}%")
