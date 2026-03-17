"""
Dasha period models for Vimshottari dasha system.
"""
from datetime import date as Date
from typing import Optional, Dict
from pydantic import BaseModel, Field
from .enums import Planet


class DashaPeriod(BaseModel):
    """Represents a single Vimshottari Dasha period."""
    planet: Planet = Field(..., description="Planet ruling this dasha period")
    start_date: Date = Field(..., description="Start date of this period")
    end_date: Date = Field(..., description="End date of this period")
    level: str = Field(..., description="Dasha level: 'mahadasha', 'antardasha', 'pratyantar', 'sookshma'")

    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Saturn",
                "start_date": "2020-01-01",
                "end_date": "2039-01-01",
                "level": "mahadasha"
            }
        }


class ActiveDashas(BaseModel):
    """Active dasha periods at a specific point in time."""
    date: Date = Field(..., description="Date for which dashas are calculated")
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
                "date": "2025-06-15",
                "mahadasha": {
                    "planet": "Saturn",
                    "start_date": "2020-01-01",
                    "end_date": "2039-01-01",
                    "level": "mahadasha"
                },
                "antardasha": {
                    "planet": "Mercury",
                    "start_date": "2024-12-01",
                    "end_date": "2027-06-01",
                    "level": "antardasha"
                },
                "pratyantar": {
                    "planet": "Mars",
                    "start_date": "2025-05-01",
                    "end_date": "2025-08-01",
                    "level": "pratyantar"
                }
            }
        }


class DashaWeight(BaseModel):
    """Dasha weight calculation for scoring."""
    planet: Planet = Field(..., description="Planet being scored")
    date: Date = Field(..., description="Date for calculation")

    # Active dashas
    mahadasha_planet: Planet = Field(..., description="Maha dasha lord")
    antardasha_planet: Planet = Field(..., description="Antar dasha lord")
    pratyantardasha_planet: Optional[Planet] = Field(None, description="Pratyantar dasha lord")
    sookshmadasha_planet: Optional[Planet] = Field(None, description="Sookshma dasha lord")

    # Individual scores (0-100)
    mahadasha_score: float = Field(..., ge=0, le=100, description="Maha dasha contribution")
    antardasha_score: float = Field(..., ge=0, le=100, description="Antar dasha contribution")
    pratyantardasha_score: float = Field(..., ge=0, le=100, description="Pratyantar dasha contribution")
    sookshmadasha_score: float = Field(..., ge=0, le=100, description="Sookshma dasha contribution")

    # Total weighted score
    total_weight: float = Field(..., ge=0, le=100, description="Total dasha weight (0-100)")

    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "date": "2026-03-17",
                "mahadasha_planet": "Ketu",
                "antardasha_planet": "Saturn",
                "pratyantardasha_planet": "Moon",
                "sookshmadasha_planet": None,
                "mahadasha_score": 0.0,
                "antardasha_score": 0.0,
                "pratyantardasha_score": 100.0,
                "sookshmadasha_score": 0.0,
                "total_weight": 20.0
            }
        }

