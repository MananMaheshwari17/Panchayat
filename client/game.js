/* ================================================
   PANCHAYAT GAME – Frontend ↔ FastAPI Backend
   ================================================ */

// ── CONFIG ──
const API_BASE = 'http://localhost:8000'; // FastAPI server
const PLAYER_CANDIDATE_ID = 4;           // Player is always candidate 4
const NUM_CANDIDATES = 5;                // 5 candidates (0-3 NPC, 4 Player)
const GROUP_CAP = 20.0;                  // Each voter group = 20% of total population
const INITIAL_SHARE = 4.0;              // GROUP_CAP / NUM_CANDIDATES = 4% each

// ── Voter Group Mapping (matches init_db.py) ──
const VOTER_GROUPS = [
    { id: 0, name: 'Farmers',      icon: '🌾', color: '#48b848' },
    { id: 1, name: 'Students',     icon: '📱', color: '#4088e0' },
    { id: 2, name: 'Tech Workers', icon: '💻', color: '#e8d040' },
    { id: 3, name: 'Laborers',     icon: '⚒️', color: '#e04848' },
    { id: 4, name: 'Youth',        icon: '🏃', color: '#a048c8' }
];

// ── NPC Candidates (matches init_db.py) ──
const NPC_CANDIDATES = [
    { id: 0, name: 'Vikas Purush',   archetype: 'vikas_purush',   emoji: '🏗️', color: '#e8a040' },
    { id: 1, name: 'Dharma Rakshak', archetype: 'dharma_rakshak', emoji: '🛡️', color: '#e04848' },
    { id: 2, name: 'Jan Neta',       archetype: 'jan_neta',       emoji: '📢', color: '#4088e0' },
    { id: 3, name: 'Mukti Devi',     archetype: 'mukti_devi',     emoji: '🕊️', color: '#a048c8' }
];

// ── Game State (local mirror of DB) ──
const gameState = {
    candidate: {
        id: PLAYER_CANDIDATE_ID,
        name: 'Player',
        party: 'Jan Seva Party',
        popularity: 2,
        coins: 1250,
        level: 1
    },
    manifesto: [],         // Player's chosen manifestos
    manifestoBank: [],     // Available manifestos from backend
    voterShares: [],       // Player's share per voter group (what bar chart shows)
    allShares: {},         // Full share table: { groupId: { candidateId: share } }
    turnNumber: 0,
    selectedPopupOptions: []
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
    sidebarScroll: document.getElementById('sidebarScroll')
};


// ══════════════════════════════════
//  API HELPERS
// ══════════════════════════════════

async function apiFetch(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json' },
            ...options
        });
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (err) {
        console.error(`API Error [${endpoint}]:`, err.message);
        throw err;
    }
}

/** GET /api/manifesto-bank → available manifestos */
async function fetchManifestoBank() {
    return apiFetch('/api/manifesto-bank');
}

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

async function init() {
    // Start pixel particles
    const particleSystem = new PixelParticleSystem(DOM.pixelCanvas);
    particleSystem.start();

    // Bind UI events
    bindEvents();

    // Fetch data from backend
    try {
        await Promise.all([
            loadManifestoBank(),
            loadVoterStanding()
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
}

/** Load available manifestos from /api/manifesto-bank */
async function loadManifestoBank() {
    const bank = await fetchManifestoBank();
    gameState.manifestoBank = bank;
}

/** Load voter standing from /api/total-standing */
async function loadVoterStanding() {
    const standings = await fetchTotalStanding();

    // standings = [{_id: candidate_id, total_support: number}, ...]
    // total_support is the SUM across all 5 groups for that candidate
    // Player starts at 4% × 5 groups = 20% total
    const playerStanding = standings.find(s => s._id === PLAYER_CANDIDATE_ID);

    // Since total-standing is aggregate, estimate per-group from local allShares
    // If we have local allShares, use those; otherwise estimate from aggregate
    if (Object.keys(gameState.allShares).length > 0) {
        gameState.voterShares = VOTER_GROUPS.map(group => ({
            ...group,
            percent: gameState.allShares[group.id]?.[PLAYER_CANDIDATE_ID] ?? INITIAL_SHARE
        }));
    } else {
        // First load — distribute total equally across groups
        gameState.voterShares = VOTER_GROUPS.map(group => ({
            ...group,
            percent: playerStanding
                ? Math.round((playerStanding.total_support / VOTER_GROUPS.length) * 100) / 100
                : INITIAL_SHARE
        }));
    }

    gameState.standings = standings;
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

    voterData.forEach((voter, index) => {
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
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && DOM.popupOverlay.classList.contains('active')) {
            closePopup();
        }
        if (e.key === 'Escape' && DOM.opponentsSidebar.classList.contains('open')) {
            closeSidebar();
        }
    });
    DOM.popupActionBtn.addEventListener('click', addToCampaign);

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
            <div class="opponent-avatar" style="background: ${npc.color};">${npc.emoji}</div>
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
        DOM.sidebarScroll.appendChild(card);
    });
}


