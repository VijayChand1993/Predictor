"""
Final scoring result models.
"""
from datetime import datetime
from typing import Dict
from pydantic import BaseModel, Field
from .scoring import PlanetScore, HouseScore
from .enums import Planet


class TimeRange(BaseModel):
    """Time range for scoring calculation."""
    start: datetime = Field(..., description="Start date of the range")
    end: datetime = Field(..., description="End date of the range")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start": "2026-02-01T00:00:00",
                "end": "2026-02-28T23:59:59"
            }
        }


class ScoringResult(BaseModel):
    """
    Complete scoring result for a time range.
    Contains planet influence scores and house activation scores.
    """
    chart_id: str = Field(..., description="ID of the natal chart used")
    time_range: TimeRange = Field(..., description="Time range for this scoring")
    
    # Planet scores
    planet_scores: Dict[Planet, PlanetScore] = Field(
        ...,
        description="Planet influence scores, keyed by planet"
    )
    
    # House scores
    house_scores: Dict[int, HouseScore] = Field(
        ...,
        description="House activation scores, keyed by house number (1-12)"
    )
    
    # Metadata
    calculated_at: datetime = Field(
        default_factory=datetime.now,
        description="When this scoring was calculated"
    )
    
    def get_top_planets(self, n: int = 3) -> list[tuple[Planet, float]]:
        """Get top N most influential planets."""
        sorted_planets = sorted(
            [(p, score.score) for p, score in self.planet_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_planets[:n]
    
    def get_top_houses(self, n: int = 3) -> list[tuple[int, float]]:
        """Get top N most activated houses."""
        sorted_houses = sorted(
            [(h, score.score) for h, score in self.house_scores.items()],
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_houses[:n]
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "chart_123456",
                "time_range": {
                    "start": "2026-02-01T00:00:00",
                    "end": "2026-02-28T23:59:59"
                },
                "planet_scores": {
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
                "house_scores": {
                    "10": {
                        "house": 10,
                        "score": 28.0,
                        "contributors": {
                            "contributors": {
                                "Saturn": 10.2,
                                "Sun": 8.5
                            }
                        }
                    }
                },
                "calculated_at": "2026-01-15T10:30:00"
            }
        }

