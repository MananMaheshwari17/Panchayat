"""
Panchayat — LangChain Tool Interface
======================================
Simplified MCP replacement: standard Python functions ready for @tool decoration.

These functions expose the data layer to LangGraph agents. Each function:
- Loads data from JSON files
- Performs search/analysis
- Returns structured text responses that Gemini can reason about

Usage with LangChain:
    from langchain_core.tools import tool
    from data.tools import search_ideology_db, get_past_policies, ...

    @tool
    def search_ideology(archetype: str, category: str) -> str:
        return search_ideology_db(archetype, category)
"""

import json
import os
from typing import Optional, List

# ─── Data Loading ────────────────────────────────────────────────────────────

DATA_DIR = os.path.dirname(os.path.abspath(__file__))


def _load_json(filename: str) -> dict:
    """Load a JSON file from the data directory."""
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_candidate(candidate_id: str) -> Optional[dict]:
    """Get a single candidate by ID."""
    data = _load_json("candidates.json")
    for c in data["candidates"]:
        if c["id"] == candidate_id:
            return c
    return None


# ─── Tool Functions (Ready for @tool decoration) ─────────────────────────────


def search_ideology_db(archetype: str, category: str) -> str:
    """
    Search the scenarios database for real-world examples matching
    an archetype's ideology and a policy category.

    Args:
        archetype: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
        category: One of 'agriculture', 'technology', 'economy', 'social_welfare', 'governance'

    Returns:
        A formatted string with matching scenarios, ready for LLM reasoning.
    """
    scenarios = _load_json("scenarios.json")["scenarios"]
    candidate = _get_candidate(archetype)

    if not candidate:
        return f"ERROR: Unknown archetype '{archetype}'. Valid: dharma_rakshak, vikas_purush, jan_neta, mukti_devi"

    # Filter by category
    matching = [s for s in scenarios if s["category"] == category]
    if not matching:
        matching = [s for s in scenarios if category.lower() in s["category"].lower()]

    if not matching:
        return f"No scenarios found for category '{category}'. Available categories: agriculture, technology, economy, social_welfare, governance"

    results = []
    for s in matching:
        analysis = s["ideology_analysis"].get(archetype, {})
        results.append(
            f"📰 {s['headline']} ({s['date_range']})\n"
            f"   Summary: {s['description'][:150]}...\n"
            f"   {candidate['name']}'s Position: {analysis.get('stance', 'unknown')} "
            f"(score: {analysis.get('score', 0):+d})\n"
            f"   Reasoning: {analysis.get('reasoning', 'N/A')}\n"
            f"   Affected Groups: {', '.join(s['affected_demographics'])}\n"
        )

    header = (
        f"=== Ideology Search Results ===\n"
        f"Archetype: {candidate['name']} ({candidate['archetype']})\n"
        f"Category: {category}\n"
        f"Found: {len(results)} matching scenarios\n\n"
    )
    return header + "\n".join(results)


def get_past_policies(archetype: str) -> str:
    """
    Get the manifesto policies for a candidate archetype.
    Also includes real-world analogues from the scenarios database.

    Args:
        archetype: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'

    Returns:
        Formatted string with the candidate's policy positions and historical context.
    """
    candidate = _get_candidate(archetype)
    if not candidate:
        return f"ERROR: Unknown archetype '{archetype}'."

    manifestos = _load_json("manifestos.json")
    policies = manifestos.get(archetype, {}).get("policies", [])

    if not policies:
        return f"No manifesto found for '{archetype}'."

    results = [
        f"=== Manifesto: {candidate['name']} ===\n"
        f"Party: {manifestos[archetype].get('party', 'N/A')}\n"
        f"Tagline: {manifestos[archetype].get('tagline', 'N/A')}\n"
    ]

    for p in policies:
        results.append(
            f"\n📋 {p['title']} [{p['category'].upper()}]\n"
            f"   {p['description']}\n"
            f"   Promise: {p['promise_to_voters']}\n"
            f"   Ideology Shift: {_format_impact(p['ideology_impact'])}\n"
        )

    # Add historical context from scenarios
    scenarios = _load_json("scenarios.json")["scenarios"]
    supported = [
        s for s in scenarios
        if s["ideology_analysis"].get(archetype, {}).get("score", 0) > 10
    ]
    if supported:
        results.append("\n📚 Historical Precedents This Candidate Would Cite:")
        for s in supported[:3]:
            analysis = s["ideology_analysis"][archetype]
            results.append(f"   • {s['headline']}: {analysis['reasoning']}")

    return "\n".join(results)


