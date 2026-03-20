"""
House Activation models for distributing planet scores to houses.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .enums import Planet


class HouseContribution(BaseModel):
    """Contribution breakdown for a single house from a planet."""
    house: int = Field(..., ge=1, le=12, description="House number (1-12)")
    transit_contribution: float = Field(0.0, description="Contribution from transit house (30%)")
    natal_contribution: float = Field(0.0, description="Contribution from natal placement (20%)")
    ownership_contribution: float = Field(0.0, description="Contribution from house ownership (30%)")
    aspect_contribution: float = Field(0.0, description="Contribution from aspects (20%)")
    total_contribution: float = Field(..., description="Total contribution to this house")
    
    class Config:
        json_schema_extra = {
            "example": {
                "house": 10,
                "transit_contribution": 4.5,
                "natal_contribution": 0.0,
                "ownership_contribution": 0.0,
                "aspect_contribution": 2.4,
                "total_contribution": 6.9
            }
        }


class PlanetHouseContributions(BaseModel):
    """All house contributions from a single planet."""
    planet: Planet = Field(..., description="The planet")
    planet_score: float = Field(..., ge=0, le=100, description="Planet's total score")
    contributions: Dict[int, HouseContribution] = Field(
        ...,
        description="Contributions to each house (house number -> contribution)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "planet_score": 15.8,
                "contributions": {
                    "1": {
                        "house": 1,
                        "transit_contribution": 0.0,
                        "natal_contribution": 3.16,
                        "ownership_contribution": 0.0,
                        "aspect_contribution": 0.0,
                        "total_contribution": 3.16
                    },
                    "10": {
                        "house": 10,
                        "transit_contribution": 4.74,
                        "natal_contribution": 0.0,
                        "ownership_contribution": 0.0,
                        "aspect_contribution": 1.58,
                        "total_contribution": 6.32
                    }
                }
            }
        }


class HouseActivation(BaseModel):
    """Activation score for a single house."""
    house: int = Field(..., ge=1, le=12, description="House number (1-12)")
    score: float = Field(..., ge=0, le=100, description="Final normalized activation score (0-100)")
    raw_score: float = Field(..., description="Raw score before normalization")
    contributors: Dict[Planet, float] = Field(
        default_factory=dict,
        description="Planet contributions to this house"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "house": 10,
                "score": 12.5,
                "raw_score": 28.4,
                "contributors": {
                    "Jupiter": 6.32,
                    "Saturn": 10.2,
                    "Sun": 8.5,
                    "Mars": 3.38
                }
            }
        }


class HouseActivationCalculation(BaseModel):
    """Complete house activation calculation for a chart."""
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date/time of calculation")
    house_activations: Dict[int, HouseActivation] = Field(
        ...,
        description="Activation scores for all houses (house number -> activation)"
    )
    planet_contributions: Dict[Planet, PlanetHouseContributions] = Field(
        ...,
        description="Detailed contributions from each planet"
    )
    
    def total_score(self) -> float:
        """Calculate total of all house scores (should be ~100)."""
        return sum(activation.score for activation in self.house_activations.values())
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-20T12:00:00",
                "house_activations": {
                    "1": {
                        "house": 1,
                        "score": 8.5,
                        "raw_score": 19.2,
                        "contributors": {
                            "Moon": 5.2,
                            "Jupiter": 3.16,
                            "Venus": 10.84
                        }
                    }
                },
                "planet_contributions": {
                    "Jupiter": {
                        "planet": "Jupiter",
                        "planet_score": 15.8,
                        "contributions": {}
                    }
                }
            }
        }


class HouseActivationRequest(BaseModel):
    """Request model for house activation calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date/time for calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-20T12:00:00"
            }
        }


class HouseActivationResponse(BaseModel):
    """Response model for house activation calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    house_activation: HouseActivationCalculation = Field(..., description="Complete house activation calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "house_activation": {
                    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                    "calculation_date": "2026-03-20T12:00:00",
                    "house_activations": {},
                    "planet_contributions": {}
                }
            }
        }

