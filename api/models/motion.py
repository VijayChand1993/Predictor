"""
Motion calculation models for planet speed and motion analysis.

Models for calculating planet motion based on:
- Speed (degrees per day)
- Motion classification (fast, normal, slow, stationary, retrograde)
- Motion modifiers for dynamic planets
"""
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .enums import Planet, MotionType


class MotionBreakdown(BaseModel):
    """Breakdown of motion components for a planet."""
    speed: float = Field(..., description="Planet's speed in degrees per day")
    motion_type: MotionType = Field(..., description="Classification of planet's motion")
    motion_modifier: int = Field(..., description="Motion modifier score (0 to +15)")
    is_significant: bool = Field(..., description="Whether motion is significant for this planet")
    
    class Config:
        json_schema_extra = {
            "example": {
                "speed": 13.2,
                "motion_type": "Fast",
                "motion_modifier": 10,
                "is_significant": True
            }
        }


class PlanetMotion(BaseModel):
    """Complete motion calculation for a single planet."""
    planet: Planet = Field(..., description="The planet")
    breakdown: MotionBreakdown = Field(..., description="Motion component breakdown")
    motion_weight: float = Field(..., description="Normalized motion weight (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Moon",
                "breakdown": {
                    "speed": 13.2,
                    "motion_type": "Fast",
                    "motion_modifier": 10,
                    "is_significant": True
                },
                "motion_weight": 60.0
            }
        }


class MotionCalculation(BaseModel):
    """Complete motion calculation for all planets at a specific time."""
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date/time of motion calculation")
    planet_motions: Dict[Planet, PlanetMotion] = Field(..., description="Motion for each planet")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-20T12:00:00",
                "planet_motions": {
                    "Moon": {
                        "planet": "Moon",
                        "breakdown": {
                            "speed": 13.2,
                            "motion_type": "Fast",
                            "motion_modifier": 10,
                            "is_significant": True
                        },
                        "motion_weight": 60.0
                    },
                    "Jupiter": {
                        "planet": "Jupiter",
                        "breakdown": {
                            "speed": 0.12,
                            "motion_type": "Normal",
                            "motion_modifier": 0,
                            "is_significant": False
                        },
                        "motion_weight": 50.0
                    }
                }
            }
        }


class MotionRequest(BaseModel):
    """Request model for motion calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date/time for motion calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-20T12:00:00"
            }
        }


class MotionResponse(BaseModel):
    """Response model for motion calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    motions: MotionCalculation = Field(..., description="Complete motion calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "motions": {
                    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                    "calculation_date": "2026-03-20T12:00:00",
                    "planet_motions": {
                        "Moon": {
                            "planet": "Moon",
                            "breakdown": {
                                "speed": 13.2,
                                "motion_type": "Fast",
                                "motion_modifier": 10,
                                "is_significant": True
                            },
                            "motion_weight": 60.0
                        }
                    }
                }
            }
        }

