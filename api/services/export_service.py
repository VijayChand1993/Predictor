"""
Export Service for generating CSV and JSON exports.
"""
import csv
import json
from io import StringIO
from datetime import datetime
from typing import Dict, List

from api.models import (
    Planet,
    PlanetInfluenceTimeline,
    HouseActivationTimeline,
    CSVExportMetadata,
)


class ExportService:
    """Service for exporting timeline data to various formats."""
    
    def export_planet_timeline_csv(
        self,
        timeline: PlanetInfluenceTimeline
    ) -> tuple[str, CSVExportMetadata]:
        """
        Export planet timeline to CSV format.
        
        Args:
            timeline: Planet influence timeline
        
        Returns:
            Tuple of (CSV content as string, metadata)
        """
        # Create CSV in memory
        output = StringIO()
        
        # Get all timestamps from first planet
        first_planet = list(timeline.timelines.values())[0]
        timestamps = [dp.timestamp for dp in first_planet.data_points]
        
        # Create column headers
        columns = ["timestamp"] + [planet.value for planet in Planet]
        
        # Write CSV
        writer = csv.writer(output)
        writer.writerow(columns)
        
        # Write data rows
        for i, timestamp in enumerate(timestamps):
            row = [timestamp.isoformat()]
            
            for planet in Planet:
                if planet in timeline.timelines:
                    score = timeline.timelines[planet].data_points[i].score
                    row.append(f"{score:.2f}")
                else:
                    row.append("")
            
            writer.writerow(row)
        
        # Create metadata
        filename = f"planet_scores_{timeline.start_date.strftime('%Y-%m')}.csv"
        metadata = CSVExportMetadata(
            chart_id=timeline.chart_id,
            start_date=timeline.start_date,
            end_date=timeline.end_date,
            filename=filename,
            rows=len(timestamps),
            columns=columns
        )
        
        return output.getvalue(), metadata
    
    def export_house_timeline_csv(
        self,
        timeline: HouseActivationTimeline
    ) -> tuple[str, CSVExportMetadata]:
        """
        Export house timeline to CSV format.
        
        Args:
            timeline: House activation timeline
        
        Returns:
            Tuple of (CSV content as string, metadata)
        """
        # Create CSV in memory
        output = StringIO()
        
        # Get all timestamps from first house
        first_house = list(timeline.timelines.values())[0]
        timestamps = [dp.timestamp for dp in first_house.data_points]
        
        # Create column headers
        columns = ["timestamp"] + [f"House_{i}" for i in range(1, 13)]
        
        # Write CSV
        writer = csv.writer(output)
        writer.writerow(columns)
        
        # Write data rows
        for i, timestamp in enumerate(timestamps):
            row = [timestamp.isoformat()]
            
            for house_num in range(1, 13):
                if house_num in timeline.timelines:
                    score = timeline.timelines[house_num].data_points[i].score
                    row.append(f"{score:.2f}")
                else:
                    row.append("")
            
            writer.writerow(row)
        
        # Create metadata
        filename = f"house_activation_{timeline.start_date.strftime('%Y-%m')}.csv"
        metadata = CSVExportMetadata(
            chart_id=timeline.chart_id,
            start_date=timeline.start_date,
            end_date=timeline.end_date,
            filename=filename,
            rows=len(timestamps),
            columns=columns
        )
        
        return output.getvalue(), metadata
    
    def export_planet_timeline_json(
        self,
        timeline: PlanetInfluenceTimeline
    ) -> str:
        """
        Export planet timeline to JSON format.
        
        Args:
            timeline: Planet influence timeline
        
        Returns:
            JSON string
        """
        # Convert to dict and serialize
        return timeline.model_dump_json(indent=2)
    
    def export_house_timeline_json(
        self,
        timeline: HouseActivationTimeline
    ) -> str:
        """
        Export house timeline to JSON format.
        
        Args:
            timeline: House activation timeline
        
        Returns:
            JSON string
        """
        # Convert to dict and serialize
        return timeline.model_dump_json(indent=2)

