"""
Pipeline models for unified analysis responses.

This module defines comprehensive response models that combine
all analysis components into a single unified response.
"""
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from api.models.natal_chart import NatalChart
from api.models.scoring import PlanetScores
from api.models.house_activation import HouseActivationCalculation
from api.models.domain_analysis import DomainAnalysis, DomainTimeline


class AnalysisRequest(BaseModel):
    """Request for complete astrological analysis."""
    
    # Birth details (for chart generation or lookup)
    chart_id: Optional[str] = Field(None, description="Existing chart ID (if available)")
    name: Optional[str] = Field(None, description="Person's name")
    birth_date: Optional[str] = Field(None, description="Birth date (YYYY-MM-DD)")
    birth_time: Optional[str] = Field(None, description="Birth time (HH:MM)")
    latitude: Optional[float] = Field(None, description="Birth latitude")
    longitude: Optional[float] = Field(None, description="Birth longitude")
    timezone: Optional[str] = Field(None, description="Birth timezone")
    
    # Analysis parameters
    calculation_date: datetime = Field(
        default_factory=datetime.now,
        description="Date for current analysis"
    )
    
    # Timeline parameters
    include_timeline: bool = Field(True, description="Include timeline analysis")
    timeline_start: Optional[datetime] = Field(None, description="Timeline start date")
    timeline_end: Optional[datetime] = Field(None, description="Timeline end date")
    timeline_days: int = Field(90, description="Timeline duration in days (if start/end not specified)")
    
    # Analysis options
    include_subdomains: bool = Field(True, description="Include subdomain analysis")
    include_events: bool = Field(True, description="Include significant events")
    use_intelligent_segmentation: bool = Field(True, description="Use Moon/Sun transitions for timeline")


class AnalysisResponse(BaseModel):
    """Unified response containing all analysis results."""
    
    # Metadata
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date of analysis")
    generated_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when analysis was generated"
    )
    
    # Core data
    natal_chart: NatalChart = Field(..., description="Natal chart data")
    
    # Current state analysis
    current_planet_scores: PlanetScores = Field(
        ...,
        description="Planet scores at calculation date"
    )
    current_house_activation: HouseActivationCalculation = Field(
        ...,
        description="House activation at calculation date"
    )
    current_domain_analysis: DomainAnalysis = Field(
        ...,
        description="Domain analysis at calculation date"
    )
    
    # Timeline analysis (optional)
    domain_timeline: Optional[DomainTimeline] = Field(
        None,
        description="Domain scores over time"
    )
    
    # Summary insights
    summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="High-level summary and insights"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-22T00:00:00",
                "generated_at": "2026-03-22T10:30:00",
                "natal_chart": {"name": "John Doe", "...": "..."},
                "current_planet_scores": {"...": "..."},
                "current_house_activation": {"...": "..."},
                "current_domain_analysis": {"...": "..."},
                "domain_timeline": {"...": "..."},
                "summary": {
                    "overall_life_quality": 72.5,
                    "strongest_domain": "Career",
                    "weakest_domain": "Health",
                    "key_insights": [
                        "Saturn Mahadasha brings career focus",
                        "10th house highly activated"
                    ]
                }
            }
        }


class QuickAnalysisRequest(BaseModel):
    """Simplified request for quick analysis of existing chart."""
    
    chart_id: str = Field(..., description="Existing chart ID")
    calculation_date: Optional[datetime] = Field(
        None,
        description="Date for analysis (defaults to now)"
    )
    include_timeline: bool = Field(False, description="Include timeline (faster without)")
    timeline_days: int = Field(30, description="Timeline duration if included")


class QuickAnalysisResponse(BaseModel):
    """Simplified response for quick analysis."""
    
    chart_id: str
    calculation_date: datetime
    overall_life_quality: float = Field(..., description="Overall score 0-100")
    strongest_domain: str
    strongest_domain_score: float
    weakest_domain: str
    weakest_domain_score: float
    top_insights: List[str] = Field(..., description="Top 5 insights")
    domain_scores: Dict[str, float] = Field(..., description="All domain scores")

