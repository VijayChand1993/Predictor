"""
Unit tests for natal chart service.
"""
import pytest
import json
from datetime import datetime
from pathlib import Path

from api.models import Location, BirthData, Planet, Sign, Dignity, Nakshatra
from api.services.natal_chart_service import NatalChartService


class TestNatalChartService:
    """Test natal chart service functionality."""

    @pytest.fixture
    def service(self, tmp_path):
        """Create a natal chart service with temporary output directory."""
        return NatalChartService(output_dir=str(tmp_path))

    @pytest.fixture
    def sample_birth_data(self):
        """Create sample birth data for testing."""
        location = Location(
            latitude=29.58633,
            longitude=80.23275,
            city="Karmala",
            country="India",
            timezone="Asia/Kolkata"
        )

        birth_data = BirthData(
            date=datetime(1993, 4, 2, 1, 15, 0),
            location=location,
            name="Vijay"
        )

        return birth_data

    @pytest.fixture
    def sample_chart_json(self):
        """Load sample chart JSON from output folder."""
        json_path = Path("output/birth_chart.json")
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        return None
    
    def test_service_initialization(self, tmp_path):
        """Test service initialization creates output directory."""
        service = NatalChartService(output_dir=str(tmp_path / "charts"))
        assert service.output_dir.exists()
        assert service.output_dir.is_dir()
    
    def test_timezone_offset_mapping(self, service):
        """Test timezone offset mapping."""
        assert service._get_timezone_offset("Asia/Kolkata") == 5.5
        assert service._get_timezone_offset("UTC") == 0.0
        assert service._get_timezone_offset("America/New_York") == -5.0
        assert service._get_timezone_offset("Unknown/Timezone") == 0.0
    
    def test_parse_chart_from_json(self, service, sample_birth_data, sample_chart_json):
        """Test parsing chart from existing JSON data."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")

        chart = service._parse_chart(sample_chart_json, sample_birth_data, "test_chart_id")

        # Verify chart structure
        assert chart.chart_id == "test_chart_id"
        assert chart.birth_data == sample_birth_data
        assert chart.ascendant_sign is not None
        assert isinstance(chart.ascendant_sign, Sign)

        # Verify planets are present
        assert len(chart.planets) == 9  # All 9 Vedic planets
        assert Planet.SUN in chart.planets
        assert Planet.MOON in chart.planets
        assert Planet.MARS in chart.planets
        assert Planet.MERCURY in chart.planets
        assert Planet.JUPITER in chart.planets
        assert Planet.VENUS in chart.planets
        assert Planet.SATURN in chart.planets
        assert Planet.RAHU in chart.planets
        assert Planet.KETU in chart.planets

        # Verify houses are present
        assert len(chart.houses) == 12
        for i in range(1, 13):
            assert i in chart.houses
            assert chart.houses[i].house_number == i
            assert chart.houses[i].sign is not None
            assert chart.houses[i].lord is not None

        # Verify Moon sign is set
        assert chart.moon_sign is not None
        assert chart.moon_sign == chart.planets[Planet.MOON].sign

    def test_planet_placements_from_json(self, service, sample_chart_json):
        """Test planet placement parsing from JSON."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")

        planets = service._parse_planets(sample_chart_json["d1Chart"]["houses"])

        # Check each planet has required fields
        for planet, placement in planets.items():
            assert placement.planet == planet
            assert placement.sign is not None
            assert 1 <= placement.house <= 12
            assert 0 <= placement.degree < 30
            assert isinstance(placement.is_retrograde, bool)

            # Check lordship houses (except Rahu/Ketu which don't rule houses)
            if planet not in [Planet.RAHU, Planet.KETU]:
                assert len(placement.rules_houses) > 0
    
    def test_dignity_mapping(self, service):
        """Test dignity string mapping."""
        assert service._map_dignity("exalted") == Dignity.EXALTED
        assert service._map_dignity("own_sign") == Dignity.OWN_SIGN
        assert service._map_dignity("moolatrikona") == Dignity.MOOLATRIKONA
        assert service._map_dignity("neutral") == Dignity.NEUTRAL
        assert service._map_dignity("debilitated") == Dignity.DEBILITATED
        assert service._map_dignity("unknown") is None
        assert service._map_dignity("") is None
    
    def test_nakshatra_mapping(self, service):
        """Test nakshatra string mapping."""
        from api.models import Nakshatra
        
        assert service._map_nakshatra("Ashwini") == Nakshatra.ASHWINI
        assert service._map_nakshatra("Pushya") == Nakshatra.PUSHYA
        assert service._map_nakshatra("Purva Ashadha") == Nakshatra.PURVA_ASHADHA
        assert service._map_nakshatra("Revati") == Nakshatra.REVATI
        assert service._map_nakshatra("Unknown") is None
    
    def test_specific_chart_values(self, service, sample_birth_data, sample_chart_json):
        """Test specific values for the sample birth chart."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")

        chart = service._parse_chart(sample_chart_json, sample_birth_data, "test_id")

        # Based on the sample JSON, we know:
        # - Ascendant should be Sagittarius
        assert chart.ascendant_sign == Sign.SAGITTARIUS

        # - Moon should be in Cancer (house 8)
        moon_placement = chart.planets[Planet.MOON]
        assert moon_placement.sign == Sign.CANCER
        assert moon_placement.house == 8

        # - Jupiter should be in Virgo (house 10)
        jupiter_placement = chart.planets[Planet.JUPITER]
        assert jupiter_placement.sign == Sign.VIRGO
        assert jupiter_placement.house == 10

        # - Saturn should be in Aquarius (own sign)
        saturn_placement = chart.planets[Planet.SATURN]
        assert saturn_placement.sign == Sign.AQUARIUS
        assert saturn_placement.dignity == Dignity.OWN_SIGN
        assert saturn_placement.house == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

