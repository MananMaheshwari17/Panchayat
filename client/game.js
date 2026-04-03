/* ================================================
   PANCHAYAT GAME – Main Game Logic
   ================================================ */

// ── Game State ──
const gameState = {
    candidate: {
        name: 'Rajesh Kumar',
        party: 'Jan Seva Party',
        popularity: 2,
        coins: 1250,
        level: 1
    },
    manifesto: [
        {
            id: 1,
            title: 'Education Reform',
            desc: 'Enormous nie to saust edmational education and labonaries.',
            category: 'education',
            icon: '🎓',
            color: '#8D6E63'
        },
        {
            id: 2,
            title: 'Economic Growth',
            desc: 'Growth growth to economic growth and growerlies and growth.',
            category: 'economy',
            icon: '📈',
            color: '#8D6E63'
        },
        {
            id: 3,
            title: 'Healthcare for All',
            desc: 'Confirms the attention of pronasional healthcare presidnceas for all.',
            category: 'health',
            icon: '⚕️',
            color: '#8D6E63'
        },
        {
            id: 4,
            title: 'Road & Infrastructure',
            desc: 'Improves prad, road & Infrastructure, road & Infrastructure.',
            category: 'infra',
            icon: '🛣️',
            color: '#8D6E63'
        }
    ],
    voters: [
        { type: 'Liberal',   icon: '🪶', percent: 20, color: '#2196F3' },
        { type: 'Conserv.',  icon: '🇺🇸', percent: 20, color: '#F44336' },
        { type: 'Youth',     icon: '👦', percent: 20, color: '#FFEB3B' },
        { type: 'Rural',     icon: '🌾', percent: 20, color: '#4CAF50' },
        { type: 'Urban',     icon: '🏢', percent: 20, color: '#9C27B0' }
    ],
    nextId: 5,
    selectedPopupOptions: []
};

// ── Popup Manifesto Options (predefined choices) ──
const popupManifestoOptions = [
    {
        id: 'water',
        icon: '💧',
        title: 'Clean Water Initiative',
        desc: 'Enormorss nio to soust edmcational education and labor-naries.',
        category: 'health'
    },
    {
        id: 'agri',
        icon: '🌾',
        title: 'Agricultural Subsidies',
        desc: 'Growth growling to economic growth and growerlies and growth.',
        category: 'economy'
    },
    {
        id: 'women',
        icon: '👩',
        title: "Women's Empowerment",
        desc: 'Empower women\'s fine staus of women in femms ts women.',
        category: 'defense'
    },
    {
        id: 'digital',
        icon: '💻',
        title: 'Digital Literacy',
        desc: 'Creater a digital Literacy and morps computer education.',
        category: 'education'
    },
    {
        id: 'transport',
        icon: '🚌',
        title: 'Public Transport',
        desc: 'Provides bus transport a public transport to consored.',
        category: 'infra'
    }
];

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
    menuBtn: document.getElementById('menuBtn')
};

// ── Initialize ──
function init() {
    renderManifesto();
    renderBarChart();
    renderPopupOptions();
    bindEvents();
}

// ── Render Manifesto List ──
function renderManifesto() {
    DOM.manifestoList.innerHTML = '';

    gameState.manifesto.forEach((item) => {
        const el = document.createElement('div');
        el.className = 'manifesto-item';

        el.innerHTML = `
            <div class="manifesto-icon">
                ${item.icon}
            </div>
            <div class="manifesto-details">
                <div class="manifesto-title">${item.title}</div>
                <div class="manifesto-desc">${item.desc}</div>
            </div>
        `;

        DOM.manifestoList.appendChild(el);
    });
}

