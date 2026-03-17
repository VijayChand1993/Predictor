"""
Birth data models for natal chart generation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    """Geographic location for birth place."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    city: Optional[str] = Field(None, description="City name")
    country: Optional[str] = Field(None, description="Country name")
    timezone: str = Field(..., description="Timezone (e.g., 'Asia/Kolkata', 'America/New_York')")

    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 28.6139,
                "longitude": 77.2090,
                "city": "New Delhi",
                "country": "India",
                "timezone": "Asia/Kolkata"
            }
        }


class BirthData(BaseModel):
    """Complete birth data for natal chart generation."""
    date: datetime = Field(..., description="Birth date and time (UTC or local with timezone)")
    location: Location = Field(..., description="Birth location")
    name: Optional[str] = Field(None, description="Person's name")
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v: datetime) -> datetime:
        """Ensure date is not in the future."""
        if v > datetime.now():
            raise ValueError("Birth date cannot be in the future")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "date": "1990-01-15T10:30:00",
                "location": {
                    "latitude": 28.6139,
                    "longitude": 77.2090,
                    "city": "New Delhi",
                    "country": "India",
                    "timezone": "Asia/Kolkata"
                },
                "name": "John Doe"
            }
        }

