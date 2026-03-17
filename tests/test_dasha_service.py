"""
Unit tests for dasha service.
"""
import pytest
import json
from datetime import date
from pathlib import Path

from api.models import Planet, ActiveDashas, DashaPeriod
from api.services.dasha_service import DashaService


class TestDashaService:
    """Test dasha service functionality."""
    
    @pytest.fixture
    def service(self):
        """Create a dasha service instance."""
        return DashaService()
    
    @pytest.fixture
    def sample_chart_json(self):
        """Load sample chart JSON from output folder."""
        json_path = Path("output/birth_chart.json")
        if json_path.exists():
            with open(json_path, 'r') as f:
                return json.load(f)
        return None
    
    def test_service_initialization(self, service):
        """Test service initializes correctly."""
        assert service is not None
        assert service.config is not None
    
    def test_parse_date(self, service):
        """Test date parsing from different formats."""
        # Test YYYY-MM-DD format
        d1 = service._parse_date("2026-03-17")
        assert d1 == date(2026, 3, 17)
        
        # Test DD-MM-YYYY format
        d2 = service._parse_date("17-03-2026")
        assert d2 == date(2026, 3, 17)
        
        # Test YYYY/MM/DD format
        d3 = service._parse_date("2026/03/17")
        assert d3 == date(2026, 3, 17)
    
    def test_get_active_dashas(self, service, sample_chart_json):
        """Test getting active dashas for a specific date."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")
        
        # Test with a date in the past (should be in Saturn mahadasha based on birth chart)
        target_date = date(1993, 4, 2)  # Birth date
        active_dashas = service.get_active_dashas(sample_chart_json, target_date)
        
        assert active_dashas is not None
        assert isinstance(active_dashas, ActiveDashas)
        assert active_dashas.date == target_date
        assert active_dashas.mahadasha is not None
        assert active_dashas.antardasha is not None
    
    def test_get_active_dashas_current(self, service, sample_chart_json):
        """Test getting active dashas for current date."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")
        
        # Test with today's date
        target_date = date.today()
        active_dashas = service.get_active_dashas(sample_chart_json, target_date)
        
        assert active_dashas is not None
        assert active_dashas.mahadasha.planet in Planet
        assert active_dashas.antardasha.planet in Planet
    
    def test_calculate_dasha_weight_match(self, service, sample_chart_json):
        """Test dasha weight calculation when planet matches."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")

        # Get active dashas
        target_date = date(1993, 4, 2)
        active_dashas = service.get_active_dashas(sample_chart_json, target_date)

        # Calculate weight for mahadasha lord (should get 40 points)
        md_planet = active_dashas.mahadasha.planet
        weight = service.calculate_dasha_weight(md_planet, active_dashas)

        assert weight.planet == md_planet
        assert weight.mahadasha_score == 40.0  # Mahadasha weight
        assert weight.total_weight == 40.0  # Only mahadasha matches
    
    def test_calculate_dasha_weight_no_match(self, service, sample_chart_json):
        """Test dasha weight calculation when planet doesn't match."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")
        
        # Get active dashas
        target_date = date(1993, 4, 2)
        active_dashas = service.get_active_dashas(sample_chart_json, target_date)
        
        # Find a planet that's not in any dasha
        test_planet = Planet.SUN
        if test_planet == active_dashas.mahadasha.planet:
            test_planet = Planet.MOON
        if test_planet == active_dashas.antardasha.planet:
            test_planet = Planet.MARS
        if active_dashas.pratyantar and test_planet == active_dashas.pratyantar.planet:
            test_planet = Planet.JUPITER
        
        weight = service.calculate_dasha_weight(test_planet, active_dashas)
        
        assert weight.planet == test_planet
        assert weight.mahadasha_score == 0.0
        assert weight.antardasha_score == 0.0
        assert weight.total_weight == 0.0
    
    def test_get_all_mahadashas(self, service, sample_chart_json):
        """Test getting all mahadasha periods."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")
        
        mahadashas = service.get_all_mahadashas(sample_chart_json)
        
        # Should have 9 mahadashas (one for each planet)
        assert len(mahadashas) == 9
        
        # Check that all planets are present
        for planet in Planet:
            assert planet in mahadashas
            assert isinstance(mahadashas[planet], DashaPeriod)
            assert mahadashas[planet].planet == planet
            assert mahadashas[planet].level == "mahadasha"
    
    def test_dasha_period_structure(self, service, sample_chart_json):
        """Test that dasha periods have correct structure."""
        if sample_chart_json is None:
            pytest.skip("Sample chart JSON not found")
        
        target_date = date(1993, 4, 2)
        active_dashas = service.get_active_dashas(sample_chart_json, target_date)
        
        # Check mahadasha
        assert active_dashas.mahadasha.level == "mahadasha"
        assert active_dashas.mahadasha.start_date < active_dashas.mahadasha.end_date
        
        # Check antardasha
        assert active_dashas.antardasha.level == "antardasha"
        assert active_dashas.antardasha.start_date < active_dashas.antardasha.end_date
        
        # Antardasha should be within mahadasha period
        assert active_dashas.antardasha.start_date >= active_dashas.mahadasha.start_date
        assert active_dashas.antardasha.end_date <= active_dashas.mahadasha.end_date

