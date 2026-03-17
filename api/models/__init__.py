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
from .dasha import DashaPeriod, ActiveDashas

# Transit data
from .transit import TransitData, TimeSegment

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
    # Transit
    "TransitData",
    "TimeSegment",
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