def analyze_player_move(action: str, archetype: str) -> str:
    """
    Cross-reference the player's policy action against an archetype's core beliefs.
    Returns how the AI candidate would perceive and react to this action.

    Args:
        action: Description of the player's policy action
        archetype: The AI candidate analyzing this action

    Returns:
        Analysis context for the LLM to generate a response.
    """
    candidate = _get_candidate(archetype)
    if not candidate:
        return f"ERROR: Unknown archetype '{archetype}'."

    # Get dialogue templates for reaction
    dialogues = _load_json("dialogues.json")
    reactions = dialogues.get(archetype, {}).get("react_to_policy", {})

    # Get scenarios for context
    scenarios = _load_json("scenarios.json")["scenarios"]

    # Keyword matching for action categorization
    action_lower = action.lower()
    category_keywords = {
        "pro_agriculture": ["farm", "agri", "msp", "crop", "kisan", "irrigation", "land", "soil"],
        "pro_technology": ["tech", "digital", "app", "5g", "data", "ai", "startup", "internet", "drone"],
        "pro_market": ["market", "business", "tax", "gst", "trade", "invest", "sez", "deregulat"],
        "pro_welfare": ["welfare", "mnrega", "health", "education", "subsid", "food", "pension", "ration"],
        "pro_reform": ["reform", "transparenc", "corruption", "governance", "decentrali", "audit"],
    }

    detected_category = "pro_reform"  # default
    max_matches = 0
    for cat, keywords in category_keywords.items():
        matches = sum(1 for kw in keywords if kw in action_lower)
        if matches > max_matches:
            max_matches = matches
            detected_category = cat

    # Build analysis context
    template_reaction = reactions.get(detected_category, "No template available.")

    # Find relevant scenarios
    relevant_scenarios = []
    for s in scenarios:
        s_text = (s["headline"] + " " + s["description"]).lower()
        if any(kw in s_text for kw in action_lower.split()[:5]):
            relevant_scenarios.append(s)

    result = (
        f"=== Player Move Analysis for {candidate['name']} ({candidate['archetype']}) ===\n\n"
        f"Player's Action: {action}\n"
        f"Detected Category: {detected_category}\n\n"
        f"📌 Candidate's Core Beliefs:\n"
    )

    # Extract key beliefs from system prompt (first 5 bullet points)
    prompt_lines = candidate["system_prompt"].split("\n")
    beliefs = [l.strip() for l in prompt_lines if l.strip().startswith("-")][:5]
    for b in beliefs:
        result += f"   {b}\n"

    result += f"\n📢 Template Reaction:\n   {template_reaction}\n"

    result += f"\n🎯 Ideology Alignment:\n"
    result += f"   Candidate scores: {_format_scores(candidate['ideology_scores'])}\n"

    result += f"\n🔍 Natural allies: {', '.join(candidate['natural_allies'])}\n"
    result += f"   Natural enemies: {', '.join(candidate['natural_enemies'])}\n"

    if relevant_scenarios:
        result += f"\n📰 Relevant Historical Context:\n"
        for s in relevant_scenarios[:2]:
            analysis = s["ideology_analysis"].get(archetype, {})
            result += (
                f"   • {s['headline']}: {analysis.get('stance', '?')} "
                f"(score: {analysis.get('score', 0):+d})\n"
            )

    result += f"\n💡 Speaking Style: {', '.join(candidate['speaking_style'])}\n"
    result += f"   Trigger Phrases: {', '.join(candidate['trigger_phrases'][:5])}\n"

    return result


