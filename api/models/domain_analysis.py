"""
Domain Analysis models for life domain scoring and analysis.
"""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
from .enums import Planet


class SubdomainScore(BaseModel):
    """Score for a specific subdomain."""
    subdomain: str = Field(..., description="Subdomain name (e.g., 'job', 'promotion')")
    score: float = Field(..., ge=0, le=100, description="Subdomain score (0-100)")
    house_contribution: float = Field(..., description="Contribution from house activation")
    planet_contribution: float = Field(..., description="Contribution from planet influence")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subdomain": "job",
                "score": 72.5,
                "house_contribution": 45.0,
                "planet_contribution": 27.5
            }
        }


class PlanetContribution(BaseModel):
    """Contribution of a planet to a domain."""
    planet: Planet = Field(..., description="The planet")
    planet_score: float = Field(..., ge=0, le=100, description="Planet's total score")
    influence: float = Field(..., ge=0, le=1, description="Planet's natural influence on this domain (0-1)")
    contribution: float = Field(..., description="Actual contribution (planet_score × influence)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "planet": "Jupiter",
                "planet_score": 65.5,
                "influence": 0.9,
                "contribution": 58.95
            }
        }


class DomainScore(BaseModel):
    """Score for a single life domain."""
    domain: str = Field(..., description="Domain name (e.g., 'Career / Work')")
    score: float = Field(..., ge=0, le=100, description="Final domain score (0-100)")
    house_contribution: float = Field(..., description="Contribution from house activation (60% weight)")
    planet_contribution: float = Field(..., description="Contribution from planet influence (40% weight)")
    driving_planets: List[PlanetContribution] = Field(
        default_factory=list,
        description="Top planets influencing this domain, sorted by contribution"
    )
    house_scores: Dict[int, float] = Field(
        default_factory=dict,
        description="Individual house activation scores contributing to this domain"
    )
    subdomains: Dict[str, SubdomainScore] = Field(
        default_factory=dict,
        description="Subdomain scores within this domain"
    )
    explanations: List[str] = Field(
        default_factory=list,
        description="Human-readable explanations for why this score is what it is"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "domain": "Career / Work",
                "score": 68.5,
                "house_contribution": 42.0,
                "planet_contribution": 26.5,
                "driving_planets": [
                    {
                        "planet": "Sun",
                        "planet_score": 75.0,
                        "influence": 0.9,
                        "contribution": 67.5
                    }
                ],
                "house_scores": {
                    "10": 60.0,
                    "6": 24.0
                },
                "subdomains": {
                    "job": {
                        "subdomain": "job",
                        "score": 72.5,
                        "house_contribution": 45.0,
                        "planet_contribution": 27.5
                    }
                }
            }
        }


class SignificantEvent(BaseModel):
    """Significant astrological event affecting domains."""
    date: datetime = Field(..., description="Date of the event")
    event_type: str = Field(..., description="Type of event (e.g., 'sign_change', 'retrograde', 'aspect')")
    description: str = Field(..., description="Human-readable description")
    planet: Optional[Planet] = Field(None, description="Planet involved in the event")
    affected_domains: List[str] = Field(
        default_factory=list,
        description="Life domains affected by this event"
    )
    impact_score: float = Field(..., ge=0, le=100, description="Estimated impact of the event (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-04-15T10:30:00",
                "event_type": "sign_change",
                "description": "Jupiter enters 10th house",
                "planet": "Jupiter",
                "affected_domains": ["Career / Work", "Wealth / Finance"],
                "impact_score": 75.0
            }
        }


class DomainAnalysis(BaseModel):
    """Complete domain analysis for a chart at a specific time."""
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date/time of calculation")
    domains: Dict[str, DomainScore] = Field(
        ...,
        description="Scores for all 7 life domains"
    )
    overall_life_quality: float = Field(..., ge=0, le=100, description="Average of all domain scores")
    strongest_domain: str = Field(..., description="Domain with highest score")
    weakest_domain: str = Field(..., description="Domain with lowest score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-20T12:00:00",
                "domains": {
                    "Career / Work": {
                        "domain": "Career / Work",
                        "score": 68.5,
                        "house_contribution": 42.0,
                        "planet_contribution": 26.5,
                        "driving_planets": [],
                        "house_scores": {},
                        "subdomains": {}
                    }
                },
                "overall_life_quality": 62.3,
                "strongest_domain": "Career / Work",
                "weakest_domain": "Transformation / Uncertainty"
            }
        }


