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
        """Test that the service initializes correctly."""
        assert scoring_engine is not None
        # Multiplicative model: weights for gated components
        assert scoring_engine.WEIGHT_TRANSIT == 0.40
        assert scoring_engine.WEIGHT_STRENGTH == 0.30
        assert scoring_engine.WEIGHT_ASPECT == 0.20
        assert scoring_engine.WEIGHT_MOTION == 0.10

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
        # dasha_gate = 40/100 = 0.4
        # weighted_transit = (80/100) * 0.40 * 0.4 * 100 = 12.8
        # weighted_strength = (45/100) * 0.30 * 0.4 * 100 = 5.4
        # weighted_aspect = (35/100) * 0.20 * 0.4 * 100 = 2.8
        # weighted_motion = (50/100) * 0.10 * 0.4 * 100 = 2.0

        assert weighted.dasha == 40.0  # Dasha is the gate, not weighted
        assert abs(weighted.transit - 12.8) < 0.001
        assert abs(weighted.strength - 5.4) < 0.001
        assert abs(weighted.aspect - 2.8) < 0.001
        assert abs(weighted.motion - 2.0) < 0.001

        # Verify total (excluding dasha gate)
        total = weighted.total()
        expected_total = 12.8 + 5.4 + 2.8 + 2.0  # 23.0
        assert abs(total - expected_total) < 0.001

    def test_raw_score_calculation(self, scoring_engine):
        """Test calculating raw score using MULTIPLICATIVE formula with enhancements."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=40.0,  # 40% dasha gate (>15, so no activation gate penalty)
            transit=80.0,
            strength=45.0,
            aspect=35.0,
            motion=50.0
        )

        raw_score = scoring_engine.calculate_raw_score(breakdown)

        # Formula (3 steps):
        # 1. Base: P_raw = dasha × (0.4×transit + 0.3×strength + 0.2×aspect + 0.1×motion)
        #    gated_sum = (80/100)*0.4 + (45/100)*0.3 + (35/100)*0.2 + (50/100)*0.1
        #              = 0.32 + 0.135 + 0.07 + 0.05 = 0.575
        #    base_score = 0.575 * (40/100) * 100 = 23.0
        # 2. Activation Gate: dasha=40 >= 15, so no penalty (×1.0)
        # 3. Contrast Boost: P_raw = 23.0 ** 1.5 = 110.36
        expected = 23.0 ** 1.5
        assert abs(raw_score - expected) < 0.1

    def test_raw_score_with_activation_gate(self, scoring_engine):
        """Test activation gate for very weak dasha."""
        from api.models import ComponentBreakdown

        breakdown = ComponentBreakdown(
            dasha=10.0,  # <15, so activation gate applies (×0.2)
            transit=80.0,
            strength=45.0,
            aspect=35.0,
            motion=50.0
        )

        raw_score = scoring_engine.calculate_raw_score(breakdown)

        # Formula (3 steps):
        # 1. Base: gated_sum = 0.575 (same as above)
        #    base_score = 0.575 * (10/100) * 100 = 5.75
        # 2. Activation Gate: dasha=10 < 15, so multiply by 0.2
        #    gated_score = 5.75 * 0.2 = 1.15
        # 3. Contrast Boost: P_raw = 1.15 ** 1.5 = 1.234
        expected = (5.75 * 0.2) ** 1.5
        assert abs(raw_score - expected) < 0.1

    def test_normalize_scores(self, scoring_engine):
        """Test normalizing scores to sum to 100."""
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

        # Verify proportions are maintained
        total_raw = sum(raw_scores.values())  # 220
        assert abs(normalized[Planet.SUN] - (50.0 / 220.0) * 100.0) < 0.001  # ~22.73
        assert abs(normalized[Planet.JUPITER] - (70.0 / 220.0) * 100.0) < 0.001  # ~31.82

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

