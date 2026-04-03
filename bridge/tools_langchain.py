"""
Panchayat Bridge — LangChain Tool Wrappers
============================================
Wraps data/ tool functions with LangChain @tool decorator
so LangGraph agents can use them for tool-augmented reasoning.
"""

from langchain_core.tools import tool


@tool
def search_ideology_db(archetype: str, category: str) -> str:
    """Search real-world Indian political scenarios matching a candidate archetype's ideology and a policy category.
    
    Args:
        archetype: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
        category: One of 'agriculture', 'technology', 'economy', 'social_welfare', 'governance'
    """
    from data.tools import search_ideology_db as _fn
    return _fn(archetype, category)


@tool
def get_past_policies(archetype: str) -> str:
    """Get the manifesto policies and historical precedents for a candidate archetype.
    
    Args:
        archetype: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
    """
    from data.tools import get_past_policies as _fn
    return _fn(archetype)


@tool
def analyze_player_move(action: str, archetype: str) -> str:
    """Analyze how a specific candidate archetype would perceive and react to the player's policy action.
    
    Args:
        action: Description of the player's policy action
        archetype: The AI candidate analyzing this action
    """
    from data.tools import analyze_player_move as _fn
    return _fn(action, archetype)


@tool
def get_demographic_sentiment(group_name: str) -> str:
    """Get current mood, demands, and sentiment of a voter demographic group.
    
    Args:
        group_name: One of 'kisan', 'yuva', 'vyapari', 'sarkari', 'gramin_nari'
    """
    from data.tools import get_demographic_sentiment as _fn
    return _fn(group_name)


@tool
def search_scenario_impact(policy_keyword: str) -> str:
    """Search for real-world impacts of similar policies from the Indian political scenarios database.
    
    Args:
        policy_keyword: A keyword or phrase to search for (e.g., 'MSP', 'digital', 'subsidy')
    """
    from data.tools import search_scenario_impact as _fn
    return _fn(policy_keyword)


@tool
def get_candidate_weakness(candidate_id: str) -> str:
    """Get scandal and weakness data for a candidate that opponents could exploit.
    
    Args:
        candidate_id: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
    """
    from data.tools import get_candidate_weakness as _fn
    return _fn(candidate_id)


def get_all_tools():
    """Return all available LangChain tools."""
    return [
        search_ideology_db,
        get_past_policies,
        analyze_player_move,
        get_demographic_sentiment,
        search_scenario_impact,
        get_candidate_weakness,
    ]
