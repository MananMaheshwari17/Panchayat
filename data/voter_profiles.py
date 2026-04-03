"""
Panchayat — Voter Demographic Profiles
=======================================
Defines the 5 voter demographics with sentiment baselines, issue priorities,
ideology alignment, and reaction computation functions.

These profiles power the voter sentiment engine and are consumed by:
- tools.py (LangChain @tool functions)
- ideology_engine.py (scoring calculations)
- bridge/ai_prompts.py (Gemini system instructions for voter feed)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import math


# ─── Data Classes ────────────────────────────────────────────────────────────

@dataclass
class VoterGroup:
    """Represents a single voter demographic in the Panchayat election."""

    id: str
    name: str                        # Display name (Hindi)
    name_en: str                     # Display name (English)
    population_pct: float            # % of total electorate (sums to 1.0)
    description: str                 # 2-3 sentence profile
    base_happiness: float            # Starting sentiment (0-100)
    issue_weights: Dict[str, float]  # Issue → importance weight (sums to 1.0)
    ideology_alignment: Dict[str, int]  # Same 8-axis as candidates (0-100)
    volatility: float                # How easily opinion swings (0.0 - 1.0)
    social_media_presence: float     # How loud in the "feed" (0.0 - 1.0)
    key_demands: List[str]           # Top 3-5 demands from leaders
    fear_triggers: List[str]         # Issues that cause panic/anger
    hope_triggers: List[str]         # Issues that cause enthusiasm
    preferred_language: str          # Primary language/dialect
    emoji: str                       # UI representation
    color_theme: str                 # UI color for this demographic


# ─── The 5 Voter Demographics ───────────────────────────────────────────────

VOTER_PROFILES: Dict[str, VoterGroup] = {

    "kisan": VoterGroup(
        id="kisan",
        name="किसान",
        name_en="Farmers",
        population_pct=0.30,
        description=(
            "The agrarian backbone of the Panchayat. Mostly small and marginal "
            "landholders (< 2 hectares) growing wheat, rice, and sugarcane. They "
            "are deeply skeptical of politicians but fiercely loyal once trust is earned. "
            "They measure promises in quintals, not percentages."
        ),
        base_happiness=42.0,
        issue_weights={
            "msp_guarantee": 0.25,
            "water_irrigation": 0.20,
            "land_rights": 0.15,
            "subsidies_loans": 0.15,
            "crop_insurance": 0.10,
            "rural_infrastructure": 0.10,
            "education": 0.05,
        },
        ideology_alignment={
            "economy": 25,
            "social_progress": 35,
            "environment": 70,
            "technology": 30,
            "defense": 50,
            "welfare": 85,
            "governance_reform": 40,
            "cultural_identity": 65,
        },
        volatility=0.3,
        social_media_presence=0.2,
        key_demands=[
            "MSP at C2+50% formula",
            "Loan waiver for small farmers",
            "Free electricity for tube wells",
            "Crop insurance that actually pays out",
            "Ban on corporate contract farming",
        ],
        fear_triggers=[
            "land acquisition",
            "corporate farming",
            "subsidy cuts",
            "water privatization",
            "import liberalization of agri products",
        ],
        hope_triggers=[
            "MSP increase",
            "loan waiver",
            "free irrigation",
            "organic farming support",
            "farmer pension scheme",
        ],
        preferred_language="Hindi / Bhojpuri",
        emoji="🌾",
        color_theme="#4CAF50",
    ),

    "yuva": VoterGroup(
        id="yuva",
        name="युवा",
        name_en="Urban Youth",
        population_pct=0.25,
        description=(
            "Ages 18-30, concentrated in district towns and small cities. They are "
            "the first generation with smartphones and social media access. They dream "
            "of government jobs or startup success. Deeply frustrated with unemployment "
            "but easily swayed by viral content and celebrity endorsements."
        ),
        base_happiness=38.0,
        issue_weights={
            "employment": 0.30,
            "education_skills": 0.20,
            "technology_access": 0.15,
            "social_media_freedom": 0.10,
            "affordable_housing": 0.10,
            "entertainment_culture": 0.10,
            "governance_transparency": 0.05,
        },
        ideology_alignment={
            "economy": 60,
            "social_progress": 75,
            "environment": 45,
            "technology": 85,
            "defense": 55,
            "welfare": 50,
            "governance_reform": 80,
            "cultural_identity": 35,
        },
        volatility=0.8,
        social_media_presence=0.95,
        key_demands=[
            "10 lakh government jobs in 1 year",
            "Free coaching for competitive exams",
            "Startup incubation centers in every district",
            "4G/5G connectivity in all areas",
            "Transparent online recruitment (no rigging)",
        ],
        fear_triggers=[
            "exam paper leaks",
            "internet shutdowns",
            "privatization of education",
            "unemployment data",
            "reservation expansion",
        ],
        hope_triggers=[
            "job creation announcements",
            "skill development programs",
            "tech parks in small cities",
            "startup funding schemes",
            "exam reform",
        ],
        preferred_language="Hinglish (Hindi + English)",
        emoji="📱",
        color_theme="#2196F3",
    ),

    "vyapari": VoterGroup(
        id="vyapari",
        name="व्यापारी",
        name_en="Small Business Owners",
        population_pct=0.20,
        description=(
            "Shopkeepers, traders, small manufacturers, and service providers. They "
            "form the commercial middle class of the Panchayat. They are pragmatic, "
            "money-minded, and vote for whoever promises lower taxes and less red tape. "
            "They hate uncertainty more than anything."
        ),
        base_happiness=45.0,
        issue_weights={
            "gst_tax_reform": 0.25,
            "easy_credit_loans": 0.20,
            "deregulation": 0.15,
            "infrastructure": 0.15,
            "market_access": 0.10,
            "law_and_order": 0.10,
            "digital_payments": 0.05,
        },
        ideology_alignment={
            "economy": 80,
            "social_progress": 40,
            "environment": 25,
            "technology": 65,
            "defense": 55,
            "welfare": 20,
            "governance_reform": 70,
            "cultural_identity": 50,
        },
        volatility=0.5,
        social_media_presence=0.5,
        key_demands=[
            "Simplify GST to single slab",
            "Collateral-free loans up to 10 lakh",
            "No inspector raj—online compliance only",
            "Better roads and logistics infrastructure",
            "Protect small retail from e-commerce giants",
        ],
        fear_triggers=[
            "demonetization-style shocks",
            "tax raids",
            "new regulations",
            "e-commerce monopolies",
            "supply chain disruptions",
        ],
        hope_triggers=[
            "tax cuts",
            "easy loan schemes",
            "infrastructure projects",
            "deregulation",
            "market expansion",
        ],
        preferred_language="Hindi",
        emoji="🏪",
        color_theme="#FF9800",
    ),

    "sarkari": VoterGroup(
        id="sarkari",
        name="सरकारी",
        name_en="Government Employees",
        population_pct=0.15,
        description=(
            "Teachers, clerks, health workers, police constables, and panchayat "
            "secretaries. They already have job security and now want better pay, "
            "promotions, and pensions. They are conservative, risk-averse, and deeply "
            "connected to the bureaucratic machinery. They influence extended families."
        ),
        base_happiness=55.0,
        issue_weights={
            "pay_commission": 0.25,
            "pension_security": 0.25,
            "job_security": 0.15,
            "transfer_policy": 0.15,
            "working_conditions": 0.10,
            "governance_status_quo": 0.10,
        },
        ideology_alignment={
            "economy": 45,
            "social_progress": 30,
            "environment": 40,
            "technology": 40,
            "defense": 70,
            "welfare": 55,
            "governance_reform": 15,
            "cultural_identity": 60,
        },
        volatility=0.2,
        social_media_presence=0.3,
        key_demands=[
            "Implement 7th Pay Commission recommendations",
            "Restore Old Pension Scheme (OPS)",
            "No lateral entry—protect seniority system",
            "Fair transfer policy (no political transfers)",
            "Better working conditions in rural postings",
        ],
        fear_triggers=[
            "privatization of government services",
            "lateral entry to bureaucracy",
            "pension reform (NPS vs OPS)",
            "contractualization of permanent posts",
            "anti-corruption crackdowns targeting low-level staff",
        ],
        hope_triggers=[
            "pay hike announcements",
            "OPS restoration",
            "permanent regularization of contractual staff",
            "transfer policy reform",
            "promotion quota increases",
        ],
        preferred_language="Hindi (formal/sarkari)",
        emoji="🏛️",
        color_theme="#607D8B",
    ),

    "gramin_nari": VoterGroup(
        id="gramin_nari",
        name="ग्रामीण नारी",
        name_en="Rural Women",
        population_pct=0.10,
        description=(
            "Women from agricultural and laborer families, aged 25-55. Many are "
            "SHG (Self-Help Group) members. They are the silent vote bank—rarely "
            "vocal in public rallies but decisive in the voting booth. They care about "
            "safety, health, and their children's futures above all else."
        ),
        base_happiness=35.0,
        issue_weights={
            "safety_security": 0.25,
            "healthcare_maternal": 0.20,
            "shg_microfinance": 0.15,
            "education_children": 0.15,
            "water_sanitation": 0.15,
            "nutrition_food_security": 0.10,
        },
        ideology_alignment={
            "economy": 30,
            "social_progress": 70,
            "environment": 65,
            "technology": 25,
            "defense": 35,
            "welfare": 90,
            "governance_reform": 55,
            "cultural_identity": 50,
        },
        volatility=0.4,
        social_media_presence=0.1,
        key_demands=[
            "Women's safety: streetlights, police patrols, fast-track courts",
            "Free maternal healthcare at PHCs",
            "Expand SHG loan limits to 5 lakh",
            "Mid-day meal quality improvement",
            "Functional toilets and clean drinking water in every hamlet",
        ],
        fear_triggers=[
            "crimes against women",
            "alcohol/liquor shops near villages",
            "closure of Anganwadi centers",
            "cuts to PDS (ration) entitlements",
            "child marriage normalization",
        ],
        hope_triggers=[
            "women's reservation in Panchayat",
            "SHG empowerment programs",
            "free healthcare schemes",
            "education scholarships for girls",
            "liquor ban",
        ],
        preferred_language="Hindi / regional dialect",
        emoji="👩‍🌾",
        color_theme="#E91E63",
    ),
}


# ─── Utility Functions ──────────────────────────────────────────────────────

def get_all_voter_ids() -> List[str]:
    """Return all voter group IDs."""
    return list(VOTER_PROFILES.keys())


def get_voter_profile(group_id: str) -> Optional[VoterGroup]:
    """Get a voter profile by ID. Returns None if not found."""
    return VOTER_PROFILES.get(group_id)


def get_demographic_sentiment(group_name: str) -> Dict:
    """
    Get the current baseline sentiment of a voter demographic.
    This is the LangChain @tool compatible function.

    Args:
        group_name: One of 'kisan', 'yuva', 'vyapari', 'sarkari', 'gramin_nari'

    Returns:
        Dict with sentiment data including happiness, key demands, and triggers.
    """
    profile = VOTER_PROFILES.get(group_name)
    if not profile:
        return {"error": f"Unknown voter group: {group_name}. Valid: {get_all_voter_ids()}"}

    return {
        "group_id": profile.id,
        "group_name": profile.name_en,
        "population_pct": f"{profile.population_pct * 100:.0f}%",
        "current_happiness": profile.base_happiness,
        "happiness_label": _happiness_label(profile.base_happiness),
        "volatility": profile.volatility,
        "top_3_issues": list(profile.issue_weights.keys())[:3],
        "key_demands": profile.key_demands,
        "fear_triggers": profile.fear_triggers[:3],
        "hope_triggers": profile.hope_triggers[:3],
        "ideology_summary": _summarize_ideology(profile.ideology_alignment),
    }


def calculate_reaction(voter_group_id: str, policy_action: Dict) -> Dict:
    """
    Calculate how a voter group reacts to a policy action.

    Args:
        voter_group_id: The voter demographic ID
        policy_action: Dict with keys 'category', 'direction' (+1 or -1),
                       'magnitude' (0.0-1.0), and 'description'

    Returns:
        Dict with sentiment_shift, new_happiness, and narrative explanation.
    """
    profile = VOTER_PROFILES.get(voter_group_id)
    if not profile:
        return {"error": f"Unknown voter group: {voter_group_id}"}

    category = policy_action.get("category", "")
    direction = policy_action.get("direction", 0)
    magnitude = policy_action.get("magnitude", 0.5)

    # Find the weight of this issue for this voter group
    issue_weight = 0.0
    for issue, weight in profile.issue_weights.items():
        if category.lower() in issue.lower() or issue.lower() in category.lower():
            issue_weight = weight
            break

    # If no direct match, use a small default weight
    if issue_weight == 0.0:
        issue_weight = 0.05

    # Calculate sentiment shift
    # shift = direction * magnitude * issue_weight * 100 * volatility_factor
    volatility_factor = 0.5 + profile.volatility  # Range: 0.5 - 1.5
    raw_shift = direction * magnitude * issue_weight * 100 * volatility_factor
    clamped_shift = max(-30.0, min(30.0, raw_shift))  # Cap single-action shift

    new_happiness = max(0.0, min(100.0, profile.base_happiness + clamped_shift))

    # Determine narrative
    if clamped_shift > 10:
        narrative = f"The {profile.name_en} are energized! This directly addresses their demands."
    elif clamped_shift > 3:
        narrative = f"The {profile.name_en} cautiously approve. A step in the right direction."
    elif clamped_shift > -3:
        narrative = f"The {profile.name_en} are indifferent. This doesn't affect their daily lives."
    elif clamped_shift > -10:
        narrative = f"The {profile.name_en} are uneasy. This feels like a broken promise."
    else:
        narrative = f"The {profile.name_en} are furious! This is a direct betrayal of their interests."

    return {
        "voter_group": profile.name_en,
        "issue_relevance": issue_weight,
        "sentiment_shift": round(clamped_shift, 2),
        "old_happiness": profile.base_happiness,
        "new_happiness": round(new_happiness, 2),
        "narrative": narrative,
        "volatility_factor": round(volatility_factor, 2),
    }


# ─── Private Helpers ─────────────────────────────────────────────────────────

def _happiness_label(score: float) -> str:
    """Convert a happiness score to a human-readable label."""
    if score >= 80:
        return "Euphoric 🎉"
    elif score >= 60:
        return "Satisfied 😊"
    elif score >= 45:
        return "Neutral 😐"
    elif score >= 30:
        return "Discontented 😤"
    elif score >= 15:
        return "Angry 😡"
    else:
        return "Revolt 🔥"


def _summarize_ideology(scores: Dict[str, int]) -> str:
    """Generate a one-line ideology summary from the 8-axis scores."""
    high_axes = [k for k, v in scores.items() if v >= 70]
    low_axes = [k for k, v in scores.items() if v <= 30]

    parts = []
    if high_axes:
        parts.append(f"Strong on: {', '.join(high_axes)}")
    if low_axes:
        parts.append(f"Weak on: {', '.join(low_axes)}")
    return " | ".join(parts) if parts else "Moderate across all axes"


# ─── Quick Test ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("PANCHAYAT — Voter Demographic Profiles")
    print("=" * 60)

    for vid, vp in VOTER_PROFILES.items():
        sentiment = get_demographic_sentiment(vid)
        print(f"\n{vp.emoji} {vp.name} ({vp.name_en}) — {sentiment['population_pct']}")
        print(f"   Happiness: {sentiment['current_happiness']}/100 [{sentiment['happiness_label']}]")
        print(f"   Volatility: {vp.volatility}")
        print(f"   Top Issues: {', '.join(sentiment['top_3_issues'])}")
        print(f"   Ideology: {sentiment['ideology_summary']}")

    print("\n" + "=" * 60)
    print("Reaction Test: Farmer reacts to MSP increase")
    print("=" * 60)
    reaction = calculate_reaction("kisan", {
        "category": "msp_guarantee",
        "direction": 1,
        "magnitude": 0.8,
        "description": "Increase MSP by 20% for wheat and rice",
    })
    for k, v in reaction.items():
        print(f"   {k}: {v}")
