/* ================================================
   PANCHAYAT GAME – Frontend ↔ FastAPI Backend
   ================================================ */

// ── CONFIG ──
// Auto-detect: if served from FastAPI (port 8000 or production), use relative URLs; otherwise point to FastAPI dev server
const API_BASE = (window.location.port === '8000' || window.location.port === '80' || window.location.port === '443' || window.location.port === '')
    ? '' : 'http://localhost:8000';
const PLAYER_CANDIDATE_ID = 4;           // Player is always candidate 4
const NUM_CANDIDATES = 5;                // 5 candidates (0-3 NPC, 4 Player)
const GROUP_CAP = 20.0;                  // Each voter group = 20% of total population
const INITIAL_SHARE = 4.0;              // GROUP_CAP / NUM_CANDIDATES = 4% each

// ── Voter Group Mapping (matches init_db.py) ──
const VOTER_GROUPS = [
    { id: 0, name: 'Farmers', icon: '🌾', color: '#48b848' },
    { id: 1, name: 'Students', icon: '📱', color: '#4088e0' },
    { id: 2, name: 'Tech Workers', icon: '💻', color: '#e8d040' },
    { id: 3, name: 'Laborers', icon: '⚒️', color: '#e04848' },
    { id: 4, name: 'Youth', icon: '🏃', color: '#a048c8' }
];

// ── NPC Candidates (matches init_db.py) ──
const NPC_CANDIDATES = [
    { id: 0, name: 'Vikas Purush', archetype: 'vikas_purush', emoji: '🏗️', color: '#e8a040', avatar: 'assets/vikas_purush_avatar.png' },
    { id: 1, name: 'Dharma Rakshak', archetype: 'dharma_rakshak', emoji: '🛡️', color: '#e04848', avatar: 'assets/dharma_rakshak_avatar.png' },
    { id: 2, name: 'Jan Neta', archetype: 'jan_neta', emoji: '📢', color: '#4088e0', avatar: 'assets/jan_neta_avatar.png' },
    { id: 3, name: 'Mukti Devi', archetype: 'mukti_devi', emoji: '🕊️', color: '#a048c8', avatar: 'assets/mukti_devi_avatar.png' }
];

// ── Game State (local mirror of DB) ──
const gameState = {
    candidate: {
        id: PLAYER_CANDIDATE_ID,
        name: 'Player',
        party: 'Jan Seva Party',
        popularity: 2,
        coins: 200,
        level: 1
    },
    manifesto: [],         // Player's chosen manifestos
    manifestoBank: [],     // Available manifestos from backend
    voterShares: [],       // Player's share per voter group (what bar chart shows)
    allShares: {},         // Full share table: { groupId: { candidateId: share } }
    npcManifestos: { 0: [], 1: [], 2: [], 3: [] },
    turnNumber: 1,
    selectedPopupOptions: [],
    voiceMap: {},          // { candidateId: voice_id } — persisted from server
    isMuted: false,        // Global mute toggle
    currentAudio: null     // Currently playing Audio object for cancellation
};

// ══════════════════════════════════
//  SOUND EFFECTS (Web Audio API)
// ══════════════════════════════════

class SoundManager {
    constructor() {
        this.ctx = null;
        this.masterGain = null;
        this.bgmGain = null;
        this.uiGain = null;
        this.buffers = {};

        // Active sources
        this.activeBGM = null;
        this.activeAmbient = null;
    }

    _initCtx() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
            this.masterGain = this.ctx.createGain();
            this.bgmGain = this.ctx.createGain();
            this.uiGain = this.ctx.createGain();

            // Routing
            this.bgmGain.connect(this.masterGain);
            this.uiGain.connect(this.masterGain);
            this.masterGain.connect(this.ctx.destination);

            // Set default volumes
            this.bgmGain.gain.value = 0.015; // Extremely low, subtle ambient background
            this.uiGain.gain.value = 0.6;
            this._updateMuteState();
        }
    }

    _updateMuteState() {
        if (!this.masterGain) return;
        this.masterGain.gain.value = gameState.isMuted ? 0 : 1;
    }

    toggleMute() {
        gameState.isMuted = !gameState.isMuted;
        this._updateMuteState();
        if (!gameState.isMuted && this.ctx && this.ctx.state === 'suspended') {
            this.ctx.resume();
        }
    }

    async loadAssets() {
        this._initCtx();
        const assets = {
            'ui_hover': 'assets/audio/ui_hover.wav',
            'ui_click': 'assets/audio/ui_click.wav',
            'error_buzz': 'assets/audio/error_buzz.wav',
            'add_manifesto': 'assets/audio/add_manifesto.wav',
            'sabotage_fuse': 'assets/audio/sabotage_fuse.wav',
            'chart_tick': 'assets/audio/chart_tick.wav',
            'round_chime': 'assets/audio/round_chime.wav',
            'bgm_village': 'assets/audio/bgm_village.mp3',
            'ambient_river': 'assets/audio/ambient_river.mp3'
        };

        for (const [name, path] of Object.entries(assets)) {
            try {
                const response = await fetch(path);
                if (response.ok) {
                    const arrayBuffer = await response.arrayBuffer();
                    this.buffers[name] = await this.ctx.decodeAudioData(arrayBuffer);
                } else {
                    console.warn(`[SoundManager] Asset missing: ${path}`);
                }
            } catch (err) {
                console.warn(`[SoundManager] Failed to load ${path}`);
            }
        }
    }

    async play(name) {
        if (gameState.isMuted) return;
        this._initCtx();
        if (this.ctx.state === 'suspended') {
            try { await this.ctx.resume(); } catch (e) { return; }
        }
        if (this.ctx.state !== 'running') return; // abort if still not running

        const buffer = this.buffers[name];
        if (buffer) {
            const source = this.ctx.createBufferSource();
            source.buffer = buffer;
            source.connect(this.uiGain);
            source.start();
        } else {
            // Procedural fallback if physical files not provided
            this._playProceduralFallback(name);
        }
    }

    _playProceduralFallback(name) {
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain).connect(this.uiGain);

        const now = this.ctx.currentTime;
        if (name === 'ui_hover') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(400, now);
            gain.gain.setValueAtTime(0.05, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.05);
            osc.start(now); osc.stop(now + 0.05);
        } else if (name === 'ui_click' || name === 'chart_tick') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(1000, now);
            gain.gain.setValueAtTime(0.1, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
            osc.start(now); osc.stop(now + 0.08);
        } else if (name === 'error_buzz') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(100, now);
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.linearRampToValueAtTime(0.001, now + 0.3);
            osc.start(now); osc.stop(now + 0.3);
        } else if (name === 'add_manifesto') {
            osc.type = 'square';
            osc.frequency.setValueAtTime(523, now);
            osc.frequency.exponentialRampToValueAtTime(1046, now + 0.15); // ascending
            gain.gain.setValueAtTime(0.15, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);
            osc.start(now); osc.stop(now + 0.2);
        } else if (name === 'sabotage_fuse') {
            osc.type = 'sawtooth';
            osc.frequency.setValueAtTime(300, now);
            osc.frequency.exponentialRampToValueAtTime(50, now + 0.5); // dropping pitch bomb
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.6);
            osc.start(now); osc.stop(now + 0.6);
        } else if (name === 'round_chime') {
            osc.type = 'sine';
            osc.frequency.setValueAtTime(440, now); // A4
            osc.frequency.setValueAtTime(554, now + 0.1); // C#5
            osc.frequency.setValueAtTime(659, now + 0.2); // E5
            gain.gain.setValueAtTime(0.2, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.8);
            osc.start(now); osc.stop(now + 0.8);
        }
    }

    async playBGM(name, loop = true) {
        if (gameState.isMuted) return;
        this._initCtx();
        if (this.ctx.state === 'suspended') {
            try { await this.ctx.resume(); } catch (e) { return; }
        }
        if (this.ctx.state !== 'running') return;

        if (this.activeBGM) {
            if (this.activeBGM.stop) this.activeBGM.stop();
        }

        const buffer = this.buffers[name];
        if (!buffer) {
            console.warn(`[SoundManager] Missing BGM track ${name}. Using procedural synth pad fallback.`);
            this._playProceduralBGM();
            return;
        }

        const source = this.ctx.createBufferSource();
        source.buffer = buffer;
        source.loop = loop;
        source.connect(this.bgmGain);
        source.start();
        this.activeBGM = source;
    }

    _playProceduralBGM() {
        const frequencies = [65.41, 164.81, 196.00, 246.94]; // Cmaj7 open drone (C2, E3, G3, B3)
        const oscillators = [];

        const masterPadGain = this.ctx.createGain();
        // Very low volume, slow 4 second fade in for smoothness
        masterPadGain.gain.setValueAtTime(0, this.ctx.currentTime);
        masterPadGain.gain.linearRampToValueAtTime(0.04, this.ctx.currentTime + 4);

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.value = 600; // Muffeled, warm, Sega ambient tone

        masterPadGain.connect(filter);
        filter.connect(this.bgmGain);

        frequencies.forEach((freq, idx) => {
            const osc = this.ctx.createOscillator();
            osc.type = 'triangle';
            // Detune slightly for chorusing effect
            osc.frequency.value = freq + (idx * 0.5);
            osc.connect(masterPadGain);
            osc.start();
            oscillators.push(osc);
        });

        // Store a custom stopper interface for the fallback BGM
        this.activeBGM = {
            isProcedural: true,
            stop: () => {
                try {
                    masterPadGain.gain.linearRampToValueAtTime(0, this.ctx.currentTime + 2);
                    setTimeout(() => {
                        oscillators.forEach(o => o.stop());
                    }, 2000);
                } catch (e) { }
            }
        };
    }

    async playAmbient(name) {
        if (gameState.isMuted) return;
        this._initCtx();
        if (this.ctx.state === 'suspended') {
            try { await this.ctx.resume(); } catch (e) { return; }
        }
        if (this.ctx.state !== 'running') return;

        if (this.activeAmbient) return; // Already playing

        const buffer = this.buffers[name];
        if (!buffer) {
            console.warn(`[SoundManager] Missing Ambient track ${name}. Using procedural river noise fallback.`);
            this._playProceduralAmbient();
            return;
        }

        const source = this.ctx.createBufferSource();
        source.buffer = buffer;
        source.loop = true;

        // Custom ambient gain for fade ins/outs
        const ambientGain = this.ctx.createGain();
        ambientGain.gain.setValueAtTime(0, this.ctx.currentTime);
        ambientGain.gain.linearRampToValueAtTime(0.2, this.ctx.currentTime + 3);

        source.connect(ambientGain).connect(this.masterGain);
        source.start();

        this.activeAmbient = { source, gainNode: ambientGain };
    }

    _playProceduralAmbient() {
        // Synthesizing water flow using a low-pass filtered white noise
        const bufferSize = this.ctx.sampleRate * 2;
        const noiseBuffer = this.ctx.createBuffer(1, bufferSize, this.ctx.sampleRate);
        const output = noiseBuffer.getChannelData(0);
        for (let i = 0; i < bufferSize; i++) {
            output[i] = Math.random() * 2 - 1;
        }

        const whiteNoise = this.ctx.createBufferSource();
        whiteNoise.buffer = noiseBuffer;
        whiteNoise.loop = true;

        const filter = this.ctx.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.value = 250; // Deep water rumble frequency

        const ambientGain = this.ctx.createGain();
        ambientGain.gain.setValueAtTime(0, this.ctx.currentTime);
        ambientGain.gain.linearRampToValueAtTime(0.06, this.ctx.currentTime + 3); // Very quiet

        whiteNoise.connect(filter);
        filter.connect(ambientGain);
        ambientGain.connect(this.masterGain);
        whiteNoise.start();

        this.activeAmbient = { source: whiteNoise, gainNode: ambientGain };
    }

    stopAmbient() {
        if (!this.activeAmbient) return;

        const { source, gainNode } = this.activeAmbient;
        if (gainNode && source) {
            try {
                gainNode.gain.linearRampToValueAtTime(0, this.ctx.currentTime + 2);
                setTimeout(() => {
                    source.stop();
                    this.activeAmbient = null;
                }, 2000);
            } catch (e) { }
        } else {
            this.activeAmbient = null;
        }
    }
}

