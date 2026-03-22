"""
Pipeline API Routes - Unified Analysis Endpoints

This module provides REST API endpoints for the end-to-end
analysis pipeline, offering a single entry point for complete
astrological analysis.
"""
from fastapi import APIRouter, HTTPException
from api.models.pipeline import (
    AnalysisRequest,
    AnalysisResponse,
    QuickAnalysisRequest,
    QuickAnalysisResponse
)
from api.services.analysis_pipeline import AnalysisPipeline
from api.services.natal_chart_service import NatalChartService
from api.services.scoring_engine import ScoringEngine
from api.services.house_activation_service import HouseActivationService
from api.services.domain_service import DomainService
from api.services.dasha_service import DashaService
from api.services.transit_service import TransitService
from api.services.strength_service import StrengthService
from api.services.aspect_service import AspectService
from api.services.motion_service import MotionService
from api.services.time_segmentation_service import TimeSegmentationService

router = APIRouter(prefix="/analyze", tags=["Analysis Pipeline"])

# Initialize services
natal_chart_service = NatalChartService()
scoring_engine = ScoringEngine()
house_activation_service = HouseActivationService()
time_segmentation_service = TimeSegmentationService()
domain_service = DomainService(
    scoring_engine=scoring_engine,
    house_activation_service=house_activation_service,
    time_segmentation_service=time_segmentation_service
)

# Initialize pipeline
pipeline = AnalysisPipeline(
    natal_chart_service=natal_chart_service,
    scoring_engine=scoring_engine,
    house_activation_service=house_activation_service,
    domain_service=domain_service
)


@router.post("/full", response_model=AnalysisResponse)
async def run_full_analysis(request: AnalysisRequest):
    """
    Run complete end-to-end astrological analysis.
    
    This is the main unified endpoint that orchestrates all analysis
    components in a single call:
    
    1. **Natal Chart**: Generate or retrieve natal chart
    2. **Planet Scores**: Calculate comprehensive planet scores
       - Dasha (35%)
       - Transit (25%)
       - Strength (20%)
       - Aspect (12%)
       - Motion (8%)
    3. **House Activation**: Convert planet scores to house scores
    4. **Domain Analysis**: Calculate 7 life domain scores
    5. **Timeline**: Generate timeline with intelligent segmentation
    6. **Summary**: High-level insights and recommendations
    
    **Parameters:**
    - `chart_id`: Existing chart ID (if available)
    - `name`, `birth_date`, `birth_time`, `latitude`, `longitude`, `timezone`: 
      Birth details (required if chart_id not provided)
    - `calculation_date`: Date for current analysis (default: now)
    - `include_timeline`: Whether to include timeline analysis (default: true)
    - `timeline_start`, `timeline_end`: Timeline date range (optional)
    - `timeline_days`: Timeline duration in days (default: 90)
    - `include_subdomains`: Include subdomain analysis (default: true)
    - `include_events`: Include significant events (default: true)
    - `use_intelligent_segmentation`: Use Moon/Sun transitions (default: true)
    
    **Returns:**
    - Complete analysis with all components
    - Explanations for all scores
    - Timeline data (if requested)
    - Summary insights
    
    **Example:**
    ```json
    {
      "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
      "calculation_date": "2026-03-22T00:00:00",
      "include_timeline": true,
      "timeline_days": 90
    }
    ```
    """
    try:
        return pipeline.run_full_analysis(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/quick", response_model=QuickAnalysisResponse)
async def run_quick_analysis(request: QuickAnalysisRequest):
    """
    Run quick analysis for existing chart.
    
    Optimized for speed - returns only essential metrics:
    - Overall life quality score
    - Strongest and weakest domains
    - Top 5 insights
    - All domain scores
    
    **Use this endpoint when:**
    - You need fast results
    - You already have a chart_id
    - You don't need detailed breakdowns
    - You want a quick health check
    
    **Parameters:**
    - `chart_id`: Existing chart ID (required)
    - `calculation_date`: Date for analysis (default: now)
    - `include_timeline`: Include timeline (default: false for speed)
    - `timeline_days`: Timeline duration if included (default: 30)
    
    **Returns:**
    - Overall life quality (0-100)
    - Strongest/weakest domains
    - Top 5 insights
    - All domain scores
    
    **Example:**
    ```json
    {
      "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"
    }
    ```
    """
    try:
        return pipeline.run_quick_analysis(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick analysis failed: {str(e)}")

