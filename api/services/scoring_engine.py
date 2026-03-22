"""
Core Scoring Engine for calculating planet scores.

Orchestrates all services to calculate final planet scores:
- Dasha (35%)
- Transit (25%)
- Strength (20%)
- Aspect (12%)
- Motion (8%)

Formula: P_raw(p) = 0.35×W_dasha + 0.25×W_transit + 0.20×W_strength + 0.12×W_aspect + 0.08×W_motion
Normalized: P(p) = 100 × P_raw(p) / Σ P_raw(all planets)
"""
from datetime import datetime
from typing import Dict
import json
from pathlib import Path as FilePath

from api.models import (
    Planet,
    NatalChart,
    ComponentBreakdown,
    WeightedComponents,
    PlanetScore,
    PlanetScores,
)
from api.services.dasha_service import DashaService
from api.services.transit_service import TransitService
from api.services.aspect_service import AspectService
from api.services.strength_service import StrengthService
from api.services.motion_service import MotionService


class ScoringEngine:
    """Core scoring engine for calculating planet scores."""
    
    # Component weights (must sum to 1.0)
    WEIGHT_DASHA = 0.35
    WEIGHT_TRANSIT = 0.25
    WEIGHT_STRENGTH = 0.20
    WEIGHT_ASPECT = 0.12
    WEIGHT_MOTION = 0.08
    
    def __init__(self):
        """Initialize the scoring engine with all required services."""
        self.dasha_service = DashaService()
        self.transit_service = TransitService()
        self.aspect_service = AspectService()
        self.strength_service = StrengthService()
        self.motion_service = MotionService()
    
    def calculate_component_breakdown(
        self,
        planet: Planet,
        natal_chart: NatalChart,
        calculation_date: datetime
    ) -> ComponentBreakdown:
        """
        Calculate all component scores for a planet.

        Args:
            planet: The planet
            natal_chart: The natal chart
            calculation_date: Date/time for calculation

        Returns:
            ComponentBreakdown with all component scores (0-100)
        """
        # 1. Dasha weight
        # Load chart JSON for dasha calculation
        chart_path = FilePath(f"output/chart_{natal_chart.chart_id}.json")
        if chart_path.exists():
            with open(chart_path, 'r') as f:
                chart_json = json.load(f)
            active_dashas = self.dasha_service.get_active_dashas(
                chart_json,
                calculation_date.date()
            )
            dasha_weight_obj = self.dasha_service.calculate_dasha_weight(planet, active_dashas)
            dasha_weight = dasha_weight_obj.total_weight
        else:
            # Default if chart JSON not found
            dasha_weight = 50.0
        
        # 2. Transit weight
        transit_data = self.transit_service.get_transit_data(
            target_date=calculation_date,
            natal_chart=natal_chart,
            save_json=False
        )
        if planet in transit_data.planets:
            transit_placement = transit_data.planets[planet]
            transit_weight = self.transit_service.calculate_transit_weight(
                planet,
                transit_placement.house
            )
        else:
            transit_weight = 50.0  # Default if planet not found
        
        # 3. Strength weight (using TRANSIT positions for dynamic calculation)
        # Get transit placements for the planet and Sun
        if planet in transit_data.planets and Planet.SUN in transit_data.planets:
            transit_placement = transit_data.planets[planet]
            sun_transit = transit_data.planets[Planet.SUN]
            planet_strength = self.strength_service.calculate_strength_from_transit(
                planet,
                transit_placement,
                sun_transit
            )
            strength_weight = planet_strength.strength_weight
        else:
            # Fallback to natal if transit data not available
            sun_placement = natal_chart.planets[Planet.SUN]
            planet_placement = natal_chart.planets[planet]
            planet_strength = self.strength_service.calculate_planet_strength(
                planet,
                planet_placement,
                sun_placement
            )
            strength_weight = planet_strength.strength_weight
        
        # 4. Aspect weight
        aspect_calculation = self.aspect_service.calculate_chart_aspects(natal_chart)
        if planet in aspect_calculation.planet_aspects:
            aspect_weight = aspect_calculation.planet_aspects[planet].aspect_weight
        else:
            aspect_weight = 0.0  # No aspects
        
        # 5. Motion weight
        motion_calculation = self.motion_service.calculate_chart_motions(
            natal_chart,
            calculation_date
        )
        if planet in motion_calculation.planet_motions:
            motion_weight = motion_calculation.planet_motions[planet].motion_weight
        else:
            motion_weight = 50.0  # Default baseline
        
        return ComponentBreakdown(
            dasha=dasha_weight,
            transit=transit_weight,
            strength=strength_weight,
            aspect=aspect_weight,
            motion=motion_weight
        )
    
    def calculate_weighted_components(
        self,
        breakdown: ComponentBreakdown
    ) -> WeightedComponents:
        """
        Apply component weights to breakdown.
        
        Args:
            breakdown: Component breakdown with raw scores (0-100)
        
        Returns:
            WeightedComponents with weighted scores
        """
        return WeightedComponents(
            dasha=breakdown.dasha * self.WEIGHT_DASHA,
            transit=breakdown.transit * self.WEIGHT_TRANSIT,
            strength=breakdown.strength * self.WEIGHT_STRENGTH,
            aspect=breakdown.aspect * self.WEIGHT_ASPECT,
            motion=breakdown.motion * self.WEIGHT_MOTION
        )
    
    def calculate_raw_score(self, weighted: WeightedComponents) -> float:
        """
        Calculate raw planet score (before normalization).
        
        Args:
            weighted: Weighted components
        
        Returns:
            Raw score (sum of weighted components)
        """
        return weighted.total()
    
    def normalize_scores(
        self,
        raw_scores: Dict[Planet, float]
    ) -> Dict[Planet, float]:
        """
        Normalize planet scores so they sum to 100.
        
        Formula: P(p) = 100 × P_raw(p) / Σ P_raw(all planets)
        
        Args:
            raw_scores: Raw scores for all planets
        
        Returns:
            Normalized scores (sum to 100)
        """
        total_raw = sum(raw_scores.values())
        
        # Handle edge case of zero total
        if total_raw == 0:
            # Equal distribution if all scores are zero
            return {planet: 100.0 / len(raw_scores) for planet in raw_scores}
        
        # Normalize
        return {
            planet: (raw_score / total_raw) * 100.0
            for planet, raw_score in raw_scores.items()
        }

    def generate_planet_explanations(
        self,
        planet: Planet,
        score: float,
        breakdown: ComponentBreakdown,
        weighted: WeightedComponents
    ) -> list[str]:
        """
        Generate human-readable explanations for a planet's score.

        Args:
            planet: The planet
            score: Final normalized score
            breakdown: Component breakdown
            weighted: Weighted components

        Returns:
            List of explanation strings
        """
        explanations = []
        planet_name = planet.value

        # 1. Overall score interpretation
        if score >= 15:
            strength = "very strong"
        elif score >= 12:
            strength = "strong"
        elif score >= 9:
            strength = "moderate"
        elif score >= 6:
            strength = "weak"
        else:
            strength = "very weak"

        explanations.append(f"{planet_name} has {strength} influence with score {score:.1f}/100")

        # 2. Identify dominant component
        components = {
            "Dasha": (breakdown.dasha, weighted.dasha, self.WEIGHT_DASHA),
            "Transit": (breakdown.transit, weighted.transit, self.WEIGHT_TRANSIT),
            "Strength": (breakdown.strength, weighted.strength, self.WEIGHT_STRENGTH),
            "Aspect": (breakdown.aspect, weighted.aspect, self.WEIGHT_ASPECT),
            "Motion": (breakdown.motion, weighted.motion, self.WEIGHT_MOTION)
        }

        # Find highest weighted component
        max_component = max(components.items(), key=lambda x: x[1][1])
        comp_name, (raw, weighted_val, weight) = max_component

        explanations.append(
            f"{comp_name} is the strongest factor (raw: {raw:.1f}, weighted: {weighted_val:.1f}, {weight*100:.0f}% weight)"
        )

        # 3. Dasha-specific explanation
        if breakdown.dasha >= 70:
            explanations.append(f"{planet_name} is in a major dasha period (Mahadasha or Antardasha)")
        elif breakdown.dasha >= 40:
            explanations.append(f"{planet_name} has moderate dasha influence")
        else:
            explanations.append(f"{planet_name} is not in an active dasha period")

        # 4. Transit-specific explanation
        if breakdown.transit >= 70:
            explanations.append(f"{planet_name} is transiting through favorable houses")
        elif breakdown.transit >= 40:
            explanations.append(f"{planet_name} has moderate transit placement")
        else:
            explanations.append(f"{planet_name} is transiting through challenging houses")

        # 5. Strength-specific explanation
        if breakdown.strength >= 70:
            explanations.append(f"{planet_name} is in a strong dignified position")
        elif breakdown.strength >= 40:
            explanations.append(f"{planet_name} has moderate positional strength")
        else:
            explanations.append(f"{planet_name} is in a weakened or debilitated state")

        # 6. Overall interpretation
        if score >= 12:
            explanations.append(f"{planet_name} is highly favorable for its significations")
        elif score >= 9:
            explanations.append(f"{planet_name} provides moderate support")
        else:
            explanations.append(f"{planet_name} may present challenges or require extra effort")

        return explanations

    def calculate_planet_scores(
        self,
        natal_chart: NatalChart,
        calculation_date: datetime
    ) -> PlanetScores:
        """
        Calculate scores for all planets in a chart.

        This is the main method that orchestrates all services:
        1. Calculate component breakdown for each planet
        2. Apply component weights
        3. Calculate raw scores
        4. Normalize scores to sum to 100

        Args:
            natal_chart: The natal chart
            calculation_date: Date/time for calculation

        Returns:
            PlanetScores with complete scoring for all planets
        """
        planet_scores = {}
        raw_scores = {}
        breakdowns = {}
        weighted_components_map = {}

        # Step 1 & 2: Calculate breakdown and weighted components for each planet
        for planet in natal_chart.planets.keys():
            # Calculate component breakdown
            breakdown = self.calculate_component_breakdown(
                planet,
                natal_chart,
                calculation_date
            )
            breakdowns[planet] = breakdown

            # Apply weights
            weighted = self.calculate_weighted_components(breakdown)
            weighted_components_map[planet] = weighted

            # Calculate raw score
            raw_score = self.calculate_raw_score(weighted)
            raw_scores[planet] = raw_score

        # Step 3: Normalize scores
        normalized_scores = self.normalize_scores(raw_scores)

        # Step 4: Build PlanetScore objects with explanations
        for planet in natal_chart.planets.keys():
            explanations = self.generate_planet_explanations(
                planet,
                normalized_scores[planet],
                breakdowns[planet],
                weighted_components_map[planet]
            )

            planet_scores[planet] = PlanetScore(
                planet=planet,
                score=normalized_scores[planet],
                breakdown=breakdowns[planet],
                weighted_components=weighted_components_map[planet],
                explanations=explanations
            )

        return PlanetScores(
            scores=planet_scores,
            calculation_date=calculation_date
        )

