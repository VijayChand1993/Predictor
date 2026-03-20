#!/usr/bin/env python3
"""Test script for sign changes in time segments."""

from datetime import datetime
from api.services.transit_service import TransitService
from api.services.natal_chart_service import NatalChartService
from api.models import BirthData, Location

def test_sign_changes():
    """Test that sign changes are properly tracked in segments."""
    
    # Create services
    transit_service = TransitService()
    natal_service = NatalChartService()
    
    # Load an existing chart
    chart_id = "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"
    natal_chart = natal_service.load_chart(chart_id)
    
    # Get segments for a 7-day period
    start_date = datetime(2026, 3, 20)
    end_date = datetime(2026, 3, 27)
    
    segments = transit_service.get_time_segments(
        start_date,
        end_date,
        natal_chart
    )
    
    print(f"Found {len(segments)} segments")
    print("=" * 80)
    
    for i, segment in enumerate(segments, 1):
        print(f"\nSegment {i}:")
        print(f"  Start: {segment.start_date}")
        print(f"  End: {segment.end_date}")
        print(f"  Duration: {segment.duration_days:.2f} days")
        
        if segment.sign_changes:
            print(f"  Sign Changes: {[p.value for p in segment.sign_changes]}")
        else:
            print(f"  Sign Changes: None (first segment)")
        
        # Show a few planet positions
        print(f"  Planet Positions:")
        for planet_name in ["Moon", "Sun", "Jupiter"]:
            from api.models import Planet
            planet = Planet(planet_name)
            if planet in segment.transit_data.planets:
                placement = segment.transit_data.planets[planet]
                print(f"    {planet_name}: {placement.sign.value} {placement.degree:.2f}°")

if __name__ == "__main__":
    test_sign_changes()

