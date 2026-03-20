"""
Strength API routes for calculating planet strength.
"""
from fastapi import APIRouter, HTTPException, Path as PathParam
from typing import Dict

from api.models import (
    Planet,
    StrengthRequest,
    StrengthResponse,
    StrengthCalculation,
    PlanetStrength,
)
from api.services.strength_service import StrengthService
from api.routes.chart import charts_db

router = APIRouter(prefix="/strength", tags=["Strength"])

# Initialize service
strength_service = StrengthService()


@router.post(
    "/calculate",
    response_model=StrengthResponse,
    summary="Calculate Planet Strengths",
    description="Calculate planet strength (Shadbala) for all planets in a natal chart"
)
async def calculate_strengths(request: StrengthRequest) -> StrengthResponse:
    """
    Calculate planet strengths for a natal chart.
    
    Calculates strength based on:
    - Dignity (exalted, own sign, friendly, neutral, enemy, debilitated)
    - Retrograde status (bonus for retrograde planets)
    - Combustion (penalty for planets too close to Sun)
    
    Formula: W_strength(p) = max(0, min(100, 50 + S(p)))
    Where S(p) = dignity + retrograde + combustion
    
    Args:
        request: StrengthRequest with chart_id
    
    Returns:
        StrengthResponse with complete strength calculation
    
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
        # Calculate strengths
        strengths = strength_service.calculate_chart_strengths(natal_chart)
        
        return StrengthResponse(
            chart_id=request.chart_id,
            strengths=strengths
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating strengths: {str(e)}"
        )


@router.get(
    "/{chart_id}",
    response_model=StrengthResponse,
    summary="Get Strengths for Chart",
    description="Get planet strengths for a specific chart"
)
async def get_strengths(
    chart_id: str = PathParam(..., description="Chart identifier")
) -> StrengthResponse:
    """
    Get planet strengths for a chart.
    
    Args:
        chart_id: Chart identifier
    
    Returns:
        StrengthResponse with strength calculation
    
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
        # Calculate strengths
        strengths = strength_service.calculate_chart_strengths(natal_chart)
        
        return StrengthResponse(
            chart_id=chart_id,
            strengths=strengths
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating strengths: {str(e)}"
        )


@router.get(
    "/{chart_id}/planet/{planet}",
    response_model=PlanetStrength,
    summary="Get Strength for Specific Planet",
    description="Get strength for a specific planet in a chart"
)
async def get_planet_strength(
    chart_id: str = PathParam(..., description="Chart identifier"),
    planet: Planet = PathParam(..., description="Planet name")
) -> PlanetStrength:
    """
    Get strength for a specific planet.
    
    Args:
        chart_id: Chart identifier
        planet: Planet name
    
    Returns:
        PlanetStrength for the specified planet
    
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
        sun_placement = natal_chart.planets[Planet.SUN]
        
        # Calculate strength for this planet
        planet_strength = strength_service.calculate_planet_strength(
            planet, placement, sun_placement
        )
        
        return planet_strength
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planet strength: {str(e)}"
        )

