"""
Natal chart models.
"""
from typing import Optional, Dict
from pydantic import BaseModel, Field
from .birth_data import BirthData
from .planet_placement import PlanetPlacement
from .enums import Sign, Planet


class HouseInfo(BaseModel):
    """Information about a house in the natal chart."""
    house_number: int = Field(..., ge=1, le=12, description="House number (1-12)")
    sign: Sign = Field(..., description="Sign on the house cusp")
    degree: float = Field(..., ge=0, lt=30, description="Degree of the house cusp")
    lord: Planet = Field(..., description="Lord (ruler) of this house")
    
    class Config:
        json_schema_extra = {
            "example": {
                "house_number": 1,
                "sign": "Sagittarius",
                "degree": 10.5,
                "lord": "Jupiter"
            }
        }


class NatalChart(BaseModel):
    """Complete natal chart data."""
    chart_id: Optional[str] = Field(None, description="Unique identifier for this chart")
    birth_data: BirthData = Field(..., description="Birth information")
    
    # Ascendant (Lagna)
    ascendant_sign: Sign = Field(..., description="Ascendant (Lagna) sign")
    ascendant_degree: float = Field(..., ge=0, lt=30, description="Degree of ascendant")
    
    # Planet placements
    planets: Dict[Planet, PlanetPlacement] = Field(
        ..., 
        description="Dictionary of planet placements keyed by planet name"
    )
    
    # House information
    houses: Dict[int, HouseInfo] = Field(
        ...,
        description="Dictionary of house information keyed by house number (1-12)"
    )
    
    # Ashtakavarga points (optional, for advanced calculations)
    ashtakavarga: Optional[Dict[int, int]] = Field(
        None,
        description="Ashtakavarga points for each house (0-48 range)"
    )
    
    # Moon sign (Chandra Lagna)
    moon_sign: Sign = Field(..., description="Moon's sign (Chandra Lagna)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "chart_123456",
                "birth_data": {
                    "date": "1990-01-15T10:30:00",
                    "location": {
                        "latitude": 28.6139,
                        "longitude": 77.2090,
                        "city": "New Delhi",
                        "country": "India",
                        "timezone": "Asia/Kolkata"
                    },
                    "name": "John Doe"
                },
                "ascendant_sign": "Sagittarius",
                "ascendant_degree": 10.5,
                "moon_sign": "Cancer",
                "planets": {},
                "houses": {},
                "ashtakavarga": {
                    "1": 28, "2": 25, "3": 30, "4": 22,
                    "5": 35, "6": 20, "7": 27, "8": 18,
                    "9": 32, "10": 38, "11": 29, "12": 21
                }
            }
        }

