"""
Scoring models for planet and house influence.
"""
from datetime import datetime
from typing import Dict, Optional, List
from pydantic import BaseModel, Field
from .enums import Planet


class ComponentBreakdown(BaseModel):
    """Breakdown of scoring components for a planet.

    NOTE: Aspect component removed as it used static natal aspects which don't
    change over time and shouldn't be in a dynamic scoring model.
    """
    dasha: float = Field(..., description="Dasha contribution (0-100)")
    transit: float = Field(..., description="Transit contribution (0-100)")
    strength: float = Field(..., description="Planet strength contribution (0-100)")
    motion: float = Field(..., description="Motion/speed contribution (0-100)")

    class Config:
        json_schema_extra = {
            "example": {
                "dasha": 40,
                "transit": 80,
                "strength": 45,
                "motion": 50
            }
        }


class WeightedComponents(BaseModel):
    """Weighted components after applying final weights.

    NOTE: Aspect component removed. Weights redistributed:
    - Dasha: 0.40 (was 0.35, +0.05)
    - Transit: 0.30 (was 0.25, +0.05)
    - Strength: 0.22 (was 0.20, +0.02)
    - Motion: 0.08 (unchanged)
    """
    dasha: float = Field(..., description="Weighted dasha (0.40 × W_dasha)")
    transit: float = Field(..., description="Weighted transit (0.30 × W_transit)")
    strength: float = Field(..., description="Weighted strength (0.22 × W_strength)")
    motion: float = Field(..., description="Weighted motion (0.08 × W_motion)")

    def total(self) -> float:
        """Calculate total of all weighted components."""
        return self.dasha + self.transit + self.strength + self.motion

    class Config:
        json_schema_extra = {
            "example": {
                "dasha": 16.0,
                "transit": 24.0,
                "strength": 9.9,
                "motion": 4.0
            }
        }


class PlanetScore(BaseModel):
    """Score for a single planet with detailed breakdown."""
    planet: Planet = Field(..., description="The planet")
    score: float = Field(..., ge=0, le=100, description="Final normalized score (0-100)")
    breakdown: ComponentBreakdown = Field(..., description="Raw component scores")
    weighted_components: WeightedComponents = Field(..., description="Weighted component scores")
    explanations: List[str] = Field(
        default_factory=list,
        description="Human-readable explanations for this planet's score"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Saturn",
                "score": 34.5,
                "breakdown": {
                    "dasha": 40,
                    "transit": 80,
                    "strength": 45,
                    "aspect": 60,
                    "motion": 50
                },
                "weighted_components": {
                    "dasha": 14.0,
                    "transit": 20.0,
                    "strength": 9.0,
                    "aspect": 7.2,
                    "motion": 4.0
                }
            }
        }


class HouseContributors(BaseModel):
    """Breakdown of which planets contribute to a house's score."""
    contributors: Dict[Planet, float] = Field(
        default_factory=dict,
        description="Planet contributions to this house"
    )
    
    def total(self) -> float:
        """Calculate total contribution."""
        return sum(self.contributors.values())
    
    class Config:
        json_schema_extra = {
            "example": {
                "contributors": {
                    "Saturn": 10.2,
                    "Sun": 8.5,
                    "Mars": 6.8,
                    "Jupiter": 2.5
                }
            }
        }


class HouseScore(BaseModel):
    """Score for a single house with contributors."""
    house: int = Field(..., ge=1, le=12, description="House number (1-12)")
    score: float = Field(..., ge=0, le=100, description="Final normalized score (0-100)")
    contributors: HouseContributors = Field(..., description="Breakdown of planet contributions")

    class Config:
        json_schema_extra = {
            "example": {
                "house": 10,
                "score": 28.0,
                "contributors": {
                    "contributors": {
                        "Saturn": 10.2,
                        "Sun": 8.5,
                        "Mars": 6.8,
                        "Jupiter": 2.5
                    }
                }
            }
        }


class PlanetScores(BaseModel):
    """Collection of planet scores."""
    scores: Dict[Planet, PlanetScore] = Field(..., description="Scores for each planet")
    calculation_date: datetime = Field(..., description="Date/time of calculation")

    def total_score(self) -> float:
        """Calculate total of all planet scores (should be ~100)."""
        return sum(score.score for score in self.scores.values())

    class Config:
        json_schema_extra = {
            "example": {
                "scores": {
                    "Saturn": {
                        "planet": "Saturn",
                        "score": 34.5,
                        "breakdown": {
                            "dasha": 40,
                            "transit": 80,
                            "strength": 45,
                            "aspect": 60,
                            "motion": 50
                        },
                        "weighted_components": {
                            "dasha": 14.0,
                            "transit": 20.0,
                            "strength": 9.0,
                            "aspect": 7.2,
                            "motion": 4.0
                        }
                    }
                },
                "calculation_date": "2026-03-20T12:00:00"
            }
        }


class ScoringRequest(BaseModel):
    """Request model for planet scoring calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date/time for scoring calculation")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-20T12:00:00"
            }
        }


class ScoringResponse(BaseModel):
    """Response model for planet scoring calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    planet_scores: PlanetScores = Field(..., description="Complete planet scoring")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "planet_scores": {
                    "scores": {
                        "Saturn": {
                            "planet": "Saturn",
                            "score": 34.5,
                            "breakdown": {
                                "dasha": 40,
                                "transit": 80,
                                "strength": 45,
                                "aspect": 60,
                                "motion": 50
                            },
                            "weighted_components": {
                                "dasha": 14.0,
                                "transit": 20.0,
                                "strength": 9.0,
                                "aspect": 7.2,
                                "motion": 4.0
                            }
                        }
                    },
                    "calculation_date": "2026-03-20T12:00:00"
                }
            }
        }

