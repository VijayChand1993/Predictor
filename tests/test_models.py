"""
Unit tests for data models.
"""
import pytest
from datetime import datetime
from api.models import (
    Planet, Sign, Nakshatra, Dignity,
    Location, BirthData,
    PlanetPlacement, TransitPlacement,
    HouseInfo, NatalChart,
    DashaPeriod, ActiveDashas,
    TransitData, TimeSegment,
    ComponentBreakdown, WeightedComponents,
    PlanetScore, HouseScore,
    TimeRange, ScoringResult,
)


class TestEnums:
    """Test enum definitions."""
    
    def test_planet_enum(self):
        """Test Planet enum."""
        assert Planet.SUN.value == "Sun"
        assert Planet.JUPITER.value == "Jupiter"
        assert len(Planet) == 9
    
    def test_sign_enum(self):
        """Test Sign enum."""
        assert Sign.ARIES.value == "Aries"
        assert Sign.PISCES.value == "Pisces"
        assert len(Sign) == 12
    
    def test_dignity_enum(self):
        """Test Dignity enum."""
        assert Dignity.EXALTED.value == "Exalted"
        assert Dignity.DEBILITATED.value == "Debilitated"


class TestBirthData:
    """Test birth data models."""
    
    def test_location_creation(self):
        """Test Location model creation."""
        location = Location(
            latitude=28.6139,
            longitude=77.2090,
            city="New Delhi",
            country="India",
            timezone="Asia/Kolkata"
        )
        assert location.latitude == 28.6139
        assert location.city == "New Delhi"
    
    def test_birth_data_creation(self):
        """Test BirthData model creation."""
        location = Location(
            latitude=28.6139,
            longitude=77.2090,
            timezone="Asia/Kolkata"
        )
        birth_data = BirthData(
            date=datetime(1990, 1, 15, 10, 30),
            location=location,
            name="Test Person"
        )
        assert birth_data.name == "Test Person"
        assert birth_data.location.latitude == 28.6139


class TestPlanetPlacement:
    """Test planet placement models."""
    
    def test_planet_placement_creation(self):
        """Test PlanetPlacement model creation."""
        placement = PlanetPlacement(
            planet=Planet.JUPITER,
            sign=Sign.SAGITTARIUS,
            house=1,
            degree=15.5,
            nakshatra=Nakshatra.MULA,
            nakshatra_pada=2,
            dignity=Dignity.OWN_SIGN,
            is_retrograde=False,
            is_combust=False,
            rules_houses=[1, 4]
        )
        assert placement.planet == Planet.JUPITER
        assert placement.dignity == Dignity.OWN_SIGN
        assert len(placement.rules_houses) == 2


class TestScoring:
    """Test scoring models."""
    
    def test_component_breakdown(self):
        """Test ComponentBreakdown model."""
        breakdown = ComponentBreakdown(
            dasha=40,
            transit=80,
            strength=45,
            motion=50
        )
        assert breakdown.dasha == 40
        assert breakdown.transit == 80
    
    def test_weighted_components(self):
        """Test WeightedComponents model."""
        weighted = WeightedComponents(
            dasha=16.0,
            transit=24.0,
            strength=9.9,
            motion=4.0
        )
        total = weighted.total()
        assert abs(total - 53.9) < 0.01
    
    def test_planet_score(self):
        """Test PlanetScore model."""
        breakdown = ComponentBreakdown(
            dasha=40, transit=80, strength=45, motion=50
        )
        weighted = WeightedComponents(
            dasha=16.0, transit=24.0, strength=9.9, motion=4.0
        )
        score = PlanetScore(
            planet=Planet.SATURN,
            score=34.5,
            breakdown=breakdown,
            weighted_components=weighted
        )
        assert score.planet == Planet.SATURN
        assert score.score == 34.5


class TestConfiguration:
    """Test configuration."""
    
    def test_config_import(self):
        """Test that config can be imported."""
        from api.core import config
        assert config is not None
        assert config.component_weights.dasha == 0.35
    
    def test_component_weights_sum(self):
        """Test that component weights sum to 1.0."""
        from api.core import config
        assert config.component_weights.validate_sum()
    
    def test_house_distribution_sum(self):
        """Test that house distribution sums to 1.0."""
        from api.core import config
        assert config.house_distribution.validate_sum()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

