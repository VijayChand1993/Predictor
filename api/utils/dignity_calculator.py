"""
Utility for calculating planet dignity based on sign placement.

This module provides Vedic astrology dignity calculations including:
- Exaltation and debilitation
- Own sign (rulership)
- Moolatrikona
- Friendship and enmity
"""
from typing import Dict, Tuple
from api.models.enums import Planet, Sign, Dignity


# Exaltation and Debilitation tables
# Format: {Planet: (exaltation_sign, debilitation_sign)}
EXALTATION_DEBILITATION: Dict[Planet, Tuple[Sign, Sign]] = {
    Planet.SUN: (Sign.ARIES, Sign.LIBRA),
    Planet.MOON: (Sign.TAURUS, Sign.SCORPIO),
    Planet.MARS: (Sign.CAPRICORN, Sign.CANCER),
    Planet.MERCURY: (Sign.VIRGO, Sign.PISCES),
    Planet.JUPITER: (Sign.CANCER, Sign.CAPRICORN),
    Planet.VENUS: (Sign.PISCES, Sign.VIRGO),
    Planet.SATURN: (Sign.LIBRA, Sign.ARIES),
    # Rahu and Ketu don't have traditional exaltation/debilitation
    # Some schools use Gemini/Sagittarius, but we'll use None
    Planet.RAHU: (Sign.GEMINI, Sign.SAGITTARIUS),  # Optional
    Planet.KETU: (Sign.SAGITTARIUS, Sign.GEMINI),  # Optional
}

# Own Sign (Rulership) tables
# Format: {Planet: [list of signs ruled]}
OWN_SIGNS: Dict[Planet, list[Sign]] = {
    Planet.SUN: [Sign.LEO],
    Planet.MOON: [Sign.CANCER],
    Planet.MARS: [Sign.ARIES, Sign.SCORPIO],
    Planet.MERCURY: [Sign.GEMINI, Sign.VIRGO],
    Planet.JUPITER: [Sign.SAGITTARIUS, Sign.PISCES],
    Planet.VENUS: [Sign.TAURUS, Sign.LIBRA],
    Planet.SATURN: [Sign.CAPRICORN, Sign.AQUARIUS],
    Planet.RAHU: [],  # Shadow planet, no rulership
    Planet.KETU: [],  # Shadow planet, no rulership
}

# Moolatrikona signs
# Format: {Planet: moolatrikona_sign}
MOOLATRIKONA: Dict[Planet, Sign] = {
    Planet.SUN: Sign.LEO,
    Planet.MOON: Sign.TAURUS,
    Planet.MARS: Sign.ARIES,
    Planet.MERCURY: Sign.VIRGO,
    Planet.JUPITER: Sign.SAGITTARIUS,
    Planet.VENUS: Sign.LIBRA,
    Planet.SATURN: Sign.AQUARIUS,
    # Rahu and Ketu don't have moolatrikona
}

