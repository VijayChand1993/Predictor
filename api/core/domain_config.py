"""
Domain configuration for life domain analysis.

This module contains mappings between:
- Life domains and Vedic astrology houses
- Planets and their natural significations (karakas)
- Subdomains and their specific indicators
"""
from typing import Dict, List
from api.models.enums import Planet


# ============================================================================
# LIFE DOMAINS
# ============================================================================

LIFE_DOMAINS = [
    "Career / Work",
    "Wealth / Finance",
    "Health / Physical",
    "Relationships",
    "Learning / Growth",
    "Mental State",
    "Transformation / Uncertainty"
]


# ============================================================================
# DOMAIN TO HOUSE MAPPING
# ============================================================================

DOMAIN_HOUSE_MAPPING: Dict[str, Dict[str, any]] = {
    "Career / Work": {
        "primary_houses": [10],      # 10th house - Career, profession, status
        "secondary_houses": [6],      # 6th house - Daily work, service, competition
        "weights": {10: 0.7, 6: 0.3}
    },
    "Wealth / Finance": {
        "primary_houses": [2, 11],    # 2nd - Wealth/savings, 11th - Gains/income
        "secondary_houses": [9],      # 9th - Fortune, luck, prosperity
        "weights": {2: 0.4, 11: 0.4, 9: 0.2}
    },
    "Health / Physical": {
        "primary_houses": [1, 6],     # 1st - Physical body, 6th - Disease/health
        "secondary_houses": [8],      # 8th - Longevity, chronic issues
        "weights": {1: 0.5, 6: 0.3, 8: 0.2}
    },
    "Relationships": {
        "primary_houses": [7],        # 7th - Spouse, partnerships, marriage
        "secondary_houses": [5, 11],  # 5th - Romance/love, 11th - Social connections
        "weights": {7: 0.6, 5: 0.25, 11: 0.15}
    },
    "Learning / Growth": {
        "primary_houses": [5, 9],     # 5th - Education/creativity, 9th - Higher learning/wisdom
        "secondary_houses": [4],      # 4th - Knowledge base, foundational learning
        "weights": {5: 0.4, 9: 0.4, 4: 0.2}
    },
    "Mental State": {
        "primary_houses": [1, 4],     # 1st - Mind/consciousness, 4th - Emotions/inner peace
        "secondary_houses": [12],     # 12th - Subconscious, meditation, isolation
        "weights": {1: 0.4, 4: 0.4, 12: 0.2}
    },
    "Transformation / Uncertainty": {
        "primary_houses": [8, 12],    # 8th - Sudden events/transformation, 12th - Loss/endings
        "secondary_houses": [6],      # 6th - Obstacles, enemies, struggles
        "weights": {8: 0.5, 12: 0.3, 6: 0.2}
    }
}


# ============================================================================
# PLANET TO DOMAIN INFLUENCE (Natural Significations / Karakas)
# ============================================================================

