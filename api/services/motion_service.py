"""
Motion/Speed Service for calculating planet motion weights.

Calculates motion factor based on:
- Planet speed (degrees per day)
- Motion classification (fast, normal, slow, stationary, retrograde)
- Significance for dynamic planets (Moon, Mars, Mercury)

Formula: W_motion(p) = 50 + motion_modifier(p)
"""
from datetime import datetime
from typing import Dict

from api.models import (
    Planet,
    MotionType,
    MOTION_MODIFIERS,
    NatalChart,
    MotionBreakdown,
    PlanetMotion,
    MotionCalculation,
    TransitPlacement,
)
from api.services.transit_service import TransitService


class MotionService:
    """Service for calculating planet motion weights."""
    
    # Planets where motion is significant
    SIGNIFICANT_PLANETS = {Planet.MOON, Planet.MARS, Planet.MERCURY}
    
    def __init__(self):
        """Initialize the motion service."""
        self.transit_service = TransitService()
    
    def is_motion_significant(self, planet: Planet) -> bool:
        """
        Check if motion is significant for a planet.
        
        Motion is most significant for fast-moving planets:
        - Moon (fastest)
        - Mars
        - Mercury
        
        For slower planets (Jupiter, Saturn), motion has less impact.
        
        Args:
            planet: The planet to check
        
        Returns:
            True if motion is significant for this planet
        """
        return planet in self.SIGNIFICANT_PLANETS
    
    def calculate_motion_breakdown(
        self,
        planet: Planet,
        transit_placement: TransitPlacement
    ) -> MotionBreakdown:
        """
        Calculate motion breakdown for a planet.
        
        Args:
            planet: The planet
            transit_placement: Transit placement with speed and motion type
        
        Returns:
            MotionBreakdown with speed, motion type, and modifier
        """
        speed = transit_placement.speed
        motion_type = transit_placement.motion_type
        
        # Get motion modifier from constants
        motion_modifier = MOTION_MODIFIERS.get(motion_type, 0)
        
        # Check if motion is significant for this planet
        is_significant = self.is_motion_significant(planet)
        
        return MotionBreakdown(
            speed=speed,
            motion_type=motion_type,
            motion_modifier=motion_modifier,
            is_significant=is_significant
        )
    
    def calculate_motion_weight(self, motion_modifier: int, is_significant: bool) -> float:
        """
        Calculate normalized motion weight (0-100).
        
        Formula from scoreLogic.md:
        W_motion(p) = 50 + motion_modifier(p)
        
        For planets where motion is not significant, use baseline of 50.
        
        Args:
            motion_modifier: Motion modifier score (0 to +15)
            is_significant: Whether motion is significant for this planet
        
        Returns:
            Motion weight (0-100)
        """
        if not is_significant:
            # For slow-moving planets, use neutral baseline
            return 50.0
        
        # Apply motion modifier
        weight = 50 + motion_modifier
        
        # Ensure bounds (should already be in range, but safety check)
        return max(0.0, min(100.0, float(weight)))
    
    def calculate_planet_motion(
        self,
        planet: Planet,
        transit_placement: TransitPlacement
    ) -> PlanetMotion:
        """
        Calculate complete motion for a single planet.
        
        Args:
            planet: The planet
            transit_placement: Transit placement with speed and motion type
        
        Returns:
            PlanetMotion with breakdown and weight
        """
        # Calculate breakdown
        breakdown = self.calculate_motion_breakdown(planet, transit_placement)
        
        # Calculate weight
        motion_weight = self.calculate_motion_weight(
            breakdown.motion_modifier,
            breakdown.is_significant
        )
        
        return PlanetMotion(
            planet=planet,
            breakdown=breakdown,
            motion_weight=motion_weight
        )
    
    def calculate_chart_motions(
        self,
        natal_chart: NatalChart,
        calculation_date: datetime
    ) -> MotionCalculation:
        """
        Calculate motion for all planets at a specific time.
        
        Uses transit service to get current planet positions and speeds.
        
        Args:
            natal_chart: The natal chart
            calculation_date: Date/time for motion calculation
        
        Returns:
            MotionCalculation with all planet motions
        """
        # Get transit data for the calculation date
        transit_data = self.transit_service.get_transit_data(
            target_date=calculation_date,
            natal_chart=natal_chart,
            save_json=False
        )
        
        planet_motions = {}
        
        # Calculate motion for each planet
        for planet, transit_placement in transit_data.planets.items():
            motion = self.calculate_planet_motion(planet, transit_placement)
            planet_motions[planet] = motion
        
        return MotionCalculation(
            chart_id=natal_chart.chart_id or "unknown",
            calculation_date=calculation_date,
            planet_motions=planet_motions
        )