def get_demographic_sentiment(group_name: str) -> str:
    """
    Get the current baseline sentiment and profile of a voter demographic.
    Wrapper that returns a formatted string for LLM consumption.

    Args:
        group_name: One of 'kisan', 'yuva', 'vyapari', 'sarkari', 'gramin_nari'

    Returns:
        Formatted string with demographic profile, sentiment, and key concerns.
    """
    from data.voter_profiles import VOTER_PROFILES, get_demographic_sentiment as _get_sentiment

    profile = VOTER_PROFILES.get(group_name)
    if not profile:
        valid = list(VOTER_PROFILES.keys())
        return f"ERROR: Unknown voter group '{group_name}'. Valid: {', '.join(valid)}"

    sentiment = _get_sentiment(group_name)

    result = (
        f"=== Voter Group: {profile.emoji} {profile.name_en} ({profile.name}) ===\n\n"
        f"Population: {sentiment['population_pct']} of electorate\n"
        f"Current Happiness: {sentiment['current_happiness']}/100 [{sentiment['happiness_label']}]\n"
        f"Volatility: {profile.volatility} ({'Very volatile' if profile.volatility > 0.6 else 'Stable' if profile.volatility < 0.3 else 'Moderate'})\n"
        f"Social Media Presence: {profile.social_media_presence} ({'Very loud' if profile.social_media_presence > 0.7 else 'Quiet' if profile.social_media_presence < 0.3 else 'Moderate'})\n\n"
        f"📋 Description:\n   {profile.description}\n\n"
        f"🔑 Key Demands:\n"
    )
    for demand in profile.key_demands:
        result += f"   • {demand}\n"

    result += f"\n⚠️ Fear Triggers (cause anger):\n"
    for fear in profile.fear_triggers:
        result += f"   • {fear}\n"

    result += f"\n✅ Hope Triggers (cause enthusiasm):\n"
    for hope in profile.hope_triggers:
        result += f"   • {hope}\n"

    result += f"\n📊 Issue Priorities:\n"
    sorted_issues = sorted(profile.issue_weights.items(), key=lambda x: x[1], reverse=True)
    for issue, weight in sorted_issues:
        bar = "█" * int(weight * 40)
        result += f"   {issue}: {weight:.0%} {bar}\n"

    return result


def search_scenario_impact(policy_keyword: str) -> str:
    """
    Search for real-world impacts of similar policies from the scenarios database.

    Args:
        policy_keyword: A keyword or phrase to search for (e.g., 'MSP', 'digital', 'subsidy')

    Returns:
        Formatted string with matching scenarios and their multi-archetype analysis.
    """
    scenarios = _load_json("scenarios.json")["scenarios"]
    keyword_lower = policy_keyword.lower()

    matching = []
    for s in scenarios:
        searchable = (
            s["headline"] + " " + s["description"] + " " +
            " ".join(s.get("policy_implications", []))
        ).lower()
        if keyword_lower in searchable:
            matching.append(s)

    if not matching:
        # Try partial matching
        for s in scenarios:
            searchable = (s["headline"] + " " + s["description"]).lower()
            if any(word in searchable for word in keyword_lower.split()):
                matching.append(s)

    if not matching:
        return f"No scenarios found matching '{policy_keyword}'. Try broader terms like 'agriculture', 'technology', 'welfare'."

    results = [
        f"=== Scenario Impact Search: '{policy_keyword}' ===\n"
        f"Found: {len(matching)} matching scenarios\n"
    ]

    for s in matching[:5]:  # Limit to 5
        results.append(f"\n📰 {s['headline']} ({s['date_range']})")
        results.append(f"   {s['description'][:200]}")
        results.append(f"\n   Multi-Archetype Analysis:")
        for archetype, analysis in s["ideology_analysis"].items():
            emoji = "✅" if analysis["score"] > 0 else "❌" if analysis["score"] < 0 else "➖"
            results.append(
                f"   {emoji} {archetype}: {analysis['stance']} ({analysis['score']:+d}) — {analysis['reasoning']}"
            )
        results.append(f"\n   Affected Groups: {', '.join(s['affected_demographics'])}")
        results.append(f"   Policy Tags: {', '.join(s.get('policy_implications', []))}")

    return "\n".join(results)


