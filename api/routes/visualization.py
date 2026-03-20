"""
Visualization API routes for chart data, heatmaps, and exports.
"""
from fastapi import APIRouter, HTTPException, Path as PathParam, Query, Response
from datetime import datetime, timedelta

from api.models import (
    ChartVisualization,
    HeatmapVisualization,
    AnalysisReport,
    CSVExportMetadata,
)
from api.services.timeline_service import TimelineService
from api.services.visualization_service import VisualizationService
from api.services.analysis_service import AnalysisService
from api.services.export_service import ExportService
from api.routes.chart import charts_db

router = APIRouter(prefix="/visualization", tags=["Visualization"])

# Initialize services
timeline_service = TimelineService()
visualization_service = VisualizationService()
analysis_service = AnalysisService()
export_service = ExportService()


@router.get(
    "/{chart_id}/timeline",
    response_model=ChartVisualization,
    summary="Get Chart Timeline Visualization",
    description="Get planet influence timeline in chart-ready format"
)
async def get_timeline_chart(
    chart_id: str = PathParam(..., description="Chart identifier"),
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
) -> ChartVisualization:
    """
    Get planet influence timeline in chart-ready format.
    
    Returns data formatted for charting libraries like Chart.js, D3, etc.
    Each planet is a separate dataset with x/y data points.
    
    Args:
        chart_id: Chart identifier
        start_date: Start of time range
        end_date: End of time range
        interval_days: Days between samples
    
    Returns:
        ChartVisualization with datasets for all planets
    
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
        
        # Transform to chart visualization
        chart_viz = visualization_service.create_planet_chart(timeline)
        
        return chart_viz
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating timeline chart: {str(e)}"
        )


@router.get(
    "/{chart_id}/heatmap",
    response_model=HeatmapVisualization,
    summary="Get House Activation Heatmap",
    description="Get house activation heatmap data"
)
async def get_heatmap(
    chart_id: str = PathParam(..., description="Chart identifier"),
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
    interval_days: int = Query(7, ge=1, le=30, description="Days between samples (default: 7 for weekly)")
) -> HeatmapVisualization:
    """
    Get house activation heatmap data.
    
    Returns a heatmap with houses as rows and time periods as columns.
    Each cell contains the activation score for that house at that time.
    
    Args:
        chart_id: Chart identifier
        start_date: Start of time range
        end_date: End of time range
        interval_days: Days between samples (default: 7 for weekly view)
    
    Returns:
        HeatmapVisualization with cells for each house/time combination
    
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

        # Transform to heatmap visualization
        heatmap = visualization_service.create_house_heatmap(timeline)

        return heatmap

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating heatmap: {str(e)}"
        )


@router.get(
    "/{chart_id}/analysis",
    response_model=AnalysisReport,
    summary="Get Analysis Report",
    description="Get analysis report with peak influences and significant events"
)
async def get_analysis(
    chart_id: str = PathParam(..., description="Chart identifier"),
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
) -> AnalysisReport:
    """
    Get analysis report with peak influences and significant events.

    Analyzes the timeline to identify:
    - Peak influence periods for each planet
    - Significant astrological events
    - Summary insights

    Args:
        chart_id: Chart identifier
        start_date: Start of time range
        end_date: End of time range
        interval_days: Days between samples

    Returns:
        AnalysisReport with peaks, events, and summary

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

        # Generate analysis report
        report = analysis_service.generate_analysis_report(timeline)

        return report

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating analysis: {str(e)}"
        )


@router.get(
    "/{chart_id}/export/planets/csv",
    summary="Export Planet Timeline as CSV",
    description="Export planet influence timeline to CSV format"
)
async def export_planets_csv(
    chart_id: str = PathParam(..., description="Chart identifier"),
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
) -> Response:
    """
    Export planet influence timeline to CSV format.

    Returns a CSV file with timestamps and planet scores.
    Suitable for spreadsheet analysis or external tools.

    Args:
        chart_id: Chart identifier
        start_date: Start of time range
        end_date: End of time range
        interval_days: Days between samples

    Returns:
        CSV file as text/csv response

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

        # Export to CSV
        csv_content, metadata = export_service.export_planet_timeline_csv(timeline)

        # Return as downloadable file
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={metadata.filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting CSV: {str(e)}"
        )


@router.get(
    "/{chart_id}/export/houses/csv",
    summary="Export House Timeline as CSV",
    description="Export house activation timeline to CSV format"
)
async def export_houses_csv(
    chart_id: str = PathParam(..., description="Chart identifier"),
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
) -> Response:
    """
    Export house activation timeline to CSV format.

    Returns a CSV file with timestamps and house activation scores.
    Suitable for spreadsheet analysis or external tools.

    Args:
        chart_id: Chart identifier
        start_date: Start of time range
        end_date: End of time range
        interval_days: Days between samples

    Returns:
        CSV file as text/csv response

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

        # Export to CSV
        csv_content, metadata = export_service.export_house_timeline_csv(timeline)

        # Return as downloadable file
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={metadata.filename}"
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting CSV: {str(e)}"
        )

