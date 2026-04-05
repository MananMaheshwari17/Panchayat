
# Panchayat

### Learn Democracy by Living It — A Retro Pixel-Art Political Simulator

**Live Demo: [http://65.20.91.167/](http://65.20.91.167/)**

**HackByte 4.0 | Claw & Shield Track (ArmorIQ x OpenClaw)**

---

## The Problem: Political Illiteracy in the World's Largest Democracy

India has **950 million** eligible voters, yet most citizens:

- Cannot name 3 policies from any party's manifesto
- Don't understand how elections are won or lost beyond caste/religion lines
- Have never experienced the strategic complexity behind policy-making
- Are unaware of election laws like the **Model Code of Conduct**, **RPA Section 125**, or **IPC Section 171**

**Panchayat** solves this by letting you *become* a politician. You don't read about democracy — you compete in it against 4 AI opponents who fight back, sabotage your campaign, and try to win the electorate. Every attack is validated by an **Election Commissioner (ArmorIQ)**. Every vote you win or lose is earned through **policy, strategy, and political combat**.

---

## What is Panchayat?

A **turn-based political simulation** with a retro 16-bit pixel-art aesthetic where you compete as an independent candidate against 4 AI-powered opponents in a Panchayat (village council) election. Over 5 rounds, you:

1. **Build your manifesto** by choosing from dozens of real-world Indian policy proposals
2. **Manage your coin economy** — every action costs coins (manifesto: 50, sabotage: 75, deepfake: 150)
3. **Launch sabotage attacks** against opponents — write your own political attack dialogue
4. **Deploy deepfake audio attacks** — AI generates fake confessions in the target's voice (Hindi)
5. **Defend with voice watermarking** — purchase audio authenticity shields to counter deepfakes
6. **Watch NPC candidates** autonomously pick manifestos, launch sabotages, and fight each other
7. **Win the election** by having the highest total voter share across 5 demographics

The twist: **Every sabotage is validated by the Election Commissioner (ArmorIQ + Groq)** — communal hate speech, fabricated criminal accusations, threats of violence, sexist attacks, and health misinformation are automatically blocked with a detailed reason citing Indian election law.

---

## Sponsor Track: Claw & Shield (ArmorIQ x OpenClaw)

### How We Implement Every Hackathon Requirement

| Hackathon Requirement | Our Implementation | Code Location |
|---|---|---|
| **Structured Intent Model** | Sabotage prompts validated against structured Election Code of Conduct | `server/fastapi_server.py:76-88` |
| **Policy-based Runtime Enforcement** | 2-layer: ArmorIQ SDK cryptographic verification, Groq LLM judge fallback | `server/fastapi_server.py:154-227` |
| **Separation of Reasoning & Execution** | Groq (reasoning) generates NPC strategy, ArmorIQ/Groq (enforcement) validates, MongoDB (state mutation) | `server/fastapi_server.py` |
| **At least 1 Allowed Action** | Policy critique, public challenge, exposing genuine weaknesses — all pass Election Commissioner | Verified in gameplay |
| **At least 1 Blocked Action** | Communal incitement, personal attacks, fabricated charges, threats, sexist attacks — deterministically blocked | Election Code of Conduct rules 1-5 |
| **Logged & Explained Decisions** | Every verdict returned with `allowed: true/false` and `reason` explaining which Code of Conduct rule was violated | API response JSON |
| **No hardcoded shortcuts** | Real Groq LLM reasoning for NPC strategy; ArmorIQ SDK for cryptographic enforcement; structured JSON election code | Full stack |

### Architecture: Election Commission as a Service

```text
PLAYER
  | (Builds manifesto -> Launches sabotage -> Buys deepfakes/watermarks)
  v
GROQ (NPC Reasoning Layer)
  | AI NPCs autonomously choose: manifesto OR sabotage
  | Output: Structured action JSON with target, sabotage_text, deepfake flag
  v
ARMORIQ + GROQ (Election Commissioner)
  | 1. ArmorIQ SDK -> Cryptographic intent verification
  | 2. Groq Judge fallback -> LLM evaluates against Election Code of Conduct
  | Output: {allowed: true/false, reason: "..."}
  v
GAME ENGINE (State Mutation in MongoDB)
  | Only processes ALLOWED actions -> Updates voter shares
  | Deepfake attacks: Groq generates Hindi confession -> ElevenLabs TTS in target voice
  | Watermark defense: FFT-based 19kHz sine wave detection blocks deepfakes
```

---

## Screenshots

<p align="center">
  <img src="client/assets/readme1.png" alt="Panchayat Gameplay - Main Interface" width="48%">
  <img src="client/assets/readme2.png" alt="Panchayat Gameplay - Election Results" width="48%">
</p>

---

## Features

### 1. Retro Pixel-Art Game Interface

The entire UI is built as a **16-bit retro game** using the `Press Start 2P` pixel font:

- **Start screen** with Single Player / Multiplayer (coming soon) menu
- **Wood-textured top bar** with level badge, round tracker, and coin counter
- **Pixel-art candidate avatars** — unique generated portraits for player and all NPCs
- **Animated firefly particle system** on canvas for atmospheric village background
- **Procedural chiptune BGM** and sound effects via Web Audio API synthesizer
- **Visual novel-style dialogue popup** with speaker portraits and audio waveform indicator
- **Responsive layout** with sidebar opponents panel and leaderboard widget

### 2. Manifesto System — Real-World Indian Policies

Each round presents policies from categories like agriculture, education, technology, labor, and governance. Examples:

- *"Mandi Modernization Act — Blockchain-tracked cold storage"*
- *"Abhyudaya Coaching Corps — Free JEE/NEET/UPSC coaching in every village"*
- *"Shramik Suraksha Insurance — Guaranteed daily-wage insurance"*
- *"Panchayat Fiber Revolution — High-speed 5G broadband"*

Each manifesto targets one of **5 voter groups** (Farmers, Students, Tech Workers, Laborers, Youth) and shifts vote shares using a **waterfall redistribution algorithm** — gaining votes from one group means rivals lose proportionally.

### 3. AI Political Agents — 4 Distinct Ideologies

Each AI candidate is a fully-realized political persona with unique system prompts, ideology scores across 8 axes, and speaking styles:

| Candidate | Title | Party | Archetype | Key Trait |
|---|---|---|---|---|
| **Pt. Vedprakash Shastri** | Dharma Rakshak | Sanskriti Seva Dal | Traditionalist | Quotes the Arthashastra; cow-based economics |
| **Arjun Mehra** | Vikas Purush | Digital Bharat Front | Techno-Populist | IIT alumnus; campaigns on Instagram Reels |
| **Comrade Meera Devi Yadav** | Jan Neta | Samta Shakti Morcha | Socialist Reformer | Led the 'Roti Andolan'; fights for daily-wage workers |
| **Nandini Krishnamurthy** | Mukti Devi | Swatantra Vikas Party | Corporate Libertarian | Former World Bank economist; 1991 reforms veteran |

NPCs are powered by **Groq (Llama 3.1 8B)** for turn strategy and by **Google Gemini + LangGraph** for in-character reactions with tool use.

### 4. Sabotage System — Political Combat

Every player and NPC can launch **sabotage attacks** against rivals:

- **Write your own attack dialogue** — expose weaknesses, scandals, policy failures
- **AI-evaluated damage** — Groq rates impact (10%-50% voter share loss) based on how well the attack targets actual weaknesses
- **NPC sabotage AI** — NPCs autonomously choose targets and craft attack dialogues using Groq
- **Coin economy** — sabotage costs 75 coins; NPCs earn 50 coins per round

### 5. Deepfake Audio Attacks

A devastating special attack (150 coins):

- **AI generates a fake admission in Hindi** (Devanagari) — as if the target candidate is confessing to a scandal
- **Spoken in the target's cloned voice** using ElevenLabs TTS
- **40%-75% voter share damage** — far more devastating than standard sabotage

### 6. Voice Watermark Defense

Players can purchase **Voice Authenticity** (100 coins):

- Injects an **inaudible 19kHz sine wave** watermark into all TTS audio using FFmpeg + NumPy
- When a deepfake targets a watermarked candidate, **FFT-based spectral analysis** detects the signature
- The deepfake attack is **blocked** and the attacker's investment is wasted

### 7. Election Commissioner — Code of Conduct Enforcement

Every sabotage (by player or NPC) passes through a **2-layer enforcement system**:

| Violation Type | Legal Reference | Action |
|---|---|---|
| Communal/religious/caste slurs | Section 125, RPA | BLOCKED |
| Fabricated criminal charges | IPC Section 171G | BLOCKED |
| Threats or incitement of violence | IPC Section 171C | BLOCKED |
| Sexist/gender-based attacks | Model Code of Conduct | BLOCKED |
| False health/death rumours | Model Code of Conduct | BLOCKED |
| Genuine policy criticism and satire | — | ALLOWED |
| Public records and RTI findings | — | ALLOWED |
| Track record attacks | — | ALLOWED |

**Layer 1**: ArmorIQ SDK — cryptographic plan capture, intent tokenization, and MCP invocation for validated enforcement.

**Layer 2 (Fallback)**: Groq LLM judge — evaluates against the full Election Code of Conduct with JSON-structured verdicts.

### 8. ElevenLabs Voice Integration

Every candidate speaks with **ElevenLabs Flash v2.5** TTS with style-specific voice settings:

- **Male Indian voice** for Vikas Purush, Dharma Rakshak, Jan Neta, and Player
- **Female Indian voice** for Mukti Devi
- **8 speech styles** — visionary, inspirational, emotional, aggressive, nationalist, etc. — each with tuned stability/similarity settings
- Voice IDs stored in **MongoDB** per candidate for persistent configuration

### 9. Dynamic Vote Distribution

Votes shift based on:

- **Manifesto policy targeting** — each policy targets a specific voter group with a fixed shift amount
- **Waterfall redistribution** — when one candidate gains, opponents lose proportionally (capped at 20% per group)
- **Sabotage damage multipliers** — losses distributed equally among all other candidates
- **5 voter demographics x 5 candidates** = 25 independent share values tracked in MongoDB

### 10. Procedural Sound System

Full **Web Audio API** sound engine with:

- **Chiptune sound effects** — procedurally synthesized hover, click, error, success, sabotage, and round chime sounds
- **Ambient village atmosphere** — procedural low-pass filtered white noise simulating river sounds
- **Background music** — procedural C major 7th drone pad with triangle waves and chorus detuning
- **Support for real audio files** — loads WAV/MP3 assets if available, falls back to synth

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Vanilla HTML + CSS + JavaScript | 16-bit pixel-art game UI with Press Start 2P font |
| **Backend** | FastAPI + Python | REST API, game engine, static file serving |
| **Database** | MongoDB Atlas (PyMongo) | Persistent game state — candidates, voter shares, manifesto bank |
| **NPC AI** | Groq (Llama 3.1 8B) | NPC strategy decisions, sabotage dialogue generation, damage evaluation |
| **Agent AI** | Google Gemini + LangGraph + LangChain | In-character candidate reactions with tool use (ReAct agent) |
| **Voice** | ElevenLabs Flash v2.5 | TTS for candidate speeches, multilingual (Hindi deepfakes) |
| **Security** | ArmorIQ SDK | Cryptographic intent verification for code of conduct enforcement |
| **Audio DSP** | FFmpeg + NumPy + SciPy | 19kHz watermark injection and FFT-based verification |
| **Deployment** | Docker + Vultr Cloud | Production container on Ubuntu with systemd auto-restart |

---

## Project Structure

```text
Panchayat/
|-- client/                              # Frontend (served as static files)
|   |-- index.html                      # Main game HTML — start screen, topbar, panels, popups
|   |-- game.js                         # Game engine — API calls, rendering, sound, dialogue system
|   |-- styles.css                      # Complete pixel-art design system (46KB)
|   +-- assets/                         # Pixel-art avatars, backgrounds, textures, audio
|       |-- pixel_candidate_avatar.png  # Player avatar
|       |-- vikas_purush_avatar.png     # NPC avatar
|       |-- dharma_rakshak_avatar.png   # NPC avatar
|       |-- jan_neta_avatar.png         # NPC avatar
|       |-- mukti_devi_avatar.png       # NPC avatar
|       |-- pixel_village_bg.png        # Game background
|       |-- wood_texture.png            # UI texture
|       +-- audio/                      # Sound effects and BGM
|-- server/                              # Backend
|   |-- fastapi_server.py               # FastAPI app — all API endpoints, ArmorIQ, Groq, TTS, watermarks
|   |-- langgraph_engine.py             # LangGraph + Gemini ReAct agent for candidate reactions
|   |-- init_db.py                      # MongoDB initialization — candidates, voter groups, shares
|   +-- .env                            # Server environment variables
|-- bridge/                              # AI module
|   |-- ai_prompts.py                   # Candidate persona system prompts and reaction builders
|   |-- tools_langchain.py              # LangChain tools for Gemini agent (FastAPI bridge)
|   |-- prototype.py                    # Early prototype code
|   +-- solana_notary.py                # Blockchain notary (experimental)
|-- data/                                # Game data and engines
|   |-- candidates.json                 # 4 NPC personas — backstories, ideology scores, system prompts
|   |-- manifesto_bank.py               # Policy bank — manifesto definitions with voter group targeting
|   |-- voter_profiles.py               # 5 voter demographics with ideology vectors
|   |-- ideology_engine.py              # Multi-axis ideology distance and election simulation
|   |-- weaknesses.json                 # Candidate vulnerability database for sabotage targeting
|   |-- scenarios.json                  # Campaign event scenarios
|   |-- dialogues.json                  # Pre-built dialogue templates
|   |-- tools.py                        # Data utility functions
|   +-- validate_data.py               # Data integrity validation
|-- Dockerfile                           # Production Docker image (Python 3.11-slim)
|-- DEPLOY.md                            # Vultr deployment guide (Docker + bare-metal)
|-- requirements.txt                     # Python dependencies (~77 packages)
|-- .env.example                         # Template for environment variables
+-- .gitignore
```

---

## Learning Outcomes for the Player

By playing Panchayat, a citizen learns:

| Lesson | How It Is Taught |
|---|---|
| **Policy trade-offs** | Choosing a farmer policy gains farmer votes but opponents lose proportionally |
| **Election law** | Attempting communal incitement shows the exact Code of Conduct rule that blocked it |
| **Strategic thinking** | Deciding whether to sabotage the leader, build manifesto, or save coins for a deepfake |
| **Media literacy** | Seeing how AI-generated deepfake audio can fabricate confessions in someone's voice |
| **Democratic accountability** | Every sabotage is reviewed by the Election Commissioner with clear reasoning |
| **Ideology spectrum** | Understanding why farmers prefer welfare while tech workers want innovation |
| **Resource management** | Balancing a coin economy between manifesto building, sabotage, and defense |
| **AI ethics** | Learning that voice watermarks and forensic detection can counter deepfake misinformation |

---

## Setup Guide

### Prerequisites

- **Python 3.11+** with pip
- **MongoDB Atlas** cluster (free tier works) — [cloud.mongodb.com](https://cloud.mongodb.com)
- **Groq API key** ([console.groq.com](https://console.groq.com)) — for NPC AI and damage evaluation
- **ElevenLabs API key** ([elevenlabs.io](https://elevenlabs.io)) — for voice synthesis
- **Google Gemini API key** ([aistudio.google.com](https://aistudio.google.com)) — for LangGraph agent
- **ArmorIQ API key** ([platform.armoriq.ai](https://platform.armoriq.ai)) — for cryptographic enforcement (optional, Groq fallback available)

### 1. Clone and Install

```bash
git clone https://github.com/AnshuKashyap01/Panchayat.git
cd Panchayat

# Create virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/Mac
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example server/.env
```

Edit `server/.env` with your keys:

```env
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
GOOGLE_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
ARMORIQ_API_KEY=your_armoriq_api_key
```

### 3. Initialize the Database

```bash
python -c "from server.init_db import restart_game_state; restart_game_state()"
```

Expected output:
```text
Database Reset: Data initialized with Roles and Archetypes.
```

### 4. Start the Server

```bash
uvicorn server.fastapi_server:app --port 8000 --host 0.0.0.0
```

Expected output:
```text
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5. Play

Open **http://localhost:8000/** in your browser.

1. Click **SINGLE PLAYER** on the start screen
2. Enter your **candidate name** and **party name**
3. Optionally enter a **dark secret** (NPCs will use it against you)
4. Click **ADD MANIFESTO** to pick your first policy
5. Click **SKIP TURN** to end your round and watch NPCs react
6. Click **SABOTAGE** to launch a political attack
7. Repeat for 5 rounds — see who wins the Panchayat election

---

## Deployment

The game is deployed at **[http://65.20.91.167/](http://65.20.91.167/)** on Vultr Cloud.

### Docker Deploy (Production)

```bash
docker build -t panchayat .
docker run -d \
  --name panchayat \
  --restart unless-stopped \
  -p 80:8000 \
  --env-file .env \
  panchayat
```

See [DEPLOY.md](DEPLOY.md) for the complete Vultr deployment guide including bare-metal, systemd, and SSL setup.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serve the game (static HTML) |
| `/api/manifesto-bank` | GET | Available (unclaimed) manifestos |
| `/api/all-manifestos` | GET | All manifestos with claim status |
| `/api/apply-manifesto` | POST | Player claims a manifesto and shifts voter shares |
| `/api/total-standing` | GET | Aggregated voter shares per candidate |
| `/api/all-shares` | GET | Detailed voter shares (per group, per candidate) |
| `/api/candidates-info` | GET | Public candidate data (name, coins, shield status) |
| `/api/end-turn` | POST | Process NPC actions — AI picks manifesto or sabotage |
| `/api/player-sabotage` | POST | Player launches sabotage (validated by Election Commissioner) |
| `/api/tts` | POST | Proxy to ElevenLabs TTS with candidate voice mapping |
| `/api/voice-map` | GET | Voice ID mapping for all candidates |
| `/api/buy-watermark` | POST | Purchase voice authenticity shield (100 coins) |
| `/api/set-player-weakness` | POST | Set player's dark secret for NPC targeting |
| `/api/restart-game` | POST | Reset all game state to initial values |
| `/api/play-turn` | POST | Run a full game turn (legacy) |

---

## Team

Built at **HackByte 4.0** for the **Claw & Shield Track** (ArmorIQ x OpenClaw).

---

*"Democracy is not just a right — it is a skill. Panchayat lets you practice it."*
