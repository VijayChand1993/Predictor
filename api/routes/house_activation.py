"""
House Activation API routes for calculating house activation scores.
"""
from fastapi import APIRouter, HTTPException, Path as PathParam
from datetime import datetime

from api.models import (
    HouseActivationRequest,
    HouseActivationResponse,
    HouseActivation,
)
from api.services.house_activation_service import HouseActivationService
from api.routes.chart import charts_db

router = APIRouter(prefix="/house-activation", tags=["House Activation"])

# Initialize service
house_activation_service = HouseActivationService()


@router.post(
    "/calculate",
    response_model=HouseActivationResponse,
    summary="Calculate House Activation Scores",
    description="Calculate house activation scores by distributing planet scores to houses"
)
async def calculate_house_activation(request: HouseActivationRequest) -> HouseActivationResponse:
    """
    Calculate house activation scores for a natal chart at a specific time.
    
    Distributes each planet's score to houses based on:
    - Transit house: 30%
    - Owned houses: 30% (split if 2 houses)
    - Natal placement: 20%
    - Aspected houses: 20% (split equally)
    
    Formula: H_raw(h) = Σ C(p → h)
    Normalized: H(h) = 100 × H_raw(h) / Σ H_raw(all houses)
    
    Args:
        request: HouseActivationRequest with chart_id and calculation_date
    
    Returns:
        HouseActivationResponse with complete house activation
    
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
        # Calculate house activation
        house_activation = house_activation_service.calculate_house_activation(
            natal_chart,
            request.calculation_date
        )
        
        return HouseActivationResponse(
            chart_id=request.chart_id,
            house_activation=house_activation
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating house activation: {str(e)}"
        )


@router.get(
    "/{chart_id}",
    response_model=HouseActivationResponse,
    summary="Get House Activation for Chart",
    description="Get house activation scores for a specific chart at current time"
)
async def get_house_activation(
    chart_id: str = PathParam(..., description="Chart identifier")
) -> HouseActivationResponse:
    """
    Get house activation scores for a chart at current time.
    
    Args:
        chart_id: Chart identifier
    
    Returns:
        HouseActivationResponse with house activation
    
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
        # Calculate house activation for current time
        house_activation = house_activation_service.calculate_house_activation(
            natal_chart,
            datetime.now()
        )
        
        return HouseActivationResponse(
            chart_id=chart_id,
            house_activation=house_activation
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating house activation: {str(e)}"
        )


@router.get(
    "/{chart_id}/house/{house_number}",
    response_model=HouseActivation,
    summary="Get Activation for Specific House",
    description="Get activation score for a specific house in a chart at current time"
)
async def get_house_score(
    chart_id: str = PathParam(..., description="Chart identifier"),
    house_number: int = PathParam(..., ge=1, le=12, description="House number (1-12)")
) -> HouseActivation:
    """
    Get activation score for a specific house at current time.
    
    Args:
        chart_id: Chart identifier
        house_number: House number (1-12)
    
    Returns:
        HouseActivation for the specified house
    
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
        # Calculate house activation for current time
        house_activation = house_activation_service.calculate_house_activation(
            natal_chart,
            datetime.now()
        )
        
        # Get activation for specific house
        if house_number not in house_activation.house_activations:
            raise HTTPException(
                status_code=404,
                detail=f"House {house_number} not found in activation calculation"
            )
        
        return house_activation.house_activations[house_number]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating house activation: {str(e)}"
        )