class DomainTimePoint(BaseModel):
    """Domain scores at a specific point in time."""
    date: datetime = Field(..., description="Date/time of this data point")
    domains: Dict[str, float] = Field(..., description="Domain scores at this time (domain -> score)")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2026-03-20T12:00:00",
                "domains": {
                    "Career / Work": 68.5,
                    "Wealth / Finance": 55.2,
                    "Health / Physical": 72.0
                }
            }
        }


class DomainTimeline(BaseModel):
    """Timeline of domain scores over a period."""
    chart_id: str = Field(..., description="Chart identifier")
    start_date: datetime = Field(..., description="Start date of timeline")
    end_date: datetime = Field(..., description="End date of timeline")
    interval_days: int = Field(..., description="Interval between data points in days")
    timeline: List[DomainTimePoint] = Field(..., description="Domain scores at each time point")
    events: List[SignificantEvent] = Field(
        default_factory=list,
        description="Significant astrological events during this period"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "interval_days": 7,
                "timeline": [
                    {
                        "date": "2026-03-01T00:00:00",
                        "domains": {
                            "Career / Work": 65.0,
                            "Wealth / Finance": 52.0
                        }
                    }
                ],
                "events": []
            }
        }


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class DomainAnalysisRequest(BaseModel):
    """Request model for domain analysis calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    calculation_date: datetime = Field(..., description="Date/time for calculation")
    include_subdomains: bool = Field(
        default=True,
        description="Whether to include subdomain calculations"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "calculation_date": "2026-03-20T12:00:00",
                "include_subdomains": True
            }
        }


class DomainAnalysisResponse(BaseModel):
    """Response model for domain analysis calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    domain_analysis: DomainAnalysis = Field(..., description="Complete domain analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "domain_analysis": {
                    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                    "calculation_date": "2026-03-20T12:00:00",
                    "domains": {},
                    "overall_life_quality": 62.3,
                    "strongest_domain": "Career / Work",
                    "weakest_domain": "Transformation / Uncertainty"
                }
            }
        }


class DomainTimelineRequest(BaseModel):
    """Request model for domain timeline calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    start_date: datetime = Field(..., description="Start date of timeline")
    end_date: datetime = Field(..., description="End date of timeline")
    interval_days: int = Field(
        default=7,
        ge=1,
        le=30,
        description="Interval between data points in days (1-30)"
    )
    include_events: bool = Field(
        default=True,
        description="Whether to include significant astrological events"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "interval_days": 7,
                "include_events": True
            }
        }


class DomainTimelineResponse(BaseModel):
    """Response model for domain timeline calculation."""
    chart_id: str = Field(..., description="Chart identifier")
    timeline: DomainTimeline = Field(..., description="Domain timeline data")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "timeline": {
                    "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                    "start_date": "2026-03-01T00:00:00",
                    "end_date": "2026-03-31T23:59:59",
                    "interval_days": 7,
                    "timeline": [],
                    "events": []
                }
            }
        }


class DomainDetailRequest(BaseModel):
    """Request model for detailed domain analysis."""
    chart_id: str = Field(..., description="Chart identifier")
    domain: str = Field(..., description="Domain name to analyze")
    calculation_date: datetime = Field(..., description="Date/time for calculation")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "domain": "Career / Work",
                "calculation_date": "2026-03-20T12:00:00"
            }
        }


class DomainDetailResponse(BaseModel):
    """Response model for detailed domain analysis."""
    chart_id: str = Field(..., description="Chart identifier")
    domain_score: DomainScore = Field(..., description="Detailed domain score with subdomains")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "domain_score": {
                    "domain": "Career / Work",
                    "score": 68.5,
                    "house_contribution": 42.0,
                    "planet_contribution": 26.5,
                    "driving_planets": [],
                    "house_scores": {},
                    "subdomains": {}
                }
            }
        }