const soundManager = new SoundManager();

// Backwards compatibility for legacy UI calls
window.SoundFX = {
    dialogueOpen: () => soundManager.play('ui_hover'),
    buttonClick: () => soundManager.play('ui_click'),
    error: () => soundManager.play('error_buzz'),
    success: () => soundManager.play('round_chime')
};

// ── DOM References ──
const DOM = {
    manifestoList: document.getElementById('manifestoList'),
    barChart: document.getElementById('barChart'),
    addManifestoBtn: document.getElementById('addManifestoBtn'),
    popupOverlay: document.getElementById('popupOverlay'),
    popupCloseBtn: document.getElementById('popupCloseBtn'),
    popupScrollArea: document.getElementById('popupScrollArea'),
    customManifestoInput: document.getElementById('customManifestoInput'),
    popupActionBtn: document.getElementById('popupActionBtn'),
    toast: document.getElementById('toast'),
    toastMsg: document.getElementById('toastMsg'),
    coinCount: document.getElementById('coinCount'),
    settingsBtn: document.getElementById('settingsBtn'),
    menuBtn: document.getElementById('menuBtn'),
    pixelCanvas: document.getElementById('pixelParticles'),
    sidebarOverlay: document.getElementById('sidebarOverlay'),
    opponentsSidebar: document.getElementById('opponentsSidebar'),
    sidebarCloseBtn: document.getElementById('sidebarCloseBtn'),
    sidebarScroll: document.getElementById('sidebarScroll'),
    restartGameBtn: document.getElementById('restartGameBtn'),
    restartOverlay: document.getElementById('restartOverlay'),
    confirmRestartBtn: document.getElementById('confirmRestartBtn'),
    cancelRestartBtn: document.getElementById('cancelRestartBtn'),
    candidateName: document.getElementById('candidateName'),
    candidateParty: document.getElementById('candidateParty'),
    npcManifestoOverlay: document.getElementById('npcManifestoOverlay'),
    npcManifestoPanel: document.getElementById('npcManifestoPanel'),
    npcManifestoCloseBtn: document.getElementById('npcManifestoCloseBtn'),
    npcManifestoTitle: document.getElementById('npcManifestoTitle'),
    npcManifestoScrollArea: document.getElementById('npcManifestoScrollArea'),
    turnAnnouncerOverlay: document.getElementById('turnAnnouncerOverlay'),
    announcerName: document.getElementById('announcerName'),
    announcerAction: document.getElementById('announcerAction'),
    playerTotalShares: document.getElementById('playerTotalShares'),
    roundTrackerText: document.getElementById('roundTrackerText'),
    endGameOverlay: document.getElementById('endGameOverlay'),
    endGameWinnerBox: document.getElementById('endGameWinnerBox'),
    endGameSubtext: document.getElementById('endGameSubtext'),
    endGameStandings: document.getElementById('endGameStandings'),
    playAgainBtn: document.getElementById('playAgainBtn'),
    sabotageBtn: document.getElementById('sabotageBtn'),
    sabotageOverlay: document.getElementById('sabotageOverlay'),
    sabotageCloseBtn: document.getElementById('sabotageCloseBtn'),
    sabotageTargetSelect: document.getElementById('sabotageTargetSelect'),
    sabotagePromptInput: document.getElementById('sabotagePromptInput'),
    sabotageSubmitBtn: document.getElementById('sabotageSubmitBtn'),
    sabotageResultOverlay: document.getElementById('sabotageResultOverlay'),
    sabotageResultTitle: document.getElementById('sabotageResultTitle'),
    sabotageResultMessage: document.getElementById('sabotageResultMessage'),
    sabotageResultDialogue: document.getElementById('sabotageResultDialogue'),
    sabotageResultCloseBtn: document.getElementById('sabotageResultCloseBtn'),
    cocBtn: document.getElementById('cocBtn'),
    cocOverlay: document.getElementById('cocOverlay'),
    cocCloseBtn: document.getElementById('cocCloseBtn'),
    cocOkBtn: document.getElementById('cocOkBtn'),
    // Dialogue popup
    dialogueOverlay: document.getElementById('dialogueOverlay'),
    dialogueSpeakerEmoji: document.getElementById('dialogueSpeakerEmoji'),
    dialogueSpeakerName: document.getElementById('dialogueSpeakerName'),
    dialogueText: document.getElementById('dialogueText'),
    dialogueContinue: document.getElementById('dialogueContinue'),
    dialogueAudioIndicator: document.getElementById('dialogueAudioIndicator'),
    // Mute button
    muteBtn: document.getElementById('muteBtn'),
    // Start Screen Elements
    startScreenOverlay: document.getElementById('startScreenOverlay'),
    startSinglePlayerBtn: document.getElementById('startSinglePlayerBtn'),
    startMultiPlayerBtn: document.getElementById('startMultiPlayerBtn'),
    startSoundToggleBtn: document.getElementById('startSoundToggleBtn')
};


// ══════════════════════════════════
//  API HELPERS
// ══════════════════════════════════

async function apiFetch(endpoint, options = {}) {
    const controller = new AbortController();
    const timeoutMs = options.timeoutMs || 15000;
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs); // default 15s timeout

    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            signal: controller.signal,
            ...options
        });
        clearTimeout(timeoutId);
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (err) {
        clearTimeout(timeoutId);
        console.error(`API Error [${endpoint}]:`, err.message);
        throw err;
    }
}

/** API logic merged into loadManifestoBank below */

/** POST /api/apply-manifesto → apply a manifesto for player */
async function applyManifesto(groupId, shiftAmount) {
    return apiFetch('/api/apply-manifesto', {
        method: 'POST',
        body: JSON.stringify({
            candidate_id: PLAYER_CANDIDATE_ID,
            group_id: groupId,
            shift_amount: shiftAmount
        })
    });
}

/** GET /api/total-standing → aggregated voter shares per candidate */
async function fetchTotalStanding() {
    return apiFetch('/api/total-standing');
}

/** GET /api/all-shares → detailed voter shares */
async function fetchAllShares() {
    return apiFetch('/api/all-shares');
}

