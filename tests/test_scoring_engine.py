"""
Unit tests for ScoringEngine.
"""
import pytest
from datetime import datetime

from api.models import (
    Planet,
    Sign,
    Dignity,
    BirthData,
    Location,
    NatalChart,
    PlanetPlacement,
    HouseInfo,
)
from api.services.scoring_engine import ScoringEngine


class TestScoringEngine:
    """Test suite for ScoringEngine."""
    
    @pytest.fixture
    def scoring_engine(self):
        """Create a ScoringEngine instance."""
        return ScoringEngine()
    
    @pytest.fixture
    def sample_chart(self):
        """Create a sample natal chart for testing."""
        birth_data = BirthData(
            date=datetime(1993, 4, 2, 1, 15),
            location=Location(
                latitude=29.58633,
                longitude=80.23275,
                city="Pithoragarh",
                country="India",
                timezone="Asia/Kolkata"
            ),
            name="Test Person"
        )
        
        # Create planet placements
        planets = {
            Planet.SUN: PlanetPlacement(
                planet=Planet.SUN,
                sign=Sign.ARIES,
                degree=10.5,
                house=5,
                nakshatra="Ashwini",
                nakshatra_pada=1,
                dignity=Dignity.EXALTED,
                is_retrograde=False
            ),
            Planet.MOON: PlanetPlacement(
                planet=Planet.MOON,
                sign=Sign.CANCER,
                degree=15.0,
                house=1,
                nakshatra="Pushya",
                nakshatra_pada=2,
                dignity=Dignity.OWN_SIGN,
                is_retrograde=False
            ),
            Planet.MARS: PlanetPlacement(
                planet=Planet.MARS,
                sign=Sign.ARIES,
                degree=12.0,
                house=5,
                nakshatra="Ashwini",
                nakshatra_pada=3,
                dignity=Dignity.OWN_SIGN,
                is_retrograde=False
            ),
            Planet.MERCURY: PlanetPlacement(
                planet=Planet.MERCURY,
                sign=Sign.PISCES,
                degree=20.0,
                house=4,
                nakshatra="Revati",
                nakshatra_pada=1,
                dignity=Dignity.DEBILITATED,
                is_retrograde=False
            ),
            Planet.JUPITER: PlanetPlacement(
                planet=Planet.JUPITER,
                sign=Sign.CANCER,
                degree=18.0,
                house=1,
                nakshatra="Ashlesha",
                nakshatra_pada=2,
                dignity=Dignity.EXALTED,
                is_retrograde=True
            ),
            Planet.VENUS: PlanetPlacement(
                planet=Planet.VENUS,
                sign=Sign.PISCES,
                degree=25.0,
                house=4,
                nakshatra="Revati",
                nakshatra_pada=4,
                dignity=Dignity.EXALTED,
                is_retrograde=False
            ),
            Planet.SATURN: PlanetPlacement(
                planet=Planet.SATURN,
                sign=Sign.CAPRICORN,
                degree=28.0,
                house=2,
                nakshatra="Dhanishta",
                nakshatra_pada=4,
                dignity=Dignity.OWN_SIGN,
                is_retrograde=False
            ),
            Planet.RAHU: PlanetPlacement(
                planet=Planet.RAHU,
                sign=Sign.SCORPIO,
                degree=5.0,
                house=11,
                nakshatra="Anuradha",
                nakshatra_pada=1,
                dignity=Dignity.NEUTRAL,
                is_retrograde=True
            ),
            Planet.KETU: PlanetPlacement(
                planet=Planet.KETU,
                sign=Sign.TAURUS,
                degree=5.0,
                house=5,
                nakshatra="Krittika",
                nakshatra_pada=1,
                dignity=Dignity.NEUTRAL,
                is_retrograde=True
            ),
        }
        
        # Create house info
        houses = {
            i: HouseInfo(
                house_number=i,
                sign=Sign.CANCER if i == 1 else Sign.ARIES,
                degree=0.0,
                lord=Planet.MOON if i == 1 else Planet.MARS
            ) for i in range(1, 13)
        }
        
        return NatalChart(
            chart_id="test_chart",
            birth_data=birth_data,
            ascendant_sign=Sign.CANCER,
            ascendant_degree=10.5,
            moon_sign=Sign.CANCER,
            planets=planets,
            houses=houses
        )
    
    def test_service_initialization(self, scoring_engine):
        """Test that the service initializes correctly (Phase 7b - Decompression)."""
        assert scoring_engine is not None
        # Phase 7b: Rebalanced weights for gated components
        assert scoring_engine.WEIGHT_TRANSIT == 0.50
        assert scoring_engine.WEIGHT_STRENGTH == 0.30
        assert scoring_engine.WEIGHT_ASPECT == 0.15
        assert scoring_engine.WEIGHT_MOTION == 0.05

        # Verify enhancement parameters (Phase 7b - Decompression)
        assert scoring_engine.DASHA_BASELINE == 0.3  # 30% baseline for non-dasha planets
        assert scoring_engine.DASHA_MULTIPLIER == 0.7  # 70% additional for dasha planets
        assert scoring_engine.SCALE_UP_FACTOR == 1.5  # Scale up to expand range
        assert scoring_engine.CONTRAST_EXPONENT == 2.0  # Competition layer (P^2)

        # Phase 5: Verify planet factors
        assert scoring_engine.PLANET_FACTOR[Planet.SATURN] == 1.25
        assert scoring_engine.PLANET_FACTOR[Planet.JUPITER] == 1.20
        assert scoring_engine.PLANET_FACTOR[Planet.RAHU] == 1.15
        assert scoring_engine.PLANET_FACTOR[Planet.KETU] == 1.10
        assert scoring_engine.PLANET_FACTOR[Planet.MARS] == 1.00
        assert scoring_engine.PLANET_FACTOR[Planet.SUN] == 0.95
        assert scoring_engine.PLANET_FACTOR[Planet.VENUS] == 0.90
        assert scoring_engine.PLANET_FACTOR[Planet.MERCURY] == 0.85
        assert scoring_engine.PLANET_FACTOR[Planet.MOON] == 0.75

        # Verify gated weights sum to 1.0
        total_weight = (
            scoring_engine.WEIGHT_TRANSIT +
            scoring_engine.WEIGHT_STRENGTH +
            scoring_engine.WEIGHT_ASPECT +
            scoring_engine.WEIGHT_MOTION
        )
        assert abs(total_weight - 1.0) < 0.001  # Allow small floating point error

    def test_component_breakdown(self, scoring_engine, sample_chart):
        """Test calculating component breakdown for a planet."""
        calculation_date = datetime(2026, 3, 20, 12, 0, 0)

        breakdown = scoring_engine.calculate_component_breakdown(
            Planet.JUPITER,
            sample_chart,
            calculation_date
        )

        # Verify all components are present and in valid range (aspect removed)
        assert 0 <= breakdown.dasha <= 100
        assert 0 <= breakdown.transit <= 100
        assert 0 <= breakdown.strength <= 100
        assert 0 <= breakdown.motion <= 100

    def test_weighted_components(self, scoring_engine):
        """Test applying MULTIPLICATIVE weights to component breakdown."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=40.0,  # 40% dasha gate
            transit=80.0,
            strength=45.0,
            aspect=35.0,
            motion=50.0
        )

        weighted = scoring_engine.calculate_weighted_components(breakdown)

        # Multiplicative formula: dasha gates the other components
        # Note: This uses the OLD formula (linear dasha gate) for display purposes
        # The actual scoring uses dasha^1.2 in calculate_raw_score
        # dasha_gate = 40/100 = 0.4
        # weighted_transit = (80/100) * 0.50 * 0.4 * 100 = 16.0
        # weighted_strength = (45/100) * 0.30 * 0.4 * 100 = 5.4
        # weighted_aspect = (35/100) * 0.15 * 0.4 * 100 = 2.1
        # weighted_motion = (50/100) * 0.05 * 0.4 * 100 = 1.0

        assert weighted.dasha == 40.0  # Dasha is the gate, not weighted
        assert abs(weighted.transit - 16.0) < 0.001
        assert abs(weighted.strength - 5.4) < 0.001
        assert abs(weighted.aspect - 2.1) < 0.001
        assert abs(weighted.motion - 1.0) < 0.001

        # Verify total (excluding dasha gate)
        total = weighted.total()
        expected_total = 16.0 + 5.4 + 2.1 + 1.0  # 24.5
        assert abs(total - expected_total) < 0.001

    def test_raw_score_calculation(self, scoring_engine):
        """Test calculating raw score using PURE MULTIPLICATIVE (Phase 7b - Decompression)."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=40.0,
            transit=80.0,
            strength=45.0,
            aspect=35.0,
            motion=50.0
        )

        # Test with Mars (planet_factor = 1.0, baseline)
        raw_score = scoring_engine.calculate_raw_score(breakdown, Planet.MARS, event_boost=0.0)

        # Formula (Phase 7b - 6 steps):
        # 1. Base: base = 0.5×0.8 + 0.3×0.45 + 0.15×0.35 + 0.05×0.5 = 0.6125
        # 2. SOFT Dasha Gate: dashaFactor = 0.3 + 0.7×0.4 = 0.58
        # 3. Apply: score = 0.6125 × 0.58 = 0.3553
        # 4. Strength AMPLIFICATION: score *= (1 + 0.5×0.45) = 0.3553 × 1.225 = 0.4352
        # 5. Planet Factor: score *= 1.0 (Mars) = 0.4352
        # 6. Scale Up: score *= 1.5 = 0.6528
        # Final: 0.6528 × 100 = 65.28
        base = 0.6125
        dasha_factor = 0.3 + 0.7 * 0.4
        after_dasha = base * dasha_factor
        strength_amp = 1.0 + 0.5 * 0.45
        after_strength = after_dasha * strength_amp
        after_planet_factor = after_strength * 1.0  # Mars
        after_scale = after_planet_factor * 1.5
        expected = after_scale * 100.0
        assert abs(raw_score - expected) < 1.0

        # Test with Saturn (planet_factor = 1.25, highest)
        raw_score_saturn = scoring_engine.calculate_raw_score(breakdown, Planet.SATURN, event_boost=0.0)
        expected_saturn = after_strength * 1.25 * 1.5 * 100.0
        assert abs(raw_score_saturn - expected_saturn) < 1.0

        # Test with Moon (planet_factor = 0.75, lowest)
        raw_score_moon = scoring_engine.calculate_raw_score(breakdown, Planet.MOON, event_boost=0.0)
        expected_moon = after_strength * 0.75 * 1.5 * 100.0
        assert abs(raw_score_moon - expected_moon) < 1.0

    def test_raw_score_with_zero_dasha(self, scoring_engine):
        """Test soft dasha gate with zero dasha (Phase 7b - prevents zero collapse)."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=0.0,  # Zero dasha (planet not in dasha period)
            transit=80.0,  # High transit
            strength=45.0,
            aspect=35.0,
            motion=50.0
        )

        # Test with Mars (planet_factor = 1.0)
        # Soft dasha: dashaFactor = 0.3 + 0.7×0.0 = 0.3 (30% baseline)
        # Planet still contributes even with zero dasha!
        raw_score = scoring_engine.calculate_raw_score(breakdown, Planet.MARS, event_boost=0.0)

        # Expected: > 0 (soft gate prevents zero collapse)
        assert raw_score > 0.0

        # Calculate expected value (Phase 7b)
        base = 0.6125
        dasha_factor = 0.3  # 30% baseline
        after_dasha = base * dasha_factor
        strength_amp = 1.0 + 0.5 * 0.45
        after_scale = after_dasha * strength_amp * 1.0 * 1.5
        expected = after_scale * 100.0
        assert abs(raw_score - expected) < 1.0

    def test_raw_score_with_low_strength(self, scoring_engine):
        """Test amplification with low strength (Phase 7b)."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=50.0,  # Medium dasha
            transit=80.0,  # High transit
            strength=10.0,  # Low strength (0.10 normalized)
            aspect=10.0,
            motion=10.0
        )

        # Test with Moon (planet_factor = 0.75, lowest)
        raw_score = scoring_engine.calculate_raw_score(breakdown, Planet.MOON, event_boost=0.0)

        # With low strength, amplification is minimal: 1 + 0.5×0.1 = 1.05
        # But score should still be > 0 due to soft dasha and scale-up
        assert raw_score > 0.0

        # Calculate expected
        base = 0.5 * 0.8 + 0.3 * 0.1 + 0.15 * 0.1 + 0.05 * 0.1
        dasha_factor = 0.3 + 0.7 * 0.5
        strength_amp = 1.0 + 0.5 * 0.1
        expected = base * dasha_factor * strength_amp * 0.75 * 1.5 * 100.0
        assert abs(raw_score - expected) < 1.0

    def test_normalize_scores(self, scoring_engine):
        """Test normalizing scores with competition layer (Phase 6)."""
        raw_scores = {
            Planet.SUN: 50.0,
            Planet.MOON: 60.0,
            Planet.MARS: 40.0,
            Planet.JUPITER: 70.0,
        }

        normalized = scoring_engine.normalize_scores(raw_scores)

        # Verify normalization
        total = sum(normalized.values())
        assert abs(total - 100.0) < 0.001

        # Competition layer changes proportions (not linear anymore)
        # Step 1: Divide by max (70) → SUN: 0.714, MOON: 0.857, MARS: 0.571, JUPITER: 1.0
        # Step 2: P^2 → SUN: 0.510, MOON: 0.735, MARS: 0.327, JUPITER: 1.0
        # Step 3: Normalize to 100 → sum = 2.572, so multiply by 100/2.572
        # Jupiter should be highest (strongest gets stronger)
        assert normalized[Planet.JUPITER] > normalized[Planet.MOON]
        assert normalized[Planet.MOON] > normalized[Planet.SUN]
        assert normalized[Planet.SUN] > normalized[Planet.MARS]

        # Jupiter should get MORE than linear proportion due to contrast boost
        linear_jupiter = (70.0 / 220.0) * 100.0  # ~31.82
        assert normalized[Planet.JUPITER] > linear_jupiter

    def test_normalize_scores_zero_total(self, scoring_engine):
        """Test normalizing when all scores are zero."""
        raw_scores = {
            Planet.SUN: 0.0,
            Planet.MOON: 0.0,
            Planet.MARS: 0.0,
        }

        normalized = scoring_engine.normalize_scores(raw_scores)

        # Should distribute equally
        for score in normalized.values():
            assert abs(score - (100.0 / 3)) < 0.001  # ~33.33

        # Total should still be 100
        total = sum(normalized.values())
        assert abs(total - 100.0) < 0.001

    def test_calculate_planet_scores(self, scoring_engine, sample_chart):
        """Test calculating scores for all planets."""
        calculation_date = datetime(2026, 3, 20, 12, 0, 0)

        planet_scores = scoring_engine.calculate_planet_scores(
            sample_chart,
            calculation_date
        )

        # Verify all planets have scores
        assert len(planet_scores.scores) == len(sample_chart.planets)

        # Verify each planet has valid score
        for planet, score_obj in planet_scores.scores.items():
            assert score_obj.planet == planet
            assert 0 <= score_obj.score <= 100
            assert score_obj.breakdown is not None
            assert score_obj.weighted_components is not None

        # Verify scores sum to 100
        total_score = planet_scores.total_score()
        assert abs(total_score - 100.0) < 0.001

        # Verify calculation date
        assert planet_scores.calculation_date == calculation_date

    def test_score_breakdown_components(self, scoring_engine, sample_chart):
        """Test that score breakdown has all required components."""
        calculation_date = datetime(2026, 3, 20, 12, 0, 0)

        planet_scores = scoring_engine.calculate_planet_scores(
            sample_chart,
            calculation_date
        )

        # Check Jupiter's breakdown
        jupiter_score = planet_scores.scores[Planet.JUPITER]

        # Verify breakdown components (aspect restored)
        assert hasattr(jupiter_score.breakdown, 'dasha')
        assert hasattr(jupiter_score.breakdown, 'transit')
        assert hasattr(jupiter_score.breakdown, 'strength')
        assert hasattr(jupiter_score.breakdown, 'aspect')
        assert hasattr(jupiter_score.breakdown, 'motion')

        # Verify weighted components (aspect restored)
        assert hasattr(jupiter_score.weighted_components, 'dasha')
        assert hasattr(jupiter_score.weighted_components, 'transit')
        assert hasattr(jupiter_score.weighted_components, 'strength')
        assert hasattr(jupiter_score.weighted_components, 'aspect')
        assert hasattr(jupiter_score.weighted_components, 'motion')

    def test_component_weights_sum(self, scoring_engine):
        """Test that gated component weights sum to 1.0."""
        total = (
            scoring_engine.WEIGHT_TRANSIT +
            scoring_engine.WEIGHT_STRENGTH +
            scoring_engine.WEIGHT_ASPECT +
            scoring_engine.WEIGHT_MOTION
        )
        assert abs(total - 1.0) < 0.001

    def test_normalize_dasha(self, scoring_engine):
        """Test dasha normalization to 0-1 scale."""
        # Test minimum (0)
        assert scoring_engine.normalize_dasha(0.0) == 0.0

        # Test maximum (100)
        assert scoring_engine.normalize_dasha(100.0) == 1.0

        # Test middle value (50)
        assert scoring_engine.normalize_dasha(50.0) == 0.5

        # Test typical value (40 = mahadasha only)
        assert abs(scoring_engine.normalize_dasha(40.0) - 0.4) < 0.001

    def test_normalize_transit(self, scoring_engine):
        """Test transit normalization to 0-1 scale."""
        # Test minimum (0)
        assert scoring_engine.normalize_transit(0.0) == 0.0

        # Test maximum (100 = Jupiter in Kendra)
        assert scoring_engine.normalize_transit(100.0) == 1.0

        # Test typical value (60 = Sun in Kendra)
        assert abs(scoring_engine.normalize_transit(60.0) - 0.6) < 0.001

    def test_normalize_strength(self, scoring_engine):
        """Test strength normalization to 0-1 scale."""
        # Test minimum (0 = debilitated + combust)
        assert scoring_engine.normalize_strength(0.0) == 0.0

        # Test maximum (100 = exalted + retrograde)
        assert scoring_engine.normalize_strength(100.0) == 1.0

        # Test neutral (50 = no dignity, no retrograde, no combustion)
        assert scoring_engine.normalize_strength(50.0) == 0.5

    def test_normalize_aspect(self, scoring_engine):
        """Test aspect normalization to 0-1 scale."""
        # Test minimum (0)
        assert scoring_engine.normalize_aspect(0.0) == 0.0

        # Test maximum (100 = AspectService max range)
        assert abs(scoring_engine.normalize_aspect(100.0) - 1.0) < 0.001

        # Test typical value (50)
        assert abs(scoring_engine.normalize_aspect(50.0) - 0.5) < 0.001

    def test_normalize_motion(self, scoring_engine):
        """Test motion normalization to 0-1 scale."""
        # Test minimum (0)
        assert scoring_engine.normalize_motion(0.0) == 0.0

        # Test maximum (65 = fastest direct motion)
        assert abs(scoring_engine.normalize_motion(65.0) - 1.0) < 0.001

        # Test neutral baseline (50 = non-significant planet)
        assert abs(scoring_engine.normalize_motion(50.0) - (50.0/65.0)) < 0.001

        # Test typical fast motion (60)
        assert abs(scoring_engine.normalize_motion(60.0) - (60.0/65.0)) < 0.001

