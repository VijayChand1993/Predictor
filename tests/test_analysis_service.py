"""
Unit tests for AnalysisService.
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
from api.services.timeline_service import TimelineService
from api.services.analysis_service import AnalysisService


class TestAnalysisService:
    """Test suite for AnalysisService."""
    
    @pytest.fixture
    def analysis_service(self):
        """Create an AnalysisService instance."""
        return AnalysisService(peak_threshold=15.0, significance_threshold=70.0)
    
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
        
        planets = {
            Planet.SUN: PlanetPlacement(
                planet=Planet.SUN, sign=Sign.ARIES, degree=10.5, house=5,
                nakshatra="Ashwini", nakshatra_pada=1, dignity=Dignity.EXALTED, is_retrograde=False
            ),
            Planet.MOON: PlanetPlacement(
                planet=Planet.MOON, sign=Sign.CANCER, degree=15.0, house=1,
                nakshatra="Pushya", nakshatra_pada=2, dignity=Dignity.OWN_SIGN, is_retrograde=False
            ),
            Planet.MARS: PlanetPlacement(
                planet=Planet.MARS, sign=Sign.ARIES, degree=12.0, house=5,
                nakshatra="Ashwini", nakshatra_pada=3, dignity=Dignity.OWN_SIGN, is_retrograde=False
            ),
            Planet.MERCURY: PlanetPlacement(
                planet=Planet.MERCURY, sign=Sign.PISCES, degree=20.0, house=4,
                nakshatra="Revati", nakshatra_pada=1, dignity=Dignity.DEBILITATED, is_retrograde=False
            ),
            Planet.JUPITER: PlanetPlacement(
                planet=Planet.JUPITER, sign=Sign.CANCER, degree=18.0, house=1,
                nakshatra="Ashlesha", nakshatra_pada=2, dignity=Dignity.EXALTED, is_retrograde=True
            ),
            Planet.VENUS: PlanetPlacement(
                planet=Planet.VENUS, sign=Sign.PISCES, degree=25.0, house=4,
                nakshatra="Revati", nakshatra_pada=4, dignity=Dignity.EXALTED, is_retrograde=False
            ),
            Planet.SATURN: PlanetPlacement(
                planet=Planet.SATURN, sign=Sign.CAPRICORN, degree=28.0, house=2,
                nakshatra="Dhanishta", nakshatra_pada=4, dignity=Dignity.OWN_SIGN, is_retrograde=False
            ),
            Planet.RAHU: PlanetPlacement(
                planet=Planet.RAHU, sign=Sign.SCORPIO, degree=5.0, house=11,
                nakshatra="Anuradha", nakshatra_pada=1, dignity=Dignity.NEUTRAL, is_retrograde=True
            ),
            Planet.KETU: PlanetPlacement(
                planet=Planet.KETU, sign=Sign.TAURUS, degree=5.0, house=5,
                nakshatra="Krittika", nakshatra_pada=1, dignity=Dignity.NEUTRAL, is_retrograde=True
            ),
        }
        
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
    
    def test_detect_planet_peaks(self, analysis_service, timeline_service, sample_chart):
        """Test detecting planet peak influences."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 10, 0, 0, 0)
        
        # Generate timeline
        timeline = timeline_service.calculate_planet_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )
        
        # Detect peaks
        peaks = analysis_service.detect_planet_peaks(timeline)
        
        # Verify peaks are detected
        assert isinstance(peaks, list)
        
        # Verify each peak
        for peak in peaks:
            assert peak.peak_score >= analysis_service.peak_threshold
            assert peak.duration_days >= 1
            assert peak.peak_time >= start
            assert peak.peak_time <= end
        
        # Verify peaks are sorted by score (highest first)
        if len(peaks) > 1:
            for i in range(len(peaks) - 1):
                assert peaks[i].peak_score >= peaks[i + 1].peak_score

    def test_detect_significant_events(self, analysis_service, timeline_service, sample_chart):
        """Test detecting significant astrological events."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 10, 0, 0, 0)

        # Generate timeline
        timeline = timeline_service.calculate_planet_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Detect events
        events = analysis_service.detect_significant_events(timeline)

        # Verify events are detected
        assert isinstance(events, list)

        # Verify each event
        for event in events:
            assert event.significance >= analysis_service.significance_threshold
            assert event.timestamp >= start
            assert event.timestamp <= end
            assert len(event.entities) > 0

        # Verify events are sorted by significance (highest first)
        if len(events) > 1:
            for i in range(len(events) - 1):
                assert events[i].significance >= events[i + 1].significance

    def test_generate_analysis_report(self, analysis_service, timeline_service, sample_chart):
        """Test generating complete analysis report."""
        start = datetime(2026, 3, 1, 0, 0, 0)
        end = datetime(2026, 3, 10, 0, 0, 0)

        # Generate timeline
        timeline = timeline_service.calculate_planet_timeline(
            sample_chart,
            start,
            end,
            interval_days=1
        )

        # Generate report
        report = analysis_service.generate_analysis_report(timeline)

        # Verify report structure
        assert report.chart_id == "test_chart"
        assert report.start_date == start
        assert report.end_date == end
        assert isinstance(report.peak_influences, list)
        assert isinstance(report.significant_events, list)
        assert isinstance(report.summary, str)
        assert len(report.summary) > 0

