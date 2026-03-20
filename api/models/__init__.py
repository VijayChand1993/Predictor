"""
Data models for the astrology scoring engine.
"""

# Enums and constants
from .enums import (
    Planet,
    Sign,
    Nakshatra,
    Dignity,
    AspectType,
    MotionType,
    HouseType,
    HOUSES,
    DIGNITY_SCORES,
    MOTION_MODIFIERS,
    COMBUSTION_PENALTY,
    ASPECT_WEIGHTS,
)

# Birth data
from .birth_data import Location, BirthData

# Planet placements
from .planet_placement import PlanetPlacement, TransitPlacement

# Natal chart
from .natal_chart import HouseInfo, NatalChart

# Dasha periods
from .dasha import DashaPeriod, ActiveDashas, DashaWeight

# Transit data
from .transit import TransitData, TimeSegment

# Aspect data
from .aspect import Aspect, PlanetAspects, AspectCalculation, AspectRequest, AspectResponse

# Strength data
from .strength import StrengthBreakdown, PlanetStrength, StrengthCalculation, StrengthRequest, StrengthResponse

# Motion data
from .motion import MotionBreakdown, PlanetMotion, MotionCalculation, MotionRequest, MotionResponse

# Scoring
from .scoring import (
    ComponentBreakdown,
    WeightedComponents,
    PlanetScore,
    HouseContributors,
    HouseScore,
)

# Results
from .result import TimeRange, ScoringResult

__all__ = [
    # Enums
    "Planet",
    "Sign",
    "Nakshatra",
    "Dignity",
    "AspectType",
    "MotionType",
    "HouseType",
    "HOUSES",
    "DIGNITY_SCORES",
    "MOTION_MODIFIERS",
    "COMBUSTION_PENALTY",
    "ASPECT_WEIGHTS",
    # Birth data
    "Location",
    "BirthData",
    # Planet placements
    "PlanetPlacement",
    "TransitPlacement",
    # Natal chart
    "HouseInfo",
    "NatalChart",
    # Dasha
    "DashaPeriod",
    "ActiveDashas",
    "DashaWeight",
    # Transit
    "TransitData",
    "TimeSegment",
    # Aspect
    "Aspect",
    "PlanetAspects",
    "AspectCalculation",
    "AspectRequest",
    "AspectResponse",
    # Strength
    "StrengthBreakdown",
    "PlanetStrength",
    "StrengthCalculation",
    "StrengthRequest",
    "StrengthResponse",
    # Motion
    "MotionBreakdown",
    "PlanetMotion",
    "MotionCalculation",
    "MotionRequest",
    "MotionResponse",
    # Scoring
    "ComponentBreakdown",
    "WeightedComponents",
    "PlanetScore",
    "HouseContributors",
    "HouseScore",
    # Results
    "TimeRange",
    "ScoringResult",
]

