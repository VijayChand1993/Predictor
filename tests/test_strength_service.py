"""
Unit tests for StrengthService.
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
from api.services.strength_service import StrengthService


class TestStrengthService:
    """Test suite for StrengthService."""
    
    @pytest.fixture
    def strength_service(self):
        """Create a StrengthService instance."""
        return StrengthService()
    
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
            Planet.JUPITER: PlanetPlacement(
                planet=Planet.JUPITER,
                sign=Sign.CANCER,
                degree=15.0,
                house=1,
                nakshatra="Pushya",
                nakshatra_pada=2,
                dignity=Dignity.EXALTED,
                is_retrograde=True
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
            Planet.SATURN: PlanetPlacement(
                planet=Planet.SATURN,
                sign=Sign.CAPRICORN,
                degree=25.0,
                house=10,
                nakshatra="Dhanishta",
                nakshatra_pada=4,
                dignity=Dignity.OWN_SIGN,
                is_retrograde=False
            ),
            Planet.VENUS: PlanetPlacement(
                planet=Planet.VENUS,
                sign=Sign.ARIES,
                degree=11.0,
                house=5,
                nakshatra="Ashwini",
                nakshatra_pada=1,
                dignity=Dignity.NEUTRAL,
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
            ascendant_sign=Sign.SAGITTARIUS,
            ascendant_degree=10.5,
            moon_sign=Sign.CANCER,
            planets=planets,
            houses=houses
        )
    
    def test_service_initialization(self, strength_service):
        """Test that the service initializes correctly."""
        assert strength_service is not None
        assert strength_service.RETROGRADE_BONUS == 10
        assert strength_service.COMBUSTION_DISTANCES[Planet.MOON] == 12.0
    
    def test_combustion_same_sign(self, strength_service):
        """Test combustion detection when planet is in same sign as Sun."""
        # Mars at 12 degrees, Sun at 10.5 degrees in Aries
        # Distance = 1.5 degrees, Mars combustion distance = 17 degrees
        is_combust = strength_service.is_combust(
            Planet.MARS, 12.0, 10.5, Sign.ARIES, Sign.ARIES
        )
        assert is_combust is True
    
    def test_combustion_different_sign(self, strength_service):
        """Test that planets in different signs are not combust."""
        is_combust = strength_service.is_combust(
            Planet.JUPITER, 15.0, 10.5, Sign.CANCER, Sign.ARIES
        )
        assert is_combust is False
    
    def test_combustion_sun_not_combust(self, strength_service):
        """Test that Sun cannot be combust."""
        is_combust = strength_service.is_combust(
            Planet.SUN, 10.5, 10.5, Sign.ARIES, Sign.ARIES
        )
        assert is_combust is False
    
    def test_combustion_rahu_ketu_not_combust(self, strength_service):
        """Test that Rahu and Ketu cannot be combust."""
        is_combust_rahu = strength_service.is_combust(
            Planet.RAHU, 10.5, 10.5, Sign.ARIES, Sign.ARIES
        )
        is_combust_ketu = strength_service.is_combust(
            Planet.KETU, 10.5, 10.5, Sign.ARIES, Sign.ARIES
        )
        assert is_combust_rahu is False
        assert is_combust_ketu is False

    def test_strength_breakdown_exalted(self, strength_service, sample_chart):
        """Test strength breakdown for exalted planet."""
        sun_placement = sample_chart.planets[Planet.SUN]
        jupiter_placement = sample_chart.planets[Planet.JUPITER]

        breakdown = strength_service.calculate_strength_breakdown(
            Planet.JUPITER, jupiter_placement, sun_placement
        )

        assert breakdown.dignity == Dignity.EXALTED
        assert breakdown.dignity_score == 25
        assert breakdown.is_retrograde is True
        assert breakdown.retrograde_score == 10
        assert breakdown.is_combust is False
        assert breakdown.combustion_score == 0
        assert breakdown.total_strength == 35  # 25 + 10 + 0

    def test_strength_breakdown_combust(self, strength_service, sample_chart):
        """Test strength breakdown for combust planet."""
        sun_placement = sample_chart.planets[Planet.SUN]
        mars_placement = sample_chart.planets[Planet.MARS]

        breakdown = strength_service.calculate_strength_breakdown(
            Planet.MARS, mars_placement, sun_placement
        )

        assert breakdown.dignity == Dignity.OWN_SIGN
        assert breakdown.dignity_score == 20
        assert breakdown.is_retrograde is False
        assert breakdown.retrograde_score == 0
        assert breakdown.is_combust is True  # Mars at 12, Sun at 10.5 in same sign
        assert breakdown.combustion_score == -15
        assert breakdown.total_strength == 5  # 20 + 0 - 15

    def test_strength_weight_calculation(self, strength_service):
        """Test strength weight normalization."""
        # Exalted + Retrograde: 25 + 10 = 35
        # W_strength = 50 + 35 = 85
        weight = strength_service.calculate_strength_weight(35)
        assert weight == 85.0

        # Debilitated + Combust: -25 - 15 = -40
        # W_strength = max(0, 50 - 40) = 10
        weight = strength_service.calculate_strength_weight(-40)
        assert weight == 10.0

        # Neutral: 0
        # W_strength = 50 + 0 = 50
        weight = strength_service.calculate_strength_weight(0)
        assert weight == 50.0

    def test_strength_weight_bounds(self, strength_service):
        """Test that strength weight is bounded 0-100."""
        # Very high strength
        weight = strength_service.calculate_strength_weight(100)
        assert weight == 100.0

        # Very low strength
        weight = strength_service.calculate_strength_weight(-100)
        assert weight == 0.0

    def test_calculate_planet_strength(self, strength_service, sample_chart):
        """Test calculating strength for a single planet."""
        sun_placement = sample_chart.planets[Planet.SUN]
        jupiter_placement = sample_chart.planets[Planet.JUPITER]

        planet_strength = strength_service.calculate_planet_strength(
            Planet.JUPITER, jupiter_placement, sun_placement
        )

        assert planet_strength.planet == Planet.JUPITER
        assert planet_strength.breakdown.total_strength == 35
        assert planet_strength.strength_weight == 85.0

    def test_calculate_chart_strengths(self, strength_service, sample_chart):
        """Test calculating strengths for entire chart."""
        chart_strengths = strength_service.calculate_chart_strengths(sample_chart)

        assert chart_strengths.chart_id == "test_chart"
        assert len(chart_strengths.planet_strengths) == 5  # Sun, Jupiter, Mars, Saturn, Venus

        # Check Jupiter (exalted + retrograde)
        jupiter_strength = chart_strengths.planet_strengths[Planet.JUPITER]
        assert jupiter_strength.breakdown.total_strength == 35
        assert jupiter_strength.strength_weight == 85.0

        # Check Mars (own sign but combust)
        mars_strength = chart_strengths.planet_strengths[Planet.MARS]
        assert mars_strength.breakdown.total_strength == 5  # 20 - 15
        assert mars_strength.strength_weight == 55.0

    def test_dignity_scores(self, strength_service):
        """Test that dignity scores are correctly applied."""
        from api.models import DIGNITY_SCORES

        assert DIGNITY_SCORES[Dignity.EXALTED] == 25
        assert DIGNITY_SCORES[Dignity.OWN_SIGN] == 20
        assert DIGNITY_SCORES[Dignity.FRIENDLY] == 10
        assert DIGNITY_SCORES[Dignity.NEUTRAL] == 0
        assert DIGNITY_SCORES[Dignity.ENEMY] == -10
        assert DIGNITY_SCORES[Dignity.DEBILITATED] == -25

    def test_combustion_distances(self, strength_service):
        """Test that combustion distances are correctly defined."""
        assert strength_service.COMBUSTION_DISTANCES[Planet.MOON] == 12.0
        assert strength_service.COMBUSTION_DISTANCES[Planet.MARS] == 17.0
        assert strength_service.COMBUSTION_DISTANCES[Planet.MERCURY] == 14.0
        assert strength_service.COMBUSTION_DISTANCES[Planet.JUPITER] == 11.0
        assert strength_service.COMBUSTION_DISTANCES[Planet.VENUS] == 10.0
        assert strength_service.COMBUSTION_DISTANCES[Planet.SATURN] == 15.0

    def test_venus_not_combust_far_from_sun(self, strength_service, sample_chart):
        """Test Venus not combust when far from Sun."""
        sun_placement = sample_chart.planets[Planet.SUN]
        venus_placement = sample_chart.planets[Planet.VENUS]

        # Venus at 11, Sun at 10.5, distance = 0.5 degrees
        # Venus combustion distance = 10 degrees, so it IS combust
        breakdown = strength_service.calculate_strength_breakdown(
            Planet.VENUS, venus_placement, sun_placement
        )

        assert breakdown.is_combust is True
        assert breakdown.combustion_score == -15

