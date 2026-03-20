"""
Aspect Calculation Service for planetary aspects (Drishti).

Implements Vedic astrology aspect rules:
- All planets: 7th house aspect (full aspect)
- Mars: 4th, 8th house aspects (special aspects)
- Jupiter: 5th, 9th house aspects (special aspects)
- Saturn: 3rd, 10th house aspects (special aspects)
"""
from typing import List, Dict
from api.models import (
    Planet,
    NatalChart,
    Aspect,
    PlanetAspects,
    AspectCalculation,
    AspectType,
    ASPECT_WEIGHTS,
)
from api.core.config import ScoringConfig


class AspectService:
    """Service for calculating planetary aspects (Drishti)."""
    
    def __init__(self, config: ScoringConfig = None):
        """
        Initialize the aspect service.
        
        Args:
            config: Scoring configuration (uses default if not provided)
        """
        self.config = config or ScoringConfig()
    
    def get_aspected_houses(self, planet: Planet, from_house: int) -> List[tuple[int, AspectType]]:
        """
        Get all houses aspected by a planet from a given house.

        Args:
            planet: The planet casting aspects
            from_house: House number the planet is placed in (1-12)

        Returns:
            List of tuples (house_number, aspect_type)
        """
        aspects = []

        # Helper function to calculate house number with proper wrapping
        def calc_house(offset: int) -> int:
            """Calculate house number with offset, wrapping 1-12."""
            result = ((from_house - 1 + offset) % 12) + 1
            return result

        # All planets aspect the 7th house (full aspect)
        seventh_house = calc_house(6)  # 7th house is 6 positions ahead
        aspects.append((seventh_house, AspectType.FULL))

        # Special aspects for Mars
        if planet == Planet.MARS:
            fourth_house = calc_house(3)  # 4th house is 3 positions ahead
            eighth_house = calc_house(7)  # 8th house is 7 positions ahead
            aspects.append((fourth_house, AspectType.SPECIAL_MARS))
            aspects.append((eighth_house, AspectType.SPECIAL_MARS))

        # Special aspects for Jupiter
        elif planet == Planet.JUPITER:
            fifth_house = calc_house(4)  # 5th house is 4 positions ahead
            ninth_house = calc_house(8)  # 9th house is 8 positions ahead
            aspects.append((fifth_house, AspectType.SPECIAL_JUPITER))
            aspects.append((ninth_house, AspectType.SPECIAL_JUPITER))

        # Special aspects for Saturn
        elif planet == Planet.SATURN:
            third_house = calc_house(2)  # 3rd house is 2 positions ahead
            tenth_house = calc_house(9)  # 10th house is 9 positions ahead
            aspects.append((third_house, AspectType.SPECIAL_SATURN))
            aspects.append((tenth_house, AspectType.SPECIAL_SATURN))

        return aspects
    
    def calculate_aspect_weight(
        self,
        planet: Planet,
        from_house: int
    ) -> float:
        """
        Calculate aspect weight for a planet.
        
        Formula: W_aspect(p) = Σ [A(p→h) × AspectWeight × HouseWeight(h)] × 20
        
        Args:
            planet: The planet
            from_house: House the planet is placed in
        
        Returns:
            Aspect weight (0-100 range)
        """
        aspected_houses = self.get_aspected_houses(planet, from_house)
        
        total_weight = 0.0
        for house_num, aspect_type in aspected_houses:
            aspect_weight = ASPECT_WEIGHTS[aspect_type]
            house_weight = self.config.house_importance.get_house_weight(house_num)
            total_weight += aspect_weight * house_weight
        
        # Apply scaling factor (× 20)
        return total_weight * self.config.aspect_scaling_factor
    
    def calculate_planet_aspects(
        self,
        planet: Planet,
        from_house: int
    ) -> PlanetAspects:
        """
        Calculate all aspects for a single planet.
        
        Args:
            planet: The planet
            from_house: House the planet is placed in
        
        Returns:
            PlanetAspects object with all aspect details
        """
        aspected_houses = self.get_aspected_houses(planet, from_house)
        
        aspects = []
        for house_num, aspect_type in aspected_houses:
            aspect_weight = ASPECT_WEIGHTS[aspect_type]
            house_weight = self.config.house_importance.get_house_weight(house_num)
            
            aspect = Aspect(
                from_planet=planet,
                to_house=house_num,
                aspect_type=aspect_type,
                aspect_weight=aspect_weight,
                house_weight=house_weight
            )
            aspects.append(aspect)
        
        # Calculate total aspect weight
        total_weight = self.calculate_aspect_weight(planet, from_house)
        
        return PlanetAspects(
            planet=planet,
            from_house=from_house,
            aspects=aspects,
            aspect_weight=total_weight
        )
    
    def calculate_chart_aspects(self, natal_chart: NatalChart) -> AspectCalculation:
        """
        Calculate aspects for all planets in a natal chart.
        
        Args:
            natal_chart: The natal chart
        
        Returns:
            AspectCalculation with all planet aspects
        """
        planet_aspects = {}
        
        for planet, placement in natal_chart.planets.items():
            aspects = self.calculate_planet_aspects(planet, placement.house)
            planet_aspects[planet] = aspects
        
        return AspectCalculation(
            chart_id=natal_chart.chart_id or "unknown",
            planet_aspects=planet_aspects
        )

