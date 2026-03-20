"""
Planet Strength Service for calculating planet strength (Shadbala).

Implements strength calculation based on:
- Dignity (exalted, own sign, friendly, neutral, enemy, debilitated)
- Retrograde status (bonus for retrograde planets)
- Combustion (penalty for planets too close to Sun)
"""
from typing import Dict
from api.models import (
    Planet,
    Sign,
    Dignity,
    NatalChart,
    PlanetPlacement,
    StrengthBreakdown,
    PlanetStrength,
    StrengthCalculation,
    DIGNITY_SCORES,
    COMBUSTION_PENALTY,
)


class StrengthService:
    """Service for calculating planet strength."""
    
    # Combustion distances (degrees from Sun)
    # Source: Traditional Vedic astrology texts
    COMBUSTION_DISTANCES = {
        Planet.MOON: 12.0,
        Planet.MARS: 17.0,
        Planet.MERCURY: 14.0,  # 14 when retrograde, 12 when direct
        Planet.JUPITER: 11.0,
        Planet.VENUS: 10.0,  # 10 when retrograde, 8 when direct
        Planet.SATURN: 15.0,
        # Rahu and Ketu cannot be combust
    }
    
    # Retrograde bonus
    RETROGRADE_BONUS = 10
    
    def __init__(self):
        """Initialize the strength service."""
        pass
    
    def is_combust(self, planet: Planet, planet_degree: float, sun_degree: float, planet_sign: Sign, sun_sign: Sign) -> bool:
        """
        Check if a planet is combust (too close to Sun).
        
        Args:
            planet: The planet to check
            planet_degree: Planet's degree in its sign
            sun_degree: Sun's degree in its sign
            planet_sign: Planet's sign
            sun_sign: Sun's sign
        
        Returns:
            bool: True if planet is combust
        """
        # Sun cannot be combust
        if planet == Planet.SUN:
            return False
        
        # Rahu and Ketu cannot be combust (shadow planets)
        if planet in [Planet.RAHU, Planet.KETU]:
            return False
        
        # Get combustion distance for this planet
        combustion_distance = self.COMBUSTION_DISTANCES.get(planet)
        if combustion_distance is None:
            return False
        
        # Calculate angular distance
        # If in same sign, simple subtraction
        if planet_sign == sun_sign:
            distance = abs(planet_degree - sun_degree)
        else:
            # If in different signs, planet is not combust
            # (combustion only occurs when in same sign)
            return False
        
        return distance <= combustion_distance
    
    def calculate_strength_breakdown(
        self,
        planet: Planet,
        placement: PlanetPlacement,
        sun_placement: PlanetPlacement
    ) -> StrengthBreakdown:
        """
        Calculate strength breakdown for a planet.
        
        Args:
            planet: The planet
            placement: Planet's placement in the chart
            sun_placement: Sun's placement (for combustion check)
        
        Returns:
            StrengthBreakdown with all components
        """
        # Dignity score
        dignity = placement.dignity or Dignity.NEUTRAL
        dignity_score = DIGNITY_SCORES.get(dignity, 0)
        
        # Retrograde bonus
        is_retrograde = placement.is_retrograde
        retrograde_score = self.RETROGRADE_BONUS if is_retrograde else 0
        
        # Combustion check
        is_combust = self.is_combust(
            planet,
            placement.degree,
            sun_placement.degree,
            placement.sign,
            sun_placement.sign
        )
        combustion_score = COMBUSTION_PENALTY if is_combust else 0
        
        # Total strength
        total_strength = dignity_score + retrograde_score + combustion_score
        
        return StrengthBreakdown(
            dignity=dignity,
            dignity_score=dignity_score,
            is_retrograde=is_retrograde,
            retrograde_score=retrograde_score,
            is_combust=is_combust,
            combustion_score=combustion_score,
            total_strength=total_strength
        )
    
    def calculate_strength_weight(self, total_strength: int) -> float:
        """
        Calculate normalized strength weight (0-100).
        
        Formula: W_strength(p) = max(0, min(100, 50 + S(p)))
        
        Args:
            total_strength: Total strength score S(p)
        
        Returns:
            Normalized strength weight (0-100)
        """
        return max(0.0, min(100.0, 50.0 + total_strength))
    
    def calculate_planet_strength(
        self,
        planet: Planet,
        placement: PlanetPlacement,
        sun_placement: PlanetPlacement
    ) -> PlanetStrength:
        """
        Calculate complete strength for a single planet.
        
        Args:
            planet: The planet
            placement: Planet's placement
            sun_placement: Sun's placement
        
        Returns:
            PlanetStrength with breakdown and weight
        """
        breakdown = self.calculate_strength_breakdown(planet, placement, sun_placement)
        strength_weight = self.calculate_strength_weight(breakdown.total_strength)
        
        return PlanetStrength(
            planet=planet,
            breakdown=breakdown,
            strength_weight=strength_weight
        )

    def calculate_chart_strengths(self, natal_chart: NatalChart) -> StrengthCalculation:
        """
        Calculate strength for all planets in a natal chart.

        Args:
            natal_chart: The natal chart

        Returns:
            StrengthCalculation with all planet strengths
        """
        planet_strengths = {}

        # Get Sun's placement for combustion checks
        sun_placement = natal_chart.planets.get(Planet.SUN)
        if not sun_placement:
            raise ValueError("Sun placement not found in chart")

        # Calculate strength for each planet
        for planet, placement in natal_chart.planets.items():
            strength = self.calculate_planet_strength(planet, placement, sun_placement)
            planet_strengths[planet] = strength

        return StrengthCalculation(
            chart_id=natal_chart.chart_id or "unknown",
            planet_strengths=planet_strengths
        )