/** POST /api/play-turn → run a full game turn */
async function playTurn(actionText) {
    return apiFetch('/api/play-turn', {
        method: 'POST',
        body: JSON.stringify({ action: actionText })
    });
}


// ══════════════════════════════════
//  PIXEL PARTICLE SYSTEM (Fireflies)
// ══════════════════════════════════

class PixelParticleSystem {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.maxParticles = 30;
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticle() {
        const colors = ['#f0c040', '#90e060', '#60d8d8', '#f0a030', '#ffffff'];
        return {
            x: Math.random() * this.canvas.width,
            y: Math.random() * this.canvas.height,
            size: Math.random() < 0.3 ? 3 : 2,
            speedX: (Math.random() - 0.5) * 0.3,
            speedY: -0.2 - Math.random() * 0.4,
            color: colors[Math.floor(Math.random() * colors.length)],
            alpha: Math.random() * 0.6 + 0.2,
            alphaDir: Math.random() < 0.5 ? 0.008 : -0.008,
            life: 0,
            maxLife: 200 + Math.random() * 300
        };
    }

    update() {
        if (this.particles.length < this.maxParticles && Math.random() < 0.08) {
            this.particles.push(this.createParticle());
        }
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            p.x += p.speedX;
            p.y += p.speedY;
            p.life++;
            p.alpha += p.alphaDir;
            if (p.alpha > 0.8) { p.alpha = 0.8; p.alphaDir = -Math.abs(p.alphaDir); }
            if (p.alpha < 0.1) { p.alpha = 0.1; p.alphaDir = Math.abs(p.alphaDir); }
            p.speedX += (Math.random() - 0.5) * 0.02;
            p.speedX = Math.max(-0.5, Math.min(0.5, p.speedX));
            if (p.life > p.maxLife || p.y < -10 || p.x < -10 || p.x > this.canvas.width + 10) {
                this.particles.splice(i, 1);
            }
        }
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        for (const p of this.particles) {
            this.ctx.globalAlpha = p.alpha;
            this.ctx.fillStyle = p.color;
            this.ctx.fillRect(Math.round(p.x), Math.round(p.y), p.size, p.size);
            this.ctx.globalAlpha = p.alpha * 0.3;
            this.ctx.fillRect(Math.round(p.x) - 1, Math.round(p.y) - 1, p.size + 2, p.size + 2);
        }
        this.ctx.globalAlpha = 1;
    }

    animate() {
        this.update();
        this.draw();
        requestAnimationFrame(() => this.animate());
    }

    start() { this.animate(); }
}


// ══════════════════════════════════
//  INITIALIZATION
// ══════════════════════════════════

async function startSinglePlayer() {
    // Initialize required background audio
    await soundManager.loadAssets();
    soundManager.playBGM('bgm_village');

    // Hide start screen
    DOM.startScreenOverlay.classList.remove('active');

    // Player Setup
    let pName = localStorage.getItem('playerName');
    let pParty = localStorage.getItem('playerParty');
    if (!pName || !pParty) {
        pName = prompt("Enter your Candidate Name:", "Player") || "Player";
        pParty = prompt("Enter your Party Name:", "Jan Seva Party") || "Jan Seva Party";
        let pSecret = prompt("Enter your Candidate's Dark Secret (Optional - Leave blank for default):");

        localStorage.setItem('playerName', pName);
        localStorage.setItem('playerParty', pParty);

        if (pSecret && pSecret.trim() !== "") {
            try {
                // Background update without blocking UI
                apiFetch('/api/set-player-weakness', {
                    method: 'POST',
                    body: { weakness_desc: pSecret.trim() },
                    timeoutMs: 5000
                }).catch(e => console.warn("Failed to set weakness", e));
            } catch (e) { }
        }
    }
    gameState.candidate.name = pName;
    gameState.candidate.party = pParty;
    DOM.candidateName.textContent = pName;
    DOM.candidateParty.textContent = pParty;

    // Load coins: prefer server value, fall back to localStorage, then default 200
    try {
        const candidatesInfo = await apiFetch('/api/candidates-info');
        const playerInfo = candidatesInfo.find(c => c.id === PLAYER_CANDIDATE_ID);
        if (playerInfo && playerInfo.coins !== undefined) {
            gameState.candidate.coins = playerInfo.coins;
            localStorage.setItem('playerCoins', gameState.candidate.coins);
        } else {
            let savedCoins = localStorage.getItem('playerCoins');
            if (savedCoins) {
                gameState.candidate.coins = parseInt(savedCoins, 10);
            }
        }
    } catch (e) {
        let savedCoins = localStorage.getItem('playerCoins');
        if (savedCoins) {
            gameState.candidate.coins = parseInt(savedCoins, 10);
        }
    }
    DOM.coinCount.textContent = gameState.candidate.coins.toLocaleString();

    let savedTurn = localStorage.getItem('turnNumber');
    gameState.turnNumber = savedTurn ? parseInt(savedTurn, 10) : 1;
    if (gameState.turnNumber <= 5) {
        DOM.roundTrackerText.textContent = `RND ${gameState.turnNumber}/5`;
    } else {
        DOM.roundTrackerText.textContent = `RND 5/5`;
    }

    // Bind UI events
    bindEvents();

    // Fetch data from backend
    try {
        await Promise.all([
            loadManifestoBank(),
            loadVoterStanding(),
            loadVoiceMap()
        ]);
        showToast('⚔️', 'Connected to server!');
    } catch (err) {
        console.warn('Backend not available, using fallback data:', err.message);
        useFallbackData();
        showToast('⚠️', 'Offline mode – no server');
    }

    // Render UI
    renderManifesto();
    renderBarChart();

    // Evaluate if game already ended previously
    if (gameState.turnNumber > 5) {
        evaluateElectionResults();
    }
}

/** Load voice mapping from server (persisted in MongoDB) */
async function loadVoiceMap() {
    try {
        const map = await apiFetch('/api/voice-map');
        gameState.voiceMap = map;
        console.log('🔊 Voice map loaded:', map);
    } catch (err) {
        console.warn('Could not load voice map:', err.message);
    }
}

/** Load all manifestos from /api/all-manifestos */
async function loadManifestoBank() {
    const allBank = await apiFetch('/api/all-manifestos');

    gameState.manifestoBank = allBank.filter(m => m.used_by === null);

    gameState.npcManifestos = { 0: [], 1: [], 2: [], 3: [] };
    for (const m of allBank) {
        if (m.used_by !== null && m.used_by < PLAYER_CANDIDATE_ID) {
            gameState.npcManifestos[m.used_by].push(m);
        }
    }
}

/** Load voter standing from /api/total-standing and /api/all-shares */
async function loadVoterStanding() {
    try {
        const allSharesRaw = await fetchAllShares();

        gameState.allShares = {};
        allSharesRaw.forEach(s => {
            if (!gameState.allShares[s.group_id]) {
                gameState.allShares[s.group_id] = {};
            }
            gameState.allShares[s.group_id][s.candidate_id] = s.share;
        });

        gameState.voterShares = VOTER_GROUPS.map(group => ({
            ...group,
            percent: Math.round((gameState.allShares[group.id]?.[PLAYER_CANDIDATE_ID] ?? INITIAL_SHARE) * 100) / 100
        }));

        gameState.standings = await fetchTotalStanding();
    } catch (err) {
        console.warn('Could not fetch granular shares from server, using fallback');

        const standings = await fetchTotalStanding();
        const playerStanding = standings.find(s => s._id === PLAYER_CANDIDATE_ID);

        if (Object.keys(gameState.allShares).length === 0) {
            gameState.voterShares = VOTER_GROUPS.map(group => ({
                ...group,
                percent: playerStanding
                    ? Math.round((playerStanding.total_support / VOTER_GROUPS.length) * 100) / 100
                    : INITIAL_SHARE
            }));
        } else {
            gameState.voterShares = VOTER_GROUPS.map(group => ({
                ...group,
                percent: gameState.allShares[group.id]?.[PLAYER_CANDIDATE_ID] ?? INITIAL_SHARE
            }));
        }

        gameState.standings = standings;
    }
}

/**
 * Initialize full share table for offline/local simulation.
 * Mirrors init_db.py: 5 groups × 5 candidates × 4% each = 20% per group.
 */
function initializeLocalShares() {
    gameState.allShares = {};
    for (let gId = 0; gId < VOTER_GROUPS.length; gId++) {
        gameState.allShares[gId] = {};
        for (let cId = 0; cId < NUM_CANDIDATES; cId++) {
            gameState.allShares[gId][cId] = INITIAL_SHARE; // 4.0%
        }
    }
}

