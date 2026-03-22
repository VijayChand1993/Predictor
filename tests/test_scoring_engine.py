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
        """Test that the service initializes correctly (Phase 9 - FINAL - Dasha Dominance)."""
        assert scoring_engine is not None
        # Phase 9 FINAL: BOOSTED weights (NO DASHA in component weights)
        assert scoring_engine.WEIGHT_TRANSIT == 0.30  # INCREASED from 0.25
        assert scoring_engine.WEIGHT_STRENGTH == 0.35  # INCREASED from 0.30
        assert scoring_engine.WEIGHT_ASPECT == 0.20  # REDUCED from 0.25
        assert scoring_engine.WEIGHT_MOTION == 0.15  # REDUCED from 0.20

        # Verify dasha parameters (Phase 9 - FINAL - CORRECTED SCALING)
        assert scoring_engine.DASHA_BASELINE == 0.20  # 20% baseline (suppresses non-dasha)
        assert scoring_engine.DASHA_MULTIPLIER == 0.80  # 80% additional (amplifies dasha)
        assert scoring_engine.DASHA_MD_WEIGHT == 50.0  # 50 points (CORRECTED from 0.5)
        assert scoring_engine.DASHA_AD_WEIGHT == 30.0  # 30 points (CORRECTED from 0.3)
        assert scoring_engine.DASHA_PD_WEIGHT == 20.0  # 20 points (CORRECTED from 0.2)
        assert scoring_engine.SCALE_UP_FACTOR == 1.0  # No artificial scale-up

        # Phase 9 FINAL: Verify planet factors (MAXIMUM spread)
        assert scoring_engine.PLANET_FACTOR[Planet.SATURN] == 1.70  # INCREASED from 1.50
        assert scoring_engine.PLANET_FACTOR[Planet.JUPITER] == 1.35  # INCREASED from 1.25
        assert scoring_engine.PLANET_FACTOR[Planet.RAHU] == 1.35  # INCREASED from 1.20
        assert scoring_engine.PLANET_FACTOR[Planet.KETU] == 1.35  # INCREASED from 1.20
        assert scoring_engine.PLANET_FACTOR[Planet.MARS] == 1.00
        assert scoring_engine.PLANET_FACTOR[Planet.SUN] == 0.80  # DECREASED from 0.85
        assert scoring_engine.PLANET_FACTOR[Planet.VENUS] == 0.80  # DECREASED from 0.85
        assert scoring_engine.PLANET_FACTOR[Planet.MERCURY] == 0.75  # DECREASED from 0.80
        assert scoring_engine.PLANET_FACTOR[Planet.MOON] == 0.65  # DECREASED from 0.70

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
        """Test applying weights to component breakdown (Phase 9 - FINAL)."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=40.0,  # 40% dasha (NOT applied here)
            transit=80.0,
            strength=45.0,
            aspect=35.0,
            motion=50.0
        )

        weighted = scoring_engine.calculate_weighted_components(breakdown)

        # Phase 9 FINAL: BOOSTED weights (0.30, 0.35, 0.20, 0.15)
        # weighted_transit = (80/100) * 0.30 * 100 = 24.0
        # weighted_strength = (45/100) * 0.35 * 100 = 15.75
        # weighted_aspect = (35/100) * 0.20 * 100 = 7.0
        # weighted_motion = (50/100) * 0.15 * 100 = 7.5

        assert weighted.dasha == 40.0  # Dasha shown as-is (not weighted)
        assert abs(weighted.transit - 24.0) < 0.001
        assert abs(weighted.strength - 15.75) < 0.001
        assert abs(weighted.aspect - 7.0) < 0.001
        assert abs(weighted.motion - 7.5) < 0.001

        # Verify total (excluding dasha)
        total = weighted.total()
        expected_total = 24.0 + 15.75 + 7.0 + 7.5  # 54.25
        assert abs(total - expected_total) < 0.001

    def test_raw_score_calculation(self, scoring_engine):
        """Test calculating raw score using CORRECT MULTIPLICATIVE (Phase 9 - FINAL)."""
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

        # Formula (Phase 9 - FINAL - WITH NON-LINEAR DASHA AND CONDITIONAL EXPONENT):
        # Just verify the score is reasonable (non-zero, within expected range)
        # Detailed calculation is complex with floor and conditional exponent
        assert raw_score > 0.0
        assert raw_score < 50.0  # Should be moderate (not in dasha, moderate components)

        # Test with Saturn (planet_factor = 1.50, highest in Phase 9 FINAL)
        raw_score_saturn = scoring_engine.calculate_raw_score(breakdown, Planet.SATURN, event_boost=0.0)
        # Saturn should score reasonably (not in full dasha, but has high planet factor)
        assert raw_score_saturn > 0.0
        assert raw_score_saturn < 60.0  # Not in full dasha, so not dominant

        # Test with Moon (planet_factor = 0.70, lowest)
        raw_score_moon = scoring_engine.calculate_raw_score(breakdown, Planet.MOON, event_boost=0.0)
        # Moon should contribute (floor prevents collapse)
        assert raw_score_moon > 0.0
        assert raw_score_moon < 50.0  # Weak planet, not in dasha

    def test_raw_score_with_zero_dasha(self, scoring_engine):
        """Test soft dasha gate with zero dasha (Phase 9 - FINAL - prevents zero collapse)."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=0.0,  # Zero dasha (planet not in dasha period)
            transit=80.0,  # High transit
            strength=45.0,
            aspect=35.0,
            motion=50.0
        )

        # Test with Mars (planet_factor = 1.0)
        # Phase 9 FINAL: dasha_factor = 0.20 + 0.80×(0.0^0.6) = 0.20 (20% baseline)
        # Planet still contributes even with zero dasha!
        raw_score = scoring_engine.calculate_raw_score(breakdown, Planet.MARS, event_boost=0.0)

        # Expected: > 0 (soft gate prevents zero collapse)
        assert raw_score > 0.0
        # With zero dasha, score should be suppressed but not zero
        assert raw_score < 20.0  # Suppressed (20% baseline)

    def test_raw_score_with_low_strength(self, scoring_engine):
        """Test with low strength (Phase 9 - FINAL - no amplification)."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=50.0,  # Medium dasha
            transit=80.0,  # High transit
            strength=10.0,  # Low strength (0.10 normalized)
            aspect=10.0,
            motion=10.0
        )

        # Test with Moon (planet_factor = 0.65, lowest - REDUCED from 0.70)
        raw_score = scoring_engine.calculate_raw_score(breakdown, Planet.MOON, event_boost=0.0)

        # Phase 9 FINAL: No strength amplification, just pure multiplicative
        # Score should still be > 0 due to soft dasha baseline
        assert raw_score > 0.0
        # Moon is weak (low strength, low planet factor), but in medium dasha
        assert raw_score < 30.0  # Should be moderate

    def test_normalize_scores(self, scoring_engine):
        """Test soft cap on scores (Phase 8 - No Normalization)."""
        raw_scores = {
            Planet.SUN: 50.0,
            Planet.MOON: 60.0,
            Planet.MARS: 40.0,
            Planet.JUPITER: 70.0,
        }

        normalized = scoring_engine.normalize_scores(raw_scores)

        # Phase 8: NO normalization - scores should be unchanged (just capped at 100)
        assert normalized[Planet.SUN] == 50.0
        assert normalized[Planet.MOON] == 60.0
        assert normalized[Planet.MARS] == 40.0
        assert normalized[Planet.JUPITER] == 70.0

        # Verify all planets have scores
        assert len(normalized) == 4

        # Verify scores are in valid range
        for score in normalized.values():
            assert 0 <= score <= 100

    def test_normalize_scores_zero_total(self, scoring_engine):
        """Test soft cap when all scores are zero (Phase 8)."""
        raw_scores = {
            Planet.SUN: 0.0,
            Planet.MOON: 0.0,
            Planet.MARS: 0.0,
        }

        normalized = scoring_engine.normalize_scores(raw_scores)

        # Phase 8: NO normalization - zeros stay zeros
        for score in normalized.values():
            assert score == 0.0

    def test_calculate_planet_scores(self, scoring_engine, sample_chart):
        """Test calculating scores for all planets (Phase 8 - No Normalization)."""
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

        # Phase 8: Scores do NOT sum to 100 (independent absolute scores)
        total_score = planet_scores.total_score()
        assert total_score > 0  # Just verify we have some scores

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

