"""
Dasha period models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .enums import Planet


class DashaPeriod(BaseModel):
    """Represents a Vimshottari Dasha period."""
    planet: Planet = Field(..., description="Planet ruling this dasha period")
    start_date: datetime = Field(..., description="Start date of this period")
    end_date: datetime = Field(..., description="End date of this period")
    level: str = Field(..., description="Dasha level: 'mahadasha', 'antardasha', 'pratyantar', 'sookshma'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Saturn",
                "start_date": "2020-01-01T00:00:00",
                "end_date": "2039-01-01T00:00:00",
                "level": "mahadasha"
            }
        }


class ActiveDashas(BaseModel):
    """Active dasha periods at a specific point in time."""
    date: datetime = Field(..., description="Date for which dashas are calculated")
    mahadasha: DashaPeriod = Field(..., description="Current Mahadasha")
    antardasha: DashaPeriod = Field(..., description="Current Antardasha")
    pratyantar: Optional[DashaPeriod] = Field(None, description="Current Pratyantar dasha")
    sookshma: Optional[DashaPeriod] = Field(None, description="Current Sookshma dasha")
    
    def get_dasha_planets(self) -> dict[str, Planet]:
        """Get planets for each dasha level."""
        return {
            "mahadasha": self.mahadasha.planet,
            "antardasha": self.antardasha.planet,
            "pratyantar": self.pratyantar.planet if self.pratyantar else None,
            "sookshma": self.sookshma.planet if self.sookshma else None,
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-06-15T00:00:00",
                "mahadasha": {
                    "planet": "Saturn",
                    "start_date": "2020-01-01T00:00:00",
                    "end_date": "2039-01-01T00:00:00",
                    "level": "mahadasha"
                },
                "antardasha": {
                    "planet": "Mercury",
                    "start_date": "2024-12-01T00:00:00",
                    "end_date": "2027-06-01T00:00:00",
                    "level": "antardasha"
                },
                "pratyantar": {
                    "planet": "Mars",
                    "start_date": "2025-05-01T00:00:00",
                    "end_date": "2025-08-01T00:00:00",
                    "level": "pratyantar"
                }
            }
        }

