"""
Timeline models for tracking scores over time ranges.
"""
from datetime import datetime
from typing import Dict, List
from pydantic import BaseModel, Field
from .enums import Planet
from .scoring import PlanetScore
from .house_activation import HouseActivation


class TimePoint(BaseModel):
    """A single point in time with associated scores."""
    timestamp: datetime = Field(..., description="Date/time of this data point")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-03-20T12:00:00"
            }
        }


class PlanetTimePoint(TimePoint):
    """Planet scores at a specific point in time."""
    planet: Planet = Field(..., description="The planet")
    score: float = Field(..., ge=0, le=100, description="Planet score at this time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-03-20T12:00:00",
                "planet": "Jupiter",
                "score": 15.8
            }
        }


class HouseTimePoint(TimePoint):
    """House activation at a specific point in time."""
    house: int = Field(..., ge=1, le=12, description="House number")
    score: float = Field(..., ge=0, le=100, description="House activation score at this time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2026-03-20T12:00:00",
                "house": 10,
                "score": 12.5
            }
        }


class PlanetTimeline(BaseModel):
    """Timeline of scores for a single planet."""
    planet: Planet = Field(..., description="The planet")
    data_points: List[PlanetTimePoint] = Field(..., description="Score data points over time")
    average_score: float = Field(..., description="Average score over the time range")
    peak_score: float = Field(..., description="Highest score in the time range")
    peak_time: datetime = Field(..., description="When the peak score occurred")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "data_points": [
                    {"timestamp": "2026-03-01T00:00:00", "planet": "Jupiter", "score": 14.2},
                    {"timestamp": "2026-03-15T00:00:00", "planet": "Jupiter", "score": 16.5}
                ],
                "average_score": 15.35,
                "peak_score": 16.5,
                "peak_time": "2026-03-15T00:00:00"
            }
        }


class HouseTimeline(BaseModel):
    """Timeline of activation scores for a single house."""
    house: int = Field(..., ge=1, le=12, description="House number")
    data_points: List[HouseTimePoint] = Field(..., description="Activation data points over time")
    average_score: float = Field(..., description="Average activation over the time range")
    peak_score: float = Field(..., description="Highest activation in the time range")
    peak_time: datetime = Field(..., description="When the peak activation occurred")
    
    class Config:
        json_schema_extra = {
            "example": {
                "house": 10,
                "data_points": [
                    {"timestamp": "2026-03-01T00:00:00", "house": 10, "score": 11.2},
                    {"timestamp": "2026-03-15T00:00:00", "house": 10, "score": 13.8}
                ],
                "average_score": 12.5,
                "peak_score": 13.8,
                "peak_time": "2026-03-15T00:00:00"
            }
        }


class PlanetInfluenceTimeline(BaseModel):
    """Complete timeline of planet influences over a time range."""
    chart_id: str = Field(..., description="Chart identifier")
    start_date: datetime = Field(..., description="Start of time range")
    end_date: datetime = Field(..., description="End of time range")
    timelines: Dict[Planet, PlanetTimeline] = Field(..., description="Timeline for each planet")
    
    def get_most_influential_planet(self) -> tuple[Planet, float]:
        """Get the planet with highest average score."""
        max_planet = max(
            self.timelines.items(),
            key=lambda x: x[1].average_score
        )
        return max_planet[0], max_planet[1].average_score
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "timelines": {
                    "Jupiter": {
                        "planet": "Jupiter",
                        "data_points": [],
                        "average_score": 15.35,
                        "peak_score": 16.5,
                        "peak_time": "2026-03-15T00:00:00"
                    }
                }
            }
        }


class HouseActivationTimeline(BaseModel):
    """Complete timeline of house activations over a time range."""
    chart_id: str = Field(..., description="Chart identifier")
    start_date: datetime = Field(..., description="Start of time range")
    end_date: datetime = Field(..., description="End of time range")
    timelines: Dict[int, HouseTimeline] = Field(..., description="Timeline for each house")
    
    def get_most_activated_house(self) -> tuple[int, float]:
        """Get the house with highest average activation."""
        max_house = max(
            self.timelines.items(),
            key=lambda x: x[1].average_score
        )
        return max_house[0], max_house[1].average_score
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "timelines": {
                    "10": {
                        "house": 10,
                        "data_points": [],
                        "average_score": 12.5,
                        "peak_score": 13.8,
                        "peak_time": "2026-03-15T00:00:00"
                    }
                }
            }
        }

