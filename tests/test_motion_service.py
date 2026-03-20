"""
Unit tests for MotionService.
"""
import pytest
from datetime import datetime

from api.models import (
    Planet,
    Sign,
    Dignity,
    MotionType,
    BirthData,
    Location,
    NatalChart,
    PlanetPlacement,
    HouseInfo,
    TransitPlacement,
)
from api.services.motion_service import MotionService


class TestMotionService:
    """Test suite for MotionService."""
    
    @pytest.fixture
    def motion_service(self):
        """Create a MotionService instance."""
        return MotionService()
    
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
        }
        
        # Create house info
        houses = {
            i: HouseInfo(
                house_number=i,
                sign=Sign.ARIES,
                degree=0.0,
                lord=Planet.MARS
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
    
    def test_service_initialization(self, motion_service):
        """Test that the service initializes correctly."""
        assert motion_service is not None
        assert Planet.MOON in motion_service.SIGNIFICANT_PLANETS
        assert Planet.MARS in motion_service.SIGNIFICANT_PLANETS
        assert Planet.MERCURY in motion_service.SIGNIFICANT_PLANETS
    
    def test_is_motion_significant(self, motion_service):
        """Test motion significance detection."""
        # Significant planets
        assert motion_service.is_motion_significant(Planet.MOON) is True
        assert motion_service.is_motion_significant(Planet.MARS) is True
        assert motion_service.is_motion_significant(Planet.MERCURY) is True
        
        # Not significant
        assert motion_service.is_motion_significant(Planet.JUPITER) is False
        assert motion_service.is_motion_significant(Planet.SATURN) is False
        assert motion_service.is_motion_significant(Planet.SUN) is False
    
    def test_motion_breakdown_fast(self, motion_service):
        """Test motion breakdown for fast-moving planet."""
        transit_placement = TransitPlacement(
            planet=Planet.MOON,
            sign=Sign.CANCER,
            house=1,
            degree=15.0,
            is_retrograde=False,
            speed=14.5,
            motion_type=MotionType.FAST
        )
        
        breakdown = motion_service.calculate_motion_breakdown(
            Planet.MOON,
            transit_placement
        )
        
        assert breakdown.speed == 14.5
        assert breakdown.motion_type == MotionType.FAST
        assert breakdown.motion_modifier == 10
        assert breakdown.is_significant is True
    
    def test_motion_breakdown_stationary(self, motion_service):
        """Test motion breakdown for stationary planet."""
        transit_placement = TransitPlacement(
            planet=Planet.MERCURY,
            sign=Sign.GEMINI,
            house=3,
            degree=10.0,
            is_retrograde=False,
            speed=0.05,
            motion_type=MotionType.STATIONARY
        )
        
        breakdown = motion_service.calculate_motion_breakdown(
            Planet.MERCURY,
            transit_placement
        )
        
        assert breakdown.speed == 0.05
        assert breakdown.motion_type == MotionType.STATIONARY
        assert breakdown.motion_modifier == 15
        assert breakdown.is_significant is True
    
    def test_motion_breakdown_retrograde(self, motion_service):
        """Test motion breakdown for retrograde planet."""
        transit_placement = TransitPlacement(
            planet=Planet.MARS,
            sign=Sign.ARIES,
            house=5,
            degree=12.0,
            is_retrograde=True,
            speed=-0.3,
            motion_type=MotionType.RETROGRADE
        )
        
        breakdown = motion_service.calculate_motion_breakdown(
            Planet.MARS,
            transit_placement
        )
        
        assert breakdown.speed == -0.3
        assert breakdown.motion_type == MotionType.RETROGRADE
        assert breakdown.motion_modifier == 10
        assert breakdown.is_significant is True

    def test_motion_breakdown_not_significant(self, motion_service):
        """Test motion breakdown for planet where motion is not significant."""
        transit_placement = TransitPlacement(
            planet=Planet.JUPITER,
            sign=Sign.SAGITTARIUS,
            house=6,
            degree=20.0,
            is_retrograde=False,
            speed=0.08,
            motion_type=MotionType.NORMAL
        )

        breakdown = motion_service.calculate_motion_breakdown(
            Planet.JUPITER,
            transit_placement
        )

        assert breakdown.speed == 0.08
        assert breakdown.motion_type == MotionType.NORMAL
        assert breakdown.motion_modifier == 0
        assert breakdown.is_significant is False

    def test_motion_weight_fast(self, motion_service):
        """Test motion weight calculation for fast motion."""
        # Fast: modifier = +10
        weight = motion_service.calculate_motion_weight(10, True)
        assert weight == 60.0  # 50 + 10

    def test_motion_weight_stationary(self, motion_service):
        """Test motion weight calculation for stationary motion."""
        # Stationary: modifier = +15
        weight = motion_service.calculate_motion_weight(15, True)
        assert weight == 65.0  # 50 + 15

    def test_motion_weight_slow(self, motion_service):
        """Test motion weight calculation for slow motion."""
        # Slow: modifier = +5
        weight = motion_service.calculate_motion_weight(5, True)
        assert weight == 55.0  # 50 + 5

    def test_motion_weight_normal(self, motion_service):
        """Test motion weight calculation for normal motion."""
        # Normal: modifier = 0
        weight = motion_service.calculate_motion_weight(0, True)
        assert weight == 50.0  # 50 + 0

    def test_motion_weight_not_significant(self, motion_service):
        """Test motion weight for planets where motion is not significant."""
        # Should always return baseline of 50
        weight = motion_service.calculate_motion_weight(10, False)
        assert weight == 50.0

        weight = motion_service.calculate_motion_weight(15, False)
        assert weight == 50.0

    def test_calculate_planet_motion(self, motion_service):
        """Test calculating motion for a single planet."""
        transit_placement = TransitPlacement(
            planet=Planet.MOON,
            sign=Sign.CANCER,
            house=1,
            degree=15.0,
            is_retrograde=False,
            speed=14.5,
            motion_type=MotionType.FAST
        )

        planet_motion = motion_service.calculate_planet_motion(
            Planet.MOON,
            transit_placement
        )

        assert planet_motion.planet == Planet.MOON
        assert planet_motion.breakdown.motion_modifier == 10
        assert planet_motion.motion_weight == 60.0

    def test_calculate_chart_motions(self, motion_service, sample_chart):
        """Test calculating motions for entire chart."""
        calculation_date = datetime(2026, 3, 20, 12, 0, 0)

        chart_motions = motion_service.calculate_chart_motions(
            sample_chart,
            calculation_date
        )

        assert chart_motions.chart_id == "test_chart"
        assert chart_motions.calculation_date == calculation_date
        assert len(chart_motions.planet_motions) > 0

        # Check that Moon motion is included
        assert Planet.MOON in chart_motions.planet_motions
        moon_motion = chart_motions.planet_motions[Planet.MOON]
        assert moon_motion.planet == Planet.MOON
        assert moon_motion.breakdown.is_significant is True

    def test_motion_modifiers_constants(self, motion_service):
        """Test that motion modifiers are correctly defined."""
        from api.models import MOTION_MODIFIERS

        assert MOTION_MODIFIERS[MotionType.FAST] == 10
        assert MOTION_MODIFIERS[MotionType.STATIONARY] == 15
        assert MOTION_MODIFIERS[MotionType.SLOW] == 5
        assert MOTION_MODIFIERS[MotionType.NORMAL] == 0
        assert MOTION_MODIFIERS[MotionType.RETROGRADE] == 10

    def test_motion_weight_bounds(self, motion_service):
        """Test that motion weight is bounded 0-100."""
        # Maximum (stationary)
        weight = motion_service.calculate_motion_weight(15, True)
        assert weight == 65.0
        assert weight <= 100.0

        # Minimum (normal for non-significant)
        weight = motion_service.calculate_motion_weight(0, False)
        assert weight == 50.0
        assert weight >= 0.0

    def test_significant_planets_list(self, motion_service):
        """Test that significant planets list is correct."""
        assert len(motion_service.SIGNIFICANT_PLANETS) == 3
        assert Planet.MOON in motion_service.SIGNIFICANT_PLANETS
        assert Planet.MARS in motion_service.SIGNIFICANT_PLANETS
        assert Planet.MERCURY in motion_service.SIGNIFICANT_PLANETS

        # Verify slow planets are not in the list
        assert Planet.JUPITER not in motion_service.SIGNIFICANT_PLANETS
        assert Planet.SATURN not in motion_service.SIGNIFICANT_PLANETS

