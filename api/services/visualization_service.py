"""
Visualization Service for transforming timeline data into chart-ready formats.
"""
from datetime import datetime
from typing import List

from api.models import (
    PlanetInfluenceTimeline,
    HouseActivationTimeline,
    ChartDataPoint,
    ChartDataset,
    ChartVisualization,
    HeatmapCell,
    HeatmapVisualization,
)


class VisualizationService:
    """Service for creating visualization-ready data from timelines."""
    
    def create_planet_chart(
        self,
        timeline: PlanetInfluenceTimeline,
        title: str = "Planet Influence Timeline"
    ) -> ChartVisualization:
        """
        Transform planet timeline into chart visualization data.
        
        Args:
            timeline: Planet influence timeline
            title: Chart title
        
        Returns:
            ChartVisualization ready for frontend charting libraries
        """
        datasets = []
        
        # Create a dataset for each planet
        for planet, planet_timeline in timeline.timelines.items():
            data_points = [
                ChartDataPoint(
                    x=dp.timestamp,
                    y=dp.score
                )
                for dp in planet_timeline.data_points
            ]
            
            datasets.append(
                ChartDataset(
                    label=planet.value,
                    data=data_points
                )
            )
        
        return ChartVisualization(
            chart_id=timeline.chart_id,
            title=title,
            start_date=timeline.start_date,
            end_date=timeline.end_date,
            datasets=datasets
        )
    
    def create_house_chart(
        self,
        timeline: HouseActivationTimeline,
        title: str = "House Activation Timeline"
    ) -> ChartVisualization:
        """
        Transform house timeline into chart visualization data.
        
        Args:
            timeline: House activation timeline
            title: Chart title
        
        Returns:
            ChartVisualization ready for frontend charting libraries
        """
        datasets = []
        
        # Create a dataset for each house
        for house_num, house_timeline in timeline.timelines.items():
            data_points = [
                ChartDataPoint(
                    x=dp.timestamp,
                    y=dp.score
                )
                for dp in house_timeline.data_points
            ]
            
            datasets.append(
                ChartDataset(
                    label=f"House {house_num}",
                    data=data_points
                )
            )
        
        return ChartVisualization(
            chart_id=timeline.chart_id,
            title=title,
            start_date=timeline.start_date,
            end_date=timeline.end_date,
            datasets=datasets
        )
    
    def create_house_heatmap(
        self,
        timeline: HouseActivationTimeline,
        title: str = "House Activation Heatmap"
    ) -> HeatmapVisualization:
        """
        Transform house timeline into heatmap visualization data.
        
        Args:
            timeline: House activation timeline
            title: Heatmap title
        
        Returns:
            HeatmapVisualization with cells for each house/time combination
        """
        # Create row labels (houses)
        row_labels = [f"House {i}" for i in range(1, 13)]
        
        # Create column labels (time periods)
        # Use the timestamps from the first house's data points
        first_house = list(timeline.timelines.values())[0]
        col_labels = [
            dp.timestamp.strftime("%b %d")
            for dp in first_house.data_points
        ]
        
        # Create cells
        cells = []
        min_value = float('inf')
        max_value = float('-inf')
        
        for house_num, house_timeline in timeline.timelines.items():
            row = house_num - 1  # 0-indexed
            
            for col, dp in enumerate(house_timeline.data_points):
                value = dp.score
                min_value = min(min_value, value)
                max_value = max(max_value, value)
                
                cells.append(
                    HeatmapCell(
                        row=house_num,
                        col=col,
                        value=value,
                        label=f"House {house_num}, {col_labels[col]}: {value:.1f}"
                    )
                )
        
        return HeatmapVisualization(
            chart_id=timeline.chart_id,
            title=title,
            start_date=timeline.start_date,
            end_date=timeline.end_date,
            row_labels=row_labels,
            col_labels=col_labels,
            cells=cells,
            min_value=min_value,
            max_value=max_value
        )