/** Fallback data when server is not running */
function useFallbackData() {
    gameState.manifestoBank = [
        { id: 201, title: 'Mandi Modernization Act', description: 'Blockchain-tracked cold storage and direct-to-city supply chains.', target_group_id: 0, shift_amount: 3.5 },
        { id: 202, title: 'Abhyudaya Coaching Corps', description: 'Free JEE/NEET/UPSC coaching centers in every village block.', target_group_id: 1, shift_amount: 4.2 },
        { id: 203, title: 'Panchayat Fiber Revolution', description: 'High-speed 5G broadband at every Village Council office.', target_group_id: 2, shift_amount: 3.0 },
        { id: 204, title: 'Shramik Suraksha Insurance', description: 'Guaranteed daily-wage insurance for unorganized laborers.', target_group_id: 3, shift_amount: 4.5 },
        { id: 205, title: 'Gramin Khel Mahotsav', description: 'Modern stadiums and talent scouting for rural athletes.', target_group_id: 4, shift_amount: 3.8 },
        { id: 206, title: 'Kisan Urja Scheme', description: '100% subsidy on solar-powered irrigation pumps.', target_group_id: 0, shift_amount: 3.2 },
        { id: 207, title: 'Digital Sanskriti Library', description: '24/7 study hubs with tablets and digital archives.', target_group_id: 1, shift_amount: 3.5 },
        { id: 208, title: 'BPO Rural Connect', description: 'Tax holidays for IT companies in Tier-3 towns.', target_group_id: 2, shift_amount: 5.0 },
        { id: 209, title: 'Vishwa Karma Safety Gear', description: 'Safety equipment and health checkups for construction workers.', target_group_id: 3, shift_amount: 2.5 },
        { id: 210, title: 'Yuva Entrepreneur Seed Fund', description: 'Interest-free startup loans up to ₹5 Lakhs for youth.', target_group_id: 4, shift_amount: 4.0 }
    ];

    // Initialize local share table: 5 groups × 5 candidates × 4% each
    initializeLocalShares();

    // Player's bar chart view: starts at 4% in each group
    gameState.voterShares = VOTER_GROUPS.map(group => ({
        ...group,
        percent: INITIAL_SHARE // 4.0% — NOT 20%
    }));
}

/** Map manifesto target_group_id to icon */
function getGroupIcon(groupId) {
    const icons = { 0: '🌾', 1: '📱', 2: '💻', 3: '⚒️', 4: '🏃' };
    return icons[groupId] || '📜';
}

/** Map manifesto target_group_id to name */
function getGroupName(groupId) {
    const group = VOTER_GROUPS.find(g => g.id === groupId);
    return group ? group.name : 'General';
}


// ══════════════════════════════════
//  RENDER: MANIFESTO LIST
// ══════════════════════════════════

function renderManifesto(animate = false) {
    DOM.manifestoList.innerHTML = '';

    if (gameState.manifesto.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'manifesto-item';
        empty.innerHTML = `
            <div class="manifesto-icon">📋</div>
            <div class="manifesto-details">
                <div class="manifesto-title">No promises yet</div>
                <div class="manifesto-desc">Click + ADD MANIFESTO to start your campaign!</div>
            </div>
        `;
        DOM.manifestoList.appendChild(empty);
        return;
    }

    gameState.manifesto.forEach((item, index) => {
        const el = document.createElement('div');
        el.className = 'manifesto-item';
        el.style.animationDelay = `${index * 60}ms`;

        if (animate && index === gameState.manifesto.length - 1) {
            el.classList.add('new-item');
        }

        const targetGroup = getGroupName(item.target_group_id);

        el.innerHTML = `
            <div class="manifesto-icon">${getGroupIcon(item.target_group_id)}</div>
            <div class="manifesto-details">
                <div class="manifesto-title">${item.title}</div>
                <div class="manifesto-desc">${item.description}</div>
                <div class="manifesto-desc" style="color: #48b848; margin-top: 2px;">► ${targetGroup} (+${item.shift_amount}%)</div>
            </div>
        `;

        DOM.manifestoList.appendChild(el);
    });

    if (animate) {
        const container = document.querySelector('.manifesto-column');
        if (container) {
            setTimeout(() => { container.scrollTop = container.scrollHeight; }, 100);
        }
    }
}


// ══════════════════════════════════
//  RENDER: BAR CHART (Voter Groups)
// ══════════════════════════════════

function renderBarChart() {
    DOM.barChart.innerHTML = '';

    // Axis line
    const axis = document.createElement('div');
    axis.className = 'chart-axis';
    DOM.barChart.appendChild(axis);

    const voterData = gameState.voterShares.length > 0
        ? gameState.voterShares
        : VOTER_GROUPS.map(g => ({ ...g, percent: INITIAL_SHARE }));

    let totalPlayerShare = 0;

    voterData.forEach((voter, index) => {
        totalPlayerShare += voter.percent;
        const group = document.createElement('div');
        group.className = 'bar-group';

        // Bar height: scale relative to GROUP_CAP (20%)
        // So 4% → 20% height, 20% → 100% height
        const barHeightPercent = Math.max((voter.percent / GROUP_CAP) * 100, 3);
        const displayPercent = Math.round(voter.percent * 100) / 100;

        group.innerHTML = `
            <div class="bar-track">
                <div class="bar-percent">${displayPercent}%</div>
                <div class="bar-color" style="height: ${barHeightPercent}%; background: ${voter.color}; animation-delay: ${index * 0.08}s;"></div>
            </div>
            <div class="bar-label-area">
                <span class="bar-icon">${voter.icon}</span>
                <span class="bar-label">${voter.name}</span>
            </div>
        `;

        DOM.barChart.appendChild(group);
    });

    if (DOM.playerTotalShares) {
        DOM.playerTotalShares.textContent = `${totalPlayerShare.toFixed(2)}% TOTAL`;
        // Make it dynamic based on threshold
        if (totalPlayerShare > 25.0) {
            DOM.playerTotalShares.style.color = '#48b848';
        } else if (totalPlayerShare < 15.0) {
            DOM.playerTotalShares.style.color = '#e04848';
        } else {
            DOM.playerTotalShares.style.color = '#f8f8f8';
        }
    }

    // Play a single chart tick when bars are rapidly redrawn
    soundManager.play('chart_tick');
}


// ══════════════════════════════════
//  RENDER: POPUP OPTIONS (from Manifesto Bank)
// ══════════════════════════════════

function renderPopupOptions() {
    DOM.popupScrollArea.innerHTML = '';
    gameState.selectedPopupOptions = [];

    const availableManifestos = gameState.manifestoBank.filter(m => {
        // Don't show already-chosen manifestos
        return !gameState.manifesto.some(chosen => chosen.id === m.id);
    });

    if (availableManifestos.length === 0) {
        const empty = document.createElement('div');
        empty.style.cssText = 'font-family: "Press Start 2P"; font-size: 8px; color: #f0c040; text-align: center; padding: 24px;';
        empty.textContent = 'No more manifestos available!';
        DOM.popupScrollArea.appendChild(empty);
        return;
    }

    availableManifestos.forEach((option) => {
        const card = document.createElement('div');
        card.className = 'popup-option-card';
        card.dataset.optionId = option.id;

        const targetGroup = getGroupName(option.target_group_id);

        card.innerHTML = `
            <div class="popup-option-icon">${getGroupIcon(option.target_group_id)}</div>
            <div class="popup-option-info">
                <div class="popup-option-title">${option.title}</div>
                <div class="popup-option-desc">${option.description}</div>
                <div class="popup-option-desc" style="color: #48b848; margin-top: 2px;">► ${targetGroup} (+${option.shift_amount}%)</div>
            </div>
        `;

        card.addEventListener('click', () => {
            card.classList.toggle('selected');
            const idx = gameState.selectedPopupOptions.indexOf(option.id);
            if (idx > -1) {
                gameState.selectedPopupOptions.splice(idx, 1);
            } else {
                gameState.selectedPopupOptions.push(option.id);
            }
        });

        DOM.popupScrollArea.appendChild(card);
    });
}


// ══════════════════════════════════
//  EVENT BINDINGS
// ══════════════════════════════════

