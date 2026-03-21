"""
Scoring API routes for calculating planet scores.
"""
from fastapi import APIRouter, HTTPException, Path as PathParam, Query
from datetime import datetime, timedelta

from api.models import (
    Planet,
    ScoringRequest,
    ScoringResponse,
    PlanetScores,
    PlanetScore,
    PlanetInfluenceTimeline,
    HouseActivationTimeline,
)
from api.services.scoring_engine import ScoringEngine
from api.services.timeline_service import TimelineService
from api.routes.chart import charts_db

router = APIRouter(prefix="/scoring", tags=["Scoring"])

# Initialize services
scoring_engine = ScoringEngine()
timeline_service = TimelineService()


@router.post(
    "/calculate",
    response_model=ScoringResponse,
    summary="Calculate Planet Scores",
    description="Calculate complete planet scores combining all components (dasha, transit, strength, aspect, motion)"
)
async def calculate_scores(request: ScoringRequest) -> ScoringResponse:
    """
    Calculate planet scores for a natal chart at a specific time.
    
    Combines all scoring components with weights:
    - Dasha: 35%
    - Transit: 25%
    - Strength: 20%
    - Aspect: 12%
    - Motion: 8%
    
    Formula: P_raw(p) = 0.35×W_dasha + 0.25×W_transit + 0.20×W_strength + 0.12×W_aspect + 0.08×W_motion
    Normalized: P(p) = 100 × P_raw(p) / Σ P_raw(all planets)
    
    Args:
        request: ScoringRequest with chart_id and calculation_date
    
    Returns:
        ScoringResponse with complete planet scoring
    
    Raises:
        HTTPException: If chart not found
    """
    # Get chart from database
    if request.chart_id not in charts_db:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {request.chart_id}"
        )
    
    natal_chart = charts_db[request.chart_id]
    
    try:
        # Calculate planet scores
        planet_scores = scoring_engine.calculate_planet_scores(
            natal_chart,
            request.calculation_date
        )
        
        return ScoringResponse(
            chart_id=request.chart_id,
            planet_scores=planet_scores
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating scores: {str(e)}"
        )


@router.get(
    "/{chart_id}",
    response_model=ScoringResponse,
    summary="Get Scores for Chart",
    description="Get planet scores for a specific chart at current time"
)
async def get_scores(
    chart_id: str = PathParam(..., description="Chart identifier", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5")
) -> ScoringResponse:
    """
    Get planet scores for a chart at current time.
    
    Args:
        chart_id: Chart identifier
    
    Returns:
        ScoringResponse with planet scoring
    
    Raises:
        HTTPException: If chart not found
    """
    # Get chart from database
    if chart_id not in charts_db:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {chart_id}"
        )
    
    natal_chart = charts_db[chart_id]
    
    try:
        # Calculate scores for current time
        planet_scores = scoring_engine.calculate_planet_scores(
            natal_chart,
            datetime.now()
        )
        
        return ScoringResponse(
            chart_id=chart_id,
            planet_scores=planet_scores
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating scores: {str(e)}"
        )


@router.get(
    "/{chart_id}/planet/{planet}",
    response_model=PlanetScore,
    summary="Get Score for Specific Planet",
    description="Get score for a specific planet in a chart at current time"
)
async def get_planet_score(
    chart_id: str = PathParam(..., description="Chart identifier", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"),
    planet: Planet = PathParam(..., description="Planet name")
) -> PlanetScore:
    """
    Get score for a specific planet at current time.
    
    Args:
        chart_id: Chart identifier
        planet: Planet name
    
    Returns:
        PlanetScore for the specified planet
    
    Raises:
        HTTPException: If chart or planet not found
    """
    # Get chart from database
    if chart_id not in charts_db:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {chart_id}"
        )
    
    natal_chart = charts_db[chart_id]
    
    # Check if planet exists in chart
    if planet not in natal_chart.planets:
        raise HTTPException(
            status_code=404,
            detail=f"Planet {planet} not found in chart"
        )
    
    try:
        # Calculate scores for current time
        planet_scores = scoring_engine.calculate_planet_scores(
            natal_chart,
            datetime.now()
        )
        
        # Get score for specific planet
        if planet not in planet_scores.scores:
            raise HTTPException(
                status_code=404,
                detail=f"Planet {planet} not found in scoring calculation"
            )
        
        return planet_scores.scores[planet]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planet score: {str(e)}"
        )


