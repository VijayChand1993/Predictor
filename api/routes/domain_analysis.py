"""
Domain Analysis API routes.

Endpoints for calculating and retrieving life domain scores and analysis.
"""
from fastapi import APIRouter, HTTPException, Depends, Path as PathParam, Query
from datetime import datetime, timedelta
from typing import List
from api.models.domain_analysis import (
    DomainAnalysisRequest,
    DomainAnalysisResponse,
    DomainTimelineRequest,
    DomainTimelineResponse,
    DomainDetailRequest,
    DomainDetailResponse,
    SignificantEvent
)
from api.services.domain_service import DomainService
from api.services.scoring_engine import ScoringEngine
from api.services.house_activation_service import HouseActivationService
from api.services.natal_chart_service import NatalChartService


router = APIRouter(
    prefix="/domain-analysis",
    tags=["Domain Analysis"],
    responses={404: {"description": "Not found"}}
)


# Dependency injection
def get_domain_service() -> DomainService:
    """Get domain service instance."""
    natal_chart_service = NatalChartService()
    scoring_engine = ScoringEngine()  # No parameters needed
    house_activation_service = HouseActivationService()  # No parameters needed
    return DomainService(scoring_engine, house_activation_service)


@router.post(
    "/calculate",
    response_model=DomainAnalysisResponse,
    summary="Calculate Domain Analysis",
    description="""
    Calculate life domain scores for a specific date.
    
    Returns scores for all 7 life domains:
    - Career / Work
    - Wealth / Finance
    - Health / Physical
    - Relationships
    - Learning / Growth
    - Mental State
    - Transformation / Uncertainty
    
    Each domain score is calculated by combining:
    - House activation (60% weight)
    - Planet influence (40% weight)
    """
)
async def calculate_domain_analysis(
    request: DomainAnalysisRequest,
    domain_service: DomainService = Depends(get_domain_service)
) -> DomainAnalysisResponse:
    """
    Calculate domain analysis for a chart at a specific date.
    
    Args:
        request: Domain analysis request with chart_id and calculation_date
        domain_service: Injected domain service
    
    Returns:
        DomainAnalysisResponse with all domain scores
    
    Raises:
        HTTPException: If chart not found or calculation fails
    """
    try:
        domain_analysis = domain_service.calculate_all_domains(
            chart_id=request.chart_id,
            calculation_date=request.calculation_date,
            include_subdomains=request.include_subdomains
        )
        
        return DomainAnalysisResponse(
            chart_id=request.chart_id,
            domain_analysis=domain_analysis
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Domain analysis calculation failed: {str(e)}")


@router.post(
    "/timeline",
    response_model=DomainTimelineResponse,
    summary="Get Domain Timeline",
    description="""
    Get domain scores over a time period.
    
    Returns timeline data showing how each domain score changes over time,
    along with significant astrological events that may affect the domains.
    """
)
async def get_domain_timeline(
    request: DomainTimelineRequest,
    domain_service: DomainService = Depends(get_domain_service)
) -> DomainTimelineResponse:
    """
    Get domain timeline for a chart over a date range.
    
    Args:
        request: Timeline request with chart_id, date range, and interval
        domain_service: Injected domain service
    
    Returns:
        DomainTimelineResponse with timeline data
    
    Raises:
        HTTPException: If chart not found or calculation fails
    """
    try:
        timeline = domain_service.calculate_domain_timeline(
            chart_id=request.chart_id,
            start_date=request.start_date,
            end_date=request.end_date,
            interval_days=request.interval_days,
            include_events=request.include_events
        )
        
        return DomainTimelineResponse(
            chart_id=request.chart_id,
            timeline=timeline
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline calculation failed: {str(e)}")


@router.post(
    "/domain-detail",
    response_model=DomainDetailResponse,
    summary="Get Detailed Domain Analysis",
    description="""
    Get detailed analysis for a specific domain.
    
    Returns:
    - Domain score with breakdown
    - Subdomain scores (e.g., for Career: job, promotion, workload, pressure)
    - Driving planets (which planets influence this domain most)
    - House contributions
    """
)
async def get_domain_detail(
    request: DomainDetailRequest,
    domain_service: DomainService = Depends(get_domain_service)
) -> DomainDetailResponse:
    """
    Get detailed analysis for a specific domain.
    
    Args:
        request: Domain detail request
        domain_service: Injected domain service
    
    Returns:
        DomainDetailResponse with detailed domain score
    
    Raises:
        HTTPException: If chart not found or domain invalid
    """
    try:
        # Calculate all domains first
        domain_analysis = domain_service.calculate_all_domains(
            chart_id=request.chart_id,
            calculation_date=request.calculation_date,
            include_subdomains=True
        )
        
        # Extract the requested domain
        if request.domain not in domain_analysis.domains:
            raise ValueError(f"Invalid domain: {request.domain}")
        
        domain_score = domain_analysis.domains[request.domain]
        
        return DomainDetailResponse(
            chart_id=request.chart_id,
            domain_score=domain_score
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Domain detail calculation failed: {str(e)}")


@router.get(
    "/{chart_id}/events",
    response_model=List[SignificantEvent],
    summary="Get Significant Events",
    description="""
    Get significant astrological events in a time period.

    Detects:
    - Planet sign changes
    - Retrograde periods
    - Major aspects
    - House ingress

    Each event includes:
    - Date and description
    - Affected life domains
    - Impact score (0-100)
    """
)
async def get_significant_events(
    chart_id: str = PathParam(..., description="Chart ID", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"),
    start_date: datetime = Query(None, description="Target date (defaults to today)", example=datetime.now()),
    end_date: datetime = Query(None, description="End date (defaults to today)", example=datetime.now() + timedelta(days=7)),
    domain_service: DomainService = Depends(get_domain_service)
) -> List[SignificantEvent]:
    """
    Get significant astrological events for a chart in a date range.

    Args:
        chart_id: Chart identifier
        start_date: Start of period
        end_date: End of period
        domain_service: Injected domain service

    Returns:
        List of SignificantEvent sorted by date

    Raises:
        HTTPException: If chart not found or calculation fails
    """
    try:
        events = domain_service.detect_significant_events(
            chart_id=chart_id,
            start_date=start_date,
            end_date=end_date
        )

        return events

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Event detection failed: {str(e)}")


@router.get(
    "/{chart_id}/drivers",
    response_model=dict,
    summary="Get Planet Drivers",
    description="""
    Get planet drivers for all domains at current time.

    Shows which planets are most influential for each life domain,
    helping to understand the astrological factors behind domain scores.
    """
)
async def get_planet_drivers(
    chart_id: str  = PathParam(..., description="Chart ID", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"),
    calculation_date: datetime = Query(None, description="Target date (defaults to today)", example=datetime.now()),
    domain_service: DomainService = Depends(get_domain_service)
) -> dict:
    """
    Get planet drivers for all domains.

    Args:
        chart_id: Chart identifier
        calculation_date: Date/time for calculation
        domain_service: Injected domain service

    Returns:
        Dictionary mapping domains to their driving planets

    Raises:
        HTTPException: If chart not found or calculation fails
    """
    try:
        # Calculate all domains
        domain_analysis = domain_service.calculate_all_domains(
            chart_id=chart_id,
            calculation_date=calculation_date,
            include_subdomains=False
        )

        # Extract driving planets for each domain
        drivers = {}
        for domain_name, domain_score in domain_analysis.domains.items():
            drivers[domain_name] = [
                {
                    "planet": contrib.planet.value,
                    "planet_score": contrib.planet_score,
                    "influence": contrib.influence,
                    "contribution": contrib.contribution
                }
                for contrib in domain_score.driving_planets[:3]  # Top 3 planets
            ]

        return {
            "chart_id": chart_id,
            "calculation_date": calculation_date,
            "drivers": drivers
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Driver calculation failed: {str(e)}")

