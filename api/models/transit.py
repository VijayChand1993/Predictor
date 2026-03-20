"""
Transit data models.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .planet_placement import TransitPlacement
from .enums import Planet


class TransitData(BaseModel):
    """Planetary positions at a specific date/time."""
    date: datetime = Field(..., description="Date and time of transit")
    planets: Dict[Planet, TransitPlacement] = Field(
        ...,
        description="Dictionary of transit placements keyed by planet"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-02-15T12:00:00",
                "planets": {
                    "Sun": {
                        "planet": "Sun",
                        "sign": "Aquarius",
                        "house": 3,
                        "degree": 2.5,
                        "is_retrograde": False,
                        "speed": 1.0,
                        "motion_type": "Normal"
                    },
                    "Moon": {
                        "planet": "Moon",
                        "sign": "Cancer",
                        "house": 8,
                        "degree": 15.3,
                        "is_retrograde": False,
                        "speed": 13.2,
                        "motion_type": "Fast"
                    }
                }
            }
        }


class TimeSegment(BaseModel):
    """
    A time segment with constant planetary positions.
    Used for efficient scoring calculations.
    """
    start_date: datetime = Field(..., description="Start of this segment")
    end_date: datetime = Field(..., description="End of this segment")
    transit_data: TransitData = Field(..., description="Transit positions during this segment")
    sign_changes: Optional[List[Planet]] = Field(
        None,
        description="List of planets that changed signs at the start of this segment"
    )

    @property
    def duration_days(self) -> float:
        """Calculate duration in days."""
        delta = self.end_date - self.start_date
        return delta.total_seconds() / 86400

    class Config:
        json_schema_extra = {
            "example": {
                "start_date": "2026-02-01T00:00:00",
                "end_date": "2026-02-03T14:30:00",
                "duration_days": 2.604,
                "transit_data": {
                    "date": "2026-02-01T00:00:00",
                    "planets": {}
                },
                "sign_changes": ["Moon", "Mars"]
            }
        }

