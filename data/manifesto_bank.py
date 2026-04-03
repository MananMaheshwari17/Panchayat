"""
Panchayat Manifesto Bank
========================
A centralized repository of political promises and their 
hardcoded effects on the voter population (0-4 groups).
"""

MANIFESTO_BANK = [
    {
        "id": 201,
        "title": "Mandi Modernization Act",
        "description": "Establishment of blockchain-tracked cold storage and direct-to-city supply chains for local produce.",
        "target_group_id": 0,  # Farmers
        "shift_amount": 3.5,
        "archetype_suitability": "vikas_purush",
        "used_by": None  # Stores candidate_id when claimed
    },
    {
        "id": 202,
        "title": "Abhyudaya Coaching Corps",
        "description": "Free high-end entrance exam coaching (JEE/NEET/UPSC) centers in every village block.",
        "target_group_id": 1,  # Students
        "shift_amount": 4.2,
        "archetype_suitability": "mukti_devi",
        "used_by": None
    },
    {
        "id": 203,
        "title": "Panchayat Fiber Revolution",
        "description": "Deployment of high-speed 5G broadband and public Wi-Fi hotspots at every Village Council office.",
        "target_group_id": 2,  # Tech Workers
        "shift_amount": 3.0,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 204,
        "title": "Shramik Suraksha Insurance",
        "description": "A guaranteed daily-wage insurance policy for unorganized laborers during health emergencies or weather disruptions.",
        "target_group_id": 3,  # Laborers
        "shift_amount": 4.5,
        "archetype_suitability": "jan_neta",
        "used_by": None
    },
    {
        "id": 205,
        "title": "Gramin Khel Mahotsav",
        "description": "Construction of modern district stadiums and a state-funded talent scouting program for rural athletes.",
        "target_group_id": 4,  # Youth
        "shift_amount": 3.8,
        "archetype_suitability": "all",
        "used_by": None
    },
    {
        "id": 206,
        "title": "Kisan Urja Scheme",
        "description": "100% subsidy on solar-powered irrigation pumps, eliminating electricity bills for small-scale farmers.",
        "target_group_id": 0,  # Farmers
        "shift_amount": 3.2,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 207,
        "title": "Digital Sanskriti Library",
        "description": "Establishment of 24/7 air-conditioned study hubs stocked with tablets and digital archives of traditional texts.",
        "target_group_id": 1,  # Students
        "shift_amount": 3.5,
        "archetype_suitability": "dharma_rakshak",
        "used_by": None
    },
    {
        "id": 208,
        "title": "BPO Rural Connect",
        "description": "Tax holidays for IT companies that set up small-scale outsourcing units in Tier-3 towns and villages.",
        "target_group_id": 2,  # Tech Workers
        "shift_amount": 5.0,
        "archetype_suitability": "vikas_purush",
        "used_by": None
    },
    {
        "id": 209,
        "title": "Vishwa Karma Safety Gear",
        "description": "Distribution of certified safety equipment and free quarterly health checkups for all registered construction workers.",
        "target_group_id": 3,  # Laborers
        "shift_amount": 2.5,
        "archetype_suitability": "all",
        "used_by": None
    },
    {
        "id": 210,
        "title": "Yuva Entrepreneur Seed Fund",
        "description": "Interest-free startup loans up to ₹5 Lakhs for youth starting local agro-processing or service businesses.",
        "target_group_id": 4,  # Youth
        "shift_amount": 4.0,
        "archetype_suitability": "jan_neta",
        "used_by": None
    }
]

def get_available_manifestos():
    """Returns only manifestos that haven't been claimed yet."""
    return [m for m in MANIFESTO_BANK if m["used_by"] is None]

def claim_manifesto(manifesto_id, candidate_id):
    """Marks a manifesto as used by a specific candidate."""
    for m in MANIFESTO_BANK:
        if m["id"] == manifesto_id and m["used_by"] is None:
            m["used_by"] = candidate_id
            return m
    return None