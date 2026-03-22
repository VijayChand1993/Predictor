"""
Core Scoring Engine for calculating planet scores.

MULTIPLICATIVE MODEL WITH STRUCTURAL FIX (Phase 6):
Complete rewrite to fix semi-additive scoring, add competition layer, and proper signal isolation.

Formula (6-step process for each planet):
1. Base: base = 0.5×transit + 0.3×strength + 0.15×aspect + 0.05×motion
2. Dasha Gate: score = (dasha^1.3) × base
3. Strength Amplification: score *= (0.7 + 0.3×strength)
4. Planet Factor: score *= PLANET_FACTOR[planet]
5. Event Boost: score += eventBoost (from transit service)
6. Hard Gate & Noise Floor: if dasha < 0.1 AND transit < 0.2, score = 0; if score < 0.05, score = 0

Competition Layer (cross-planet normalization):
1. Divide by max: score = score / max(all_scores)
2. Contrast boost: score = score^2
3. Normalize to 100: score = (score / sum(all_scores)) * 100

This means:
- If dasha = 0 (planet not in dasha), score ≈ 0 (planet inactive)
- If dasha < 10 (very weak dasha), score is heavily suppressed (×0.2)
- If dasha = 100 (all dasha levels match), score = full weighted sum
- Dasha exponent (^1.2) slightly amplifies strong dasha periods
- Contrast boost (^1.7) makes strong planets stronger, weak planets weaker
- Planet factor (0.75-1.25) adjusts for intrinsic importance

Component Weights (within the gated sum):
- Transit: 50% - Where the planet is transiting (INCREASED)
- Strength: 30% - Dignity, retrograde, combustion
- Aspect: 15% - Houses the planet aspects (DECREASED)
- Motion: 5% - Retrograde/direct motion speed (DECREASED)

Planet Factors (intrinsic importance):
- Saturn: 1.25 (slowest, most karmic)
- Jupiter: 1.20 (great benefic, slow)
- Rahu: 1.15 (shadow planet, karmic)
- Ketu: 1.10 (shadow planet, spiritual)
- Mars: 1.00 (baseline, medium speed)
- Sun: 0.95 (fast, but important - soul)
- Venus: 0.90 (fast benefic)
- Mercury: 0.85 (very fast, changeable)
- Moon: 0.75 (fastest, most changeable - mind)

PHASE 1 CHANGES:
- Default values changed from 50.0 to 0.0 (eliminates noise floor)

PHASE 2 CHANGES (Normalization):
- All components normalized to 0-1 scale before weighting
- Ensures consistent scale across all components

PHASE 3 CHANGES (Multiplicative Model):
- Dasha now gates all other components (multiplicative, not additive)
- Aspect component restored (20% of gated sum)
- Weight distribution: Transit 40%, Strength 30%, Aspect 20%, Motion 10%

PHASE 4 CHANGES (Refined Formula):
- Dasha exponent: dasha^1.2 (amplifies strong dasha periods)
- Rebalanced weights: Transit 50%, Strength 30%, Aspect 15%, Motion 5%
- Activation gate threshold: dasha < 10 (was 15)
- Contrast boost exponent: P^1.7 (was 1.5) - stronger amplification

PHASE 5 CHANGES (Planet Factor):
- Planet factor: Intrinsic importance based on speed and traditional hierarchy
- Slow planets (Saturn, Jupiter) get higher factors (1.20-1.25)
- Fast planets (Moon, Mercury) get lower factors (0.75-0.85)
- Applied after contrast boost, before normalization

Component Normalization Ranges:
- Dasha: 0-100 → 0-1 (max = 100) - GATING FUNCTION (with ^1.2 exponent)
- Transit: 0-100 → 0-1 (max = 100)
- Strength: 0-100 → 0-1 (max = 100)
- Aspect: 0-100 → 0-1 (max = 100)
- Motion: 0-65 → 0-1 (max = 65)

Formula Steps:
1. Normalize each component: C_norm = C_raw / C_max
2. Scale to 0-100 for display: C_display = C_norm × 100
3. Calculate gated sum: S = 0.5×transit + 0.3×strength + 0.15×aspect + 0.05×motion
4. Apply dasha gate with exponent: P_raw(p) = ((dasha/100)^1.2) × S × 100
5. Apply activation gate: if dasha < 10, P_raw *= 0.2
6. Apply contrast boost: P_raw = P_raw ** 1.7
7. Apply planet factor: P_raw *= PLANET_FACTOR[planet]
8. Normalize across planets: P(p) = 100 × P_raw(p) / Σ P_raw(all planets)
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

    # MULTIPLICATIVE MODEL (Phase 4): Dasha gates the other components
    # Weights for the gated components (must sum to 1.0)
    WEIGHT_TRANSIT = 0.50    # Transit contribution within gated sum (INCREASED from 0.40)
    WEIGHT_STRENGTH = 0.30   # Strength contribution within gated sum
    WEIGHT_ASPECT = 0.15     # Aspect contribution within gated sum (DECREASED from 0.20)
    WEIGHT_MOTION = 0.05     # Motion contribution within gated sum (DECREASED from 0.10)

    # Enhancement parameters (Phase 6 - Structural Fix)
    DASHA_EXPONENT = 1.3     # Dasha exponent (increased from 1.2 for stronger gating)
    HARD_GATE_DASHA = 0.1    # Hard gate: if dasha < 0.1 AND transit < 0.2, score = 0
    HARD_GATE_TRANSIT = 0.2  # Hard gate transit threshold
    NOISE_FLOOR = 0.05       # If final score < 0.05, set to 0
    CONTRAST_EXPONENT = 2.0  # Competition layer contrast (P^2)

    # Planet Factor (Phase 5): Intrinsic importance of each planet
    # Based on traditional Vedic astrology hierarchy
    # Slow-moving planets (Saturn, Jupiter) have more impact
    # Fast-moving planets (Moon, Mercury) have less impact
    PLANET_FACTOR = {
        Planet.SATURN: 1.25,   # Slowest, most karmic
        Planet.JUPITER: 1.20,  # Great benefic, slow
        Planet.RAHU: 1.15,     # Shadow planet, karmic
        Planet.KETU: 1.10,     # Shadow planet, spiritual
        Planet.MARS: 1.00,     # Baseline (medium speed)
        Planet.SUN: 0.95,      # Fast, but important (soul)
        Planet.VENUS: 0.90,    # Fast benefic
        Planet.MERCURY: 0.85,  # Very fast, changeable
        Planet.MOON: 0.75,     # Fastest, most changeable (mind)
    }

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

        # 4. Aspect weight - USING TRANSIT HOUSE (dynamic, not static natal)
        # Signal Isolation: Aspect must use transit position, not natal position
        if planet in transit_data.planets:
            transit_placement = transit_data.planets[planet]
            aspect_weight_raw = self.aspect_service.calculate_aspect_weight(
                planet,
                transit_placement.house  # Use TRANSIT house, not natal house
            )
        else:
            # Fallback to natal if transit data not available
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

    def calculate_raw_score(self, breakdown: ComponentBreakdown, planet: Planet = None, event_boost: float = 0.0) -> float:
        """
        Calculate raw planet score using MULTIPLICATIVE formula (Phase 6 - Structural Fix).

        Formula (NEW - 6 steps):
        1. Base: base = 0.5×transit + 0.3×strength + 0.15×aspect + 0.05×motion
        2. Dasha Gate: score = (dasha^1.3) × base
        3. Strength Amplification: score *= (0.7 + 0.3×strength)
        4. Planet Factor: score *= PLANET_FACTOR[planet]
        5. Event Boost: score += eventBoost (from transit service)
        6. Hard Gate & Noise Floor: if dasha < 0.1 AND transit < 0.2, score = 0; if score < 0.05, score = 0

        Args:
            breakdown: Component breakdown with normalized scores (0-100)
            planet: The planet (for planet factor application)
            event_boost: Event boost from transit service (sign changes, conjunctions, etc.)

        Returns:
            Raw score (before competition layer normalization)
        """
        # Normalize components to 0-1 range
        dasha_norm = breakdown.dasha / 100.0
        transit_norm = breakdown.transit / 100.0
        strength_norm = breakdown.strength / 100.0
        aspect_norm = breakdown.aspect / 100.0
        motion_norm = breakdown.motion / 100.0

        # HARD GATE: If dasha < 0.1 AND transit < 0.2, planet is completely inactive
        if dasha_norm < self.HARD_GATE_DASHA and transit_norm < self.HARD_GATE_TRANSIT:
            return 0.0

        # Step 1: Calculate base weighted sum
        base = (
            self.WEIGHT_TRANSIT * transit_norm +
            self.WEIGHT_STRENGTH * strength_norm +
            self.WEIGHT_ASPECT * aspect_norm +
            self.WEIGHT_MOTION * motion_norm
        )

        # Step 2: Apply dasha gate with exponent (dasha^1.3)
        dasha_gate = dasha_norm ** self.DASHA_EXPONENT
        score = dasha_gate * base

        # Step 3: Strength amplification (NOT addition - multiplicative)
        # Score is amplified by strength: 70% base + 30% strength-dependent
        strength_amplifier = 0.7 + 0.3 * strength_norm
        score *= strength_amplifier

        # Step 4: Planet Factor - apply intrinsic importance
        if planet is not None:
            planet_factor = self.PLANET_FACTOR.get(planet, 1.0)
            score *= planet_factor

        # Step 5: Event Boost - add (not multiply) event-based bonus
        score += event_boost

        # Step 6: Noise Floor - eliminate very weak signals
        if score < self.NOISE_FLOOR:
            score = 0.0

        # Scale to 0-100 range for consistency
        return score * 100.0
    
    def normalize_scores(
        self,
        raw_scores: Dict[Planet, float]
    ) -> Dict[Planet, float]:
        """
        Normalize planet scores with COMPETITION LAYER (Phase 6 - Structural Fix).

        Formula (3 steps):
        1. Divide by max: score = score / max(all_scores)
        2. Contrast boost: score = score^2 (amplifies differences)
        3. Normalize to 100: score = (score / sum(all_scores)) * 100

        This creates competition between planets - strong planets get much stronger,
        weak planets get much weaker.

        Args:
            raw_scores: Raw scores for all planets

        Returns:
            Normalized scores (sum to 100)
        """
        # Handle edge case of zero total
        if not raw_scores or all(s == 0 for s in raw_scores.values()):
            # Equal distribution if all scores are zero
            return {planet: 100.0 / len(raw_scores) for planet in raw_scores}

        # Step 1: Divide by max value (normalize to 0-1 range based on strongest planet)
        max_score = max(raw_scores.values())
        if max_score == 0:
            return {planet: 100.0 / len(raw_scores) for planet in raw_scores}

        normalized_to_max = {
            planet: score / max_score
            for planet, score in raw_scores.items()
        }

        # Step 2: Apply contrast boost (P^2) - makes strong planets stronger
        contrasted = {
            planet: score ** self.CONTRAST_EXPONENT
            for planet, score in normalized_to_max.items()
        }

        # Step 3: Normalize to sum to 100
        total_contrasted = sum(contrasted.values())
        if total_contrasted == 0:
            return {planet: 100.0 / len(raw_scores) for planet in raw_scores}

        return {
            planet: (score / total_contrasted) * 100.0
            for planet, score in contrasted.items()
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
            # Pass planet for planet factor application
            raw_score = self.calculate_raw_score(breakdown, planet)
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

