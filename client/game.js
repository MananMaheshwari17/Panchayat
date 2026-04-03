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
    selectedCategory: 'education'
};

// ── DOM References ──
const DOM = {
    manifestoList: document.getElementById('manifestoList'),
    barChart: document.getElementById('barChart'),
    addManifestoBtn: document.getElementById('addManifestoBtn'),
    modalOverlay: document.getElementById('modalOverlay'),
    modalClose: document.getElementById('modalClose'),
    promiseTitle: document.getElementById('promiseTitle'),
    promiseDesc: document.getElementById('promiseDesc'),
    categoryPicker: document.getElementById('categoryPicker'),
    submitPromise: document.getElementById('submitPromise'),
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
    bindEvents();
}

// ── Render Manifesto List ──
function renderManifesto() {
    DOM.manifestoList.innerHTML = '';

    gameState.manifesto.forEach((item, index) => {
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
    // Generate the bars + axis + labels based on design
    DOM.barChart.innerHTML = '';

    // Axis line
    const axis = document.createElement('div');
    axis.className = 'chart-axis';
    DOM.barChart.appendChild(axis);

    gameState.voters.forEach((voter) => {
        const group = document.createElement('div');
        group.className = 'bar-group';

        const barHeight = Math.max(voter.percent, 10); // visually a minimum height

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

// ── Event Bindings ──
function bindEvents() {
    DOM.addManifestoBtn.addEventListener('click', () => {
        DOM.modalOverlay.classList.add('active');
        DOM.promiseTitle.value = '';
        DOM.promiseDesc.value = '';
        DOM.promiseTitle.focus();
    });

    DOM.modalClose.addEventListener('click', closeModal);
    DOM.modalOverlay.addEventListener('click', (e) => {
        if (e.target === DOM.modalOverlay) closeModal();
    });

    DOM.categoryPicker.addEventListener('click', (e) => {
        const btn = e.target.closest('.cat-btn');
        if (!btn) return;
        document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        gameState.selectedCategory = btn.dataset.cat;
    });

    DOM.submitPromise.addEventListener('click', addNewPromise);
}

function addNewPromise() {
    const title = DOM.promiseTitle.value.trim();
    const desc = DOM.promiseDesc.value.trim();
    if (!title) return;

    const activeBtn = document.querySelector('.cat-btn.active');
    
    gameState.manifesto.push({
        id: gameState.nextId++,
        title,
        desc: desc || 'A promise to the people.',
        category: gameState.selectedCategory,
        icon: activeBtn.dataset.icon,
        color: '#8D6E63'
    });
    
    renderManifesto();
    closeModal();
    showToast('🎉', 'Manifesto added!');
}

function closeModal() {
    DOM.modalOverlay.classList.remove('active');
}

function showToast(icon, msg) {
    DOM.toast.querySelector('.toast-icon').textContent = icon;
    DOM.toastMsg.textContent = msg;
    DOM.toast.classList.add('show');
    setTimeout(() => DOM.toast.classList.remove('show'), 2000);
}

// ── Boot ──
document.addEventListener('DOMContentLoaded', init);
