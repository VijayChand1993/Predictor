"""
Unit tests for TimelineService.
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


class TestTimelineService:
    """Test suite for TimelineService."""
    
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

    def test_service_initialization(self, timeline_service):
        """Test that the service initializes correctly."""
        assert timeline_service is not None
        assert timeline_service.scoring_engine is not None
        assert timeline_service.house_activation_service is not None

    def test_generate_time_points(self, timeline_service):
        """Test time point generation."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 5, 0, 0, 0)

        # Test with 1-day interval
        points = timeline_service.generate_time_points(start, end, interval_days=1)
        assert len(points) == 5  # 1st, 2nd, 3rd, 4th, 5th
        assert points[0] == start
        assert points[-1] == end

        # Test with 2-day interval
        points = timeline_service.generate_time_points(start, end, interval_days=2)
        assert len(points) == 3  # 1st, 3rd, 5th
        assert points[0] == start
        assert points[-1] == end

    def test_calculate_planet_timeline(self, timeline_service, sample_chart):
        """Test calculating planet influence timeline."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 3, 0, 0, 0)

        timeline = timeline_service.calculate_planet_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Verify basic structure
        assert timeline.chart_id == "test_chart"
        assert timeline.start_date == start
        assert timeline.end_date == end

        # Verify all planets have timelines
        assert len(timeline.timelines) == len(Planet)

        # Verify each planet timeline
        for planet, planet_timeline in timeline.timelines.items():
            assert planet_timeline.planet == planet
            assert len(planet_timeline.data_points) == 3  # 3 days
            assert planet_timeline.average_score >= 0
            assert planet_timeline.average_score <= 100
            assert planet_timeline.peak_score >= 0
            assert planet_timeline.peak_score <= 100
            assert planet_timeline.peak_time >= start
            assert planet_timeline.peak_time <= end

            # Verify data points
            for dp in planet_timeline.data_points:
                assert dp.planet == planet
                assert dp.timestamp >= start
                assert dp.timestamp <= end
                assert 0 <= dp.score <= 100

    def test_calculate_house_timeline(self, timeline_service, sample_chart):
        """Test calculating house activation timeline."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 3, 0, 0, 0)

        timeline = timeline_service.calculate_house_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Verify basic structure
        assert timeline.chart_id == "test_chart"
        assert timeline.start_date == start
        assert timeline.end_date == end

        # Verify all houses have timelines
        assert len(timeline.timelines) == 12

        # Verify each house timeline
        for house_num, house_timeline in timeline.timelines.items():
            assert house_timeline.house == house_num
            assert 1 <= house_num <= 12
            assert len(house_timeline.data_points) == 3  # 3 days
            assert house_timeline.average_score >= 0
            assert house_timeline.average_score <= 100
            assert house_timeline.peak_score >= 0
            assert house_timeline.peak_score <= 100
            assert house_timeline.peak_time >= start
            assert house_timeline.peak_time <= end

            # Verify data points
            for dp in house_timeline.data_points:
                assert dp.house == house_num
                assert dp.timestamp >= start
                assert dp.timestamp <= end
                assert 0 <= dp.score <= 100

    def test_planet_timeline_statistics(self, timeline_service, sample_chart):
        """Test that timeline statistics are calculated correctly."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 5, 0, 0, 0)

        timeline = timeline_service.calculate_planet_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Check that average is actually the average
        for planet, planet_timeline in timeline.timelines.items():
            scores = [dp.score for dp in planet_timeline.data_points]
            calculated_avg = sum(scores) / len(scores)
            assert abs(planet_timeline.average_score - calculated_avg) < 0.001

            # Check that peak is actually the max
            calculated_peak = max(scores)
            assert planet_timeline.peak_score == calculated_peak

    def test_house_timeline_statistics(self, timeline_service, sample_chart):
        """Test that house timeline statistics are calculated correctly."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 5, 0, 0, 0)

        timeline = timeline_service.calculate_house_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Check that average is actually the average
        for house_num, house_timeline in timeline.timelines.items():
            scores = [dp.score for dp in house_timeline.data_points]
            calculated_avg = sum(scores) / len(scores)
            assert abs(house_timeline.average_score - calculated_avg) < 0.001

            # Check that peak is actually the max
            calculated_peak = max(scores)
            assert house_timeline.peak_score == calculated_peak

    def test_get_most_influential_planet(self, timeline_service, sample_chart):
        """Test getting the most influential planet."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 3, 0, 0, 0)

        timeline = timeline_service.calculate_planet_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        planet, score = timeline.get_most_influential_planet()
        assert planet in Planet
        assert 0 <= score <= 100

        # Verify it's actually the highest
        for p, pt in timeline.timelines.items():
            assert pt.average_score <= score

    def test_get_most_activated_house(self, timeline_service, sample_chart):
        """Test getting the most activated house."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 3, 0, 0, 0)

        timeline = timeline_service.calculate_house_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        house, score = timeline.get_most_activated_house()
        assert 1 <= house <= 12
        assert 0 <= score <= 100

        # Verify it's actually the highest
        for h, ht in timeline.timelines.items():
            assert ht.average_score <= score