function bindEvents() {
    DOM.addManifestoBtn.addEventListener('click', openPopup);
    DOM.popupCloseBtn.addEventListener('click', closePopup);
    DOM.popupOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.popupOverlay) closePopup();
    });

    // NPC Manifesto Overlay Closers
    DOM.npcManifestoCloseBtn.addEventListener('click', () => {
        DOM.npcManifestoOverlay.classList.remove('active');
    });
    DOM.npcManifestoOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.npcManifestoOverlay) {
            DOM.npcManifestoOverlay.classList.remove('active');
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && DOM.popupOverlay.classList.contains('active')) {
            closePopup();
        }
        if (e.key === 'Escape' && DOM.npcManifestoOverlay.classList.contains('active')) {
            DOM.npcManifestoOverlay.classList.remove('active');
        }
        if (e.key === 'Escape' && DOM.opponentsSidebar.classList.contains('open')) {
            closeSidebar();
        }
        if (e.key === 'Escape' && DOM.cocOverlay.classList.contains('active')) {
            DOM.cocOverlay.classList.remove('active');
        }
    });
    DOM.popupActionBtn.addEventListener('click', addToCampaign);
    DOM.playAgainBtn.addEventListener('click', restartGameAction);

    // Hamburger → toggle opponents sidebar
    DOM.menuBtn.addEventListener('click', toggleSidebar);
    DOM.sidebarCloseBtn.addEventListener('click', closeSidebar);
    DOM.sidebarOverlay.addEventListener('click', closeSidebar);

    // Button press effects
    DOM.addManifestoBtn.addEventListener('mousedown', () => {
        DOM.addManifestoBtn.style.transform = 'translateY(4px)';
    });
    DOM.addManifestoBtn.addEventListener('mouseup', () => {
        DOM.addManifestoBtn.style.transform = '';
    });
    DOM.addManifestoBtn.addEventListener('mouseleave', () => {
        DOM.addManifestoBtn.style.transform = '';
    });

    // Restart game bindings
    DOM.restartGameBtn.addEventListener('click', () => {
        DOM.restartOverlay.classList.add('active');
    });
    DOM.cancelRestartBtn.addEventListener('click', () => {
        DOM.restartOverlay.classList.remove('active');
    });
    DOM.confirmRestartBtn.addEventListener('click', restartGameAction);

    // Code of Conduct
    DOM.cocBtn.addEventListener('click', () => {
        DOM.cocOverlay.classList.add('active');
    });
    DOM.cocCloseBtn.addEventListener('click', () => {
        DOM.cocOverlay.classList.remove('active');
    });
    DOM.cocOkBtn.addEventListener('click', () => {
        DOM.cocOverlay.classList.remove('active');
    });
    DOM.cocOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.cocOverlay) DOM.cocOverlay.classList.remove('active');
    });

    // Mute toggle
    if (DOM.muteBtn) {
        // Restore mute state
        gameState.isMuted = localStorage.getItem('gameMuted') === 'true';
        if (gameState.isMuted) {
            DOM.muteBtn.textContent = '🔇';
            DOM.muteBtn.classList.add('muted');
            soundManager._updateMuteState();
        }
        DOM.muteBtn.addEventListener('click', () => {
            soundManager.toggleMute();
            localStorage.setItem('gameMuted', gameState.isMuted);
            DOM.muteBtn.textContent = gameState.isMuted ? '🔇' : '🔊';
            DOM.muteBtn.classList.toggle('muted', gameState.isMuted);
            showToast(gameState.isMuted ? '🔇' : '🔊', gameState.isMuted ? 'Sound muted' : 'Sound enabled');

            if (DOM.startSoundToggleBtn) {
                DOM.startSoundToggleBtn.innerHTML = gameState.isMuted
                    ? '<span class="btn-icon">🔇</span> SOUND: OFF'
                    : '<span class="btn-icon">🔊</span> SOUND: ON';
            }
        });
    }
}

async function restartGameAction() {
    // Close the restart overlay immediately so user sees feedback
    DOM.restartOverlay.classList.remove('active');
    showToast('🔄', 'Restarting game...');

    try {
        await apiFetch('/api/restart-game', { method: 'POST', timeoutMs: 30000 });
        // Clear ALL localStorage (coins, turn, name, party, mute, etc.)
        localStorage.clear();
        showToast('✅', 'Game Restarted!');
        // Reload page to reset everything
        setTimeout(() => {
            window.location.reload();
        }, 500);
    } catch (err) {
        console.error('Failed to restart:', err);
        showToast('❌', 'Error restarting — try refreshing the page');
        // Even if server fails, clear local state and reload
        localStorage.clear();
        setTimeout(() => {
            window.location.reload();
        }, 1500);
    }
}

function openPopup() {
    renderPopupOptions();
    DOM.customManifestoInput.value = '';
    DOM.popupOverlay.classList.add('active');
}

function closePopup() {
    DOM.popupOverlay.classList.remove('active');
}


// ══════════════════════════════════
//  OPPONENTS SIDEBAR
// ══════════════════════════════════

function toggleSidebar() {
    if (DOM.opponentsSidebar.classList.contains('open')) {
        closeSidebar();
    } else {
        openSidebar();
    }
}

function openSidebar() {
    renderOpponentsSidebar();
    DOM.opponentsSidebar.classList.add('open');
    DOM.sidebarOverlay.classList.add('active');
}

function closeSidebar() {
    DOM.opponentsSidebar.classList.remove('open');
    DOM.sidebarOverlay.classList.remove('active');
}

/**
 * Render all 4 NPC opponents' voter share bar charts.
 * Each opponent gets a card showing their per-group voter shares.
 */
function renderOpponentsSidebar() {
    DOM.sidebarScroll.innerHTML = '';

    NPC_CANDIDATES.forEach(npc => {
        const card = document.createElement('div');
        card.className = 'opponent-card';

        // Calculate total support for this NPC
        let totalSupport = 0;
        VOTER_GROUPS.forEach(group => {
            const share = gameState.allShares[group.id]?.[npc.id] ?? INITIAL_SHARE;
            totalSupport += share;
        });
        totalSupport = Math.round(totalSupport * 100) / 100;

        // Header with name and total
        const header = document.createElement('div');
        header.className = 'opponent-card-header';
        header.innerHTML = `
            <img src="${npc.avatar}" alt="${npc.name}" class="opponent-avatar-img" style="width: 36px; height: 36px; border: 2px solid ${npc.color}; object-fit: cover; image-rendering: pixelated;">
            <span class="opponent-name">${npc.name}</span>
            <span class="opponent-total">${totalSupport}%</span>
        `;
        card.appendChild(header);

        // Mini bar chart
        const barsContainer = document.createElement('div');
        barsContainer.className = 'opponent-bars';

        VOTER_GROUPS.forEach(group => {
            const share = gameState.allShares[group.id]?.[npc.id] ?? INITIAL_SHARE;
            const barHeightPercent = Math.max((share / GROUP_CAP) * 100, 2);
            const displayPct = Math.round(share * 100) / 100;

            const barGroup = document.createElement('div');
            barGroup.className = 'opp-bar-group';
            barGroup.innerHTML = `
                <div class="opp-bar-pct">${displayPct}%</div>
                <div class="opp-bar-fill" style="height: ${barHeightPercent}%; background: ${group.color};"></div>
                <span class="opp-bar-label">${group.icon}</span>
            `;
            barsContainer.appendChild(barGroup);
        });

        card.appendChild(barsContainer);
        card.style.cursor = 'pointer';
        card.addEventListener('click', () => {
            openNpcManifesto(npc.id);
        });

        DOM.sidebarScroll.appendChild(card);
    });
}


function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function openNpcManifesto(npcId) {
    const npc = NPC_CANDIDATES.find(n => n.id === npcId);
    DOM.npcManifestoTitle.textContent = `${npc.name.toUpperCase()} MANIFESTOS`;
    DOM.npcManifestoScrollArea.innerHTML = '';

    const theirManifestos = gameState.npcManifestos[npcId] || [];
    if (theirManifestos.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'manifesto-item';
        empty.innerHTML = `<div class="manifesto-details"><div class="manifesto-title">No promises yet</div></div>`;
        DOM.npcManifestoScrollArea.appendChild(empty);
    } else {
        theirManifestos.forEach((item, index) => {
            const mCard = document.createElement('div');
            mCard.className = 'manifesto-item';
            const targetGroup = getGroupName(item.target_group_id);
            mCard.innerHTML = `
                <div class="manifesto-icon">${getGroupIcon(item.target_group_id)}</div>
                <div class="manifesto-details">
                    <div class="manifesto-title">${item.title}</div>
                    <div class="manifesto-desc">${item.description}</div>
                    <div class="manifesto-desc" style="color: #e04848; margin-top: 2px;">► ${targetGroup} (+${item.shift_amount}%)</div>
                </div>
            `;
            DOM.npcManifestoScrollArea.appendChild(mCard);
        });
    }

    DOM.npcManifestoOverlay.classList.add('active');
}

async function animateNpcTurns(npcActions) {
    DOM.turnAnnouncerOverlay.classList.add('active');

    for (const action of npcActions) {
        const npc = NPC_CANDIDATES.find(n => n.id === action.candidate_id);
        if (!npc) continue;

        DOM.announcerName.textContent = npc.name.toUpperCase();
        DOM.announcerName.style.color = npc.color;

        if (action.type === "manifesto" || !action.type) {
            soundManager.play('ui_hover');
            DOM.announcerAction.textContent = "is thinking...";
            await sleep(800);

            DOM.announcerAction.innerHTML = `Chose: <br><br> <span style="color:#fff; font-size:12px;">${action.title}</span> <br><br> <span style="color:#e04848">(+${action.shift_amount}% for ${getGroupName(action.group_id)})</span>`;

            if (!gameState.npcManifestos[npc.id]) {
                gameState.npcManifestos[npc.id] = [];
            }
            gameState.npcManifestos[npc.id].push({
                id: action.manifesto_id,
                title: action.title,
                description: "(Opponent Campaign Promise)",
                target_group_id: action.group_id,
                shift_amount: action.shift_amount
            });
            await sleep(1500);

            // If this NPC action has dialogue, show the dialogue popup with TTS
            if (action.dialogue && action.dialogue.trim()) {
                DOM.turnAnnouncerOverlay.classList.remove('active');
                await showDialoguePopup(
                    npc.name,
                    action.dialogue,
                    npc.emoji,
                    npc.color,
                    action.candidate_id,
                    action.speech_style || 'neutral'
                );
                DOM.turnAnnouncerOverlay.classList.add('active');
            } else {
                await sleep(500);
            }
        } else if (action.type === "sabotage") {
            soundManager.play('sabotage_fuse');
            let vicName = "Someone";
            if (action.target_id === 4) vicName = "YOU";
            else {
                let vicData = NPC_CANDIDATES.find(n => n.id === action.target_id);
                if (vicData) vicName = vicData.name;
            }

            DOM.announcerAction.innerHTML = `<span style="color:#e04848; font-size:12px;">💣 launched SABOTAGE against ${vicName}!</span>`;
            await sleep(1500);

            let sabText = `<br><span style="color:#999; font-style:italic; font-size:9px;">"${action.sabotage_text || ''}"</span><br><br>`;

            if (action.blocked) {
                DOM.announcerAction.innerHTML += sabText + `<span style="color:#48b848; font-size:14px; font-weight:bold;">⚖️ BLOCKED!</span><br><span style="color:#888; font-size:9px;">Election Commissioner: ${action.reason || 'Code of conduct violation'}</span>`;
            } else {
                let damagePct = action.multiplier ? Math.round(action.multiplier * 100) : '??';
                DOM.announcerAction.innerHTML += sabText + `<span style="color:#e04848; font-size:14px; font-weight:bold;">💥 SABOTAGE SUCCESS!</span><br><span style="color:#e8a040; font-size:9px;">${action.dialogue || ''}</span><br><span style="color:#e04848; font-size:8px;">${vicName} lost ${damagePct}% voter share!</span>`;
            }
            await sleep(2000);
        }
    }

    DOM.turnAnnouncerOverlay.classList.remove('active');
}


