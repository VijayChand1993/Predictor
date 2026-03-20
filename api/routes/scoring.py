"""
Scoring API routes for calculating planet scores.
"""
from fastapi import APIRouter, HTTPException, Path as PathParam
from datetime import datetime

from api.models import (
    Planet,
    ScoringRequest,
    ScoringResponse,
    PlanetScores,
    PlanetScore,
)
from api.services.scoring_engine import ScoringEngine
from api.routes.chart import charts_db

router = APIRouter(prefix="/scoring", tags=["Scoring"])

# Initialize service
scoring_engine = ScoringEngine()


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
    chart_id: str = PathParam(..., description="Chart identifier")
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
    chart_id: str = PathParam(..., description="Chart identifier"),
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

