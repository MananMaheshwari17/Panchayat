"""
Panchayat — Data Package
=========================
Exports all data models, tools, and engine functions for use by bridge/ and server/.

Usage:
    from data import VOTER_PROFILES, load_candidates, search_ideology_db
    from data.ideology_engine import compute_ideology_distance
    from data.tools import analyze_player_move
"""

# Voter profiles and sentiment functions
from data.voter_profiles import (
    VoterGroup,
    VOTER_PROFILES,
    get_all_voter_ids,
    get_voter_profile,
    get_demographic_sentiment,
    calculate_reaction,
)

# Ideology scoring engine
from data.ideology_engine import (
    IDEOLOGY_AXES,
    compute_ideology_distance,
    compute_euclidean_distance,
    compute_policy_impact,
    rank_candidates_for_voter,
    simulate_election_result,
    load_candidates,
    load_scenarios,
    load_manifestos,
    load_weaknesses,
    load_dialogues,
    get_candidate_ideologies,
)

# LangChain tool functions (simplified MCP replacement)
from data.tools import (
    search_ideology_db,
    get_past_policies,
    analyze_player_move,
    search_scenario_impact,
    get_candidate_weakness,
    get_candidate_dialogue,
)

__version__ = "1.0.0"
__all__ = [
    # Voter profiles
    "VoterGroup",
    "VOTER_PROFILES",
    "get_all_voter_ids",
    "get_voter_profile",
    "get_demographic_sentiment",
    "calculate_reaction",
    # Ideology engine
    "IDEOLOGY_AXES",
    "compute_ideology_distance",
    "compute_euclidean_distance",
    "compute_policy_impact",
    "rank_candidates_for_voter",
    "simulate_election_result",
    # Data loaders
    "load_candidates",
    "load_scenarios",
    "load_manifestos",
    "load_weaknesses",
    "load_dialogues",
    "get_candidate_ideologies",
    # LangChain tools
    "search_ideology_db",
    "get_past_policies",
    "analyze_player_move",
    "search_scenario_impact",
    "get_candidate_weakness",
    "get_candidate_dialogue",
]