// ══════════════════════════════════
//  ADD TO CAMPAIGN (core action)
// ══════════════════════════════════

async function addToCampaign() {
    const customText = DOM.customManifestoInput.value.trim();
    let addedCount = 0;
    const apiSyncTasks = []; // Background API calls

    // Check if empty
    if (gameState.selectedPopupOptions.length === 0 && !customText) {
        DOM.popupActionBtn.style.animation = 'shake 0.4s ease-out';
        setTimeout(() => DOM.popupActionBtn.style.animation = '', 400);
        return;
    }

    // Check if enough coins
    let pendingCount = gameState.selectedPopupOptions.length + (customText ? 1 : 0);
    if (gameState.candidate.coins < pendingCount * 50) {
        soundManager.play('error_buzz');
        showToast('❌', 'Not enough coins!');
        return;
    }

    try {
        // Process selected manifesto bank options
        for (const optId of gameState.selectedPopupOptions) {
            const option = gameState.manifestoBank.find(o => o.id === optId);
            if (!option) continue;
            if (gameState.manifesto.some(m => m.id === option.id)) continue;

            // 1. Apply waterfall LOCALLY first (instant)
            applyWaterfallLocally(option.target_group_id, option.shift_amount);

            // 2. Add to local manifesto list immediately
            gameState.manifesto.push({
                id: option.id,
                title: option.title,
                description: option.description,
                target_group_id: option.target_group_id,
                shift_amount: option.shift_amount,
                icon: getGroupIcon(option.target_group_id)
            });

            // 3. Remove from available bank
            gameState.manifestoBank = gameState.manifestoBank.filter(m => m.id !== option.id);

            // 4. Queue background API sync (non-blocking)
            apiSyncTasks.push(
                applyManifesto(option.target_group_id, option.shift_amount)
                    .then(result => {
                        if (result.new_shares) {
                            gameState.allShares[option.target_group_id] = {};
                            for (const [cId, share] of Object.entries(result.new_shares)) {
                                gameState.allShares[option.target_group_id][Number(cId)] = share;
                            }
                        }
                        console.log(`✅ Synced manifesto ${option.id} with server`);
                    })
                    .catch(err => console.warn(`Server sync skipped for ${option.id}:`, err.message))
            );

            addedCount++;
        }

        // Handle custom manifesto text
        if (customText) {
            gameState.manifesto.push({
                id: Date.now(),
                title: customText,
                description: 'A custom promise to the people.',
                target_group_id: -1,
                shift_amount: 0,
                icon: '📜'
            });
            addedCount++;
        }

        if (addedCount > 0) {
            // Update voterShares from allShares for bar chart
            gameState.voterShares = VOTER_GROUPS.map(group => ({
                ...group,
                percent: Math.round((gameState.allShares[group.id]?.[PLAYER_CANDIDATE_ID] ?? INITIAL_SHARE) * 100) / 100
            }));

            // Immediate UI update — no waiting for server
            renderManifesto(true);
            renderBarChart();
            closePopup();
            soundManager.play('add_manifesto');
            showToast('⚔️', `${addedCount} manifesto${addedCount > 1 ? 's' : ''} deployed!`);

            // Update coin count
            gameState.candidate.coins -= addedCount * 50;
            localStorage.setItem('playerCoins', gameState.candidate.coins);
            DOM.coinCount.textContent = gameState.candidate.coins.toLocaleString();

            // Show dialogue popup for the LAST selected manifesto with TTS
            const lastOption = gameState.manifestoBank.length > 0 ? null : null;
            const lastSelectedId = gameState.selectedPopupOptions[gameState.selectedPopupOptions.length - 1];
            // Find the full manifesto data from the original bank
            const allBank = await apiFetch('/api/all-manifestos').catch(() => []);
            const lastManifesto = allBank.find(m => m.id === lastSelectedId);

            if (lastManifesto && lastManifesto.dialogue && lastManifesto.dialogue.trim()) {
                await showDialoguePopup(
                    gameState.candidate.name,
                    lastManifesto.dialogue,
                    '🎤',
                    '#48b848',
                    PLAYER_CANDIDATE_ID,
                    lastManifesto.speech_style || 'neutral'
                );
            }

            // Let API calls finish
            await Promise.allSettled(apiSyncTasks);

            // NPC Turn
            try {
                const npcRes = await apiFetch('/api/end-turn', { method: 'POST', timeoutMs: 60000 });
                if (npcRes.npc_actions && npcRes.npc_actions.length > 0) {
                    await animateNpcTurns(npcRes.npc_actions);
                }
            } catch (err) {
                console.error("NPC turn failed:", err);
            }

            // Re-sync UI state after ALL animations/errors
            await loadVoterStanding();
            renderBarChart();
            renderOpponentsSidebar();

            // Gain round reward
            gameState.candidate.coins += 25;
            localStorage.setItem('playerCoins', gameState.candidate.coins);
            DOM.coinCount.textContent = gameState.candidate.coins.toLocaleString();
            setTimeout(() => showToast('🪙', 'Round End! +25 Coins Granted'), 500);

            // Track & evaluate turn limit
            gameState.turnNumber++;
            localStorage.setItem('turnNumber', gameState.turnNumber);

            if (gameState.turnNumber <= 5) {
                DOM.roundTrackerText.textContent = `RND ${gameState.turnNumber}/5`;
            } else {
                DOM.roundTrackerText.textContent = `RND 5/5`;
                setTimeout(() => evaluateElectionResults(), 1000);
            }

        } else {
            closePopup();
            showToast('📋', 'Already in your manifesto!');
        }
    } catch (err) {
        console.error('Error in addToCampaign:', err);
        showToast('❌', 'Something went wrong!');
    }
}

/**
 * Waterfall Redistribution (matches fastapi_server.py logic exactly)
 * ─────────────────────────────────────────────────────────────────
 * When player gains X% in a voter group:
 *   1. Player's share increases (capped at GROUP_CAP = 20%)
 *   2. The actual increase is deducted equally from opponents
 *   3. If an opponent hits 0%, remaining debt waterfalls to others
 *   4. Total shares in any group always sum to GROUP_CAP (20%)
 */
function applyWaterfallLocally(groupId, shiftAmount) {
    const shares = gameState.allShares[groupId];
    if (!shares) return;

    const targetId = PLAYER_CANDIDATE_ID;

    // 1. Apply gain to player (cap at GROUP_CAP)
    const oldShare = shares[targetId];
    const newShare = Math.min(GROUP_CAP, oldShare + shiftAmount);
    const actualIncrease = newShare - oldShare;
    shares[targetId] = newShare;

    // 2. Waterfall: deduct actualIncrease from opponents
    let debt = actualIncrease;
    let opponents = Object.keys(shares)
        .map(Number)
        .filter(cId => cId !== targetId && shares[cId] > 0);

    while (debt > 0.001 && opponents.length > 0) {
        const sharePerOpponent = debt / opponents.length;
        const nextOpponents = [];

        for (const oppId of opponents) {
            const reduction = Math.min(shares[oppId], sharePerOpponent);
            shares[oppId] = Math.round((shares[oppId] - reduction) * 10000) / 10000;
            debt -= reduction;

            // Keep opponent if they still have shares
            if (shares[oppId] > 0) {
                nextOpponents.push(oppId);
            }
        }

        opponents = nextOpponents;
    }

    // 3. Update player's bar chart view
    const voterShare = gameState.voterShares.find(v => v.id === groupId);
    if (voterShare) {
        voterShare.percent = Math.round(shares[targetId] * 100) / 100;
    }

    console.log(`📊 Group ${groupId} after waterfall:`, { ...shares });
}


// ══════════════════════════════════
//  TOAST NOTIFICATION
// ══════════════════════════════════

