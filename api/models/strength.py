"""
Strength calculation models for planet strength analysis.

Models for calculating planet strength based on:
- Dignity (exalted, own sign, friendly, etc.)
- Retrograde status
- Combustion (proximity to Sun)
"""
from typing import Dict, Optional
from pydantic import BaseModel, Field
from .enums import Planet, Dignity


class StrengthBreakdown(BaseModel):
    """Breakdown of strength components for a planet."""
    dignity: Dignity = Field(..., description="Planet's dignity in current sign")
    dignity_score: int = Field(..., description="Dignity score (-25 to +25)")
    is_retrograde: bool = Field(..., description="Whether planet is retrograde")
    retrograde_score: int = Field(..., description="Retrograde bonus (0 or +10)")
    is_combust: bool = Field(..., description="Whether planet is combust")
    combustion_score: int = Field(..., description="Combustion penalty (0 or -15)")
    total_strength: int = Field(..., description="Total strength score (S(p) = dignity + retrograde + combustion)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "dignity": "Exalted",
                "dignity_score": 25,
                "is_retrograde": True,
                "retrograde_score": 10,
                "is_combust": False,
                "combustion_score": 0,
                "total_strength": 35
            }
        }


class PlanetStrength(BaseModel):
    """Complete strength calculation for a single planet."""
    planet: Planet = Field(..., description="The planet")
    breakdown: StrengthBreakdown = Field(..., description="Strength component breakdown")
    strength_weight: float = Field(..., description="Normalized strength weight (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "breakdown": {
                    "dignity": "Exalted",
                    "dignity_score": 25,
                    "is_retrograde": True,
                    "retrograde_score": 10,
                    "is_combust": False,
                    "combustion_score": 0,
                    "total_strength": 35
                },
                "strength_weight": 85.0
            }
        }


class StrengthCalculation(BaseModel):
    """Complete strength calculation for all planets in a chart."""
    chart_id: str = Field(..., description="Chart identifier")
    planet_strengths: Dict[Planet, PlanetStrength] = Field(..., description="Strength for each planet")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "planet_strengths": {
                    "Jupiter": {
                        "planet": "Jupiter",
                        "breakdown": {
                            "dignity": "Exalted",
                            "dignity_score": 25,
                            "is_retrograde": True,
                            "retrograde_score": 10,
                            "is_combust": False,
                            "combustion_score": 0,
                            "total_strength": 35
                        },
                        "strength_weight": 85.0
                    },
                    "Mars": {
                        "planet": "Mars",
                        "breakdown": {
                            "dignity": "Own Sign",
                            "dignity_score": 20,
                            "is_retrograde": False,
                            "retrograde_score": 0,
                            "is_combust": True,
                            "combustion_score": -15,
                            "total_strength": 5
                        },
                        "strength_weight": 55.0
                    }
                }
            }
        }


class StrengthRequest(BaseModel):
    """Request model for strength calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"
            }
        }


class StrengthResponse(BaseModel):
    """Response model for strength calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    strengths: StrengthCalculation = Field(..., description="Complete strength calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "strengths": {
                    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                    "planet_strengths": {
                        "Jupiter": {
                            "planet": "Jupiter",
                            "breakdown": {
                                "dignity": "Exalted",
                                "dignity_score": 25,
                                "is_retrograde": True,
                                "retrograde_score": 10,
                                "is_combust": False,
                                "combustion_score": 0,
                                "total_strength": 35
                            },
                            "strength_weight": 85.0
                        }
                    }
                }
            }
        }