PLANET_DOMAIN_INFLUENCE: Dict[str, Dict[str, float]] = {
    "Sun": {
        "Career / Work": 0.9,          # Authority, leadership, government, status
        "Health / Physical": 0.7,      # Vitality, life force, bones
        "Mental State": 0.6,           # Confidence, ego, self-esteem
        "Wealth / Finance": 0.4,       # Power brings wealth
    },
    "Moon": {
        "Mental State": 0.9,           # Emotions, mind, mental peace
        "Health / Physical": 0.6,      # Fluids, general health, immunity
        "Relationships": 0.5,          # Emotional connections, mother
        "Wealth / Finance": 0.3,       # Fluctuating finances
    },
    "Mars": {
        "Career / Work": 0.7,          # Energy, action, courage, competition
        "Health / Physical": 0.8,      # Stamina, injuries, blood, muscles
        "Transformation / Uncertainty": 0.6,  # Sudden events, accidents, conflicts
        "Relationships": 0.4,          # Passion, conflicts in relationships
    },
    "Mercury": {
        "Learning / Growth": 0.9,      # Intelligence, education, communication
        "Career / Work": 0.7,          # Business, trade, analytical work
        "Mental State": 0.7,           # Analytical thinking, logic, speech
        "Wealth / Finance": 0.6,       # Business acumen, trading
    },
    "Jupiter": {
        "Learning / Growth": 0.9,      # Wisdom, higher knowledge, philosophy
        "Wealth / Finance": 0.8,       # Prosperity, expansion, fortune
        "Relationships": 0.6,          # Marriage (for women), children
        "Career / Work": 0.5,          # Teaching, advisory roles
    },
    "Venus": {
        "Relationships": 0.9,          # Love, romance, spouse, harmony
        "Wealth / Finance": 0.7,       # Luxury, comforts, material gains
        "Mental State": 0.5,           # Happiness, contentment, pleasure
        "Learning / Growth": 0.4,      # Arts, creativity
    },
    "Saturn": {
        "Career / Work": 0.8,          # Hard work, discipline, service, labor
        "Transformation / Uncertainty": 0.7,  # Delays, obstacles, karmic lessons
        "Health / Physical": 0.6,      # Chronic issues, bones, teeth
        "Mental State": 0.5,           # Depression, anxiety, detachment
    },
    "Rahu": {
        "Transformation / Uncertainty": 0.9,  # Sudden changes, obsession, illusion
        "Career / Work": 0.6,          # Unconventional paths, foreign connections
        "Mental State": 0.7,           # Confusion, obsession, desires
        "Wealth / Finance": 0.5,       # Sudden gains/losses, speculation
    },
    "Ketu": {
        "Transformation / Uncertainty": 0.8,  # Detachment, loss, spiritual transformation
        "Learning / Growth": 0.7,      # Spiritual wisdom, intuition, moksha
        "Mental State": 0.6,           # Detachment, confusion, spirituality
        "Health / Physical": 0.4,      # Mysterious ailments
    }
}


# ============================================================================
# SUBDOMAIN MAPPING
# ============================================================================

SUBDOMAIN_MAPPING: Dict[str, Dict[str, any]] = {
    # Career / Work subdomains
    "job": {
        "houses": {10: 0.8, 6: 0.2},
        "planets": {Planet.SUN: 0.7, Planet.SATURN: 0.6, Planet.MERCURY: 0.5}
    },
    "promotion": {
        "houses": {10: 0.7, 11: 0.3},
        "planets": {Planet.SUN: 0.8, Planet.JUPITER: 0.7, Planet.MARS: 0.5}
    },
    "workload": {
        "houses": {6: 0.7, 10: 0.3},
        "planets": {Planet.MARS: 0.7, Planet.SATURN: 0.8}
    },
    "pressure": {
        "houses": {6: 0.6, 10: 0.4},
        "planets": {Planet.SATURN: 0.9, Planet.MARS: 0.6, Planet.RAHU: 0.5}
    },

    # Wealth / Finance subdomains
    "income": {
        "houses": {11: 0.7, 2: 0.3},
        "planets": {Planet.JUPITER: 0.8, Planet.MERCURY: 0.6, Planet.VENUS: 0.5}
    },
    "savings": {
        "houses": {2: 0.8, 11: 0.2},
        "planets": {Planet.JUPITER: 0.7, Planet.SATURN: 0.6, Planet.VENUS: 0.5}
    },
    "gains": {
        "houses": {11: 0.8, 9: 0.2},
        "planets": {Planet.JUPITER: 0.9, Planet.VENUS: 0.6, Planet.MERCURY: 0.5}
    },

    # Health / Physical subdomains
    "illness": {
        "houses": {6: 0.7, 8: 0.3},
        "planets": {Planet.SATURN: 0.7, Planet.MARS: 0.6, Planet.KETU: 0.4}
    },
    "recovery": {
        "houses": {1: 0.6, 6: 0.4},
        "planets": {Planet.SUN: 0.7, Planet.JUPITER: 0.6, Planet.MOON: 0.5}
    },
    "stamina": {
        "houses": {1: 0.7, 6: 0.3},
        "planets": {Planet.MARS: 0.8, Planet.SUN: 0.7, Planet.MOON: 0.4}
    },

    # Relationships subdomains
    "spouse": {
        "houses": {7: 0.9, 2: 0.1},
        "planets": {Planet.VENUS: 0.9, Planet.JUPITER: 0.6, Planet.MARS: 0.4}
    },
    "romance": {
        "houses": {5: 0.7, 7: 0.3},
        "planets": {Planet.VENUS: 0.9, Planet.MARS: 0.5, Planet.RAHU: 0.4}
    },
    "conflicts": {
        "houses": {7: 0.6, 6: 0.4},
        "planets": {Planet.MARS: 0.8, Planet.SATURN: 0.6, Planet.RAHU: 0.5}
    },

    # Learning / Growth subdomains
    "education": {
        "houses": {5: 0.6, 4: 0.4},
        "planets": {Planet.MERCURY: 0.9, Planet.JUPITER: 0.7, Planet.SUN: 0.4}
    },
    "wisdom": {
        "houses": {9: 0.8, 5: 0.2},
        "planets": {Planet.JUPITER: 0.9, Planet.KETU: 0.6, Planet.MERCURY: 0.5}
    },
    "luck": {
        "houses": {9: 0.7, 11: 0.3},
        "planets": {Planet.JUPITER: 0.9, Planet.VENUS: 0.5, Planet.MOON: 0.4}
    },

    # Mental State subdomains
    "stress": {
        "houses": {6: 0.5, 12: 0.3, 8: 0.2},
        "planets": {Planet.SATURN: 0.8, Planet.RAHU: 0.7, Planet.MARS: 0.5}
    },
    "clarity": {
        "houses": {1: 0.6, 4: 0.4},
        "planets": {Planet.MERCURY: 0.8, Planet.JUPITER: 0.7, Planet.SUN: 0.6}
    },
    "focus": {
        "houses": {1: 0.7, 5: 0.3},
        "planets": {Planet.MERCURY: 0.8, Planet.SATURN: 0.6, Planet.MARS: 0.5}
    },

    # Transformation / Uncertainty subdomains
    "sudden_change": {
        "houses": {8: 0.7, 12: 0.3},
        "planets": {Planet.RAHU: 0.9, Planet.KETU: 0.7, Planet.MARS: 0.5}
    },
    "instability": {
        "houses": {8: 0.5, 12: 0.3, 6: 0.2},
        "planets": {Planet.RAHU: 0.8, Planet.SATURN: 0.6, Planet.KETU: 0.5}
    },
}


