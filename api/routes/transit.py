"""
Transit calculation API routes.
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from api.models import (
    Planet, TransitData, TransitPlacement, TimeSegment
)
from api.services.transit_service import TransitService

# Import the shared charts database from chart routes
from api.routes.chart import charts_db

router = APIRouter(prefix="/transit", tags=["Transit"])

# Initialize services
transit_service = TransitService()


class TransitRequest(BaseModel):
    """Request model for transit calculation."""
    chart_id: str = Field(..., description="Natal chart ID", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5")
    target_date: datetime = Field(..., description="Date/time for transit calculation", example=datetime.now().date())
    save_json: bool = Field(False, description="Whether to save raw transit JSON")


class TransitWeightRequest(BaseModel):
    """Request model for transit weight calculation."""
    planet: Planet = Field(..., description="Planet to calculate weight for")
    transit_house: int = Field(..., ge=1, le=12, description="House number the planet is transiting")


class TransitWeightResponse(BaseModel):
    """Response model for transit weight."""
    planet: Planet
    transit_house: int
    planet_weight: float
    house_weight: float
    total_weight: float


class PlanetHouseWeight(BaseModel):
    """Weight for a specific planet-house combination."""
    house: int = Field(..., ge=1, le=12, description="House number")
    planet_weight: float = Field(..., description="Planet's inherent weight")
    house_weight: float = Field(..., description="House importance weight")
    total_weight: float = Field(..., description="Combined transit weight")


class AllTransitWeightsResponse(BaseModel):
    """Response model for all transit weights."""
    weights: Dict[Planet, List[PlanetHouseWeight]] = Field(
        ...,
        description="Dictionary of planet weights across all 12 houses"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "weights": {
                    "Jupiter": [
                        {"house": 1, "planet_weight": 1.0, "house_weight": 1.0, "total_weight": 100.0},
                        {"house": 2, "planet_weight": 1.0, "house_weight": 0.7, "total_weight": 70.0}
                    ]
                }
            }
        }


class TimeSegmentRequest(BaseModel):
    """Request model for time segmentation."""
    chart_id: str = Field(..., description="Natal chart ID", example="04ecf146-d0e1-4e72-8c30-fb8bba03e2e5")
    start_date: datetime = Field(..., description="Start of date range", example=datetime.now().date())
    end_date: datetime = Field(..., description="End of date range", example=datetime.now().date() + timedelta(days=7))
    fast_planets: Optional[List[Planet]] = Field(
        None,
        description="Planets to track for sign changes (default: Moon, Sun, Mars, Mercury)",
        example=[Planet.MOON, Planet.SUN, Planet.MARS, Planet.MERCURY,
                Planet.JUPITER, Planet.VENUS, Planet.SATURN,
                Planet.RAHU, Planet.KETU]
    )


@router.post("/calculate", response_model=TransitData)
async def calculate_transit(request: TransitRequest):
    """
    Calculate planetary positions for a specific date/time.
    
    Returns transit data with all planetary positions relative to the natal chart.
    """
    try:
        # Load natal chart from shared database
        if request.chart_id not in charts_db:
            raise HTTPException(status_code=404, detail=f"Chart {request.chart_id} not found")

        natal_chart = charts_db[request.chart_id]
        
        # Calculate transit
        transit_data = transit_service.get_transit_data(
            target_date=request.target_date,
            natal_chart=natal_chart,
            save_json=request.save_json
        )
        
        return transit_data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Chart {request.chart_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating transit: {str(e)}")


@router.post("/weight", response_model=TransitWeightResponse)
async def calculate_transit_weight(request: TransitWeightRequest):
    """
    Calculate transit weight for a planet in a specific house.

    Formula: W_transit(p) = 100 × PlanetWeight(p) × HouseWeight(h_transit)
    """
    try:
        # Calculate weight
        total_weight = transit_service.calculate_transit_weight(
            planet=request.planet,
            transit_house=request.transit_house
        )

        # Get individual weights for breakdown
        planet_weight = transit_service.config.planet_importance.get_weight(request.planet)
        house_weight = transit_service.config.house_importance.get_house_weight(request.transit_house)

        return TransitWeightResponse(
            planet=request.planet,
            transit_house=request.transit_house,
            planet_weight=planet_weight,
            house_weight=house_weight,
            total_weight=total_weight
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating weight: {str(e)}")


@router.get("/weight/all", response_model=AllTransitWeightsResponse)
async def get_all_transit_weights():
    """
    Get transit weights for all planets across all 12 houses.

    Returns a comprehensive matrix of weights showing how each planet's
    importance varies across different house placements.

    Formula: W_transit(p) = 100 × PlanetWeight(p) × HouseWeight(h_transit)

    This is a pure calculation endpoint that doesn't require any chart data.
    Useful for understanding relative planetary influences across houses.
    """
    try:
        weights = {}

        # Calculate weights for each planet
        for planet in Planet:
            planet_weights = []
            planet_weight = transit_service.config.planet_importance.get_weight(planet)

            # Calculate weight for each house
            for house in range(1, 13):
                house_weight = transit_service.config.house_importance.get_house_weight(house)
                total_weight = transit_service.calculate_transit_weight(planet, house)

                planet_weights.append(PlanetHouseWeight(
                    house=house,
                    planet_weight=planet_weight,
                    house_weight=house_weight,
                    total_weight=total_weight
                ))

            weights[planet] = planet_weights

        return AllTransitWeightsResponse(weights=weights)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating all weights: {str(e)}")


@router.post("/segments", response_model=List[TimeSegment])
async def get_time_segments(request: TimeSegmentRequest):
    """
    Generate time segments based on transit changes.
    
    Detects sign changes for fast-moving planets and creates segments
    where planetary positions are constant.
    """
    try:
        # Load natal chart from shared database
        if request.chart_id not in charts_db:
            raise HTTPException(status_code=404, detail=f"Chart {request.chart_id} not found")

        natal_chart = charts_db[request.chart_id]
        
        # Generate segments
        segments = transit_service.get_time_segments(
            start_date=request.start_date,
            end_date=request.end_date,
            natal_chart=natal_chart,
            fast_planets=request.fast_planets
        )
        
        return segments
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Chart {request.chart_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating segments: {str(e)}")


@router.get("/current/{chart_id}", response_model=TransitData)
async def get_current_transit(chart_id: str, save_json: bool = Query(False)):
    """
    Get current planetary transits for a natal chart.
    
    Convenience endpoint that uses the current date/time.
    """
    try:
        # Load natal chart from shared database
        if chart_id not in charts_db:
            raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")

        natal_chart = charts_db[chart_id]
        
        # Calculate current transit
        transit_data = transit_service.get_transit_data(
            target_date=datetime.now(),
            natal_chart=natal_chart,
            save_json=save_json
        )
        
        return transit_data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Chart {chart_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating transit: {str(e)}")