# Friendship tables
# Format: {Planet: {"friends": [...], "enemies": [...], "neutrals": [...]}}
RELATIONSHIPS: Dict[Planet, Dict[str, list[Sign]]] = {
    Planet.SUN: {
        "friends": [Sign.ARIES, Sign.LEO, Sign.SAGITTARIUS, Sign.SCORPIO],  # Mars, Jupiter, Moon (partial)
        "enemies": [Sign.LIBRA, Sign.AQUARIUS, Sign.CAPRICORN],  # Venus, Saturn
        "neutrals": [Sign.GEMINI, Sign.VIRGO],  # Mercury
    },
    Planet.MOON: {
        "friends": [Sign.CANCER, Sign.LEO, Sign.TAURUS, Sign.LIBRA],  # Sun, Mercury (partial), Venus (partial)
        "enemies": [],  # Moon has no enemies
        "neutrals": [Sign.ARIES, Sign.SCORPIO, Sign.SAGITTARIUS, Sign.PISCES, Sign.CAPRICORN, Sign.AQUARIUS],
    },
    Planet.MARS: {
        "friends": [Sign.LEO, Sign.CANCER, Sign.SAGITTARIUS, Sign.PISCES],  # Sun, Moon, Jupiter
        "enemies": [Sign.GEMINI, Sign.VIRGO],  # Mercury
        "neutrals": [Sign.TAURUS, Sign.LIBRA, Sign.CAPRICORN, Sign.AQUARIUS],  # Venus, Saturn
    },
    Planet.MERCURY: {
        "friends": [Sign.LEO, Sign.TAURUS, Sign.LIBRA],  # Sun, Venus
        "enemies": [Sign.CANCER],  # Moon
        "neutrals": [Sign.ARIES, Sign.SCORPIO, Sign.SAGITTARIUS, Sign.PISCES, Sign.CAPRICORN, Sign.AQUARIUS],
    },
    Planet.JUPITER: {
        "friends": [Sign.LEO, Sign.CANCER, Sign.ARIES, Sign.SCORPIO],  # Sun, Moon, Mars
        "enemies": [Sign.GEMINI, Sign.VIRGO, Sign.TAURUS, Sign.LIBRA],  # Mercury, Venus
        "neutrals": [Sign.CAPRICORN, Sign.AQUARIUS],  # Saturn
    },
    Planet.VENUS: {
        "friends": [Sign.GEMINI, Sign.VIRGO, Sign.CAPRICORN, Sign.AQUARIUS],  # Mercury, Saturn
        "enemies": [Sign.LEO, Sign.CANCER, Sign.ARIES, Sign.SCORPIO],  # Sun, Moon, Mars (partial)
        "neutrals": [Sign.SAGITTARIUS, Sign.PISCES],  # Jupiter
    },
    Planet.SATURN: {
        "friends": [Sign.GEMINI, Sign.VIRGO, Sign.TAURUS, Sign.LIBRA],  # Mercury, Venus
        "enemies": [Sign.LEO, Sign.CANCER, Sign.ARIES, Sign.SCORPIO],  # Sun, Moon, Mars
        "neutrals": [Sign.SAGITTARIUS, Sign.PISCES],  # Jupiter
    },
    # Rahu and Ketu use simplified relationships
    Planet.RAHU: {
        "friends": [Sign.GEMINI, Sign.VIRGO, Sign.TAURUS, Sign.LIBRA, Sign.CAPRICORN, Sign.AQUARIUS],
        "enemies": [Sign.LEO, Sign.CANCER],
        "neutrals": [Sign.ARIES, Sign.SCORPIO, Sign.SAGITTARIUS, Sign.PISCES],
    },
    Planet.KETU: {
        "friends": [Sign.ARIES, Sign.SCORPIO, Sign.SAGITTARIUS, Sign.PISCES],
        "enemies": [Sign.GEMINI, Sign.VIRGO],
        "neutrals": [Sign.TAURUS, Sign.LIBRA, Sign.CANCER, Sign.LEO, Sign.CAPRICORN, Sign.AQUARIUS],
    },
}


def calculate_dignity(planet: Planet, sign: Sign) -> Dignity:
    """
    Calculate the dignity of a planet in a given sign.
    
    Priority order:
    1. Exaltation
    2. Debilitation
    3. Own Sign
    4. Moolatrikona (subset of Own Sign)
    5. Friendly
    6. Enemy
    7. Neutral (default)
    
    Args:
        planet: The planet
        sign: The sign the planet is in
        
    Returns:
        Dignity enum value
    """
    # Check exaltation
    if planet in EXALTATION_DEBILITATION:
        exalt_sign, debil_sign = EXALTATION_DEBILITATION[planet]
        if sign == exalt_sign:
            return Dignity.EXALTED
        if sign == debil_sign:
            return Dignity.DEBILITATED
    
    # Check own sign
    if planet in OWN_SIGNS and sign in OWN_SIGNS[planet]:
        # Check if it's also moolatrikona
        if planet in MOOLATRIKONA and sign == MOOLATRIKONA[planet]:
            return Dignity.MOOLATRIKONA
        return Dignity.OWN_SIGN
    
    # Check friendship
    if planet in RELATIONSHIPS:
        relationships = RELATIONSHIPS[planet]
        if sign in relationships["friends"]:
            return Dignity.FRIENDLY
        if sign in relationships["enemies"]:
            return Dignity.ENEMY
    
    # Default to neutral
    return Dignity.NEUTRAL