// ── Render Bar Chart ──
function renderBarChart() {
    DOM.barChart.innerHTML = '';

    // Axis line
    const axis = document.createElement('div');
    axis.className = 'chart-axis';
    DOM.barChart.appendChild(axis);

    gameState.voters.forEach((voter) => {
        const group = document.createElement('div');
        group.className = 'bar-group';

        const barHeight = Math.max(voter.percent, 10);

        group.innerHTML = `
            <div class="bar-track">
                <div class="bar-percent">${voter.percent}%</div>
                <div class="bar-color" style="height: ${barHeight}%; background: ${voter.color};"></div>
            </div>
            <div class="bar-label-area">
                <span class="bar-icon">${voter.icon}</span>
                <span class="bar-label">${voter.type}</span>
            </div>
        `;

        DOM.barChart.appendChild(group);
    });
}

// ── Render Popup Manifesto Options ──
function renderPopupOptions() {
    DOM.popupScrollArea.innerHTML = '';
    gameState.selectedPopupOptions = [];

    popupManifestoOptions.forEach((option) => {
        const card = document.createElement('div');
        card.className = 'popup-option-card';
        card.dataset.optionId = option.id;

        card.innerHTML = `
            <div class="popup-option-icon">${option.icon}</div>
            <div class="popup-option-info">
                <div class="popup-option-title">${option.title}</div>
                <div class="popup-option-desc">${option.desc}</div>
            </div>
        `;

        // Toggle selection on click
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

// ── Event Bindings ──
function bindEvents() {
    // Open popup
    DOM.addManifestoBtn.addEventListener('click', openPopup);

    // Close popup
    DOM.popupCloseBtn.addEventListener('click', closePopup);
    DOM.popupOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.popupOverlay) closePopup();
    });

    // Keyboard: Escape closes popup
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && DOM.popupOverlay.classList.contains('active')) {
            closePopup();
        }
    });

    // Add to Campaign
    DOM.popupActionBtn.addEventListener('click', addToCampaign);
}

function openPopup() {
    // Reset state
    renderPopupOptions();
    DOM.customManifestoInput.value = '';

    // Show
    DOM.popupOverlay.classList.add('active');
}

function closePopup() {
    DOM.popupOverlay.classList.remove('active');
}

function addToCampaign() {
    const customText = DOM.customManifestoInput.value.trim();
    let addedCount = 0;

    // Add selected predefined options
    gameState.selectedPopupOptions.forEach((optId) => {
        const option = popupManifestoOptions.find(o => o.id === optId);
        if (option) {
            // Check if already in manifesto
            const alreadyExists = gameState.manifesto.some(m => m.title === option.title);
            if (!alreadyExists) {
                gameState.manifesto.push({
                    id: gameState.nextId++,
                    title: option.title,
                    desc: option.desc,
                    category: option.category,
                    icon: option.icon,
                    color: '#8D6E63'
                });
                addedCount++;
            }
        }
    });

    // Add custom manifesto if provided
    if (customText) {
        gameState.manifesto.push({
            id: gameState.nextId++,
            title: customText,
            desc: 'A custom promise to the people.',
            category: 'custom',
            icon: '📜',
            color: '#8D6E63'
        });
        addedCount++;
    }

    if (addedCount > 0) {
        renderManifesto();
        closePopup();
        showToast('🎉', `${addedCount} manifesto${addedCount > 1 ? 's' : ''} added!`);
    } else if (gameState.selectedPopupOptions.length === 0 && !customText) {
        // Nothing selected — subtle feedback
        DOM.popupActionBtn.style.animation = 'shake 0.4s ease';
        setTimeout(() => DOM.popupActionBtn.style.animation = '', 400);
    } else {
        closePopup();
        showToast('ℹ️', 'Already in your manifesto!');
    }
}

function showToast(icon, msg) {
    DOM.toast.querySelector('.toast-icon').textContent = icon;
    DOM.toastMsg.textContent = msg;
    DOM.toast.classList.add('show');
    setTimeout(() => DOM.toast.classList.remove('show'), 2000);
}

// ── Boot ──
document.addEventListener('DOMContentLoaded', init);