function showToast(icon, msg) {
    DOM.toast.querySelector('.toast-icon').textContent = icon;
    DOM.toastMsg.textContent = msg;
    DOM.toast.classList.add('show');
    setTimeout(() => DOM.toast.classList.remove('show'), 2000);
}


// ══════════════════════════════════
//  TTS & DIALOGUE SYSTEM
// ══════════════════════════════════

/**
 * Play TTS audio for a character via the server proxy.
 * Returns an object with:
 *   - onStarted: Promise that resolves when audio actually starts playing
 *   - onEnded: Promise that resolves when audio finishes
 * If muted or error, both resolve immediately.
 */
function playCharacterSpeech(text, candidateId, speechStyle = 'neutral') {
    // Immediate resolve for muted/empty
    if (gameState.isMuted || !text) {
        return {
            onStarted: Promise.resolve(),
            onEnded: Promise.resolve()
        };
    }

    let startResolve, endResolve;
    const onStarted = new Promise(r => { startResolve = r; });
    const onEnded = new Promise(r => { endResolve = r; });

    // Fetch + play in background
    (async () => {
        try {
            const resp = await fetch(`${API_BASE}/api/tts`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text: text,
                    candidate_id: candidateId,
                    speech_style: speechStyle
                })
            });

            if (!resp.ok) {
                console.warn('TTS request failed:', resp.status);
                startResolve();
                endResolve();
                return;
            }

            const blob = await resp.blob();
            const url = URL.createObjectURL(blob);
            const audio = new Audio(url);
            gameState.currentAudio = audio;

            audio.playbackRate = 1.15; // Slightly faster speech
            audio.addEventListener('playing', () => {
                startResolve();
            }, { once: true });

            audio.onended = () => {
                URL.revokeObjectURL(url);
                gameState.currentAudio = null;
                endResolve();
            };
            audio.onerror = () => {
                URL.revokeObjectURL(url);
                gameState.currentAudio = null;
                startResolve();
                endResolve();
            };

            audio.play().catch(() => {
                gameState.currentAudio = null;
                startResolve();
                endResolve();
            });

            // Safety: if 'playing' event never fires, unblock after 2s
            setTimeout(() => { startResolve(); }, 2000);
        } catch (err) {
            console.warn('TTS error:', err.message);
            startResolve();
            endResolve();
        }
    })();

    return { onStarted, onEnded };
}

/**
 * Show a visual novel-style dialogue popup with typewriter effect and TTS.
 * The typewriter only starts AFTER the voice begins playing — no desync.
 * Blocks until user clicks to dismiss (after audio finishes or on click-to-skip).
 * Returns a Promise that resolves when dismissed.
 */
function showDialoguePopup(speakerName, dialogueText, emoji, color, candidateId, speechStyle) {
    return new Promise((resolve) => {
        SoundFX.dialogueOpen();

        // Set speaker info
        DOM.dialogueSpeakerEmoji.textContent = emoji || '🎤';
        DOM.dialogueSpeakerName.textContent = speakerName.toUpperCase();
        DOM.dialogueSpeakerName.style.color = color || '#f0c040';
        DOM.dialogueText.textContent = '';
        DOM.dialogueText.classList.add('typing');
        DOM.dialogueContinue.classList.remove('visible');
        DOM.dialogueAudioIndicator.classList.remove('playing');

        // Show overlay
        DOM.dialogueOverlay.classList.add('active');

        let charIndex = 0;
        let typewriterDone = false;
        let audioDone = false;
        let dismissed = false;
        let typewriterInterval = null;
        let typewriterStarted = false;

        function startTypewriter() {
            if (typewriterStarted) return;
            typewriterStarted = true;

            // Clear loading message and begin typing
            DOM.dialogueText.textContent = '';
            DOM.dialogueText.classList.add('typing');

            const typeSpeed = 20; // ms per character (fast typewriter)
            typewriterInterval = setInterval(() => {
                if (charIndex < dialogueText.length) {
                    DOM.dialogueText.textContent += dialogueText[charIndex];
                    charIndex++;
                    // Auto-scroll
                    const textArea = DOM.dialogueText.closest('.dialogue-text-area');
                    if (textArea) textArea.scrollTop = textArea.scrollHeight;
                } else {
                    clearInterval(typewriterInterval);
                    typewriterInterval = null;
                    typewriterDone = true;
                    DOM.dialogueText.classList.remove('typing');
                    checkShowContinue();
                }
            }, typeSpeed);
        }

        // Start TTS audio — typewriter waits for it
        DOM.dialogueAudioIndicator.classList.add('playing');
        DOM.dialogueText.textContent = '🔊 Loading voice...';

        const { onStarted, onEnded } = playCharacterSpeech(dialogueText, candidateId, speechStyle);

        // When audio actually starts playing → begin the typewriter
        onStarted.then(() => {
            startTypewriter();
        });

        // When audio ends → mark done
        onEnded.then(() => {
            audioDone = true;
            DOM.dialogueAudioIndicator.classList.remove('playing');
            checkShowContinue();
        }).catch(() => {
            audioDone = true;
            DOM.dialogueAudioIndicator.classList.remove('playing');
            checkShowContinue();
        });

        // If muted, start typewriter immediately (no voice to wait for)
        if (gameState.isMuted) {
            audioDone = true;
            DOM.dialogueAudioIndicator.classList.remove('playing');
            startTypewriter();
        }

        function checkShowContinue() {
            // Show continue button when BOTH typewriter and audio are done
            // OR if audio failed/muted, just when typewriter is done
            if (typewriterDone && (audioDone || gameState.isMuted)) {
                DOM.dialogueContinue.classList.add('visible');
            }
        }

        // Click to skip/dismiss
        function onDismiss() {
            if (dismissed) return;

            if (!typewriterStarted) {
                // Audio hasn't started yet — skip waiting, show full text
                startTypewriter();
                if (typewriterInterval) clearInterval(typewriterInterval);
                typewriterInterval = null;
                DOM.dialogueText.textContent = dialogueText;
                DOM.dialogueText.classList.remove('typing');
                typewriterDone = true;
                checkShowContinue();
                return;
            }

            if (!typewriterDone) {
                // Skip typewriter — show full text immediately
                if (typewriterInterval) clearInterval(typewriterInterval);
                typewriterInterval = null;
                DOM.dialogueText.textContent = dialogueText;
                DOM.dialogueText.classList.remove('typing');
                typewriterDone = true;
                checkShowContinue();
                return;
            }

            if (!audioDone && !gameState.isMuted) {
                // Skip audio — stop it
                if (gameState.currentAudio) {
                    gameState.currentAudio.pause();
                    gameState.currentAudio = null;
                }
                audioDone = true;
                DOM.dialogueAudioIndicator.classList.remove('playing');
                checkShowContinue();
                return;
            }

            // Dismiss completely
            dismissed = true;
            soundManager.play('ui_click');
            DOM.dialogueOverlay.classList.remove('active');
            DOM.dialogueOverlay.removeEventListener('click', onDismiss);
            resolve();
        }

        DOM.dialogueOverlay.addEventListener('click', onDismiss);
    });
}

// ══════════════════════════════════
//  ELECTION ENDGAME LOGIC
// ══════════════════════════════════

function evaluateElectionResults() {
    const candidateTotals = [];

    // NPCs (0 to 3) + Player (4)
    for (let cid = 0; cid <= 4; cid++) {
        let total = 0;
        let maxGroup = 0;
        if (cid === PLAYER_CANDIDATE_ID) {
            gameState.voterShares.forEach(g => {
                total += g.percent;
                if (g.percent > maxGroup) maxGroup = g.percent;
            });
        } else {
            VOTER_GROUPS.forEach(g => {
                const s = gameState.allShares[g.id]?.[cid] ?? INITIAL_SHARE;
                total += s;
                if (s > maxGroup) maxGroup = s;
            });
        }

        let pName = cid === PLAYER_CANDIDATE_ID ? gameState.candidate.name + " (You)" : NPC_CANDIDATES.find(n => n.id === cid).name;

        candidateTotals.push({
            id: cid,
            name: pName,
            total: Math.round(total * 100) / 100,
            maxGroup: Math.round(maxGroup * 100) / 100
        });
    }

    // Sort by absolute highest total, tiebreak with highest peak
    candidateTotals.sort((a, b) => {
        if (b.total !== a.total) return b.total - a.total;
        return b.maxGroup - a.maxGroup;
    });

    let winnerText = "";
    let subText = "";
    let boxColor = "";

    // Check coalition tie
    if (candidateTotals[0].total === candidateTotals[1].total && candidateTotals[0].maxGroup === candidateTotals[1].maxGroup) {
        let playerIsTied1st = candidateTotals[0].total === candidateTotals.find(c => c.id === PLAYER_CANDIDATE_ID).total &&
            candidateTotals[0].maxGroup === candidateTotals.find(c => c.id === PLAYER_CANDIDATE_ID).maxGroup;

        if (playerIsTied1st) {
            winnerText = "SABKA SAATH SABKA VIKAS";
            subText = "Coalition Government! You tied for first place.";
            boxColor = "#a0a0f0";
        } else {
            winnerText = "DEFEATED";
            subText = `${candidateTotals[0].name.replace(" (You)", "")} led a coalition against you!`;
            boxColor = "#e04848";
        }
    } else {
        if (candidateTotals[0].id === PLAYER_CANDIDATE_ID) {
            winnerText = "VICTORY!";
            subText = "You won the Panchayat Election!";
            boxColor = "#48b848";
        } else {
            winnerText = "DEFEATED";
            subText = `${candidateTotals[0].name} won the election.`;
            boxColor = "#e04848";
        }
    }

    DOM.endGameWinnerBox.textContent = winnerText;
    DOM.endGameWinnerBox.style.color = boxColor;
    DOM.endGameSubtext.textContent = subText;

    DOM.endGameStandings.innerHTML = '';
    candidateTotals.forEach((c, idx) => {
        const row = document.createElement('div');
        row.style.cssText = "font-family:'Press Start 2P'; font-size: 8px; margin-bottom: 12px; color: " + (c.id === PLAYER_CANDIDATE_ID ? "#48b848" : "#ccc") + ";";
        row.textContent = `${idx + 1}. ${c.name} - ${c.total.toFixed(2)}% (Peak: ${c.maxGroup.toFixed(2)}%)`;
        DOM.endGameStandings.appendChild(row);
    });

    DOM.endGameOverlay.classList.add('active');
    DOM.addManifestoBtn.style.opacity = '0.5';
    DOM.addManifestoBtn.style.pointerEvents = 'none';

    // Play victory/defeat sound
    if (candidateTotals[0].id === PLAYER_CANDIDATE_ID) {
        soundManager.play('round_chime');
    } else {
        soundManager.play('error_buzz');
    }
}