def get_candidate_weakness(candidate_id: str) -> str:
    """
    Get scandal/weakness data for a candidate.

    Args:
        candidate_id: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'

    Returns:
        Formatted string with weaknesses, severity, and counter-narratives.
    """
    weaknesses = _load_json("weaknesses.json")
    candidate = _get_candidate(candidate_id)

    if not candidate:
        return f"ERROR: Unknown candidate '{candidate_id}'."

    scandals = weaknesses.get(candidate_id, [])
    if not scandals:
        return f"No weaknesses found for '{candidate_id}'."

    result = [
        f"=== Vulnerabilities: {candidate['name']} ({candidate['archetype']}) ===\n"
    ]

    for s in scandals:
        severity_bar = "🔴" * s["severity"] + "⚪" * (5 - s["severity"])
        result.append(
            f"\n💣 {s['title']}\n"
            f"   Severity: {severity_bar} ({s['severity']}/5)\n"
            f"   {s['description']}\n"
            f"   Evidence: {s['evidence']}\n"
            f"   Counter-Narrative: \"{s['counter_narrative']}\"\n"
            f"   Demographic Impact:"
        )
        for demo, impact in s["affected_demographics"].items():
            result.append(f"      {demo}: {impact:+d} happiness points")

    return "\n".join(result)


def get_candidate_dialogue(candidate_id: str, dialogue_type: str) -> str:
    """
    Get a specific dialogue template for a candidate.

    Args:
        candidate_id: One of 'dharma_rakshak', 'vikas_purush', 'jan_neta', 'mukti_devi'
        dialogue_type: One of 'rally_speech', 'attack_opponent', 'defend_scandal',
                       'react_to_policy', 'victory_speech', 'defeat_speech'

    Returns:
        The dialogue text.
    """
    dialogues = _load_json("dialogues.json")
    candidate = _get_candidate(candidate_id)

    if not candidate:
        return f"ERROR: Unknown candidate '{candidate_id}'."

    candidate_dialogues = dialogues.get(candidate_id, {})
    if dialogue_type not in candidate_dialogues:
        valid = list(candidate_dialogues.keys())
        return f"ERROR: Unknown dialogue type '{dialogue_type}'. Valid: {', '.join(valid)}"

    content = candidate_dialogues[dialogue_type]
    if isinstance(content, dict):
        return json.dumps(content, indent=2, ensure_ascii=False)
    return str(content)


# ─── Private Helpers ─────────────────────────────────────────────────────────

def _format_impact(impact: dict) -> str:
    """Format ideology impact as a compact string."""
    parts = []
    for axis, shift in impact.items():
        if shift > 0:
            parts.append(f"{axis}:+{shift}")
        elif shift < 0:
            parts.append(f"{axis}:{shift}")
    return ", ".join(parts) if parts else "No significant shifts"


def _format_scores(scores: dict) -> str:
    """Format ideology scores as a compact string."""
    return ", ".join(f"{k}:{v}" for k, v in scores.items())


# ─── Quick Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("PANCHAYAT — Tool Functions Test")
    print("=" * 60)

    print("\n1. search_ideology_db('dharma_rakshak', 'agriculture'):")
    print(search_ideology_db("dharma_rakshak", "agriculture"))

    print("\n2. get_past_policies('vikas_purush'):")
    print(get_past_policies("vikas_purush")[:500] + "...")

    print("\n3. analyze_player_move('Increase MSP by 50%', 'jan_neta'):")
    print(analyze_player_move("Increase MSP by 50% for all crops", "jan_neta")[:500] + "...")

    print("\n4. get_demographic_sentiment('kisan'):")
    print(get_demographic_sentiment("kisan")[:500] + "...")

    print("\n5. search_scenario_impact('demonetization'):")
    print(search_scenario_impact("demonetization")[:500] + "...")

    print("\n6. get_candidate_weakness('mukti_devi'):")
    print(get_candidate_weakness("mukti_devi")[:500] + "...")
