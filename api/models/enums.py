"""
Enums and constants for the astrology scoring engine.
"""
from enum import Enum


class Planet(str, Enum):
    """Vedic astrology planets (Grahas)."""
    SUN = "Sun"
    MOON = "Moon"
    MARS = "Mars"
    MERCURY = "Mercury"
    JUPITER = "Jupiter"
    VENUS = "Venus"
    SATURN = "Saturn"
    RAHU = "Rahu"
    KETU = "Ketu"


class Sign(str, Enum):
    """Zodiac signs (Rashis)."""
    ARIES = "Aries"
    TAURUS = "Taurus"
    GEMINI = "Gemini"
    CANCER = "Cancer"
    LEO = "Leo"
    VIRGO = "Virgo"
    LIBRA = "Libra"
    SCORPIO = "Scorpio"
    SAGITTARIUS = "Sagittarius"
    CAPRICORN = "Capricorn"
    AQUARIUS = "Aquarius"
    PISCES = "Pisces"


class Nakshatra(str, Enum):
    """27 Nakshatras."""
    ASHWINI = "Ashwini"
    BHARANI = "Bharani"
    KRITTIKA = "Krittika"
    ROHINI = "Rohini"
    MRIGASHIRA = "Mrigashira"
    ARDRA = "Ardra"
    PUNARVASU = "Punarvasu"
    PUSHYA = "Pushya"
    ASHLESHA = "Ashlesha"
    MAGHA = "Magha"
    PURVA_PHALGUNI = "Purva Phalguni"
    UTTARA_PHALGUNI = "Uttara Phalguni"
    HASTA = "Hasta"
    CHITRA = "Chitra"
    SWATI = "Swati"
    VISHAKHA = "Vishakha"
    ANURADHA = "Anuradha"
    JYESHTHA = "Jyeshtha"
    MULA = "Mula"
    PURVA_ASHADHA = "Purva Ashadha"
    UTTARA_ASHADHA = "Uttara Ashadha"
    SHRAVANA = "Shravana"
    DHANISHTA = "Dhanishta"
    SHATABHISHA = "Shatabhisha"
    PURVA_BHADRAPADA = "Purva Bhadrapada"
    UTTARA_BHADRAPADA = "Uttara Bhadrapada"
    REVATI = "Revati"


class Dignity(str, Enum):
    """Planet dignity (strength based on sign placement)."""
    EXALTED = "Exalted"
    OWN_SIGN = "Own Sign"
    MOOLATRIKONA = "Moolatrikona"
    FRIENDLY = "Friendly"
    NEUTRAL = "Neutral"
    ENEMY = "Enemy"
    DEBILITATED = "Debilitated"


class AspectType(str, Enum):
    """Types of planetary aspects (Drishti)."""
    FULL = "Full"  # 7th house aspect (all planets)
    SPECIAL_MARS = "Special Mars"  # 4th, 8th aspects
    SPECIAL_JUPITER = "Special Jupiter"  # 5th, 9th aspects
    SPECIAL_SATURN = "Special Saturn"  # 3rd, 10th aspects


class MotionType(str, Enum):
    """Planet motion classification."""
    FAST = "Fast"
    NORMAL = "Normal"
    SLOW = "Slow"
    STATIONARY = "Stationary"
    RETROGRADE = "Retrograde"


class HouseType(str, Enum):
    """House classification."""
    KENDRA = "Kendra"  # 1, 4, 7, 10
    TRIKONA = "Trikona"  # 1, 5, 9
    UPACHAYA = "Upachaya"  # 3, 6, 10, 11
    DUSTHANA = "Dusthana"  # 6, 8, 12
    OTHER = "Other"


# House numbers (1-12)
HOUSES = list(range(1, 13))

# Dignity scores (from scoreLogic.md)
DIGNITY_SCORES = {
    Dignity.EXALTED: 25,
    Dignity.OWN_SIGN: 20,
    Dignity.MOOLATRIKONA: 20,
    Dignity.FRIENDLY: 10,
    Dignity.NEUTRAL: 0,
    Dignity.ENEMY: -10,
    Dignity.DEBILITATED: -25,
}

# Motion modifiers (from scoreLogic.md)
MOTION_MODIFIERS = {
    MotionType.FAST: 10,
    MotionType.STATIONARY: 15,
    MotionType.SLOW: 5,
    MotionType.NORMAL: 0,
    MotionType.RETROGRADE: 10,  # Retrograde bonus
}

# Combustion penalty
COMBUSTION_PENALTY = -15

# Aspect weights
ASPECT_WEIGHTS = {
    AspectType.FULL: 1.0,
    AspectType.SPECIAL_MARS: 0.8,
    AspectType.SPECIAL_JUPITER: 0.8,
    AspectType.SPECIAL_SATURN: 0.8,
}

