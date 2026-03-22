"""
Core Scoring Engine for calculating planet scores.

MULTIPLICATIVE MODEL WITH ENHANCEMENTS (Phase 3+):
Dasha acts as a gating function - planets only matter when their dasha is active.

Formula (3-step process):
1. Base: P_raw = dasha × (0.4×transit + 0.3×strength + 0.2×aspect + 0.1×motion)
2. Activation Gate: if dasha < 15, multiply by 0.2 (suppress weak signals)
3. Contrast Boost: P_raw = P_raw ** 1.5 (amplify differences)
4. Normalize: P = 100 × P_raw / Σ P_raw (sum to 100)

This means:
- If dasha = 0 (planet not in dasha), score ≈ 0 (planet inactive)
- If dasha < 15 (very weak dasha), score is heavily suppressed (×0.2)
- If dasha = 100 (all dasha levels match), score = full weighted sum
- Contrast boost (^1.5) makes strong planets stronger, weak planets weaker

Component Weights (within the gated sum):
- Transit: 40% - Where the planet is transiting
- Strength: 30% - Dignity, retrograde, combustion
- Aspect: 20% - Houses the planet aspects
- Motion: 10% - Retrograde/direct motion speed

PHASE 1 CHANGES:
- Default values changed from 50.0 to 0.0 (eliminates noise floor)

PHASE 2 CHANGES (Normalization):
- All components normalized to 0-1 scale before weighting
- Ensures consistent scale across all components

PHASE 3 CHANGES (Multiplicative Model):
- Dasha now gates all other components (multiplicative, not additive)
- Aspect component restored (20% of gated sum)
- New weight distribution: Transit 40%, Strength 30%, Aspect 20%, Motion 10%

PHASE 3+ CHANGES (Activation Gate + Contrast Boost):
- Activation gate: Suppress planets with dasha < 15 (×0.2 penalty)
- Contrast boost: Apply P^1.5 to amplify differences between planets
- Better differentiation between dominant and weak planets

Component Normalization Ranges:
- Dasha: 0-100 → 0-1 (max = 100) - GATING FUNCTION
- Transit: 0-100 → 0-1 (max = 100)
- Strength: 0-100 → 0-1 (max = 100)
- Aspect: 0-100 → 0-1 (max = 100)
- Motion: 0-65 → 0-1 (max = 65)

Formula Steps:
1. Normalize each component: C_norm = C_raw / C_max
2. Scale to 0-100 for display: C_display = C_norm × 100
3. Calculate gated sum: S = 0.4×transit + 0.3×strength + 0.2×aspect + 0.1×motion
4. Apply dasha gate: P_raw(p) = (dasha/100) × S × 100
5. Apply activation gate: if dasha < 15, P_raw *= 0.2
6. Apply contrast boost: P_raw = P_raw ** 1.5
7. Normalize across planets: P(p) = 100 × P_raw(p) / Σ P_raw(all planets)
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
from api.services.aspect_service import AspectService  # Restored for multiplicative model
from api.services.strength_service import StrengthService
from api.services.motion_service import MotionService


class ScoringEngine:
    """Core scoring engine for calculating planet scores."""

    # MULTIPLICATIVE MODEL: Dasha gates the other components
    # Weights for the gated components (must sum to 1.0)
    WEIGHT_TRANSIT = 0.40    # Transit contribution within gated sum
    WEIGHT_STRENGTH = 0.30   # Strength contribution within gated sum
    WEIGHT_ASPECT = 0.20     # Aspect contribution within gated sum (restored!)
    WEIGHT_MOTION = 0.10     # Motion contribution within gated sum

    # Component normalization ranges (for converting to 0-1 scale)
    # These represent the theoretical maximum values each component can produce
    DASHA_MAX = 100.0        # Max: Mahadasha(40) + Antardasha(30) + Pratyantar(20) + Sookshma(10)
    TRANSIT_MAX = 100.0      # Max: 100 × planet_weight(1.0) × house_weight(1.0)
    STRENGTH_MAX = 100.0     # Max: 50 + total_strength(50) = 100
    ASPECT_MAX = 100.0       # Max: Aspect service returns 0-100 range
    MOTION_MAX = 65.0        # Max: 50 + motion_modifier(15) = 65

    def __init__(self):
        """Initialize the scoring engine with all required services."""
        self.dasha_service = DashaService()
        self.transit_service = TransitService()
        self.aspect_service = AspectService()  # Restored for multiplicative model
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

    def normalize_aspect(self, aspect_weight: float) -> float:
        """
        Normalize aspect weight to 0-1 scale.

        Range: 0-100 (varies by planet and house placement)
        Max: 100 (AspectService returns values in 0-100 range)

        Args:
            aspect_weight: Raw aspect weight (0-100)

        Returns:
            Normalized value (0-1)
        """
        return aspect_weight / self.ASPECT_MAX

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

        # 4. Aspect weight - RESTORED for multiplicative model
        # Using natal aspects (static) - could be enhanced with transit aspects later
        planet_placement = natal_chart.planets[planet]
        aspect_weight_raw = self.aspect_service.calculate_aspect_weight(
            planet,
            planet_placement.house
        )

        # Normalize aspect to 0-1, then scale to 0-100 for display
        aspect_normalized = self.normalize_aspect(aspect_weight_raw) * 100.0

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
            aspect=aspect_normalized,
            motion=motion_normalized
        )
    
    def calculate_weighted_components(
        self,
        breakdown: ComponentBreakdown
    ) -> WeightedComponents:
        """
        Apply MULTIPLICATIVE formula: P_raw = dasha × (weighted sum of other components).

        This implements the gating function where dasha controls whether other
        components matter. If dasha = 0, score = 0 regardless of other components.

        Args:
            breakdown: Component breakdown with normalized scores (0-100)

        Returns:
            WeightedComponents with weighted scores (after dasha gating)
        """
        # Apply dasha gate: multiply by dasha (0-100 scale)
        dasha_gate = breakdown.dasha / 100.0  # Convert to 0-1

        # For display purposes, show individual weighted contributions
        # (these are gated by dasha)
        return WeightedComponents(
            dasha=breakdown.dasha,  # Dasha is the gate, not a weighted component
            transit=(breakdown.transit / 100.0) * self.WEIGHT_TRANSIT * dasha_gate * 100.0,
            strength=(breakdown.strength / 100.0) * self.WEIGHT_STRENGTH * dasha_gate * 100.0,
            aspect=(breakdown.aspect / 100.0) * self.WEIGHT_ASPECT * dasha_gate * 100.0,
            motion=(breakdown.motion / 100.0) * self.WEIGHT_MOTION * dasha_gate * 100.0
        )

    def calculate_raw_score(self, breakdown: ComponentBreakdown) -> float:
        """
        Calculate raw planet score using MULTIPLICATIVE formula with enhancements.

        Formula (3 steps):
        1. Base: P_raw = dasha × (0.4×transit + 0.3×strength + 0.2×aspect + 0.1×motion)
        2. Activation Gate: if dasha < 15, multiply by 0.2 (suppress weak dasha signals)
        3. Contrast Boost: P_raw = P_raw ** 1.5 (amplify differences)

        Args:
            breakdown: Component breakdown with normalized scores (0-100)

        Returns:
            Raw score (before cross-planet normalization)
        """
        # Calculate the gated sum
        gated_sum = (
            (breakdown.transit / 100.0) * self.WEIGHT_TRANSIT +
            (breakdown.strength / 100.0) * self.WEIGHT_STRENGTH +
            (breakdown.aspect / 100.0) * self.WEIGHT_ASPECT +
            (breakdown.motion / 100.0) * self.WEIGHT_MOTION
        )

        # Apply dasha gate
        dasha_gate = breakdown.dasha / 100.0
        raw_score = gated_sum * dasha_gate * 100.0

        # Step 1: Activation Gate - suppress very weak dasha signals
        if breakdown.dasha < 15.0:
            raw_score *= 0.2

        # Step 2: Contrast Boost - amplify differences between planets
        raw_score = raw_score ** 1.5

        return raw_score
    
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

        # 2. Dasha gate explanation (most important in multiplicative model)
        if breakdown.dasha >= 70:
            explanations.append(f"Dasha gate is VERY STRONG ({breakdown.dasha:.1f}/100) - planet is highly active")
        elif breakdown.dasha >= 40:
            explanations.append(f"Dasha gate is ACTIVE ({breakdown.dasha:.1f}/100) - planet has moderate influence")
        elif breakdown.dasha > 0:
            explanations.append(f"Dasha gate is WEAK ({breakdown.dasha:.1f}/100) - planet has limited influence")
        else:
            explanations.append(f"Dasha gate is INACTIVE (0/100) - planet is dormant")

        # 3. Identify dominant gated component (excluding dasha)
        gated_components = {
            "Transit": (breakdown.transit, weighted.transit, self.WEIGHT_TRANSIT),
            "Strength": (breakdown.strength, weighted.strength, self.WEIGHT_STRENGTH),
            "Aspect": (breakdown.aspect, weighted.aspect, self.WEIGHT_ASPECT),
            "Motion": (breakdown.motion, weighted.motion, self.WEIGHT_MOTION)
        }

        # Find highest weighted component
        max_component = max(gated_components.items(), key=lambda x: x[1][1])
        comp_name, (raw, weighted_val, weight) = max_component

        explanations.append(
            f"{comp_name} is the strongest gated factor (raw: {raw:.1f}, weighted: {weighted_val:.1f}, {weight*100:.0f}% of gated sum)"
        )

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

            # Apply weights (multiplicative formula)
            weighted = self.calculate_weighted_components(breakdown)
            weighted_components_map[planet] = weighted

            # Calculate raw score (using breakdown, not weighted)
            raw_score = self.calculate_raw_score(breakdown)
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

