# 📖 Panchayat Data Layer — Technical Documentation

> **Author**: Apurva Verma  
> **Last Updated**: April 3, 2026  
> **Status**: ✅ Complete & Tested (694/694 validations pass)

---

## Table of Contents

1. [What Is This?](#what-is-this)
2. [Architecture Overview](#architecture-overview)
3. [File Reference](#file-reference)
4. [The 4 AI Candidates](#the-4-ai-candidates)
5. [The 5 Voter Demographics](#the-5-voter-demographics)
6. [The 8-Axis Ideology Model](#the-8-axis-ideology-model)
7. [How to Use — Quick Start](#how-to-use--quick-start)
8. [API Reference — Python Functions](#api-reference--python-functions)
9. [How It Connects to the Game](#how-it-connects-to-the-game)
10. [Bridge Layer — LangGraph + Gemini Prototype](#bridge-layer--langgraph--gemini-prototype)
11. [For Teammates — Integration Guide](#for-teammates--integration-guide)
12. [Validation & Testing](#validation--testing)

---

## What Is This?

The `data/` folder is the **complete intelligence layer** for Panchayat — an AI-powered political simulator. It contains:

- **4 AI candidate personas** with Gemini system prompts, ideology vectors, and backstories
- **5 voter demographics** with sentiment baselines, issue priorities, and reaction engines
- **20 real Indian political scenarios** (replacing the n8n automation pipeline)
- **20 policy manifestos** with ideology impact scores
- **Dialogue templates** for rally speeches, attacks, defenses (Hindi + English)
- **12 scandal/weakness cards** with severity and counter-narratives
- **Mathematical scoring engine** (cosine similarity, election simulation)
- **6 LangChain-compatible tool functions** (simplified MCP replacement)

**Zero external dependencies** — the data layer runs on pure Python 3.10+ standard library.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        GAME CLIENT (UI)                         │
│                   (React/Next.js or Terminal)                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     bridge/ (Integration)                        │
│  ┌─────────────┐  ┌──────────────────┐  ┌─────────────────┐    │
│  │ ai_prompts   │  │ langgraph_engine │  │ tools_langchain │    │
│  │ .py          │  │ .py              │  │ .py             │    │
│  │              │  │                  │  │                 │    │
│  │ Builds       │  │ LangGraph state  │  │ @tool wrappers  │    │
│  │ system       │  │ machine: ReAct   │  │ for LangChain   │    │
│  │ prompts from │  │ agents per       │  │                 │    │
│  │ candidate    │  │ candidate        │  │ 6 functions     │    │
│  │ data         │  │                  │  │ ready for       │    │
│  │              │  │ Gemini 2.5       │  │ Gemini tool     │    │
│  │              │  │ Flash Lite       │  │ calling         │    │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬────────┘    │
└─────────┼───────────────────┼─────────────────────┼─────────────┘
          │                   │                     │
┌─────────▼───────────────────▼─────────────────────▼─────────────┐
│                       data/ (THIS FOLDER)                        │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │ candidates.json  │  │ scenarios.json   │  │ manifestos.json│   │
│  │ 4 AI personas    │  │ 20 real-world    │  │ 20 policies    │   │
│  │ + system prompts │  │ Indian events    │  │ 5 per candidate│   │
│  └────────┬─────────┘  └────────┬─────────┘  └───────┬────────┘  │
│           │                     │                     │          │
│  ┌────────▼─────────┐  ┌───────▼──────────┐  ┌───────▼────────┐ │
│  │ voter_profiles.py │  │ ideology_engine  │  │ tools.py       │ │
│  │ 5 demographics    │  │ .py              │  │ 6 search/query │ │
│  │ + sentiment calc  │  │ cosine sim,      │  │ functions      │ │
│  │                   │  │ election sim     │  │                │ │
│  └───────────────────┘  └──────────────────┘  └────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │ dialogues.json   │  │ weaknesses.json  │  │validate_data.py│   │
│  │ speeches, attacks│  │ 12 scandals      │  │ 694 tests      │   │
│  └──────────────────┘  └──────────────────┘  └────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## File Reference

| File | Type | Size | What It Contains |
|------|------|------|-----------------|
| `candidates.json` | Data | 15.7 KB | 4 AI candidate archetypes with system prompts, ideology scores (0-100 on 8 axes), backstories, speaking styles, trigger phrases, natural allies/enemies |
| `voter_profiles.py` | Code + Data | 18.8 KB | 5 voter demographics as Python dataclasses with sentiment baselines, issue weights, ideology alignment, volatility, `calculate_reaction()` function |
| `manifestos.json` | Data | 15.5 KB | 20 policy planks (5 per candidate) with ideology impact vectors showing how each policy shifts the 8-axis scores |
| `dialogues.json` | Data | 12.9 KB | Rally speeches (Hindi + English), attack lines against each opponent, defense templates, policy reaction templates, victory/defeat speeches |
| `weaknesses.json` | Data | 9.2 KB | 12 scandals (3 per candidate) with severity (1-5), evidence descriptions, demographic impact scores, counter-narratives the AI can use to defend itself |
| `scenarios.json` | Data | 27.4 KB | 20 curated real Indian political events (2006-2024) with pre-computed 4-way ideology analysis, affected voter groups, and policy tags. **Replaces n8n live-news pipeline** |
| `ideology_engine.py` | Code | 11.8 KB | Cosine similarity between ideology vectors, policy impact calculation, candidate ranking per voter group, election simulation using softmax-weighted voting |
| `tools.py` | Code | 17.0 KB | 7 search/query functions that the LLM calls during reasoning. **Replaces formal MCP servers** with standard Python functions |
| `validate_data.py` | Code | 15.7 KB | Comprehensive schema validation — checks all JSON schemas, cross-references IDs, validates score ranges, tests functions |
| `__init__.py` | Code | 1.9 KB | Package exports — makes all functions importable via `from data import ...` |

---

## The 4 AI Candidates

Each candidate is a fully realized political persona with a Gemini `system_instruction` that locks the LLM into character.

### 🕉️ Pt. Vedprakash Shastri — **Dharma Rakshak** (Traditionalist)

| Field | Value |
|-------|-------|
| Party | Sanskriti Seva Dal |
| Age | 62 |
| Backstory | Former Sanskrit professor from Varanasi. Rose through temple reform movements. Quotes the Arthashastra in every debate. |
| Core Beliefs | Ancient Indian wisdom > Western models. Protect farmers, cows, temples. Ban foreign investment in agriculture. |
| Speaking Style | Measured, philosophical, patronizing. Uses Sanskrit slokas. |
| Natural Allies | 🌾 Kisan (Farmers), 🏛️ Sarkari (Govt. Employees) |
| Natural Enemies | 📱 Yuva (Youth), 🏪 Vyapari (Business) |
| Top Ideology Scores | Cultural Identity: 95, Defense: 80, Environment: 55 |
| Bottom Scores | Social Progress: 15, Technology: 20, Governance Reform: 25 |

### 📱 Arjun Mehra — **Vikas Purush** (Techno-Populist)

| Field | Value |
|-------|-------|
| Party | Digital Bharat Front |
| Age | 44 |
| Backstory | IIT Delhi alumnus, fintech founder. Brought UPI to 500 villages. Runs campaigns on Instagram Reels. |
| Core Beliefs | Every problem has a digital solution. Data-driven governance. Startups > factories. |
| Speaking Style | TED-talk energy, rapid-fire, startup jargon, stats-heavy. |
| Natural Allies | 📱 Yuva (Youth), 🏪 Vyapari (Business) |
| Natural Enemies | 🌾 Kisan (Farmers), 👩‍🌾 Rural Women |
| Top Ideology Scores | Technology: 95, Governance Reform: 85, Economy: 75 |
| Bottom Scores | Cultural Identity: 30, Welfare: 35 |

### ✊ Comrade Meera Devi Yadav — **Jan Neta** (Socialist Reformer)

| Field | Value |
|-------|-------|
| Party | Samta Shakti Morcha |
| Age | 51 |
| Backstory | Former MNREGA supervisor from Jharkhand. Organized 10,000 tribal women. Led the 'Roti Andolan'. |
| Core Beliefs | Land to the tiller. MNREGA to 200 days. Caste justice. Corporations are neo-zamindars. |
| Speaking Style | Fiery, confrontational, storytelling, colloquial Hindi/Bhojpuri. |
| Natural Allies | 🌾 Kisan (Farmers), 👩‍🌾 Rural Women |
| Natural Enemies | 🏪 Vyapari (Business), 🏛️ Sarkari (Govt. Employees) |
| Top Ideology Scores | Welfare: 95, Social Progress: 85, Governance Reform: 70 |
| Bottom Scores | Economy: 15, Technology: 25 |

### 📈 Nandini Krishnamurthy — **Mukti Devi** (Corporate Libertarian)

| Field | Value |
|-------|-------|
| Party | Swatantra Vikas Party |
| Age | 48 |
| Backstory | Former World Bank economist. Part of the 1991 liberalization team. Founded 'Pragati Foundation' think tank. |
| Core Beliefs | Free markets solve everything. Privatize services. Replace subsidies with cash transfers. |
| Speaking Style | Polished, professional McKinsey-speak, economic jargon, international references. |
| Natural Allies | 🏪 Vyapari (Business), 📱 Yuva (Youth) |
| Natural Enemies | 🌾 Kisan (Farmers), 👩‍🌾 Rural Women |
| Top Ideology Scores | Economy: 95, Governance Reform: 80, Technology: 70 |
| Bottom Scores | Welfare: 10, Cultural Identity: 20 |

---

## The 5 Voter Demographics

Each voter group has a `base_happiness` (starting mood), `issue_weights` (what they care about), and `volatility` (how easily their opinion swings).

| Group | Pop% | Start Happiness | Volatility | Top Issues |
|-------|------|----------------|-----------|------------|
| 🌾 **Kisan** (Farmers) | 30% | 42 😤 | 0.3 (Stable) | MSP guarantee, Water/irrigation, Land rights |
| 📱 **Yuva** (Urban Youth) | 25% | 38 😤 | 0.8 (Very volatile) | Employment, Education/skills, Tech access |
| 🏪 **Vyapari** (Small Business) | 20% | 45 😐 | 0.5 (Moderate) | GST/tax reform, Easy loans, Deregulation |
| 🏛️ **Sarkari** (Govt. Employees) | 15% | 55 😐 | 0.2 (Very stable) | Pay commission, Pension security, Job security |
| 👩‍🌾 **Gramin Nari** (Rural Women) | 10% | 35 😤 | 0.4 (Moderate) | Safety/security, Healthcare, SHG/microfinance |

**Key Design**: Population sums to 100%. Issue weights per group sum to 1.0. Volatility ranges from 0-1 and acts as a multiplier on sentiment shifts.

---

## The 8-Axis Ideology Model

Every candidate and voter group is scored on 8 independent axes (0-100 scale):

| Axis | Low (0) | High (100) | What It Measures |
|------|---------|-----------|-----------------|
| **Economy** | Socialist | Free Market | State control vs market freedom |
| **Social Progress** | Conservative | Progressive | Traditional hierarchy vs equality |
| **Environment** | Exploit | Protect | Industrial growth vs conservation |
| **Technology** | Skeptic | Evangelist | Cautious vs aggressive digitization |
| **Defense** | Dove | Hawk | Diplomacy vs military strength |
| **Welfare** | Minimal | Universal | Self-reliance vs state safety nets |
| **Governance Reform** | Status Quo | Radical Reform | Institutional continuity vs overhaul |
| **Cultural Identity** | Cosmopolitan | Nativist | Globalized vs indigenous preservation |

**Why 8 axes?** Simple left-right doesn't capture Indian politics. A candidate can be economically socialist but culturally conservative (like Jan Neta). The 8-axis model creates meaningful differentiation.

**Cosine similarity** is used to compare ideology vectors. Two candidates with similar directional preferences score close to 1.0 regardless of absolute magnitude.

---

## How to Use — Quick Start

### Installation

```bash
# The data layer needs ZERO pip installs
# Only Python 3.10+ standard library
cd ~/Panchayat
python3 -m data.validate_data   # Run 694 validation tests
```

### Basic Usage in Python

```python
import sys
sys.path.insert(0, '/path/to/Panchayat')

# ─── Load candidate data ────────────────────────────
from data.ideology_engine import load_candidates, get_candidate_ideologies

candidates = load_candidates()
for c in candidates["candidates"]:
    print(f"{c['emoji']} {c['name']} ({c['archetype']})")
    print(f"   System prompt: {c['system_prompt'][:80]}...")

# ─── Get voter sentiments ───────────────────────────
from data.voter_profiles import VOTER_PROFILES, get_demographic_sentiment

sentiment = get_demographic_sentiment("kisan")
print(f"Farmer happiness: {sentiment['current_happiness']}/100")
print(f"Top demand: {sentiment['key_demands'][0]}")

# ─── Calculate voter reaction to a policy ────────────
from data.voter_profiles import calculate_reaction

reaction = calculate_reaction("kisan", {
    "category": "msp_guarantee",
    "direction": 1,      # positive
    "magnitude": 0.8,    # strong
    "description": "Increase MSP by 50%",
})
print(f"Sentiment shift: {reaction['sentiment_shift']:+.1f}")
print(f"Narrative: {reaction['narrative']}")
# Output: +16.0, "The Farmers are energized!"

# ─── Rank candidates for a voter group ───────────────
from data.ideology_engine import rank_candidates_for_voter, get_candidate_ideologies

rankings = rank_candidates_for_voter(
    VOTER_PROFILES["kisan"].ideology_alignment,
    get_candidate_ideologies()
)
for rank, (cid, score) in enumerate(rankings, 1):
    print(f"#{rank} {cid}: {score:.4f}")
# Output: #1 jan_neta, #2 dharma_rakshak, #3 vikas_purush, #4 mukti_devi

# ─── Simulate an election ───────────────────────────
from data.ideology_engine import simulate_election_result

result = simulate_election_result(
    voter_sentiments={"kisan": {"jan_neta": 80, "dharma_rakshak": 70, ...}, ...},
    voter_populations={"kisan": 0.30, "yuva": 0.25, ...}
)
print(f"Winner: {result['winner']}, Margin: {result['margin']:.1f}%")

# ─── Use tool functions (for LLM agents) ────────────
from data.tools import search_ideology_db, analyze_player_move

# Search for real-world scenarios
context = search_ideology_db("dharma_rakshak", "agriculture")
print(context)  # Returns formatted text with Farm Bills, PM-KISAN, etc.

# Analyze how a candidate would react
analysis = analyze_player_move("Build 5G towers in villages", "jan_neta")
print(analysis)  # Returns ideology analysis, template reaction, historical context
```

---

## API Reference — Python Functions

### `data/voter_profiles.py`

| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| `get_demographic_sentiment(group_id)` | `str` | `Dict` | Get full sentiment profile of a voter group |
| `calculate_reaction(group_id, policy_action)` | `str, Dict` | `Dict` | Compute how a policy shifts voter sentiment |
| `get_voter_profile(group_id)` | `str` | `VoterGroup` | Get the raw dataclass for a voter group |
| `get_all_voter_ids()` | — | `List[str]` | Returns `['kisan', 'yuva', 'vyapari', 'sarkari', 'gramin_nari']` |

### `data/ideology_engine.py`

| Function | Args | Returns | Description |
|----------|------|---------|-------------|
| `compute_ideology_distance(a, b)` | `Dict, Dict` | `float (0-1)` | Cosine similarity between two ideology vectors |
| `compute_euclidean_distance(a, b)` | `Dict, Dict` | `float (0-1)` | Normalized Euclidean distance |
| `compute_policy_impact(policy, voter, weights, category)` | Multiple | `Dict` | How a policy shifts a voter group's sentiment |
| `rank_candidates_for_voter(voter, candidates)` | `Dict, Dict` | `List[Tuple]` | Rank candidates by ideology alignment |
| `simulate_election_result(sentiments, populations)` | `Dict, Dict` | `Dict` | Softmax-weighted voting simulation |
| `load_candidates()` / `load_scenarios()` / ... | — | `Dict` | Load JSON data files |

### `data/tools.py` — LLM Tool Functions

These are the functions Gemini calls during reasoning. Each returns formatted text.

| Function | Args | Description |
|----------|------|-------------|
| `search_ideology_db(archetype, category)` | `str, str` | Search scenarios DB for real-world examples matching an archetype |
| `get_past_policies(archetype)` | `str` | Get candidate's manifesto + historical precedents |
| `analyze_player_move(action, archetype)` | `str, str` | Cross-reference player's action against candidate's beliefs |
| `get_demographic_sentiment(group)` | `str` | Get voter group's current mood and demands |
| `search_scenario_impact(keyword)` | `str` | Search for real-world impacts of similar policies |
| `get_candidate_weakness(candidate_id)` | `str` | Get scandal data opponents could exploit |
| `get_candidate_dialogue(candidate_id, type)` | `str, str` | Get specific dialogue template |

---

## How It Connects to the Game

### Game Turn Flow

```
PLAYER picks a policy (e.g., "Increase MSP by 50%")
    │
    ▼
┌── BRIDGE: LangGraph ReAct Agent (per candidate) ──────────┐
│   1. Agent receives player action                         │
│   2. Gemini decides: "I need context" → calls tools       │
│   3. Tool: search_ideology_db("dharma_rakshak", "agri")   │
│      → Returns Farm Bills 2020, PM-KISAN scenarios        │
│   4. Tool: get_demographic_sentiment("kisan")             │
│      → Returns farmer mood: 42/100, demands MSP           │
│   5. Gemini generates in-character reaction                │
│      → "As Chanakya taught us... this is vikas ka bhram"   │
└────────────────────────────────────────────────────────────┘
    │
    ▼
┌── DATA: Ideology Engine ──────────────────────────────────┐
│   1. calculate_reaction() for each voter group            │
│   2. Farmers: +16 happiness (MSP directly addresses them) │
│   3. Business: -3 happiness (worried about cost)          │
│   4. simulate_election_result() with new sentiments       │
│      → Updated poll numbers                               │
└────────────────────────────────────────────────────────────┘
    │
    ▼
UI displays: candidate reactions + voter shifts + new polls
```

### What Each Module Provides to the Game

| Game Feature | Data Module Used |
|-------------|-----------------|
| AI candidate personality | `candidates.json` → `system_prompt` field |
| What candidates say in rallies | `dialogues.json` → `rally_speech`, `attack_opponent` |
| What policies are available | `manifestos.json` → 5 policies per candidate |
| How voters react to policies | `voter_profiles.py` → `calculate_reaction()` |
| Who is winning the election | `ideology_engine.py` → `simulate_election_result()` |
| Which candidate appeals to whom | `ideology_engine.py` → `rank_candidates_for_voter()` |
| Scandals that can be played | `weaknesses.json` → severity, demographic impact |
| Real-world grounding for AI | `scenarios.json` → 20 Indian political events |
| LLM tool calling during reasoning | `tools.py` → 7 search/query functions |

---

## Bridge Layer — LangGraph + Gemini Prototype

The `bridge/` folder contains the working integration:

### Files

| File | What It Does |
|------|-------------|
| `bridge/tools_langchain.py` | Wraps `data/tools.py` functions with `@tool` decorator for LangChain |
| `bridge/ai_prompts.py` | Builds Gemini system instructions from `candidates.json` persona data |
| `bridge/langgraph_engine.py` | LangGraph ReAct agents — one per candidate. Each agent can call tools, reason, and respond in character |
| `bridge/prototype.py` | Rich terminal UI for interactive demo |

### Tech Stack

| Component | Package | Version | Purpose |
|-----------|---------|---------|---------|
| LLM | `langchain-google-genai` | 4.2.1 | Gemini ↔ LangChain bridge |
| Model | `gemini-2.5-flash-lite` | — | Free tier: 10 RPM, 20 RPD |
| Orchestration | `langgraph` | 1.1.5 | Stateful agent workflow graphs |
| Tools | `langchain-core` | 1.2.25 | `@tool` decorator for function calling |
| UI | `rich` | 14.3.3 | Beautiful terminal output |

### Running the Prototype

```bash
# 1. Activate venv
cd ~/Panchayat && source .venv/bin/activate

# 2. Set your Gemini API key in .env
echo 'GOOGLE_API_KEY=your_key_here' > .env

# 3. Run prototype
python3 -m bridge.prototype

# 4. Or test a single candidate
python3 -m bridge.langgraph_engine
```

### Rate Limits (Free Tier)

- **Model**: `gemini-2.5-flash-lite`
- **10 RPM** (requests per minute) → 7-second delay between API calls
- **20 RPD** (requests per day) → ~4-5 full game turns per day
- Each turn = 4 API calls (one per AI candidate)

---

## For Teammates — Integration Guide

### If you're working on the **Frontend (client/)**:

The data layer provides all the content you need to render:

```javascript
// Candidate cards — use data from candidates.json
fetch('/api/candidates')  // returns { candidates: [...] }
// Each has: id, name, emoji, color_theme, backstory, archetype

// Voter dashboard — use sentiment values
fetch('/api/voters')  // returns { kisan: {happiness: 42, ...}, ... }
// Color code: green (>60), yellow (40-60), red (<40)

// Policy options — use from manifestos.json
fetch('/api/manifestos')  // returns policies per candidate
```

### If you're working on the **Server (server/)**:

Import data functions directly:

```python
# In server/main.py
import sys
sys.path.insert(0, '..')

# For game logic
from data.ideology_engine import simulate_election_result
from data.voter_profiles import calculate_reaction, VOTER_PROFILES

# For AI agent responses
from bridge.langgraph_engine import run_full_turn, GameState
```

### If you're working on the **Blockchain (bridge/solana_notary.py)**:

The game state to notarize after each turn:

```python
game_state = {
    "turn": 3,
    "voter_sentiments": {"kisan": 58.4, "yuva": 41.2, ...},
    "candidate_scores": {"dharma_rakshak": 52.1, ...},
    "action_hash": "sha256_of_player_action",
}
# Notarize this on Solana after each turn
```

### Adding New Content

**New candidate:**
1. Add entry to `candidates.json` with all fields
2. Add manifesto to `manifestos.json` (5 policies)
3. Add dialogues to `dialogues.json`
4. Add weaknesses to `weaknesses.json` (2-3 scandals)
5. Add ideology_analysis entry in each scenario in `scenarios.json`
6. Run `python3 -m data.validate_data` to verify

**New voter group:**
1. Add `VoterGroup` entry to `VOTER_PROFILES` in `voter_profiles.py`
2. Ensure population percentages still sum to 1.0
3. Ensure issue_weights sum to 1.0
4. Add this group to affected_demographics in relevant scenarios
5. Run validation

**New scenario:**
1. Add entry to `scenarios.json` with ideology_analysis for ALL 4 candidates
2. Run validation

---

## Validation & Testing

```bash
# Full validation (694 tests)
python3 -m data.validate_data

# Test voter profiles + reaction math
python3 -m data.voter_profiles

# Test ideology engine + election simulation
python3 -m data.ideology_engine

# Test tools (requires no API key)
python3 -c "from data.tools import search_ideology_db; print(search_ideology_db('dharma_rakshak', 'agriculture'))"

# Test LangGraph engine (requires API key in .env)
python3 -m bridge.langgraph_engine

# Full interactive prototype
python3 -m bridge.prototype
```

### Validation Checks (694 total)

- ✅ All 5 JSON files parse correctly
- ✅ 4 candidates have all required fields
- ✅ All ideology scores in 0-100 range
- ✅ System prompts are substantive (>200 chars)
- ✅ All ally/enemy references are valid voter IDs
- ✅ 5 voter profiles with correct population sum (1.0)
- ✅ Issue weights sum to 1.0 for each voter
- ✅ 5 policies per manifesto, covering 4+ categories
- ✅ All dialogue types present for all candidates
- ✅ 2+ weaknesses per candidate, severity 1-5
- ✅ 20 scenarios covering 4+ categories
- ✅ All scenarios have analysis for all 4 candidates
- ✅ Tool functions return valid data
- ✅ Ideology engine math produces correct ranges

---

## Design Decisions & Tradeoffs

| Decision | Why |
|----------|-----|
| **8-axis ideology** instead of left-right | Indian politics is multidimensional. A candidate can be pro-welfare but anti-tech. |
| **Cosine similarity** instead of Euclidean | Measures direction of ideology, not magnitude. Two candidates can differ in intensity but agree on direction. |
| **Softmax voting** instead of simple max | Creates non-linear dynamics. Small sentiment shifts near the top have outsized effects. |
| **Hindi + English dialogues** | Authenticity for Indian political setting. Code-switching is natural. |
| **No n8n automation** | Hackathon tradeoff. 20 curated scenarios > unreliable live pipeline. |
| **No formal MCP servers** | Standard `@tool` functions achieve the same result with 50% less boilerplate. |
| **Pre-computed ideology analysis** | Scenarios have all 4 candidates' positions pre-mapped, eliminating an LLM call during game. |
