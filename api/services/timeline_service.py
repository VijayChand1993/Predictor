"""
Timeline Service for calculating scores over time ranges.

Generates time-series data for planet influence and house activation.
"""
from datetime import datetime, timedelta
from typing import Dict, List

from api.models import (
    Planet,
    NatalChart,
    PlanetTimePoint,
    HouseTimePoint,
    PlanetTimeline,
    HouseTimeline,
    PlanetInfluenceTimeline,
    HouseActivationTimeline,
)
from api.services.scoring_engine import ScoringEngine
from api.services.house_activation_service import HouseActivationService


class TimelineService:
    """Service for calculating score timelines over date ranges."""
    
    def __init__(self):
        """Initialize the timeline service."""
        self.scoring_engine = ScoringEngine()
        self.house_activation_service = HouseActivationService()
    
    def generate_time_points(
        self,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 1
    ) -> List[datetime]:
        """
        Generate time points for sampling scores.
        
        Args:
            start_date: Start of time range
            end_date: End of time range
            interval_days: Days between samples (default: 1 day)
        
        Returns:
            List of datetime points to sample
        """
        time_points = []
        current = start_date
        
        while current <= end_date:
            time_points.append(current)
            current += timedelta(days=interval_days)
        
        # Always include the end date if not already included
        if time_points[-1] != end_date:
            time_points.append(end_date)
        
        return time_points
    
    def calculate_planet_timeline(
        self,
        natal_chart: NatalChart,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 1
    ) -> PlanetInfluenceTimeline:
        """
        Calculate planet influence timeline over a date range.
        
        Args:
            natal_chart: The natal chart
            start_date: Start of time range
            end_date: End of time range
            interval_days: Days between samples
        
        Returns:
            PlanetInfluenceTimeline with data for all planets
        """
        # Generate time points
        time_points = self.generate_time_points(start_date, end_date, interval_days)
        
        # Initialize data structure for each planet
        planet_data: Dict[Planet, List[PlanetTimePoint]] = {
            planet: [] for planet in Planet
        }
        
        # Calculate scores at each time point
        for timestamp in time_points:
            planet_scores = self.scoring_engine.calculate_planet_scores(
                natal_chart,
                timestamp
            )
            
            for planet, score_obj in planet_scores.scores.items():
                planet_data[planet].append(
                    PlanetTimePoint(
                        timestamp=timestamp,
                        planet=planet,
                        score=score_obj.score
                    )
                )
        
        # Build timeline for each planet
        timelines = {}
        for planet, data_points in planet_data.items():
            if not data_points:
                continue
            
            scores = [dp.score for dp in data_points]
            average_score = sum(scores) / len(scores)
            peak_score = max(scores)
            peak_index = scores.index(peak_score)
            peak_time = data_points[peak_index].timestamp
            
            timelines[planet] = PlanetTimeline(
                planet=planet,
                data_points=data_points,
                average_score=average_score,
                peak_score=peak_score,
                peak_time=peak_time
            )
        
        return PlanetInfluenceTimeline(
            chart_id=natal_chart.chart_id or "unknown",
            start_date=start_date,
            end_date=end_date,
            timelines=timelines
        )
    
    def calculate_house_timeline(
        self,
        natal_chart: NatalChart,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 1
    ) -> HouseActivationTimeline:
        """
        Calculate house activation timeline over a date range.
        
        Args:
            natal_chart: The natal chart
            start_date: Start of time range
            end_date: End of time range
            interval_days: Days between samples
        
        Returns:
            HouseActivationTimeline with data for all houses
        """
        # Generate time points
        time_points = self.generate_time_points(start_date, end_date, interval_days)
        
        # Initialize data structure for each house
        house_data: Dict[int, List[HouseTimePoint]] = {
            house: [] for house in range(1, 13)
        }
        
        # Calculate activations at each time point
        for timestamp in time_points:
            house_activation = self.house_activation_service.calculate_house_activation(
                natal_chart,
                timestamp
            )
            
            for house_num, activation in house_activation.house_activations.items():
                house_data[house_num].append(
                    HouseTimePoint(
                        timestamp=timestamp,
                        house=house_num,
                        score=activation.score
                    )
                )
        
        # Build timeline for each house
        timelines = {}
        for house_num, data_points in house_data.items():
            if not data_points:
                continue
            
            scores = [dp.score for dp in data_points]
            average_score = sum(scores) / len(scores)
            peak_score = max(scores)
            peak_index = scores.index(peak_score)
            peak_time = data_points[peak_index].timestamp
            
            timelines[house_num] = HouseTimeline(
                house=house_num,
                data_points=data_points,
                average_score=average_score,
                peak_score=peak_score,
                peak_time=peak_time
            )
        
        return HouseActivationTimeline(
            chart_id=natal_chart.chart_id or "unknown",
            start_date=start_date,
            end_date=end_date,
            timelines=timelines
        )

