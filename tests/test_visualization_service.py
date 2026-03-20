"""
Unit tests for VisualizationService.
"""
import pytest
from datetime import datetime, timedelta

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
from api.services.timeline_service import TimelineService
from api.services.visualization_service import VisualizationService


class TestVisualizationService:
    """Test suite for VisualizationService."""
    
    @pytest.fixture
    def visualization_service(self):
        """Create a VisualizationService instance."""
        return VisualizationService()
    
    @pytest.fixture
    def timeline_service(self):
        """Create a TimelineService instance."""
        return TimelineService()
    
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

    def test_create_planet_chart(self, visualization_service, timeline_service, sample_chart):
        """Test creating planet chart visualization."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 3, 0, 0, 0)

        # Generate timeline
        timeline = timeline_service.calculate_planet_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Create chart visualization
        chart_viz = visualization_service.create_planet_chart(timeline)

        # Verify structure
        assert chart_viz.chart_id == "test_chart"
        assert chart_viz.title == "Planet Influence Timeline"
        assert chart_viz.start_date == start
        assert chart_viz.end_date == end

        # Verify datasets (one per planet)
        assert len(chart_viz.datasets) == len(Planet)

        # Verify each dataset
        for dataset in chart_viz.datasets:
            assert dataset.label in [p.value for p in Planet]
            assert len(dataset.data) == 3  # 3 days

            # Verify data points
            for dp in dataset.data:
                assert dp.x >= start
                assert dp.x <= end
                assert 0 <= dp.y <= 100

    def test_create_house_chart(self, visualization_service, timeline_service, sample_chart):
        """Test creating house chart visualization."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 3, 0, 0, 0)

        # Generate timeline
        timeline = timeline_service.calculate_house_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Create chart visualization
        chart_viz = visualization_service.create_house_chart(timeline)

        # Verify structure
        assert chart_viz.chart_id == "test_chart"
        assert chart_viz.title == "House Activation Timeline"
        assert chart_viz.start_date == start
        assert chart_viz.end_date == end

        # Verify datasets (one per house)
        assert len(chart_viz.datasets) == 12

        # Verify each dataset
        for dataset in chart_viz.datasets:
            assert dataset.label.startswith("House ")
            assert len(dataset.data) == 3  # 3 days

            # Verify data points
            for dp in dataset.data:
                assert dp.x >= start
                assert dp.x <= end
                assert 0 <= dp.y <= 100

    def test_create_house_heatmap(self, visualization_service, timeline_service, sample_chart):
        """Test creating house heatmap visualization."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 5, 0, 0, 0)

        # Generate timeline
        timeline = timeline_service.calculate_house_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Create heatmap
        heatmap = visualization_service.create_house_heatmap(timeline)

        # Verify structure
        assert heatmap.chart_id == "test_chart"
        assert heatmap.title == "House Activation Heatmap"
        assert heatmap.start_date == start
        assert heatmap.end_date == end

        # Verify labels
        assert len(heatmap.row_labels) == 12  # 12 houses
        assert len(heatmap.col_labels) == 5  # 5 days

        # Verify cells (12 houses × 5 days = 60 cells)
        assert len(heatmap.cells) == 60

        # Verify min/max values
        assert heatmap.min_value >= 0
        assert heatmap.max_value <= 100
        assert heatmap.min_value <= heatmap.max_value

        # Verify each cell
        for cell in heatmap.cells:
            assert 1 <= cell.row <= 12
            assert 0 <= cell.col < 5
            assert heatmap.min_value <= cell.value <= heatmap.max_value
            assert cell.label.startswith("House ")

