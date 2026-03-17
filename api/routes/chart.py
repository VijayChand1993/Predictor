"""
Chart API routes for natal chart generation and retrieval.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field

from api.models import BirthData, Location, NatalChart, Planet
from api.services.natal_chart_service import NatalChartService

router = APIRouter(prefix="/chart", tags=["Natal Chart"])

# Initialize service
chart_service = NatalChartService(output_dir="output")

# In-memory storage for demo (replace with database in production)
charts_db = {}


class ChartGenerateRequest(BaseModel):
    """Request model for generating a natal chart."""
    name: str = Field(..., description="Person's name", example="Vijay")
    birth_date: datetime = Field(..., description="Birth date and time", example="1993-04-02T01:15:00")
    latitude: float = Field(..., ge=-90, le=90, description="Birth location latitude", example=29.58633)
    longitude: float = Field(..., ge=-180, le=180, description="Birth location longitude", example=80.23275)
    city: Optional[str] = Field(None, description="City name", example="Pithoragarh")
    country: Optional[str] = Field(None, description="Country name", example="India")
    timezone: str = Field("UTC", description="Timezone", example="Asia/Kolkata")


class ChartGenerateResponse(BaseModel):
    """Response model for chart generation."""
    chart_id: str = Field(..., description="Unique chart identifier")
    message: str = Field(..., description="Success message")
    chart: NatalChart = Field(..., description="Complete natal chart data")


class ChartListResponse(BaseModel):
    """Response model for listing charts."""
    total: int = Field(..., description="Total number of charts")
    charts: list[dict] = Field(..., description="List of chart summaries")


@router.post(
    "/generate",
    response_model=ChartGenerateResponse,
    summary="Generate Natal Chart",
    description="Generate a complete Vedic natal chart from birth data using jyotishganit library"
)
async def generate_chart(request: ChartGenerateRequest):
    """
    Generate a natal chart from birth information.
    
    This endpoint:
    - Calculates the complete Vedic birth chart
    - Extracts all planet placements with dignities
    - Determines house cusps and lords
    - Saves raw JSON to output folder
    - Returns structured chart data
    """
    try:
        # Create birth data model
        location = Location(
            latitude=request.latitude,
            longitude=request.longitude,
            city=request.city,
            country=request.country,
            timezone=request.timezone
        )
        
        birth_data = BirthData(
            date=request.birth_date,
            location=location,
            name=request.name
        )
        
        # Generate chart
        chart = chart_service.generate_chart(birth_data, save_json=True)
        
        # Store in memory (replace with DB in production)
        charts_db[chart.chart_id] = chart
        
        return ChartGenerateResponse(
            chart_id=chart.chart_id,
            message=f"Chart generated successfully for {request.name}",
            chart=chart
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart: {str(e)}")


@router.get(
    "/{chart_id}",
    response_model=NatalChart,
    summary="Get Natal Chart",
    description="Retrieve a previously generated natal chart by ID"
)
async def get_chart(chart_id: str):
    """
    Retrieve a natal chart by its ID.
    
    Returns the complete chart data including:
    - Ascendant (Lagna)
    - All planet placements
    - House information
    - Moon sign
    """
    if chart_id not in charts_db:
        raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")
    
    return charts_db[chart_id]


@router.get(
    "/",
    response_model=ChartListResponse,
    summary="List All Charts",
    description="Get a list of all generated charts"
)
async def list_charts():
    """
    List all generated charts.
    
    Returns a summary of each chart including:
    - Chart ID
    - Person's name
    - Birth date
    - Ascendant sign
    """
    chart_summaries = [
        {
            "chart_id": chart.chart_id,
            "name": chart.birth_data.name,
            "birth_date": chart.birth_data.date.isoformat(),
            "ascendant": chart.ascendant_sign.value,
            "moon_sign": chart.moon_sign.value
        }
        for chart in charts_db.values()
    ]
    
    return ChartListResponse(
        total=len(chart_summaries),
        charts=chart_summaries
    )


@router.get(
    "/{chart_id}/planets",
    summary="Get Planet Placements",
    description="Get all planet placements for a specific chart"
)
async def get_planets(chart_id: str):
    """
    Get all planet placements for a chart.

    Returns detailed information for all 9 planets including:
    - Sign and house placement
    - Degree and nakshatra
    - Dignity and retrograde status
    - Lordship houses
    """
    if chart_id not in charts_db:
        raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")

    chart = charts_db[chart_id]
    return {
        "chart_id": chart_id,
        "planets": chart.planets
    }


@router.get(
    "/{chart_id}/planet/{planet_name}",
    summary="Get Specific Planet",
    description="Get placement details for a specific planet"
)
async def get_planet(
    chart_id: str,
    planet_name: str = Path(..., description="Planet name (Sun, Moon, Mars, etc.)")
):
    """
    Get placement details for a specific planet.

    Returns:
    - Sign and house placement
    - Exact degree
    - Nakshatra and pada
    - Dignity
    - Retrograde status
    - Houses ruled by this planet
    """
    if chart_id not in charts_db:
        raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")

    chart = charts_db[chart_id]

    # Convert string to Planet enum
    try:
        planet = Planet(planet_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid planet name: {planet_name}")

    if planet not in chart.planets:
        raise HTTPException(status_code=404, detail=f"Planet {planet_name} not found in chart")

    return {
        "chart_id": chart_id,
        "planet": planet_name,
        "placement": chart.planets[planet]
    }


@router.get(
    "/{chart_id}/houses",
    summary="Get House Information",
    description="Get all house cusps and lords for a specific chart"
)
async def get_houses(chart_id: str):
    """
    Get all house information for a chart.

    Returns details for all 12 houses including:
    - Sign on cusp
    - Cusp degree
    - House lord
    """
    if chart_id not in charts_db:
        raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")

    chart = charts_db[chart_id]
    return {
        "chart_id": chart_id,
        "houses": chart.houses
    }


@router.get(
    "/{chart_id}/ascendant",
    summary="Get Ascendant Details",
    description="Get ascendant (Lagna) information"
)
async def get_ascendant(chart_id: str):
    """
    Get ascendant (Lagna) details.

    Returns:
    - Ascendant sign
    - Exact degree
    - Moon sign (Chandra Lagna)
    """
    if chart_id not in charts_db:
        raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")

    chart = charts_db[chart_id]
    return {
        "chart_id": chart_id,
        "ascendant_sign": chart.ascendant_sign,
        "ascendant_degree": chart.ascendant_degree,
        "moon_sign": chart.moon_sign
    }