// ══════════════════════════════════
//  ADD TO CAMPAIGN (core action)
// ══════════════════════════════════

async function addToCampaign() {
    const customText = DOM.customManifestoInput.value.trim();
    let addedCount = 0;

    // Disable button during API calls
    DOM.popupActionBtn.disabled = true;
    DOM.popupActionBtn.style.opacity = '0.6';

    try {
        // Process selected manifesto bank options
        for (const optId of gameState.selectedPopupOptions) {
            const option = gameState.manifestoBank.find(o => o.id === optId);
            if (!option) continue;

            // Check if already in player's manifesto
            if (gameState.manifesto.some(m => m.id === option.id)) continue;

            // Call backend: apply this manifesto's effect
            try {
                const result = await applyManifesto(option.target_group_id, option.shift_amount);
                console.log(`✅ Applied manifesto ${option.id} → group ${option.target_group_id}`, result);
                // Sync returned shares into local state
                if (result.new_shares) {
                    gameState.allShares[option.target_group_id] = {};
                    for (const [cId, share] of Object.entries(result.new_shares)) {
                        gameState.allShares[option.target_group_id][Number(cId)] = share;
                    }
                }
            } catch (apiErr) {
                console.warn(`Backend call failed for manifesto ${option.id}:`, apiErr.message);
                // Apply waterfall locally as fallback
                applyWaterfallLocally(option.target_group_id, option.shift_amount);
            }

            // Add to local manifesto list
            gameState.manifesto.push({
                id: option.id,
                title: option.title,
                description: option.description,
                target_group_id: option.target_group_id,
                shift_amount: option.shift_amount,
                icon: getGroupIcon(option.target_group_id)
            });

            // Remove from available bank
            gameState.manifestoBank = gameState.manifestoBank.filter(m => m.id !== option.id);

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

            renderManifesto(true);
            renderBarChart();
            closePopup();
            showToast('⚔️', `${addedCount} manifesto${addedCount > 1 ? 's' : ''} deployed!`);

            // Update coin count (spend coins for each manifesto)
            gameState.candidate.coins -= addedCount * 50;
            DOM.coinCount.textContent = gameState.candidate.coins.toLocaleString();

        } else if (gameState.selectedPopupOptions.length === 0 && !customText) {
            // Nothing selected — shake
            DOM.popupActionBtn.style.animation = 'shake 0.4s steps(4)';
            setTimeout(() => DOM.popupActionBtn.style.animation = '', 400);
        } else {
            closePopup();
            showToast('📋', 'Already in your manifesto!');
        }
    } catch (err) {
        console.error('Error in addToCampaign:', err);
        showToast('❌', 'Something went wrong!');
    } finally {
        DOM.popupActionBtn.disabled = false;
        DOM.popupActionBtn.style.opacity = '';
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
//  BOOT
// ══════════════════════════════════

document.addEventListener('DOMContentLoaded', init);
