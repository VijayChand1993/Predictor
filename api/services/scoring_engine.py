"""
Core Scoring Engine for calculating planet scores.

PHASE 9: CORRECT MULTIPLICATIVE MODEL - FINAL (Dasha Dominance Fixed)

Formula (6-step process for each planet):
1. Base: base = 0.25×transit + 0.30×strength + 0.25×aspect + 0.20×motion
2. Dasha Factor: dasha_factor = 0.20 + 0.80 × (dasha/100)
   - Safety: max(dasha_factor, 0.20) to prevent zero cascade
3. Apply dasha: score = base × dasha_factor
4. Planet Factor: score × planet_factor (widened spread: 1.5 to 0.7)
5. Event Boost: score + event_boost
6. Contrast Boost: score^1.2 (spreads distribution)
7. Final: score × 100

Key Principles (Phase 9 - FINAL):
- Dasha DOMINATES (not just gates) - non-dasha planets suppressed to 20%
- Transit weight REDUCED (0.25) - transit < dasha in importance
- Planet factors WIDENED (Saturn 1.5, Moon 0.7) - slow planets dominate
- Contrast boost (^1.2) - strong planets amplified, weak suppressed
- No cross-planet normalization (absolute scoring)

Component Weights (base calculation, NO DASHA):
- Transit: 25% - Where the planet is transiting (REDUCED from 0.35)
- Strength: 30% - Dignity, retrograde, combustion
- Aspect: 25% - Houses the planet aspects (INCREASED from 0.20)
- Motion: 20% - Retrograde/direct motion speed (INCREASED from 0.15)

Dasha Factor (multiplicative - FINAL):
- Formula: 0.20 + 0.80 × dasha_normalized
- Non-dasha planets: 20% baseline (SUPPRESSED - prevents dominance)
- Full dasha planets: 20% + 80% = 100% (full strength)
- This creates STRONG hierarchy: dasha planets clearly dominate
- Safety check ensures dasha_factor >= 0.20 (NEVER zero)

Planet Factors (intrinsic importance - WIDENED SPREAD):
- Saturn: 1.50 (slowest, most karmic) - INCREASED from 1.30
- Jupiter: 1.25 (great benefic, slow) - INCREASED from 1.20
- Rahu: 1.20 (shadow planet, karmic) - INCREASED from 1.15
- Ketu: 1.20 (shadow planet, spiritual) - INCREASED from 1.15
- Mars: 1.00 (baseline, medium speed)
- Sun: 0.85 (fast but important) - DECREASED from 0.90
- Venus: 0.85 (fast benefic) - DECREASED from 0.90
- Mercury: 0.80 (very fast, changeable) - DECREASED from 0.85
- Moon: 0.70 (fastest, most changeable) - DECREASED from 0.75

Expected Output Ranges (Phase 9 - FINAL):
- Dominant dasha planets (Saturn in dasha): 70-90
- Strong dasha planets: 50-70
- Medium planets: 25-40
- Non-dasha planets: 10-20 (SUPPRESSED)
- Weak planets: 5-15

Component Normalization Ranges:
- Dasha: 0-100 → 0-1 (max = 100) - MULTIPLICATIVE FACTOR
- Transit: 0-100 → 0-1 (max = 100)
- Strength: 0-100 → 0-1 (max = 100)
- Aspect: 0-100 → 0-1 (max = 100)
- Motion: 0-65 → 0-1 (max = 65)
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

    # MULTIPLICATIVE MODEL (Phase 9 - FINAL): Dasha is multiplicative, not additive
    # Weights for the base components (must sum to 1.0) - NO DASHA HERE
    # BOOSTED: Increased transit and strength to amplify base signal
    WEIGHT_TRANSIT = 0.30    # Transit contribution (where planet is now) - INCREASED from 0.25
    WEIGHT_STRENGTH = 0.35   # Strength contribution (dignity, combustion) - INCREASED from 0.30
    WEIGHT_ASPECT = 0.20     # Aspect contribution (houses aspected) - REDUCED from 0.25
    WEIGHT_MOTION = 0.15     # Motion contribution (retrograde, speed) - REDUCED from 0.20

    # Dasha parameters (Phase 9 - Multiplicative Model - FINAL - CORRECTED SCALING)
    # Formula: dasha_factor = 0.20 + 0.80 * (50*md + 30*ad + 20*pd)/100
    # where md, ad, pd are 0 or 1 (match or no match)
    DASHA_BASELINE = 0.20    # Baseline for non-dasha planets (20% - suppresses non-dasha)
    DASHA_MULTIPLIER = 0.80  # Multiplier for dasha strength (80% - amplifies dasha)
    DASHA_MD_WEIGHT = 50.0   # Mahadasha contribution (50 points) - CORRECTED from 0.5
    DASHA_AD_WEIGHT = 30.0   # Antardasha contribution (30 points) - CORRECTED from 0.3
    DASHA_PD_WEIGHT = 20.0   # Pratyantar contribution (20 points) - CORRECTED from 0.2

    SCALE_UP_FACTOR = 1.0    # No artificial scale-up (removed)

    # Planet Factor (Phase 9 - FINAL): Intrinsic importance of each planet
    # Based on traditional Vedic astrology hierarchy
    # MAXIMUM SPREAD: Slow-moving planets dominate, fast planets heavily suppressed
    PLANET_FACTOR = {
        Planet.SATURN: 1.70,   # Slowest, most karmic (INCREASED from 1.50)
        Planet.JUPITER: 1.35,  # Great benefic, slow (INCREASED from 1.25)
        Planet.RAHU: 1.35,     # Shadow planet, karmic (INCREASED from 1.20)
        Planet.KETU: 1.35,     # Shadow planet, spiritual (INCREASED from 1.20)
        Planet.MARS: 1.00,     # Baseline (medium speed)
        Planet.SUN: 0.80,      # Fast but important (DECREASED from 0.85)
        Planet.VENUS: 0.80,    # Fast benefic (DECREASED from 0.85)
        Planet.MERCURY: 0.75,  # Very fast, changeable (DECREASED from 0.80)
        Planet.MOON: 0.65,     # Fastest, most changeable (DECREASED from 0.70)
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
        Calculate weighted components for DISPLAY ONLY (Phase 9 - CORRECTED).

        CRITICAL: Dasha is NOT applied here - it's applied in calculate_raw_score.
        This method is for display/debugging purposes only.

        Args:
            breakdown: Component breakdown with normalized scores (0-100)

        Returns:
            WeightedComponents with weighted scores (NO dasha gating)
        """
        # For display purposes, show individual weighted contributions
        # WITHOUT dasha gating (dasha applied separately in calculate_raw_score)
        return WeightedComponents(
            dasha=breakdown.dasha,  # Dasha shown as-is (not weighted)
            transit=(breakdown.transit / 100.0) * self.WEIGHT_TRANSIT * 100.0,
            strength=(breakdown.strength / 100.0) * self.WEIGHT_STRENGTH * 100.0,
            aspect=(breakdown.aspect / 100.0) * self.WEIGHT_ASPECT * 100.0,
            motion=(breakdown.motion / 100.0) * self.WEIGHT_MOTION * 100.0
        )

    def calculate_raw_score(self, breakdown: ComponentBreakdown, planet: Planet = None, event_boost: float = 0.0) -> float:
        """
        Calculate raw planet score using CORRECT MULTIPLICATIVE MODEL (Phase 9 - FINAL).

        Formula (CORRECTED - 6 steps):
        1. Base: base = 0.25×transit + 0.30×strength + 0.25×aspect + 0.20×motion
        2. Dasha Factor: dasha_factor = 0.20 + 0.80 × dasha_normalized
           - Safety: max(dasha_factor, 0.20) to prevent zero cascade
        3. Apply dasha: score = base × dasha_factor
        4. Planet Factor: score × planet_factor (1.5 for Saturn, 0.7 for Moon)
        5. Event Boost: score + event_boost
        6. Contrast Boost: score^1.2 (spreads distribution)
        7. Final: score × 100

        Key Changes (Phase 9 - FINAL):
        - Reduced transit weight from 0.35 to 0.25 (transit < dasha)
        - Reverted baseline to 0.20 (suppresses non-dasha planets)
        - Widened planet factor spread (Saturn 1.5, Moon 0.7)
        - Added ^1.2 exponent for contrast boost
        - This creates STRONG hierarchy: dasha planets dominate clearly

        Args:
            breakdown: Component breakdown with normalized scores (0-100)
            planet: The planet (for planet factor application)
            event_boost: Event boost from transit service (sign changes, conjunctions, etc.)

        Returns:
            Raw score (0-100 range, absolute not normalized)
        """
        # Normalize components to 0-1 range
        dasha_norm = breakdown.dasha / 100.0
        transit_norm = breakdown.transit / 100.0
        strength_norm = breakdown.strength / 100.0
        aspect_norm = breakdown.aspect / 100.0
        motion_norm = breakdown.motion / 100.0

        # Step 1: Calculate base weighted sum (NO DASHA)
        base = (
            self.WEIGHT_TRANSIT * transit_norm +
            self.WEIGHT_STRENGTH * strength_norm +
            self.WEIGHT_ASPECT * aspect_norm +
            self.WEIGHT_MOTION * motion_norm
        )

        # Step 1b: Boost base energy - amplify mid-range values
        # Example: 0.4 → 0.55, 0.6 → 0.72
        # This increases raw signal before dasha multiplication
        base = base ** 0.85

        # Step 2: Dasha Factor (MULTIPLICATIVE, not additive)
        # Formula: 0.20 + 0.80 × (dasha_normalized ^ 0.6)
        # Non-linear boost: ^0.6 exponent HEAVILY amplifies dasha dominance
        # Examples: 0.3 → 0.60 (was 0.55), 0.5 → 0.78 (was 0.75)
        # Non-dasha planets: 20% baseline (suppressed)
        # Full dasha planets: 20% + 80% = 100% (full strength)
        dasha_norm_boosted = dasha_norm ** 0.6
        dasha_factor = self.DASHA_BASELINE + self.DASHA_MULTIPLIER * dasha_norm_boosted

        # Safety check: dasha_factor must NEVER be 0 (prevents zero cascade)
        dasha_factor = max(dasha_factor, self.DASHA_BASELINE)

        # Step 3: Apply dasha factor
        score = base * dasha_factor

        # Step 4: Planet Factor - apply intrinsic importance
        if planet is not None:
            planet_factor = self.PLANET_FACTOR.get(planet, 1.0)
            score *= planet_factor

        # Step 5: Event Boost - add (not multiply) event-based bonus
        score += event_boost

        # Step 6: Score Floor - prevent collapse to near-zero
        # CRITICAL: Apply BEFORE exponent (exponent shrinks small values)
        score = max(score, 0.05)

        # Step 7: Conditional Contrast Boost - apply ^1.4 exponent ONLY if score > 0.3
        # INCREASED from 1.35 to 1.4 for MAXIMUM separation
        # This spreads distribution for strong planets without crushing weak ones
        # For strong planets (>0.3): amplifies contrast significantly
        # For weak planets (<0.3): preserves minimum visibility
        if score > 0.3:
            score = score ** 1.4

        # Convert to 0-100 scale
        return score * 100.0
    
    def normalize_scores(
        self,
        raw_scores: Dict[Planet, float]
    ) -> Dict[Planet, float]:
        """
        Apply soft cap to planet scores (Phase 8 - Remove Normalization Cascade).

        REMOVED (Phase 8 Fix):
        - Cross-planet normalization (was forcing sum to 100)
        - Contrast boost P^2 (was creating winner-takes-all)
        - Division by max (was compressing magnitude)

        NEW APPROACH:
        - Each planet has independent absolute score
        - Soft cap at 100 to prevent overflow
        - No forced competition between planets

        This fixes the normalization cascade that was crushing domain scores.

        Args:
            raw_scores: Raw scores for all planets

        Returns:
            Scores with soft cap applied (independent, not summing to 100)
        """
        if not raw_scores:
            return {}

        # Simply apply soft cap - no normalization, no contrast boost
        return {
            planet: min(score, 100.0)
            for planet, score in raw_scores.items()
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

