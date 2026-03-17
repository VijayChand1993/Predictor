"""
Dasha API routes for Vimshottari dasha calculations.
"""
from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException, Path as PathParam, Query
from pydantic import BaseModel, Field
import json
from pathlib import Path as FilePath

from api.models import Planet, ActiveDashas, DashaPeriod, DashaWeight
from api.services.dasha_service import DashaService

router = APIRouter(prefix="/dasha", tags=["Dasha"])

# Initialize service
dasha_service = DashaService()


class ActiveDashasRequest(BaseModel):
    """Request model for getting active dashas."""
    chart_id: str = Field(..., description="Chart ID from natal chart generation")
    target_date: date = Field(..., description="Date for which to calculate active dashas", example="2026-03-17")


class DashaWeightRequest(BaseModel):
    """Request model for calculating dasha weight."""
    chart_id: str = Field(..., description="Chart ID from natal chart generation")
    planet: Planet = Field(..., description="Planet to calculate weight for")
    target_date: date = Field(..., description="Date for calculation", example="2026-03-17")


@router.post(
    "/active",
    response_model=ActiveDashas,
    summary="Get Active Dashas",
    description="Get active Vimshottari dasha periods for a specific date"
)
async def get_active_dashas(request: ActiveDashasRequest):
    """
    Get active dasha periods for a specific date.
    
    Returns:
    - Mahadasha (major period)
    - Antardasha (sub-period)
    - Pratyantar dasha (sub-sub-period)
    - Sookshma dasha (if available)
    """
    try:
        # Load chart JSON from output folder
        chart_path = FilePath(f"output/chart_{request.chart_id}.json")
        if not chart_path.exists():
            raise HTTPException(status_code=404, detail=f"Chart {request.chart_id} not found")
        
        with open(chart_path, 'r') as f:
            chart_json = json.load(f)
        
        # Get active dashas
        active_dashas = dasha_service.get_active_dashas(chart_json, request.target_date)
        
        return active_dashas
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating dashas: {str(e)}")


@router.get(
    "/{chart_id}/active",
    response_model=ActiveDashas,
    summary="Get Active Dashas (GET)",
    description="Get active Vimshottari dasha periods for a specific date using GET"
)
async def get_active_dashas_get(
    chart_id: str = PathParam(..., description="Chart ID"),
    target_date: Optional[date] = Query(None, description="Target date (defaults to today)")
):
    """
    Get active dasha periods for a specific date.
    
    If no date is provided, uses today's date.
    """
    if target_date is None:
        target_date = date.today()
    
    request = ActiveDashasRequest(chart_id=chart_id, target_date=target_date)
    return await get_active_dashas(request)


@router.post(
    "/weight",
    response_model=DashaWeight,
    summary="Calculate Dasha Weight",
    description="Calculate dasha weight contribution for a planet"
)
async def calculate_dasha_weight(request: DashaWeightRequest):
    """
    Calculate dasha weight for a planet.
    
    The weight is calculated using the formula:
    Score = 40·D_md + 30·D_ad + 20·D_pd + 10·D_sd
    
    Where:
    - D_md = 100 if planet is Mahadasha lord, 0 otherwise
    - D_ad = 100 if planet is Antardasha lord, 0 otherwise
    - D_pd = 100 if planet is Pratyantar lord, 0 otherwise
    - D_sd = 100 if planet is Sookshma lord, 0 otherwise
    
    Returns a score between 0-100.
    """
    try:
        # Load chart JSON
        chart_path = FilePath(f"output/chart_{request.chart_id}.json")
        if not chart_path.exists():
            raise HTTPException(status_code=404, detail=f"Chart {request.chart_id} not found")
        
        with open(chart_path, 'r') as f:
            chart_json = json.load(f)
        
        # Get active dashas
        active_dashas = dasha_service.get_active_dashas(chart_json, request.target_date)
        
        # Calculate weight
        weight = dasha_service.calculate_dasha_weight(request.planet, active_dashas)
        
        return weight
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating weight: {str(e)}")


@router.get(
    "/{chart_id}/mahadashas",
    summary="Get All Mahadashas",
    description="Get all mahadasha periods for a birth chart"
)
async def get_all_mahadashas(chart_id: str = PathParam(..., description="Chart ID")):
    """
    Get all mahadasha periods from birth to 120 years.
    
    Returns a list of all 9 mahadasha periods with their start and end dates.
    """
    try:
        # Load chart JSON
        chart_path = FilePath(f"output/chart_{chart_id}.json")
        if not chart_path.exists():
            raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")

        with open(chart_path, 'r') as f:
            chart_json = json.load(f)
        
        # Get all mahadashas
        mahadashas = dasha_service.get_all_mahadashas(chart_json)
        
        return {
            "chart_id": chart_id,
            "total": len(mahadashas),
            "mahadashas": mahadashas
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting mahadashas: {str(e)}")