# ============================================================================
# DOMAIN WEIGHTS
# ============================================================================

# Weight distribution between house activation and planet influence
DOMAIN_CALCULATION_WEIGHTS = {
    "house_weight": 0.6,      # 60% from house activation
    "planet_weight": 0.4      # 40% from planet influence
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_domain_houses(domain: str) -> List[int]:
    """Get all houses (primary + secondary) for a domain."""
    if domain not in DOMAIN_HOUSE_MAPPING:
        return []

    mapping = DOMAIN_HOUSE_MAPPING[domain]
    return mapping["primary_houses"] + mapping["secondary_houses"]


def get_domain_house_weight(domain: str, house: int) -> float:
    """Get the weight of a specific house for a domain."""
    if domain not in DOMAIN_HOUSE_MAPPING:
        return 0.0

    weights = DOMAIN_HOUSE_MAPPING[domain]["weights"]
    return weights.get(house, 0.0)


def get_planet_domain_influence(planet: Planet, domain: str) -> float:
    """Get the influence of a planet on a specific domain."""
    planet_str = planet.value if isinstance(planet, Planet) else str(planet)

    if planet_str not in PLANET_DOMAIN_INFLUENCE:
        return 0.0

    return PLANET_DOMAIN_INFLUENCE[planet_str].get(domain, 0.0)


def get_subdomain_parent(subdomain: str) -> str:
    """Get the parent domain for a subdomain."""
    subdomain_to_domain = {
        "job": "Career / Work",
        "promotion": "Career / Work",
        "workload": "Career / Work",
        "pressure": "Career / Work",
        "income": "Wealth / Finance",
        "savings": "Wealth / Finance",
        "gains": "Wealth / Finance",
        "illness": "Health / Physical",
        "recovery": "Health / Physical",
        "stamina": "Health / Physical",
        "spouse": "Relationships",
        "romance": "Relationships",
        "conflicts": "Relationships",
        "education": "Learning / Growth",
        "wisdom": "Learning / Growth",
        "luck": "Learning / Growth",
        "stress": "Mental State",
        "clarity": "Mental State",
        "focus": "Mental State",
        "sudden_change": "Transformation / Uncertainty",
        "instability": "Transformation / Uncertainty",
    }
    return subdomain_to_domain.get(subdomain, "")


