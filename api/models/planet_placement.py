"""
Planet placement models.
"""
from typing import Optional
from pydantic import BaseModel, Field
from .enums import Planet, Sign, Nakshatra, Dignity, MotionType


class PlanetPlacement(BaseModel):
    """Represents a planet's placement in the natal chart."""
    planet: Planet = Field(..., description="The planet")
    sign: Sign = Field(..., description="Zodiac sign the planet is in")
    house: int = Field(..., ge=1, le=12, description="House number (1-12)")
    degree: float = Field(..., ge=0, lt=30, description="Degree within the sign (0-30)")
    nakshatra: Optional[Nakshatra] = Field(None, description="Nakshatra (lunar mansion)")
    nakshatra_pada: Optional[int] = Field(None, ge=1, le=4, description="Nakshatra pada (1-4)")
    dignity: Optional[Dignity] = Field(None, description="Planet's dignity in this sign")
    is_retrograde: bool = Field(False, description="Whether the planet is retrograde")
    is_combust: bool = Field(False, description="Whether the planet is combust (too close to Sun)")
    
    # Lordship information
    rules_houses: list[int] = Field(default_factory=list, description="Houses this planet rules")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "sign": "Sagittarius",
                "house": 1,
                "degree": 15.5,
                "nakshatra": "Mula",
                "nakshatra_pada": 2,
                "dignity": "Own Sign",
                "is_retrograde": False,
                "is_combust": False,
                "rules_houses": [1, 4]
            }
        }


class TransitPlacement(BaseModel):
    """Represents a planet's transit position at a specific time."""
    planet: Planet = Field(..., description="The planet")
    sign: Sign = Field(..., description="Zodiac sign the planet is transiting")
    house: int = Field(..., ge=1, le=12, description="House number relative to natal chart")
    degree: float = Field(..., ge=0, lt=30, description="Degree within the sign")
    is_retrograde: bool = Field(False, description="Whether the planet is retrograde")
    speed: float = Field(..., description="Planet's speed in degrees per day")
    motion_type: MotionType = Field(..., description="Classification of planet's motion")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Moon",
                "sign": "Cancer",
                "house": 4,
                "degree": 12.3,
                "is_retrograde": False,
                "speed": 13.2,
                "motion_type": "Fast"
            }
        }