@router.get(
    "/{chart_id}/planets",
    response_model=PlanetInfluenceTimeline,
    summary="Get Planet Influence Timeline",
    description="Get planet influence scores over a time range"
)
async def get_planet_timeline(
    chart_id: str = PathParam(..., description="Chart identifier", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"),
    start_date: datetime = Query(
        ...,
        description="Start date of time range",
        example=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ),
    end_date: datetime = Query(
        ...,
        description="End date of time range",
        example=(datetime.now() + timedelta(days=30)).replace(hour=23, minute=59, second=59, microsecond=0)
    ),
    interval_days: int = Query(1, ge=1, le=30, description="Days between samples (1-30)")
) -> PlanetInfluenceTimeline:
    """
    Get planet influence timeline over a date range.

    This endpoint calculates planet scores at regular intervals over the specified
    time range and returns a timeline showing how each planet's influence changes.

    Args:
        chart_id: Chart identifier
        start_date: Start of time range
        end_date: End of time range
        interval_days: Days between samples (default: 1)

    Returns:
        PlanetInfluenceTimeline with data for all planets

    Raises:
        HTTPException: If chart not found or dates invalid
    """
    # Get chart from database
    if chart_id not in charts_db:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {chart_id}"
        )

    # Validate date range
    if end_date <= start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    # Check if range is too large (max 1 year)
    max_range = timedelta(days=365)
    if (end_date - start_date) > max_range:
        raise HTTPException(
            status_code=400,
            detail="Time range cannot exceed 1 year"
        )

    natal_chart = charts_db[chart_id]

    try:
        # Calculate planet timeline
        timeline = timeline_service.calculate_planet_timeline(
            natal_chart,
            start_date,
            end_date,
            interval_days
        )

        return timeline

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planet timeline: {str(e)}"
        )


@router.get(
    "/{chart_id}/houses",
    response_model=HouseActivationTimeline,
    summary="Get House Activation Timeline",
    description="Get house activation scores over a time range"
)
async def get_house_timeline(
    chart_id: str = PathParam(..., description="Chart identifier", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"),
    start_date: datetime = Query(
        ...,
        description="Start date of time range",
        example=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    ),
    end_date: datetime = Query(
        ...,
        description="End date of time range",
        example=(datetime.now() + timedelta(days=30)).replace(hour=23, minute=59, second=59, microsecond=0)
    ),
    interval_days: int = Query(1, ge=1, le=30, description="Days between samples (1-30)")
) -> HouseActivationTimeline:
    """
    Get house activation timeline over a date range.

    This endpoint calculates house activation scores at regular intervals over the
    specified time range and returns a timeline showing how each house's activation changes.

    Args:
        chart_id: Chart identifier
        start_date: Start of time range
        end_date: End of time range
        interval_days: Days between samples (default: 1)

    Returns:
        HouseActivationTimeline with data for all houses

    Raises:
        HTTPException: If chart not found or dates invalid
    """
    # Get chart from database
    if chart_id not in charts_db:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {chart_id}"
        )

    # Validate date range
    if end_date <= start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )

    # Check if range is too large (max 1 year)
    max_range = timedelta(days=365)
    if (end_date - start_date) > max_range:
        raise HTTPException(
            status_code=400,
            detail="Time range cannot exceed 1 year"
        )

    natal_chart = charts_db[chart_id]

    try:
        # Calculate house timeline
        timeline = timeline_service.calculate_house_timeline(
            natal_chart,
            start_date,
            end_date,
            interval_days
        )

        return timeline

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating house timeline: {str(e)}"
        )

