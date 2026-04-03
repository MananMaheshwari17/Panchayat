"""
Panchayat — Data Validation Script
====================================
Validates all JSON files and Python data structures for schema integrity.

Run with: python -m data.validate_data
"""

import json
import os
import sys
from typing import List, Tuple

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Validation Helpers ──────────────────────────────────────────────────────

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"

results: List[Tuple[str, str, str]] = []


def check(condition: bool, test_name: str, detail: str = ""):
    """Record a test result."""
    status = PASS if condition else FAIL
    results.append((status, test_name, detail))
    return condition


def warn(test_name: str, detail: str = ""):
    """Record a warning."""
    results.append((WARN, test_name, detail))


# ─── JSON Loading ────────────────────────────────────────────────────────────

def load_json_safe(filename: str):
    """Load JSON with error handling."""
    path = os.path.join(DATA_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        check(True, f"Load {filename}", f"Loaded successfully ({os.path.getsize(path)} bytes)")
        return data
    except FileNotFoundError:
        check(False, f"Load {filename}", "File not found!")
        return None
    except json.JSONDecodeError as e:
        check(False, f"Load {filename}", f"JSON parse error: {e}")
        return None


# ─── Validation Functions ────────────────────────────────────────────────────

REQUIRED_IDEOLOGY_AXES = [
    "economy", "social_progress", "environment", "technology",
    "defense", "welfare", "governance_reform", "cultural_identity"
]

VALID_CANDIDATE_IDS = ["dharma_rakshak", "vikas_purush", "jan_neta", "mukti_devi"]
VALID_VOTER_IDS = ["kisan", "yuva", "vyapari", "sarkari", "gramin_nari"]


def validate_candidates(data):
    """Validate candidates.json schema."""
    if not data:
        return

    check("candidates" in data, "candidates.json has 'candidates' key")
    check("ideology_axes" in data, "candidates.json has 'ideology_axes' key")

    candidates = data.get("candidates", [])
    check(len(candidates) == 4, "Exactly 4 candidates", f"Found {len(candidates)}")

    candidate_ids = []
    for c in candidates:
        cid = c.get("id", "MISSING")
        candidate_ids.append(cid)

        check("id" in c, f"Candidate '{cid}' has 'id'")
        check("name" in c, f"Candidate '{cid}' has 'name'")
        check("archetype" in c, f"Candidate '{cid}' has 'archetype'")
        check("system_prompt" in c, f"Candidate '{cid}' has 'system_prompt'")
        check("ideology_scores" in c, f"Candidate '{cid}' has 'ideology_scores'")

        # Validate ideology scores
        scores = c.get("ideology_scores", {})
        for axis in REQUIRED_IDEOLOGY_AXES:
            has_axis = axis in scores
            check(has_axis, f"Candidate '{cid}' has score for '{axis}'")
            if has_axis:
                val = scores[axis]
                check(0 <= val <= 100, f"Candidate '{cid}' {axis} score in range", f"Value: {val}")

        # Validate system prompt length
        prompt_len = len(c.get("system_prompt", ""))
        check(prompt_len > 200, f"Candidate '{cid}' system_prompt is substantial", f"{prompt_len} chars")

        # Validate allies/enemies reference valid voter IDs
        for ally in c.get("natural_allies", []):
            check(ally in VALID_VOTER_IDS, f"Candidate '{cid}' ally '{ally}' is valid voter ID")
        for enemy in c.get("natural_enemies", []):
            check(enemy in VALID_VOTER_IDS, f"Candidate '{cid}' enemy '{enemy}' is valid voter ID")

    # Check all expected IDs present
    for expected_id in VALID_CANDIDATE_IDS:
        check(expected_id in candidate_ids, f"Required candidate '{expected_id}' exists")


def validate_voter_profiles():
    """Validate voter_profiles.py data structures."""
    try:
        from data.voter_profiles import VOTER_PROFILES, get_demographic_sentiment, calculate_reaction
        check(True, "Import voter_profiles module")
    except ImportError as e:
        check(False, "Import voter_profiles module", str(e))
        return

    check(len(VOTER_PROFILES) == 5, "Exactly 5 voter profiles", f"Found {len(VOTER_PROFILES)}")

    total_population = 0.0
    for vid in VALID_VOTER_IDS:
        has_profile = vid in VOTER_PROFILES
        check(has_profile, f"Voter profile '{vid}' exists")
        if not has_profile:
            continue

        vp = VOTER_PROFILES[vid]
        total_population += vp.population_pct

        # Check population is reasonable
        check(0 < vp.population_pct <= 1.0, f"Voter '{vid}' population in range", f"{vp.population_pct}")

        # Check base happiness
        check(0 <= vp.base_happiness <= 100, f"Voter '{vid}' base_happiness in range", f"{vp.base_happiness}")

        # Check issue weights sum to ~1.0
        weight_sum = sum(vp.issue_weights.values())
        check(abs(weight_sum - 1.0) < 0.01, f"Voter '{vid}' issue weights sum to 1.0", f"Sum: {weight_sum:.4f}")

        # Check ideology alignment has all axes
        for axis in REQUIRED_IDEOLOGY_AXES:
            check(axis in vp.ideology_alignment, f"Voter '{vid}' has ideology axis '{axis}'")

        # Check volatility range
        check(0 <= vp.volatility <= 1.0, f"Voter '{vid}' volatility in range", f"{vp.volatility}")

    # Check total population sums to 1.0
    check(abs(total_population - 1.0) < 0.01, "Total voter population sums to 1.0", f"Sum: {total_population:.4f}")

    # Test sentiment function
    sentiment = get_demographic_sentiment("kisan")
    check("error" not in sentiment, "get_demographic_sentiment('kisan') works")
    check("current_happiness" in sentiment, "Sentiment result has 'current_happiness'")

    # Test reaction function
    reaction = calculate_reaction("kisan", {
        "category": "msp_guarantee", "direction": 1, "magnitude": 0.5
    })
    check("error" not in reaction, "calculate_reaction works")
    check("sentiment_shift" in reaction, "Reaction result has 'sentiment_shift'")


def validate_manifestos(data):
    """Validate manifestos.json schema."""
    if not data:
        return

    for cid in VALID_CANDIDATE_IDS:
        has_candidate = cid in data
        check(has_candidate, f"Manifesto for '{cid}' exists")
        if not has_candidate:
            continue

        policies = data[cid].get("policies", [])
        check(len(policies) == 5, f"Manifesto '{cid}' has 5 policies", f"Found {len(policies)}")

        categories_seen = set()
        for p in policies:
            check("id" in p, f"Policy in '{cid}' has 'id'")
            check("title" in p, f"Policy '{p.get('id', '?')}' has 'title'")
            check("category" in p, f"Policy '{p.get('id', '?')}' has 'category'")
            check("ideology_impact" in p, f"Policy '{p.get('id', '?')}' has 'ideology_impact'")

            if "category" in p:
                categories_seen.add(p["category"])

            # Validate ideology impact values
            for axis, val in p.get("ideology_impact", {}).items():
                check(-25 <= val <= 25, f"Policy '{p.get('id', '?')}' impact '{axis}' in range", f"Value: {val}")

        check(len(categories_seen) >= 4, f"Manifesto '{cid}' covers ≥4 categories", f"Categories: {categories_seen}")


def validate_dialogues(data):
    """Validate dialogues.json schema."""
    if not data:
        return

    required_types = ["rally_speech", "attack_opponent", "react_to_policy", "victory_speech", "defeat_speech"]

    for cid in VALID_CANDIDATE_IDS:
        has_candidate = cid in data
        check(has_candidate, f"Dialogues for '{cid}' exist")
        if not has_candidate:
            continue

        for dtype in required_types:
            check(dtype in data[cid], f"Dialogue '{cid}' has '{dtype}'")


def validate_weaknesses(data):
    """Validate weaknesses.json schema."""
    if not data:
        return

    for cid in VALID_CANDIDATE_IDS:
        has_candidate = cid in data
        check(has_candidate, f"Weaknesses for '{cid}' exist")
        if not has_candidate:
            continue

        scandals = data[cid]
        check(len(scandals) >= 2, f"Candidate '{cid}' has ≥2 weaknesses", f"Found {len(scandals)}")

        for s in scandals:
            check("severity" in s, f"Weakness '{s.get('id', '?')}' has severity")
            if "severity" in s:
                check(1 <= s["severity"] <= 5, f"Weakness severity in range", f"Value: {s['severity']}")

            check("affected_demographics" in s, f"Weakness '{s.get('id', '?')}' has affected_demographics")
            check("counter_narrative" in s, f"Weakness '{s.get('id', '?')}' has counter_narrative")


def validate_scenarios(data):
    """Validate scenarios.json schema."""
    if not data:
        return

    scenarios = data.get("scenarios", [])
    check(len(scenarios) >= 15, f"At least 15 scenarios", f"Found {len(scenarios)}")

    categories_seen = set()
    for s in scenarios:
        check("id" in s, f"Scenario has 'id'")
        check("headline" in s, f"Scenario '{s.get('id', '?')}' has headline")
        check("category" in s, f"Scenario '{s.get('id', '?')}' has category")
        check("ideology_analysis" in s, f"Scenario '{s.get('id', '?')}' has ideology_analysis")

        if "category" in s:
            categories_seen.add(s["category"])

        # Check all candidates have analysis
        analysis = s.get("ideology_analysis", {})
        for cid in VALID_CANDIDATE_IDS:
            check(cid in analysis, f"Scenario '{s.get('id', '?')}' has analysis for '{cid}'")

    check(len(categories_seen) >= 4, f"Scenarios cover ≥4 categories", f"Categories: {categories_seen}")


def validate_tools():
    """Validate tools.py functions work."""
    try:
        from data.tools import (
            search_ideology_db,
            get_past_policies,
            analyze_player_move,
            get_demographic_sentiment as tool_sentiment,
            search_scenario_impact,
            get_candidate_weakness,
            get_candidate_dialogue,
        )
        check(True, "Import tools module")
    except ImportError as e:
        check(False, "Import tools module", str(e))
        return

    # Test each function with valid inputs
    r1 = search_ideology_db("dharma_rakshak", "agriculture")
    check("ERROR" not in r1, "search_ideology_db works", r1[:80])

    r2 = get_past_policies("vikas_purush")
    check("ERROR" not in r2, "get_past_policies works", r2[:80])

    r3 = analyze_player_move("Build 5G towers in villages", "jan_neta")
    check("ERROR" not in r3, "analyze_player_move works", r3[:80])

    r4 = tool_sentiment("kisan")
    check("ERROR" not in r4, "get_demographic_sentiment (tool) works", r4[:80])

    r5 = search_scenario_impact("farm")
    check("No scenarios found" not in r5, "search_scenario_impact works", r5[:80])

    r6 = get_candidate_weakness("mukti_devi")
    check("ERROR" not in r6, "get_candidate_weakness works", r6[:80])


def validate_ideology_engine():
    """Validate ideology_engine.py functions."""
    try:
        from data.ideology_engine import (
            compute_ideology_distance,
            compute_policy_impact,
            rank_candidates_for_voter,
            simulate_election_result,
            get_candidate_ideologies,
        )
        check(True, "Import ideology_engine module")
    except ImportError as e:
        check(False, "Import ideology_engine module", str(e))
        return

    # Test cosine similarity
    scores_a = {"economy": 80, "social_progress": 20, "environment": 50,
                "technology": 90, "defense": 50, "welfare": 30,
                "governance_reform": 70, "cultural_identity": 20}
    scores_b = {"economy": 20, "social_progress": 80, "environment": 50,
                "technology": 10, "defense": 50, "welfare": 90,
                "governance_reform": 30, "cultural_identity": 80}

    sim = compute_ideology_distance(scores_a, scores_b)
    check(0 <= sim <= 1, "Cosine similarity in valid range", f"Value: {sim}")

    # Self-similarity should be 1.0
    self_sim = compute_ideology_distance(scores_a, scores_a)
    check(abs(self_sim - 1.0) < 0.001, "Self-similarity ≈ 1.0", f"Value: {self_sim}")

    # Test candidate rankings
    ideologies = get_candidate_ideologies()
    check(len(ideologies) == 4, "get_candidate_ideologies returns 4", f"Found {len(ideologies)}")

    rankings = rank_candidates_for_voter(scores_a, ideologies)
    check(len(rankings) == 4, "Rankings include all 4 candidates")


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("🏛️  PANCHAYAT — Data Validation Report")
    print("=" * 60)

    # Add parent directory to path for module imports
    parent = os.path.dirname(DATA_DIR)
    if parent not in sys.path:
        sys.path.insert(0, parent)

    print("\n📁 Validating JSON files...")
    candidates_data = load_json_safe("candidates.json")
    manifestos_data = load_json_safe("manifestos.json")
    dialogues_data = load_json_safe("dialogues.json")
    weaknesses_data = load_json_safe("weaknesses.json")
    scenarios_data = load_json_safe("scenarios.json")

    print("\n👤 Validating candidates...")
    validate_candidates(candidates_data)

    print("\n🗳️ Validating voter profiles...")
    validate_voter_profiles()

    print("\n📋 Validating manifestos...")
    validate_manifestos(manifestos_data)

    print("\n💬 Validating dialogues...")
    validate_dialogues(dialogues_data)

    print("\n💣 Validating weaknesses...")
    validate_weaknesses(weaknesses_data)

    print("\n📰 Validating scenarios...")
    validate_scenarios(scenarios_data)

    print("\n🔧 Validating tools...")
    validate_tools()

    print("\n⚙️ Validating ideology engine...")
    validate_ideology_engine()

    # Print results
    print("\n" + "=" * 60)
    print("📊 VALIDATION RESULTS")
    print("=" * 60)

    passed = sum(1 for r in results if r[0] == PASS)
    failed = sum(1 for r in results if r[0] == FAIL)
    warnings = sum(1 for r in results if r[0] == WARN)

    # Print failures first
    if failed:
        print(f"\n{FAIL} FAILURES ({failed}):")
        for status, name, detail in results:
            if status == FAIL:
                print(f"   {FAIL} {name}")
                if detail:
                    print(f"      → {detail}")

    # Print warnings
    if warnings:
        print(f"\n{WARN} WARNINGS ({warnings}):")
        for status, name, detail in results:
            if status == WARN:
                print(f"   {WARN} {name}: {detail}")

    # Summary
    print(f"\n{'─' * 40}")
    print(f"   {PASS} Passed: {passed}")
    print(f"   {FAIL} Failed: {failed}")
    print(f"   {WARN} Warnings: {warnings}")
    print(f"   Total: {len(results)}")
    print(f"{'─' * 40}")

    if failed == 0:
        print(f"\n🎉 ALL VALIDATIONS PASSED! Data layer is ready.")
    else:
        print(f"\n🚨 {failed} VALIDATION(S) FAILED. Fix before committing.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
