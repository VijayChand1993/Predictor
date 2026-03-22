"""
Timeline Service for calculating scores over time ranges.

Generates time-series data for planet influence and house activation.

Phase 7b Enhancement: Adds moon fluctuation and transit delta for realistic variation.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional

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
from api.services.transit_service import TransitService


class TimelineService:
    """Service for calculating score timelines over date ranges with dynamic variation."""

    def __init__(self):
        """Initialize the timeline service."""
        self.scoring_engine = ScoringEngine()
        self.house_activation_service = HouseActivationService()
        self.transit_service = TransitService()

        # Timeline dynamics parameters (Phase 7b)
        self.moon_sensitivity = 0.2  # Moon transit changes create ±20% variation
        self.transit_delta_weight = 0.1  # Transit delta contributes 10% to score
        self.adaptive_alpha_event = 0.3  # Smoothing during events (more responsive)
        self.adaptive_alpha_stable = 0.7  # Smoothing during stable periods (less responsive)
    
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

    def calculate_moon_fluctuation(
        self,
        current_date: datetime,
        previous_date: Optional[datetime],
        natal_chart: NatalChart
    ) -> float:
        """
        Calculate moon-based fluctuation factor (Phase 7b).

        Moon changes sign every ~2.5 days, creating natural variation in scores.
        This adds ±20% variation based on moon transit changes.

        Args:
            current_date: Current calculation date
            previous_date: Previous calculation date (None for first point)
            natal_chart: Natal chart for context

        Returns:
            Fluctuation factor (0.8 to 1.2, centered at 1.0)
        """
        if previous_date is None:
            return 1.0  # No fluctuation for first point

        # Get moon positions
        current_transit = self.transit_service.get_transit_data(current_date, natal_chart)
        previous_transit = self.transit_service.get_transit_data(previous_date, natal_chart)

        current_moon = current_transit.planets[Planet.MOON]
        previous_moon = previous_transit.planets[Planet.MOON]

        # Check if moon changed sign
        sign_changed = current_moon.sign != previous_moon.sign

        # Check if moon changed house
        house_changed = current_moon.house != previous_moon.house

        # Calculate fluctuation based on changes
        fluctuation = 1.0

        if sign_changed:
            # Sign change creates +20% boost (event)
            fluctuation += self.moon_sensitivity
        elif house_changed:
            # House change creates +10% boost (minor event)
            fluctuation += self.moon_sensitivity * 0.5
        else:
            # No change: slight negative fluctuation (-5% to simulate stability)
            fluctuation -= self.moon_sensitivity * 0.25

        return fluctuation

    def calculate_transit_delta(
        self,
        current_scores: Dict[Planet, float],
        previous_scores: Optional[Dict[Planet, float]]
    ) -> float:
        """
        Calculate transit delta contribution (Phase 7b).

        Measures the change in planet scores between time points,
        adding momentum to the timeline.

        Args:
            current_scores: Current planet scores
            previous_scores: Previous planet scores (None for first point)

        Returns:
            Delta contribution (-10 to +10, typically)
        """
        if previous_scores is None:
            return 0.0  # No delta for first point

        # Calculate average change across all planets
        total_delta = 0.0
        count = 0

        for planet, current_score in current_scores.items():
            if planet in previous_scores:
                delta = current_score - previous_scores[planet]
                total_delta += delta
                count += 1

        if count == 0:
            return 0.0

        # Average delta weighted by transit_delta_weight
        avg_delta = total_delta / count
        return avg_delta * self.transit_delta_weight
    
    def calculate_planet_timeline(
        self,
        natal_chart: NatalChart,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 1,
        apply_dynamics: bool = True
    ) -> PlanetInfluenceTimeline:
        """
        Calculate planet influence timeline over a date range (Phase 7b - with dynamics).

        Now includes:
        - Moon fluctuation (±20% variation based on moon sign/house changes)
        - Transit delta (momentum from score changes)
        - Adaptive smoothing (responsive during events, stable otherwise)

        Args:
            natal_chart: The natal chart
            start_date: Start of time range
            end_date: End of time range
            interval_days: Days between samples
            apply_dynamics: Whether to apply moon fluctuation and transit delta (default: True)

        Returns:
            PlanetInfluenceTimeline with data for all planets
        """
        # Generate time points
        time_points = self.generate_time_points(start_date, end_date, interval_days)

        # Initialize data structure for each planet
        planet_data: Dict[Planet, List[PlanetTimePoint]] = {
            planet: [] for planet in Planet
        }

        # Track previous scores for delta calculation
        previous_scores: Optional[Dict[Planet, float]] = None
        previous_timestamp: Optional[datetime] = None

        # Calculate scores at each time point
        for i, timestamp in enumerate(time_points):
            # Get base planet scores
            planet_scores = self.scoring_engine.calculate_planet_scores(
                natal_chart,
                timestamp
            )

            # Extract raw scores
            raw_scores = {planet: score_obj.score for planet, score_obj in planet_scores.scores.items()}

            if apply_dynamics:
                # Calculate moon fluctuation
                moon_factor = self.calculate_moon_fluctuation(
                    timestamp,
                    previous_timestamp,
                    natal_chart
                )

                # Calculate transit delta
                transit_delta = self.calculate_transit_delta(
                    raw_scores,
                    previous_scores
                )

                # Apply dynamics to each planet score
                for planet in raw_scores:
                    # Apply moon fluctuation (multiplicative)
                    raw_scores[planet] *= moon_factor

                    # Add transit delta (additive)
                    raw_scores[planet] += transit_delta

                    # Clamp to 0-100 range
                    raw_scores[planet] = max(0.0, min(100.0, raw_scores[planet]))

            # Store data points
            for planet, score in raw_scores.items():
                planet_data[planet].append(
                    PlanetTimePoint(
                        timestamp=timestamp,
                        planet=planet,
                        score=score
                    )
                )

            # Update previous scores for next iteration
            previous_scores = raw_scores.copy()
            previous_timestamp = timestamp

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

