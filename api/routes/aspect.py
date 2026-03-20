"""
Aspect API routes for calculating planetary aspects (Drishti).
"""
from fastapi import APIRouter, HTTPException, Path as PathParam
from typing import Dict

from api.models import (
    Planet,
    AspectRequest,
    AspectResponse,
    AspectCalculation,
    PlanetAspects,
)
from api.services.aspect_service import AspectService
from api.routes.chart import charts_db

router = APIRouter(prefix="/aspect", tags=["Aspects"])

# Initialize service
aspect_service = AspectService()


@router.post(
    "/calculate",
    response_model=AspectResponse,
    summary="Calculate Planetary Aspects",
    description="Calculate all planetary aspects (Drishti) for a natal chart"
)
async def calculate_aspects(request: AspectRequest) -> AspectResponse:
    """
    Calculate planetary aspects for a natal chart.
    
    Implements Vedic astrology aspect rules:
    - All planets: 7th house aspect (full aspect)
    - Mars: 4th, 8th house aspects (special aspects)
    - Jupiter: 5th, 9th house aspects (special aspects)
    - Saturn: 3rd, 10th house aspects (special aspects)
    
    Args:
        request: AspectRequest with chart_id
    
    Returns:
        AspectResponse with complete aspect calculation
    
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
        # Calculate aspects
        aspects = aspect_service.calculate_chart_aspects(natal_chart)
        
        return AspectResponse(
            chart_id=request.chart_id,
            aspects=aspects
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating aspects: {str(e)}"
        )


@router.get(
    "/{chart_id}",
    response_model=AspectResponse,
    summary="Get Aspects for Chart",
    description="Get planetary aspects for a specific chart"
)
async def get_aspects(
    chart_id: str = PathParam(..., description="Chart identifier")
) -> AspectResponse:
    """
    Get planetary aspects for a chart.
    
    Args:
        chart_id: Chart identifier
    
    Returns:
        AspectResponse with aspect calculation
    
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
        # Calculate aspects
        aspects = aspect_service.calculate_chart_aspects(natal_chart)
        
        return AspectResponse(
            chart_id=chart_id,
            aspects=aspects
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating aspects: {str(e)}"
        )


@router.get(
    "/{chart_id}/planet/{planet}",
    response_model=PlanetAspects,
    summary="Get Aspects for Specific Planet",
    description="Get aspects cast by a specific planet in a chart"
)
async def get_planet_aspects(
    chart_id: str = PathParam(..., description="Chart identifier"),
    planet: Planet = PathParam(..., description="Planet name")
) -> PlanetAspects:
    """
    Get aspects for a specific planet.
    
    Args:
        chart_id: Chart identifier
        planet: Planet name
    
    Returns:
        PlanetAspects for the specified planet
    
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
        # Get planet placement
        placement = natal_chart.planets[planet]
        
        # Calculate aspects for this planet
        planet_aspects = aspect_service.calculate_planet_aspects(planet, placement.house)
        
        return planet_aspects
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planet aspects: {str(e)}"
        )

