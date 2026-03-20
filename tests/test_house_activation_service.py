"""
Unit tests for HouseActivationService.
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
from api.services.house_activation_service import HouseActivationService


class TestHouseActivationService:
    """Test suite for HouseActivationService."""
    
    @pytest.fixture
    def house_activation_service(self):
        """Create a HouseActivationService instance."""
        return HouseActivationService()
    
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
            1: HouseInfo(house_number=1, sign=Sign.CANCER, degree=0.0, lord=Planet.MOON),
            2: HouseInfo(house_number=2, sign=Sign.LEO, degree=0.0, lord=Planet.SUN),
            3: HouseInfo(house_number=3, sign=Sign.VIRGO, degree=0.0, lord=Planet.MERCURY),
            4: HouseInfo(house_number=4, sign=Sign.LIBRA, degree=0.0, lord=Planet.VENUS),
            5: HouseInfo(house_number=5, sign=Sign.SCORPIO, degree=0.0, lord=Planet.MARS),
            6: HouseInfo(house_number=6, sign=Sign.SAGITTARIUS, degree=0.0, lord=Planet.JUPITER),
            7: HouseInfo(house_number=7, sign=Sign.CAPRICORN, degree=0.0, lord=Planet.SATURN),
            8: HouseInfo(house_number=8, sign=Sign.AQUARIUS, degree=0.0, lord=Planet.SATURN),
            9: HouseInfo(house_number=9, sign=Sign.PISCES, degree=0.0, lord=Planet.JUPITER),
            10: HouseInfo(house_number=10, sign=Sign.ARIES, degree=0.0, lord=Planet.MARS),
            11: HouseInfo(house_number=11, sign=Sign.TAURUS, degree=0.0, lord=Planet.VENUS),
            12: HouseInfo(house_number=12, sign=Sign.GEMINI, degree=0.0, lord=Planet.MERCURY),
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

    def test_service_initialization(self, house_activation_service):
        """Test that the service initializes correctly."""
        assert house_activation_service is not None
        assert house_activation_service.TRANSIT_PERCENTAGE == 0.30
        assert house_activation_service.OWNERSHIP_PERCENTAGE == 0.30
        assert house_activation_service.NATAL_PERCENTAGE == 0.20
        assert house_activation_service.ASPECT_PERCENTAGE == 0.20

        # Verify percentages sum to 1.0
        total = (
            house_activation_service.TRANSIT_PERCENTAGE +
            house_activation_service.OWNERSHIP_PERCENTAGE +
            house_activation_service.NATAL_PERCENTAGE +
            house_activation_service.ASPECT_PERCENTAGE
        )
        assert abs(total - 1.0) < 0.001

    def test_get_owned_houses(self, house_activation_service, sample_chart):
        """Test getting houses owned by a planet."""
        # Moon owns house 1
        moon_houses = house_activation_service.get_owned_houses(Planet.MOON, sample_chart)
        assert 1 in moon_houses
        assert len(moon_houses) == 1

        # Jupiter owns houses 6 and 9
        jupiter_houses = house_activation_service.get_owned_houses(Planet.JUPITER, sample_chart)
        assert 6 in jupiter_houses
        assert 9 in jupiter_houses
        assert len(jupiter_houses) == 2

        # Saturn owns houses 7 and 8
        saturn_houses = house_activation_service.get_owned_houses(Planet.SATURN, sample_chart)
        assert 7 in saturn_houses
        assert 8 in saturn_houses
        assert len(saturn_houses) == 2

    def test_get_aspected_houses(self, house_activation_service, sample_chart):
        """Test getting houses aspected by a planet."""
        # Jupiter in house 1 aspects houses 5, 7, 9
        jupiter_aspects = house_activation_service.get_aspected_houses(Planet.JUPITER, sample_chart)
        assert 5 in jupiter_aspects  # 5th aspect from house 1
        assert 7 in jupiter_aspects  # 7th aspect from house 1
        assert 9 in jupiter_aspects  # 9th aspect from house 1

        # Mars in house 5 aspects houses 8, 11, 12
        mars_aspects = house_activation_service.get_aspected_houses(Planet.MARS, sample_chart)
        assert 8 in mars_aspects  # 4th aspect from house 5
        assert 11 in mars_aspects  # 7th aspect from house 5
        assert 12 in mars_aspects  # 8th aspect from house 5

    def test_calculate_planet_house_contributions(self, house_activation_service, sample_chart):
        """Test calculating house contributions for a planet."""
        calculation_date = datetime(2026, 3, 20, 12, 0, 0)
        planet_score = 15.8  # Example score for Jupiter

        contributions = house_activation_service.calculate_planet_house_contributions(
            Planet.JUPITER,
            planet_score,
            sample_chart,
            calculation_date
        )

        # Verify basic structure
        assert contributions.planet == Planet.JUPITER
        assert contributions.planet_score == planet_score
        assert len(contributions.contributions) > 0

        # Verify contributions sum to planet score
        total_contrib = sum(c.total_contribution for c in contributions.contributions.values())
        assert abs(total_contrib - planet_score) < 0.001

    def test_aggregate_house_scores(self, house_activation_service):
        """Test aggregating house scores from planet contributions."""
        from api.models import PlanetHouseContributions, HouseContribution

        # Create mock planet contributions
        planet_contributions = {
            Planet.JUPITER: PlanetHouseContributions(
                planet=Planet.JUPITER,
                planet_score=15.8,
                contributions={
                    1: HouseContribution(
                        house=1,
                        transit_contribution=0.0,
                        natal_contribution=3.16,
                        ownership_contribution=0.0,
                        aspect_contribution=0.0,
                        total_contribution=3.16
                    ),
                    10: HouseContribution(
                        house=10,
                        transit_contribution=4.74,
                        natal_contribution=0.0,
                        ownership_contribution=0.0,
                        aspect_contribution=1.58,
                        total_contribution=6.32
                    )
                }
            )
        }

        house_activations = house_activation_service.aggregate_house_scores(planet_contributions)

        # Verify all houses are present
        assert len(house_activations) == 12

        # Verify scores sum to 100
        total_score = sum(h.score for h in house_activations.values())
        assert abs(total_score - 100.0) < 0.001

    def test_calculate_house_activation(self, house_activation_service, sample_chart):
        """Test calculating complete house activation."""
        calculation_date = datetime(2026, 3, 20, 12, 0, 0)

        house_activation = house_activation_service.calculate_house_activation(
            sample_chart,
            calculation_date
        )

        # Verify basic structure
        assert house_activation.chart_id == "test_chart"
        assert house_activation.calculation_date == calculation_date

        # Verify all houses have activations
        assert len(house_activation.house_activations) == 12

        # Verify all planets have contributions
        assert len(house_activation.planet_contributions) == len(sample_chart.planets)

        # Verify house scores sum to 100
        total_score = house_activation.total_score()
        assert abs(total_score - 100.0) < 0.001

        # Verify each house has valid score
        for house_num, activation in house_activation.house_activations.items():
            assert 1 <= house_num <= 12
            assert 0 <= activation.score <= 100
            assert activation.raw_score >= 0

    def test_distribution_percentages(self, house_activation_service):
        """Test that distribution percentages are correct."""
        assert house_activation_service.TRANSIT_PERCENTAGE == 0.30
        assert house_activation_service.OWNERSHIP_PERCENTAGE == 0.30
        assert house_activation_service.NATAL_PERCENTAGE == 0.20
        assert house_activation_service.ASPECT_PERCENTAGE == 0.20

        # Sum should be 1.0
        total = (
            house_activation_service.TRANSIT_PERCENTAGE +
            house_activation_service.OWNERSHIP_PERCENTAGE +
            house_activation_service.NATAL_PERCENTAGE +
            house_activation_service.ASPECT_PERCENTAGE
        )
        assert total == 1.0

