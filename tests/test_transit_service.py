"""
Tests for transit calculation service.
"""
import pytest
from datetime import datetime, timedelta
from api.services.transit_service import TransitService
from api.services.natal_chart_service import NatalChartService
from api.models import Location, BirthData, Planet, Sign


@pytest.fixture
def natal_chart_service():
    """Create natal chart service."""
    return NatalChartService(output_dir="output")


@pytest.fixture
def transit_service():
    """Create transit service."""
    return TransitService(output_dir="output")


@pytest.fixture
def sample_birth_data():
    """Sample birth data for testing."""
    location = Location(
        latitude=28.6139,
        longitude=77.2090,
        city="Delhi",
        country="India",
        timezone="Asia/Kolkata"
    )
    
    return BirthData(
        date=datetime(1993, 4, 2, 1, 15, 0),
        location=location,
        name="Test Person"
    )


@pytest.fixture
def sample_natal_chart(natal_chart_service, sample_birth_data):
    """Generate a sample natal chart."""
    return natal_chart_service.generate_chart(sample_birth_data, save_json=False)


class TestTransitService:
    """Test suite for TransitService."""
    
    def test_service_initialization(self, transit_service):
        """Test that service initializes correctly."""
        assert transit_service is not None
        assert transit_service.config is not None
        assert transit_service.output_dir.exists()
    
    def test_get_transit_data(self, transit_service, sample_natal_chart):
        """Test getting transit data for a specific date."""
        target_date = datetime(2026, 3, 19, 18, 21, 59)
        
        transit_data = transit_service.get_transit_data(
            target_date=target_date,
            natal_chart=sample_natal_chart,
            save_json=False
        )
        
        # Verify transit data structure
        assert transit_data is not None
        assert transit_data.date == target_date
        assert len(transit_data.planets) == 9
        
        # Verify all planets are present
        for planet in Planet:
            assert planet in transit_data.planets
            placement = transit_data.planets[planet]
            assert placement.planet == planet
            assert placement.sign is not None
            assert 1 <= placement.house <= 12
            assert 0 <= placement.degree < 30
            assert isinstance(placement.is_retrograde, bool)
            assert placement.speed >= 0
            assert placement.motion_type is not None
    
    def test_sign_num_to_sign_conversion(self, transit_service):
        """Test sign number to Sign enum conversion."""
        assert transit_service._sign_num_to_sign(1) == Sign.ARIES
        assert transit_service._sign_num_to_sign(6) == Sign.VIRGO
        assert transit_service._sign_num_to_sign(12) == Sign.PISCES
    
    def test_sign_to_num_conversion(self, transit_service):
        """Test Sign enum to number conversion."""
        assert transit_service._sign_to_num(Sign.ARIES) == 1
        assert transit_service._sign_to_num(Sign.VIRGO) == 6
        assert transit_service._sign_to_num(Sign.PISCES) == 12
    
    def test_house_calculation(self, transit_service, sample_natal_chart):
        """Test house calculation from transit position."""
        # Test with known values
        # If ascendant is in sign X at degree Y,
        # a planet in the same sign should be in house 1
        asc_sign_num = transit_service._sign_to_num(sample_natal_chart.ascendant_sign)
        asc_degree = sample_natal_chart.ascendant_degree
        
        # Planet at same position as ascendant should be in house 1
        house = transit_service._calculate_house(
            transit_sign_num=asc_sign_num,
            transit_degree=asc_degree,
            natal_chart=sample_natal_chart
        )
        assert house == 1
        
        # Planet 30 degrees ahead should be in house 2
        next_sign = (asc_sign_num % 12) + 1
        house = transit_service._calculate_house(
            transit_sign_num=next_sign,
            transit_degree=asc_degree,
            natal_chart=sample_natal_chart
        )
        assert house == 2
    
    def test_calculate_transit_weight(self, transit_service):
        """Test transit weight calculation."""
        # Jupiter in Kendra house (1,4,7,10) should have high weight
        weight = transit_service.calculate_transit_weight(
            planet=Planet.JUPITER,
            transit_house=1
        )
        assert weight > 0
        assert weight <= 100
        
        # Mercury in Dusthana house (6,8,12) should have lower weight
        weight_dusthana = transit_service.calculate_transit_weight(
            planet=Planet.MERCURY,
            transit_house=6
        )
        assert weight_dusthana > 0
        assert weight_dusthana < weight  # Should be less than Jupiter in Kendra
    
    def test_average_speed(self, transit_service):
        """Test average speed retrieval."""
        # Moon should be fastest
        moon_speed = transit_service._get_average_speed(Planet.MOON)
        assert moon_speed > 10
        
        # Saturn should be slowest
        saturn_speed = transit_service._get_average_speed(Planet.SATURN)
        assert saturn_speed < 0.1
        
        # Sun should be moderate
        sun_speed = transit_service._get_average_speed(Planet.SUN)
        assert 0.5 < sun_speed < 2.0
    
    def test_motion_type_determination(self, transit_service):
        """Test motion type classification."""
        from api.models import MotionType
        
        # Retrograde planet
        motion = transit_service._determine_motion_type(
            planet=Planet.MERCURY,
            speed=1.0,
            is_retrograde=True
        )
        assert motion == MotionType.RETROGRADE
        
        # Fast Moon
        motion = transit_service._determine_motion_type(
            planet=Planet.MOON,
            speed=15.0,
            is_retrograde=False
        )
        assert motion == MotionType.FAST

    def test_get_time_segments(self, transit_service, sample_natal_chart):
        """Test time segmentation based on transit changes."""
        # Test a short date range (3 days)
        start_date = datetime(2026, 3, 19, 0, 0, 0)
        end_date = datetime(2026, 3, 22, 0, 0, 0)

        segments = transit_service.get_time_segments(
            start_date=start_date,
            end_date=end_date,
            natal_chart=sample_natal_chart,
            fast_planets=[Planet.MOON]  # Only track Moon for faster testing
        )

        # Verify segments
        assert len(segments) > 0

        # First segment should start at start_date
        assert segments[0].start_date == start_date

        # Last segment should end at end_date
        assert segments[-1].end_date == end_date

        # Segments should be continuous
        for i in range(len(segments) - 1):
            # Next segment should start where previous ended
            assert segments[i].end_date <= segments[i + 1].start_date

        # Each segment should have transit data
        for segment in segments:
            assert segment.transit_data is not None
            assert len(segment.transit_data.planets) == 9
            assert segment.duration_days >= 0

    def test_save_transit_json(self, transit_service, sample_natal_chart, tmp_path):
        """Test saving transit data to JSON."""
        # Use temporary directory
        transit_service.output_dir = tmp_path

        target_date = datetime(2026, 3, 19, 18, 21, 59)

        transit_data = transit_service.get_transit_data(
            target_date=target_date,
            natal_chart=sample_natal_chart,
            save_json=True
        )

        # Check that JSON file was created
        json_files = list(tmp_path.glob("transit_*.json"))
        assert len(json_files) == 1

        # Verify JSON content
        import json
        with open(json_files[0]) as f:
            data = json.load(f)

        assert data["date"] == target_date.strftime("%Y-%m-%d")
        assert data["time"] == target_date.strftime("%H:%M:%S")
        assert len(data["planets"]) == 9

        # Verify planet data structure
        for planet_data in data["planets"]:
            assert "name" in planet_data
            assert "vedic_name" in planet_data
            assert "sign_num" in planet_data
            assert "degree" in planet_data
            assert "retrograde" in planet_data
            assert 1 <= planet_data["sign_num"] <= 12
            assert 0 <= planet_data["degree"] < 30

    def test_transit_weight_formula(self, transit_service):
        """Test that transit weight follows the correct formula."""
        # W_transit(p) = 100 × PlanetWeight(p) × HouseWeight(h_transit)

        planet = Planet.JUPITER
        house = 1  # Kendra house

        # Get individual weights
        planet_weight = transit_service.config.planet_importance.get_weight(planet)
        house_weight = transit_service.config.house_importance.get_house_weight(house)

        # Calculate expected weight
        expected_weight = 100 * planet_weight * house_weight

        # Get actual weight
        actual_weight = transit_service.calculate_transit_weight(planet, house)

        # Should match
        assert abs(actual_weight - expected_weight) < 0.01

    def test_all_planets_have_speeds(self, transit_service):
        """Test that all planets have defined average speeds."""
        for planet in Planet:
            speed = transit_service._get_average_speed(planet)
            assert speed > 0
            assert speed < 20  # Moon is fastest at ~13.2

    def test_retrograde_planets(self, transit_service, sample_natal_chart):
        """Test handling of retrograde planets."""
        target_date = datetime(2026, 3, 19, 18, 21, 59)

        transit_data = transit_service.get_transit_data(
            target_date=target_date,
            natal_chart=sample_natal_chart,
            save_json=False
        )

        # Check that retrograde status is captured
        for planet, placement in transit_data.planets.items():
            if placement.is_retrograde:
                # Retrograde planets should have RETROGRADE motion type
                from api.models import MotionType
                assert placement.motion_type == MotionType.RETROGRADE

