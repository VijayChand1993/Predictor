"""
Unit tests for AspectService.
"""
import pytest
from datetime import datetime

from api.models import (
    Planet,
    Sign,
    AspectType,
    BirthData,
    Location,
    NatalChart,
    PlanetPlacement,
    HouseInfo,
)
from api.services.aspect_service import AspectService


class TestAspectService:
    """Test suite for AspectService."""
    
    @pytest.fixture
    def aspect_service(self):
        """Create an AspectService instance."""
        return AspectService()
    
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
                nakshatra_pada=1
            ),
            Planet.JUPITER: PlanetPlacement(
                planet=Planet.JUPITER,
                sign=Sign.SAGITTARIUS,
                degree=15.0,
                house=1,
                nakshatra="Mula",
                nakshatra_pada=2
            ),
            Planet.MARS: PlanetPlacement(
                planet=Planet.MARS,
                sign=Sign.CAPRICORN,
                degree=20.0,
                house=2,
                nakshatra="Shravana",
                nakshatra_pada=3
            ),
            Planet.SATURN: PlanetPlacement(
                planet=Planet.SATURN,
                sign=Sign.CAPRICORN,
                degree=25.0,
                house=10,
                nakshatra="Dhanishta",
                nakshatra_pada=4
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
    
    def test_service_initialization(self, aspect_service):
        """Test that the service initializes correctly."""
        assert aspect_service is not None
        assert aspect_service.config is not None
    
    def test_get_aspected_houses_all_planets(self, aspect_service):
        """Test that all planets aspect the 7th house."""
        # Sun in house 1 should aspect house 7
        aspects = aspect_service.get_aspected_houses(Planet.SUN, 1)
        house_numbers = [h for h, _ in aspects]
        assert 7 in house_numbers
        
        # Moon in house 5 should aspect house 11
        aspects = aspect_service.get_aspected_houses(Planet.MOON, 5)
        house_numbers = [h for h, _ in aspects]
        assert 11 in house_numbers
    
    def test_mars_special_aspects(self, aspect_service):
        """Test Mars special aspects (4th and 8th)."""
        # Mars in house 1 should aspect houses 4, 7, 8
        aspects = aspect_service.get_aspected_houses(Planet.MARS, 1)
        house_numbers = [h for h, _ in aspects]
        
        assert 4 in house_numbers  # 4th aspect
        assert 7 in house_numbers  # 7th aspect (full)
        assert 8 in house_numbers  # 8th aspect
        assert len(aspects) == 3
    
    def test_jupiter_special_aspects(self, aspect_service):
        """Test Jupiter special aspects (5th and 9th)."""
        # Jupiter in house 1 should aspect houses 5, 7, 9
        aspects = aspect_service.get_aspected_houses(Planet.JUPITER, 1)
        house_numbers = [h for h, _ in aspects]
        
        assert 5 in house_numbers  # 5th aspect
        assert 7 in house_numbers  # 7th aspect (full)
        assert 9 in house_numbers  # 9th aspect
        assert len(aspects) == 3
    
    def test_saturn_special_aspects(self, aspect_service):
        """Test Saturn special aspects (3rd and 10th)."""
        # Saturn in house 1 should aspect houses 3, 7, 10
        aspects = aspect_service.get_aspected_houses(Planet.SATURN, 1)
        house_numbers = [h for h, _ in aspects]

        assert 3 in house_numbers  # 3rd aspect
        assert 7 in house_numbers  # 7th aspect (full)
        assert 10 in house_numbers  # 10th aspect
        assert len(aspects) == 3

    def test_aspect_types(self, aspect_service):
        """Test that aspect types are correctly assigned."""
        # Jupiter in house 1
        aspects = aspect_service.get_aspected_houses(Planet.JUPITER, 1)
        aspect_dict = {h: t for h, t in aspects}

        assert aspect_dict[7] == AspectType.FULL
        assert aspect_dict[5] == AspectType.SPECIAL_JUPITER
        assert aspect_dict[9] == AspectType.SPECIAL_JUPITER

    def test_house_wrapping(self, aspect_service):
        """Test that house numbers wrap correctly (1-12)."""
        # Jupiter in house 10 should aspect houses 2, 4, 6
        aspects = aspect_service.get_aspected_houses(Planet.JUPITER, 10)
        house_numbers = [h for h, _ in aspects]

        assert 2 in house_numbers  # 5th from 10 = 2
        assert 4 in house_numbers  # 7th from 10 = 4
        assert 6 in house_numbers  # 9th from 10 = 6

    def test_calculate_aspect_weight(self, aspect_service):
        """Test aspect weight calculation."""
        # Jupiter in house 1 (Kendra)
        weight = aspect_service.calculate_aspect_weight(Planet.JUPITER, 1)

        # Jupiter aspects houses 5 (Trikona), 7 (Kendra), 9 (Trikona)
        # Weight = (0.8 × 0.9 + 1.0 × 1.0 + 0.8 × 0.9) × 20
        # Weight = (0.72 + 1.0 + 0.72) × 20 = 2.44 × 20 = 48.8
        assert weight > 0
        assert weight <= 100

    def test_calculate_planet_aspects(self, aspect_service):
        """Test calculating aspects for a single planet."""
        planet_aspects = aspect_service.calculate_planet_aspects(Planet.JUPITER, 1)

        assert planet_aspects.planet == Planet.JUPITER
        assert planet_aspects.from_house == 1
        assert len(planet_aspects.aspects) == 3
        assert planet_aspects.aspect_weight > 0

    def test_calculate_chart_aspects(self, aspect_service, sample_chart):
        """Test calculating aspects for entire chart."""
        chart_aspects = aspect_service.calculate_chart_aspects(sample_chart)

        assert chart_aspects.chart_id == "test_chart"
        assert len(chart_aspects.planet_aspects) == 4  # Sun, Jupiter, Mars, Saturn

        # Check that each planet has aspects
        for planet in [Planet.SUN, Planet.JUPITER, Planet.MARS, Planet.SATURN]:
            assert planet in chart_aspects.planet_aspects
            planet_aspect = chart_aspects.planet_aspects[planet]
            assert len(planet_aspect.aspects) > 0
            assert planet_aspect.aspect_weight > 0

    def test_aspect_weight_range(self, aspect_service):
        """Test that aspect weights are in valid range."""
        # Test various planets and houses
        test_cases = [
            (Planet.SUN, 1),
            (Planet.JUPITER, 5),
            (Planet.MARS, 10),
            (Planet.SATURN, 7),
        ]

        for planet, house in test_cases:
            weight = aspect_service.calculate_aspect_weight(planet, house)
            assert 0 <= weight <= 100, f"{planet} in house {house} has invalid weight: {weight}"

    def test_all_planets_have_at_least_one_aspect(self, aspect_service):
        """Test that all planets have at least the 7th house aspect."""
        for planet in Planet:
            aspects = aspect_service.get_aspected_houses(planet, 1)
            assert len(aspects) >= 1, f"{planet} should have at least one aspect"

    def test_special_aspect_planets_have_more_aspects(self, aspect_service):
        """Test that Mars, Jupiter, Saturn have more than just 7th aspect."""
        special_planets = [Planet.MARS, Planet.JUPITER, Planet.SATURN]

        for planet in special_planets:
            aspects = aspect_service.get_aspected_houses(planet, 1)
            assert len(aspects) == 3, f"{planet} should have 3 aspects (7th + 2 special)"

    def test_regular_planets_have_only_seventh_aspect(self, aspect_service):
        """Test that regular planets only have 7th house aspect."""
        regular_planets = [Planet.SUN, Planet.MOON, Planet.MERCURY, Planet.VENUS, Planet.RAHU, Planet.KETU]

        for planet in regular_planets:
            aspects = aspect_service.get_aspected_houses(planet, 1)
            assert len(aspects) == 1, f"{planet} should have only 1 aspect (7th house)"
            assert aspects[0][1] == AspectType.FULL

