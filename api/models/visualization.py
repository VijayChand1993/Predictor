"""
Visualization models for chart-ready data and analysis.
"""
from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .enums import Planet


class ChartDataPoint(BaseModel):
    """A single data point for charting libraries (e.g., Chart.js, D3)."""
    x: datetime = Field(..., description="X-axis value (timestamp)")
    y: float = Field(..., description="Y-axis value (score)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "x": "2026-03-15T00:00:00",
                "y": 15.8
            }
        }


class ChartDataset(BaseModel):
    """A dataset for charting (one line/series in a chart)."""
    label: str = Field(..., description="Dataset label (e.g., planet name)")
    data: List[ChartDataPoint] = Field(..., description="Data points for this series")
    
    class Config:
        json_schema_extra = {
            "example": {
                "label": "Jupiter",
                "data": [
                    {"x": "2026-03-01T00:00:00", "y": 14.2},
                    {"x": "2026-03-15T00:00:00", "y": 16.5}
                ]
            }
        }


class ChartVisualization(BaseModel):
    """Complete chart visualization data ready for frontend charting libraries."""
    chart_id: str = Field(..., description="Chart identifier")
    title: str = Field(..., description="Chart title")
    start_date: datetime = Field(..., description="Start of time range")
    end_date: datetime = Field(..., description="End of time range")
    datasets: List[ChartDataset] = Field(..., description="All datasets (one per planet/house)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "title": "Planet Influence Timeline",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "datasets": [
                    {
                        "label": "Jupiter",
                        "data": [
                            {"x": "2026-03-01T00:00:00", "y": 14.2},
                            {"x": "2026-03-15T00:00:00", "y": 16.5}
                        ]
                    }
                ]
            }
        }


class HeatmapCell(BaseModel):
    """A single cell in a heatmap."""
    row: int = Field(..., description="Row index (e.g., house number)")
    col: int = Field(..., description="Column index (e.g., time period)")
    value: float = Field(..., description="Cell value (score)")
    label: str = Field(..., description="Cell label for tooltip")
    
    class Config:
        json_schema_extra = {
            "example": {
                "row": 10,
                "col": 2,
                "value": 13.8,
                "label": "House 10, Week 2: 13.8"
            }
        }


class HeatmapVisualization(BaseModel):
    """Heatmap visualization data for house activations over time."""
    chart_id: str = Field(..., description="Chart identifier")
    title: str = Field(..., description="Heatmap title")
    start_date: datetime = Field(..., description="Start of time range")
    end_date: datetime = Field(..., description="End of time range")
    row_labels: List[str] = Field(..., description="Row labels (house names)")
    col_labels: List[str] = Field(..., description="Column labels (time periods)")
    cells: List[HeatmapCell] = Field(..., description="All heatmap cells")
    min_value: float = Field(..., description="Minimum value for color scale")
    max_value: float = Field(..., description="Maximum value for color scale")
    
    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "title": "House Activation Heatmap",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "row_labels": ["House 1", "House 2", "..."],
                "col_labels": ["Week 1", "Week 2", "..."],
                "cells": [
                    {"row": 1, "col": 1, "value": 8.5, "label": "House 1, Week 1: 8.5"}
                ],
                "min_value": 5.0,
                "max_value": 15.0
            }
        }


class PeakInfluence(BaseModel):
    """Information about a peak influence period."""
    entity: str = Field(..., description="Planet or house name")
    peak_score: float = Field(..., description="Peak score value")
    peak_time: datetime = Field(..., description="When the peak occurred")
    duration_days: int = Field(..., description="Duration of elevated influence (days)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "entity": "Jupiter",
                "peak_score": 18.5,
                "peak_time": "2026-03-15T00:00:00",
                "duration_days": 7
            }
        }


class SignificantEvent(BaseModel):
    """A significant astrological event detected in the timeline."""
    event_type: str = Field(..., description="Type of event (e.g., 'peak_influence', 'transit_change')")
    description: str = Field(..., description="Human-readable description")
    timestamp: datetime = Field(..., description="When the event occurs")
    entities: List[str] = Field(..., description="Affected planets/houses")
    significance: float = Field(..., ge=0, le=100, description="Significance score (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "peak_influence",
                "description": "Jupiter reaches peak influence",
                "timestamp": "2026-03-15T00:00:00",
                "entities": ["Jupiter"],
                "significance": 85.0
            }
        }


class AnalysisReport(BaseModel):
    """Complete analysis report for a time period."""
    chart_id: str = Field(..., description="Chart identifier")
    start_date: datetime = Field(..., description="Start of analysis period")
    end_date: datetime = Field(..., description="End of analysis period")
    peak_influences: List[PeakInfluence] = Field(..., description="Peak influence periods")
    significant_events: List[SignificantEvent] = Field(..., description="Significant events detected")
    summary: str = Field(..., description="Text summary of the analysis")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "peak_influences": [
                    {
                        "entity": "Jupiter",
                        "peak_score": 18.5,
                        "peak_time": "2026-03-15T00:00:00",
                        "duration_days": 7
                    }
                ],
                "significant_events": [
                    {
                        "event_type": "peak_influence",
                        "description": "Jupiter reaches peak influence",
                        "timestamp": "2026-03-15T00:00:00",
                        "entities": ["Jupiter"],
                        "significance": 85.0
                    }
                ],
                "summary": "Jupiter shows strong influence mid-month with peak on March 15th."
            }
        }


class ExportFormat(BaseModel):
    """Base class for export formats."""
    chart_id: str = Field(..., description="Chart identifier")
    start_date: datetime = Field(..., description="Start of time range")
    end_date: datetime = Field(..., description="End of time range")
    generated_at: datetime = Field(default_factory=datetime.now, description="When export was generated")


class CSVExportMetadata(ExportFormat):
    """Metadata for CSV export."""
    filename: str = Field(..., description="Suggested filename")
    rows: int = Field(..., description="Number of data rows")
    columns: List[str] = Field(..., description="Column names")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_id": "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5",
                "start_date": "2026-03-01T00:00:00",
                "end_date": "2026-03-31T23:59:59",
                "generated_at": "2026-03-20T12:00:00",
                "filename": "planet_scores_2026-03.csv",
                "rows": 30,
                "columns": ["timestamp", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
            }
        }

