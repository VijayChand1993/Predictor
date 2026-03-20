"""
Aspect (Drishti) models for planetary aspects.
"""
from typing import List, Dict
from pydantic import BaseModel, Field
from .enums import Planet, AspectType


class Aspect(BaseModel):
    """Represents a single planetary aspect."""
    from_planet: Planet = Field(..., description="Planet casting the aspect")
    to_house: int = Field(..., ge=1, le=12, description="House being aspected")
    aspect_type: AspectType = Field(..., description="Type of aspect (Full, Special)")
    aspect_weight: float = Field(..., ge=0, le=1, description="Weight of the aspect (0-1)")
    house_weight: float = Field(..., ge=0, le=1, description="Weight of the aspected house")
    
    class Config:
        json_schema_extra = {
            "example": {
                "from_planet": "Jupiter",
                "to_house": 5,
                "aspect_type": "Special Jupiter",
                "aspect_weight": 0.8,
                "house_weight": 0.9
            }
        }


class PlanetAspects(BaseModel):
    """All aspects cast by a single planet."""
    planet: Planet = Field(..., description="The planet casting aspects")
    from_house: int = Field(..., ge=1, le=12, description="House the planet is placed in")
    aspects: List[Aspect] = Field(default_factory=list, description="List of aspects cast by this planet")
    aspect_weight: float = Field(..., ge=0, le=100, description="Total aspect weight (W_aspect)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "from_house": 1,
                "aspects": [
                    {
                        "from_planet": "Jupiter",
                        "to_house": 5,
                        "aspect_type": "Special Jupiter",
                        "aspect_weight": 0.8,
                        "house_weight": 0.9
                    },
                    {
                        "from_planet": "Jupiter",
                        "to_house": 7,
                        "aspect_type": "Full",
                        "aspect_weight": 1.0,
                        "house_weight": 1.0
                    },
                    {
                        "from_planet": "Jupiter",
                        "to_house": 9,
                        "aspect_type": "Special Jupiter",
                        "aspect_weight": 0.8,
                        "house_weight": 0.9
                    }
                ],
                "aspect_weight": 52.0
            }
        }


class AspectCalculation(BaseModel):
    """Complete aspect calculation for all planets in a chart."""
    chart_id: str = Field(..., description="Chart identifier")
    planet_aspects: Dict[Planet, PlanetAspects] = Field(
        default_factory=dict,
        description="Aspects for each planet"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "chart_123456",
                "planet_aspects": {
                    "Jupiter": {
                        "planet": "Jupiter",
                        "from_house": 1,
                        "aspects": [],
                        "aspect_weight": 52.0
                    },
                    "Saturn": {
                        "planet": "Saturn",
                        "from_house": 10,
                        "aspects": [],
                        "aspect_weight": 48.0
                    }
                }
            }
        }


class AspectRequest(BaseModel):
    """Request model for calculating aspects."""
    chart_id: str = Field(..., description="Chart identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"
            }
        }


class AspectResponse(BaseModel):
    """Response model for aspect calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    aspects: AspectCalculation = Field(..., description="Complete aspect calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "aspects": {
                    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                    "planet_aspects": {}
                }
            }
        }

