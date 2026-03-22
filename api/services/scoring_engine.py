"""
Core Scoring Engine for calculating planet scores.

Orchestrates all services to calculate final planet scores:
- Dasha (40%) - Increased from 35%
- Transit (30%) - Increased from 25%
- Strength (22%) - Increased from 20%
- Motion (8%) - Unchanged

PHASE 1 CHANGES:
- Aspect component removed (was 12%) as it used static natal aspects
- Default values changed from 50.0 to 0.0 (eliminates noise floor)
- Weights redistributed: +5% to Dasha, +5% to Transit, +2% to Strength

PHASE 2 CHANGES (Normalization):
- All components normalized to 0-1 scale before weighting
- Ensures consistent scale across all components
- Prevents any single component from dominating due to scale differences

Component Normalization Ranges:
- Dasha: 0-100 → 0-1 (max = 100)
- Transit: 0-100 → 0-1 (max = 100)
- Strength: 0-100 → 0-1 (max = 100)
- Motion: 0-65 → 0-1 (max = 65, typical range 50-65)

Formula:
1. Normalize each component: C_norm = C_raw / C_max
2. Scale to 0-100 for display: C_display = C_norm × 100
3. Apply weights: P_raw(p) = 0.40×C_dasha + 0.30×C_transit + 0.22×C_strength + 0.08×C_motion
4. Normalize across planets: P(p) = 100 × P_raw(p) / Σ P_raw(all planets)
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
# AspectService removed - static natal aspects don't belong in dynamic scoring
from api.services.strength_service import StrengthService
from api.services.motion_service import MotionService


class ScoringEngine:
    """Core scoring engine for calculating planet scores."""

    # Component weights (must sum to 1.0)
    # Aspect component removed - redistributed to other components
    WEIGHT_DASHA = 0.40      # Was 0.35 (+0.05)
    WEIGHT_TRANSIT = 0.30    # Was 0.25 (+0.05)
    WEIGHT_STRENGTH = 0.22   # Was 0.20 (+0.02)
    WEIGHT_MOTION = 0.08     # Unchanged

    # Component normalization ranges (for converting to 0-1 scale)
    # These represent the theoretical maximum values each component can produce
    DASHA_MAX = 100.0        # Max: Mahadasha(40) + Antardasha(30) + Pratyantar(20) + Sookshma(10)
    TRANSIT_MAX = 100.0      # Max: 100 × planet_weight(1.0) × house_weight(1.0)
    STRENGTH_MAX = 100.0     # Max: 50 + total_strength(50) = 100
    MOTION_MAX = 65.0        # Max: 50 + motion_modifier(15) = 65

    def __init__(self):
        """Initialize the scoring engine with all required services."""
        self.dasha_service = DashaService()
        self.transit_service = TransitService()
        # aspect_service removed - static natal aspects don't belong in dynamic scoring
        self.strength_service = StrengthService()
        self.motion_service = MotionService()

    def normalize_dasha(self, dasha_weight: float) -> float:
        """
        Normalize dasha weight to 0-1 scale.

        Range: 0-100 (sum of all dasha levels)
        Max: 100 (all 4 levels match)

        Args:
            dasha_weight: Raw dasha weight (0-100)

        Returns:
            Normalized value (0-1)
        """
        return dasha_weight / self.DASHA_MAX

    def normalize_transit(self, transit_weight: float) -> float:
        """
        Normalize transit weight to 0-1 scale.

        Range: 0-100 (planet_importance × house_importance × 100)
        Max: 100 (Jupiter in 1st/4th/7th/10th house)

        Args:
            transit_weight: Raw transit weight (0-100)

        Returns:
            Normalized value (0-1)
        """
        return transit_weight / self.TRANSIT_MAX

    def normalize_strength(self, strength_weight: float) -> float:
        """
        Normalize strength weight to 0-1 scale.

        Range: 0-100 (50 + total_strength where total_strength is -50 to +50)
        Max: 100 (exalted + retrograde + not combust)

        Args:
            strength_weight: Raw strength weight (0-100)

        Returns:
            Normalized value (0-1)
        """
        return strength_weight / self.STRENGTH_MAX

    def normalize_motion(self, motion_weight: float) -> float:
        """
        Normalize motion weight to 0-1 scale.

        Range: 50-65 for significant planets (50 + modifier where modifier is 0-15)
        Range: 50 for non-significant planets (neutral baseline)
        Max: 65 (fastest direct motion)

        Args:
            motion_weight: Raw motion weight (0-100, typically 50-65)

        Returns:
            Normalized value (0-1)
        """
        return motion_weight / self.MOTION_MAX
    
    def calculate_component_breakdown(
        self,
        planet: Planet,
        natal_chart: NatalChart,
        calculation_date: datetime
    ) -> ComponentBreakdown:
        """
        Calculate all component scores for a planet with normalization.

        Phase 2 Enhancement: All components are now normalized to 0-1 scale
        before being stored, then scaled back to 0-100 for display consistency.

        Args:
            planet: The planet
            natal_chart: The natal chart
            calculation_date: Date/time for calculation

        Returns:
            ComponentBreakdown with all component scores (0-100, normalized)
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
            dasha_weight_raw = dasha_weight_obj.total_weight
        else:
            # No dasha data = no contribution (was 50.0, now 0.0 to eliminate noise floor)
            dasha_weight_raw = 0.0

        # Normalize dasha to 0-1, then scale to 0-100 for display
        dasha_normalized = self.normalize_dasha(dasha_weight_raw) * 100.0

        # 2. Transit weight
        transit_data = self.transit_service.get_transit_data(
            target_date=calculation_date,
            natal_chart=natal_chart,
            save_json=False
        )
        if planet in transit_data.planets:
            transit_placement = transit_data.planets[planet]
            transit_weight_raw = self.transit_service.calculate_transit_weight(
                planet,
                transit_placement.house
            )
        else:
            # No transit data = no contribution (was 50.0, now 0.0 to eliminate noise floor)
            transit_weight_raw = 0.0

        # Normalize transit to 0-1, then scale to 0-100 for display
        transit_normalized = self.normalize_transit(transit_weight_raw) * 100.0

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
            strength_weight_raw = planet_strength.strength_weight
        else:
            # Fallback to natal if transit data not available
            sun_placement = natal_chart.planets[Planet.SUN]
            planet_placement = natal_chart.planets[planet]
            planet_strength = self.strength_service.calculate_planet_strength(
                planet,
                planet_placement,
                sun_placement
            )
            strength_weight_raw = planet_strength.strength_weight

        # Normalize strength to 0-1, then scale to 0-100 for display
        strength_normalized = self.normalize_strength(strength_weight_raw) * 100.0

        # 4. Aspect weight - REMOVED (static natal aspects don't belong in dynamic scoring)
        # The 12% weight has been redistributed to other components

        # 5. Motion weight
        motion_calculation = self.motion_service.calculate_chart_motions(
            natal_chart,
            calculation_date
        )
        if planet in motion_calculation.planet_motions:
            motion_weight_raw = motion_calculation.planet_motions[planet].motion_weight
        else:
            # No motion data = no contribution (was 50.0, now 0.0 to eliminate noise floor)
            motion_weight_raw = 0.0

        # Normalize motion to 0-1, then scale to 0-100 for display
        motion_normalized = self.normalize_motion(motion_weight_raw) * 100.0

        return ComponentBreakdown(
            dasha=dasha_normalized,
            transit=transit_normalized,
            strength=strength_normalized,
            motion=motion_normalized
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

