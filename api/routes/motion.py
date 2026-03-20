"""
Motion API routes for calculating planet motion/speed.
"""
from fastapi import APIRouter, HTTPException, Path as PathParam
from typing import Dict

from api.models import (
    Planet,
    MotionRequest,
    MotionResponse,
    MotionCalculation,
    PlanetMotion,
)
from api.services.motion_service import MotionService
from api.routes.chart import charts_db

router = APIRouter(prefix="/motion", tags=["Motion"])

# Initialize service
motion_service = MotionService()


@router.post(
    "/calculate",
    response_model=MotionResponse,
    summary="Calculate Planet Motions",
    description="Calculate planet motion/speed for all planets at a specific time"
)
async def calculate_motions(request: MotionRequest) -> MotionResponse:
    """
    Calculate planet motions for a natal chart at a specific time.
    
    Calculates motion based on:
    - Speed (degrees per day)
    - Motion classification (fast, normal, slow, stationary, retrograde)
    - Significance for dynamic planets (Moon, Mars, Mercury)
    
    Formula: W_motion(p) = 50 + motion_modifier(p)
    
    Motion modifiers:
    - Fast: +10
    - Stationary: +15
    - Slow: +5
    - Normal: 0
    - Retrograde: +10
    
    Args:
        request: MotionRequest with chart_id and calculation_date
    
    Returns:
        MotionResponse with complete motion calculation
    
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
        # Calculate motions
        motions = motion_service.calculate_chart_motions(
            natal_chart,
            request.calculation_date
        )
        
        return MotionResponse(
            chart_id=request.chart_id,
            motions=motions
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating motions: {str(e)}"
        )


@router.get(
    "/{chart_id}",
    response_model=MotionResponse,
    summary="Get Motions for Chart",
    description="Get planet motions for a specific chart at current time"
)
async def get_motions(
    chart_id: str = PathParam(..., description="Chart identifier")
) -> MotionResponse:
    """
    Get planet motions for a chart at current time.
    
    Args:
        chart_id: Chart identifier
    
    Returns:
        MotionResponse with motion calculation
    
    Raises:
        HTTPException: If chart not found
    """
    from datetime import datetime
    
    # Get chart from database
    if chart_id not in charts_db:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {chart_id}"
        )
    
    natal_chart = charts_db[chart_id]
    
    try:
        # Calculate motions for current time
        motions = motion_service.calculate_chart_motions(
            natal_chart,
            datetime.now()
        )
        
        return MotionResponse(
            chart_id=chart_id,
            motions=motions
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating motions: {str(e)}"
        )


@router.get(
    "/{chart_id}/planet/{planet}",
    response_model=PlanetMotion,
    summary="Get Motion for Specific Planet",
    description="Get motion for a specific planet in a chart at current time"
)
async def get_planet_motion(
    chart_id: str = PathParam(..., description="Chart identifier"),
    planet: Planet = PathParam(..., description="Planet name")
) -> PlanetMotion:
    """
    Get motion for a specific planet at current time.
    
    Args:
        chart_id: Chart identifier
        planet: Planet name
    
    Returns:
        PlanetMotion for the specified planet
    
    Raises:
        HTTPException: If chart or planet not found
    """
    from datetime import datetime
    
    # Get chart from database
    if chart_id not in charts_db:
        raise HTTPException(
            status_code=404,
            detail=f"Chart not found: {chart_id}"
        )
    
    natal_chart = charts_db[chart_id]
    
    try:
        # Calculate motions for current time
        motions = motion_service.calculate_chart_motions(
            natal_chart,
            datetime.now()
        )
        
        # Get motion for specific planet
        if planet not in motions.planet_motions:
            raise HTTPException(
                status_code=404,
                detail=f"Planet {planet} not found in motion calculation"
            )
        
        return motions.planet_motions[planet]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planet motion: {str(e)}"
        )