// ══════════════════════════════════
//  BOOT
// ══════════════════════════════════

// ══════════════════════════════════
//  SABOTAGE SYSTEM
// ══════════════════════════════════

function openSabotagePopup() {
    if (gameState.candidate.coins < 75) {
        soundManager.play('error_buzz');
        showToast('❌', 'Need 75 coins for sabotage!');
        return;
    }
    DOM.sabotagePromptInput.value = '';
    DOM.sabotageOverlay.classList.add('active');
}

function closeSabotagePopup() {
    DOM.sabotageOverlay.classList.remove('active');
}

async function executeSabotage() {
    const targetId = parseInt(DOM.sabotageTargetSelect.value);
    const sabotageText = DOM.sabotagePromptInput.value.trim();

    if (!sabotageText) {
        showToast('❌', 'Write your sabotage attack!');
        return;
    }

    if (gameState.candidate.coins < 75) {
        soundManager.play('error_buzz');
        showToast('❌', 'Not enough coins!');
        return;
    }

    // Disable button during API call
    DOM.sabotageSubmitBtn.disabled = true;
    DOM.sabotageSubmitBtn.querySelector('.popup-action-text').textContent = '⏳ SENDING...';

    try {
        const result = await apiFetch('/api/player-sabotage', {
            method: 'POST',
            body: JSON.stringify({ target_id: targetId, sabotage_prompt: sabotageText }),
            timeoutMs: 30000
        });

        closeSabotagePopup();

        // Deduct coins locally
        gameState.candidate.coins -= 75;
        localStorage.setItem('playerCoins', gameState.candidate.coins);
        DOM.coinCount.textContent = gameState.candidate.coins.toLocaleString();

        // Show result popup
        if (result.status === 'blocked') {
            DOM.sabotageResultTitle.textContent = '⚖️ BLOCKED!';
            DOM.sabotageResultTitle.style.color = '#e04848';
            DOM.sabotageResultMessage.textContent = result.message;
            DOM.sabotageResultDialogue.textContent = `Reason: ${result.reason}`;
        } else {
            let damagePct = result.multiplier ? Math.round(result.multiplier * 100) : '??';
            DOM.sabotageResultTitle.textContent = '💥 SABOTAGE SUCCESS!';
            DOM.sabotageResultTitle.style.color = '#48b848';
            DOM.sabotageResultMessage.textContent = `${result.target_name} lost ${damagePct}% voter share!`;
            DOM.sabotageResultDialogue.textContent = result.dialogue || '';
        }
        DOM.sabotageResultOverlay.classList.add('active');

        // Re-sync shares after sabotage
        await loadVoterStanding();
        renderBarChart();
        renderOpponentsSidebar();

        // NPC Turn (same as after ADD MANIFESTO)
        try {
            const npcRes = await apiFetch('/api/end-turn', { method: 'POST', timeoutMs: 60000 });
            if (npcRes.npc_actions && npcRes.npc_actions.length > 0) {
                await animateNpcTurns(npcRes.npc_actions);
            }
        } catch (err) {
            console.error("NPC turn failed:", err);
        }

        // Re-sync after NPC turns
        await loadVoterStanding();
        renderBarChart();
        renderOpponentsSidebar();

        // Round reward
        gameState.candidate.coins += 25;
        localStorage.setItem('playerCoins', gameState.candidate.coins);
        DOM.coinCount.textContent = gameState.candidate.coins.toLocaleString();
        setTimeout(() => showToast('🪙', 'Round End! +25 Coins Granted'), 500);

        // Track round
        gameState.turnNumber++;
        localStorage.setItem('turnNumber', gameState.turnNumber);
        if (gameState.turnNumber <= 5) {
            DOM.roundTrackerText.textContent = `RND ${gameState.turnNumber}/5`;
            soundManager.play('round_chime');
        } else {
            DOM.roundTrackerText.textContent = `RND 5/5`;
            setTimeout(() => evaluateElectionResults(), 1000);
        }

    } catch (err) {
        console.error('Sabotage error:', err);
        showToast('❌', 'Sabotage failed! Try again.');
    } finally {
        DOM.sabotageSubmitBtn.disabled = false;
        DOM.sabotageSubmitBtn.querySelector('.popup-action-text').textContent = '💣 LAUNCH SABOTAGE';
    }
}

// Sabotage event listeners
if (DOM.sabotageBtn) DOM.sabotageBtn.addEventListener('click', openSabotagePopup);
if (DOM.sabotageCloseBtn) DOM.sabotageCloseBtn.addEventListener('click', closeSabotagePopup);
if (DOM.sabotageSubmitBtn) DOM.sabotageSubmitBtn.addEventListener('click', executeSabotage);
if (DOM.sabotageResultCloseBtn) DOM.sabotageResultCloseBtn.addEventListener('click', () => {
    DOM.sabotageResultOverlay.classList.remove('active');
});


// ══════════════════════════════════
//  BOOT
// ══════════════════════════════════

function init() {
    // Attempt to load background audio assets silently
    soundManager.loadAssets();

    // Start pixel particles in the background immediately
    const particleSystem = new PixelParticleSystem(DOM.pixelCanvas);
    particleSystem.start();

    // Global UI hovers and standard clicks
    const uiElements = document.querySelectorAll('.start-menu-btn, .settings-btn, .coc-btn, .hamburger-btn, .sidebar-close-btn, .add-manifesto-btn, .popup-close-btn, .popup-action-btn');
    uiElements.forEach(btn => {
        btn.addEventListener('mouseenter', () => soundManager.play('ui_hover'));
        btn.addEventListener('click', () => {
            // Only play standard click if it's NOT a custom mechanic button (sabotage/manifesto handled independently)
            if (btn.id !== 'addManifestoBtn' && btn.id !== 'sabotageBtn') {
                soundManager.play('ui_click');
            }
        });
    });

    // Bind Start Screen Events
    if (DOM.startSinglePlayerBtn) {
        DOM.startSinglePlayerBtn.addEventListener('click', () => {
            soundManager.play('ui_click');

            // Execute the original start logic if it exists (handles game startup)
            if (typeof startSinglePlayer === 'function') {
                startSinglePlayer();
            } else {
                // If startSinglePlayer was removed by user layout rollback, just dismiss the overlay
                DOM.startScreenOverlay.style.opacity = '0';
                setTimeout(() => DOM.startScreenOverlay.style.display = 'none', 500);
            }
        });
    }

    if (DOM.startMultiPlayerBtn) {
        DOM.startMultiPlayerBtn.addEventListener('click', () => {
            showToast('🌐', 'Multiplayer coming soon!');
        });
    }

    if (DOM.startSoundToggleBtn) {
        DOM.startSoundToggleBtn.addEventListener('click', () => {
            soundManager.toggleMute();
            DOM.startSoundToggleBtn.innerHTML = gameState.isMuted
                ? '<span class="btn-icon">🔇</span> SOUND: OFF'
                : '<span class="btn-icon">🔊</span> SOUND: ON';
            if (DOM.muteBtn) {
                if (gameState.isMuted) DOM.muteBtn.classList.add('muted');
                else DOM.muteBtn.classList.remove('muted');
            }
        });
    }
    // Note: DOM.muteBtn logic is handled earlier in bindEvents()
    // Set initial mute matching state
    if (gameState.isMuted && DOM.startSoundToggleBtn) {
        DOM.startSoundToggleBtn.innerHTML = '<span class="btn-icon">🔇</span> SOUND: OFF';
    }
}

document.addEventListener('DOMContentLoaded', init);
