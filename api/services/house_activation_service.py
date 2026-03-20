"""
House Activation Service for distributing planet scores to houses.

Distributes each planet's score to houses based on:
- Transit house: 30%
- Owned houses: 30% (split if 2 houses)
- Natal placement: 20%
- Aspected houses: 20% (split equally)

Formula: H_raw(h) = Σ C(p → h)
Normalized: H(h) = 100 × H_raw(h) / Σ H_raw(all houses)
"""
from datetime import datetime
from typing import Dict, List

from api.models import (
    Planet,
    NatalChart,
    HouseContribution,
    PlanetHouseContributions,
    HouseActivation,
    HouseActivationCalculation,
)
from api.services.scoring_engine import ScoringEngine
from api.services.aspect_service import AspectService
from api.services.transit_service import TransitService


class HouseActivationService:
    """Service for calculating house activation scores from planet scores."""
    
    # Distribution percentages
    TRANSIT_PERCENTAGE = 0.30  # 30%
    OWNERSHIP_PERCENTAGE = 0.30  # 30%
    NATAL_PERCENTAGE = 0.20  # 20%
    ASPECT_PERCENTAGE = 0.20  # 20%
    
    def __init__(self):
        """Initialize the house activation service."""
        self.scoring_engine = ScoringEngine()
        self.aspect_service = AspectService()
        self.transit_service = TransitService()
    
    def get_owned_houses(self, planet: Planet, natal_chart: NatalChart) -> List[int]:
        """
        Get houses owned (ruled) by a planet.
        
        Args:
            planet: The planet
            natal_chart: The natal chart
        
        Returns:
            List of house numbers owned by the planet
        """
        owned_houses = []
        for house_num, house_info in natal_chart.houses.items():
            if house_info.lord == planet:
                owned_houses.append(house_num)
        return owned_houses
    
    def get_aspected_houses(self, planet: Planet, natal_chart: NatalChart) -> List[int]:
        """
        Get houses aspected by a planet.
        
        Args:
            planet: The planet
            natal_chart: The natal chart
        
        Returns:
            List of house numbers aspected by the planet
        """
        planet_placement = natal_chart.planets[planet]
        from_house = planet_placement.house
        
        # Get aspected houses from aspect service
        aspected = self.aspect_service.get_aspected_houses(planet, from_house)
        
        # Extract just the house numbers
        return [house_num for house_num, _ in aspected]
    
    def calculate_planet_house_contributions(
        self,
        planet: Planet,
        planet_score: float,
        natal_chart: NatalChart,
        calculation_date: datetime
    ) -> PlanetHouseContributions:
        """
        Calculate how a planet's score is distributed to houses.
        
        Args:
            planet: The planet
            planet_score: The planet's total score (0-100)
            natal_chart: The natal chart
            calculation_date: Date/time for calculation
        
        Returns:
            PlanetHouseContributions with distribution to all houses
        """
        contributions = {}
        
        # Get planet's natal house
        natal_house = natal_chart.planets[planet].house
        
        # Get transit house
        transit_data = self.transit_service.get_transit_data(
            target_date=calculation_date,
            natal_chart=natal_chart,
            save_json=False
        )
        transit_house = transit_data.planets[planet].house if planet in transit_data.planets else natal_house
        
        # Get owned houses
        owned_houses = self.get_owned_houses(planet, natal_chart)
        
        # Get aspected houses
        aspected_houses = self.get_aspected_houses(planet, natal_chart)
        
        # Calculate contributions for each house
        for house_num in range(1, 13):
            transit_contrib = 0.0
            natal_contrib = 0.0
            ownership_contrib = 0.0
            aspect_contrib = 0.0
            
            # Transit contribution (30%)
            if house_num == transit_house:
                transit_contrib = planet_score * self.TRANSIT_PERCENTAGE
            
            # Natal placement contribution (20%)
            if house_num == natal_house:
                natal_contrib = planet_score * self.NATAL_PERCENTAGE
            
            # Ownership contribution (30%, split if multiple)
            if house_num in owned_houses:
                ownership_contrib = (planet_score * self.OWNERSHIP_PERCENTAGE) / len(owned_houses)
            
            # Aspect contribution (20%, split equally)
            if house_num in aspected_houses:
                aspect_contrib = (planet_score * self.ASPECT_PERCENTAGE) / len(aspected_houses)
            
            # Total contribution to this house
            total_contrib = transit_contrib + natal_contrib + ownership_contrib + aspect_contrib
            
            # Only add if there's a contribution
            if total_contrib > 0:
                contributions[house_num] = HouseContribution(
                    house=house_num,
                    transit_contribution=transit_contrib,
                    natal_contribution=natal_contrib,
                    ownership_contribution=ownership_contrib,
                    aspect_contribution=aspect_contrib,
                    total_contribution=total_contrib
                )
        
        return PlanetHouseContributions(
            planet=planet,
            planet_score=planet_score,
            contributions=contributions
        )

    def aggregate_house_scores(
        self,
        planet_contributions: Dict[Planet, PlanetHouseContributions]
    ) -> Dict[int, HouseActivation]:
        """
        Aggregate contributions from all planets to calculate house scores.

        Args:
            planet_contributions: Contributions from all planets

        Returns:
            Dict mapping house number to HouseActivation
        """
        # Initialize raw scores for all houses
        house_raw_scores = {h: 0.0 for h in range(1, 13)}
        house_contributors = {h: {} for h in range(1, 13)}

        # Sum contributions from all planets
        for planet, planet_contrib in planet_contributions.items():
            for house_num, contribution in planet_contrib.contributions.items():
                house_raw_scores[house_num] += contribution.total_contribution
                house_contributors[house_num][planet] = contribution.total_contribution

        # Calculate total raw score
        total_raw = sum(house_raw_scores.values())

        # Handle edge case of zero total
        if total_raw == 0:
            # Equal distribution if all scores are zero
            normalized_scores = {h: 100.0 / 12 for h in range(1, 13)}
        else:
            # Normalize scores to sum to 100
            normalized_scores = {
                h: (raw_score / total_raw) * 100.0
                for h, raw_score in house_raw_scores.items()
            }

        # Build HouseActivation objects
        house_activations = {}
        for house_num in range(1, 13):
            house_activations[house_num] = HouseActivation(
                house=house_num,
                score=normalized_scores[house_num],
                raw_score=house_raw_scores[house_num],
                contributors=house_contributors[house_num]
            )

        return house_activations

    def calculate_house_activation(
        self,
        natal_chart: NatalChart,
        calculation_date: datetime
    ) -> HouseActivationCalculation:
        """
        Calculate house activation scores for a natal chart.

        This is the main method that:
        1. Calculates planet scores using ScoringEngine
        2. Distributes each planet's score to houses
        3. Aggregates contributions from all planets
        4. Normalizes house scores to sum to 100

        Args:
            natal_chart: The natal chart
            calculation_date: Date/time for calculation

        Returns:
            HouseActivationCalculation with complete house activation
        """
        # Step 1: Calculate planet scores
        planet_scores = self.scoring_engine.calculate_planet_scores(
            natal_chart,
            calculation_date
        )

        # Step 2: Calculate house contributions for each planet
        planet_contributions = {}
        for planet, score_obj in planet_scores.scores.items():
            contributions = self.calculate_planet_house_contributions(
                planet,
                score_obj.score,
                natal_chart,
                calculation_date
            )
            planet_contributions[planet] = contributions

        # Step 3: Aggregate house scores
        house_activations = self.aggregate_house_scores(planet_contributions)

        return HouseActivationCalculation(
            chart_id=natal_chart.chart_id or "unknown",
            calculation_date=calculation_date,
            house_activations=house_activations,
            planet_contributions=planet_contributions
        )

