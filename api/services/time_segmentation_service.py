"""
Time Segmentation Service for detecting astrological transitions.

Automatically detects Moon and Sun sign changes to create optimal
calculation points for timeline analysis, replacing fixed-interval sampling.
"""
from datetime import datetime, timedelta
from typing import List, Tuple, Optional
from dataclasses import dataclass

from api.models import Planet, Sign, NatalChart
from api.services.transit_service import TransitService


@dataclass
class TransitionEvent:
    """Represents an astrological transition event."""
    timestamp: datetime
    planet: Planet
    from_sign: Sign
    to_sign: Sign
    event_type: str  # "sign_change"
    
    def __str__(self):
        return f"{self.planet.value} enters {self.to_sign.value} at {self.timestamp}"


@dataclass
class TimeSegment:
    """A time segment with stable planetary positions."""
    start: datetime
    end: datetime
    transition_event: Optional[TransitionEvent] = None
    
    def duration_days(self) -> float:
        """Get segment duration in days."""
        return (self.end - self.start).total_seconds() / 86400
    
    def midpoint(self) -> datetime:
        """Get the midpoint of the segment."""
        delta = (self.end - self.start) / 2
        return self.start + delta


class TimeSegmentationService:
    """Service for intelligent time segmentation based on astrological transitions."""
    
    def __init__(self, transit_service: TransitService = None):
        """
        Initialize the time segmentation service.
        
        Args:
            transit_service: Transit service for planetary position calculations
        """
        self.transit_service = transit_service or TransitService()
    
    def get_planet_sign(
        self,
        planet: Planet,
        date: datetime,
        natal_chart: NatalChart
    ) -> Sign:
        """
        Get the sign a planet is in at a specific date.
        
        Args:
            planet: The planet to check
            date: The date/time
            natal_chart: Natal chart for context
        
        Returns:
            Sign the planet is in
        """
        transit_data = self.transit_service.get_transit_data(date, natal_chart)
        return transit_data.planets[planet].sign
    
    def find_sign_change(
        self,
        planet: Planet,
        start_date: datetime,
        end_date: datetime,
        natal_chart: NatalChart,
        precision_hours: float = 1.0
    ) -> Optional[TransitionEvent]:
        """
        Find the exact moment a planet changes signs within a date range.
        
        Uses binary search to find the transition point with specified precision.
        
        Args:
            planet: The planet to track
            start_date: Start of search range
            end_date: End of search range
            natal_chart: Natal chart for context
            precision_hours: Precision in hours (default: 1 hour)
        
        Returns:
            TransitionEvent if a sign change occurred, None otherwise
        """
        # Get signs at start and end
        start_sign = self.get_planet_sign(planet, start_date, natal_chart)
        end_sign = self.get_planet_sign(planet, end_date, natal_chart)
        
        # No change occurred
        if start_sign == end_sign:
            return None
        
        # Binary search for the transition point
        left = start_date
        right = end_date
        precision_delta = timedelta(hours=precision_hours)
        
        while (right - left) > precision_delta:
            mid = left + (right - left) / 2
            mid_sign = self.get_planet_sign(planet, mid, natal_chart)
            
            if mid_sign == start_sign:
                left = mid
            else:
                right = mid
        
        # Use the midpoint as the transition time
        transition_time = left + (right - left) / 2
        
        return TransitionEvent(
            timestamp=transition_time,
            planet=planet,
            from_sign=start_sign,
            to_sign=end_sign,
            event_type="sign_change"
        )

    def generate_segments(
        self,
        start_date: datetime,
        end_date: datetime,
        natal_chart: NatalChart,
        track_planets: List[Planet] = None,
        max_segment_days: float = 7.0
    ) -> List[TimeSegment]:
        """
        Generate time segments based on planetary sign changes.

        This is the main method that creates intelligent segments by detecting
        when Moon and/or Sun change signs, creating calculation points at
        astrologically significant moments rather than arbitrary intervals.

        Args:
            start_date: Start of timeline
            end_date: End of timeline
            natal_chart: Natal chart for context
            track_planets: Planets to track for transitions (default: Moon and Sun)
            max_segment_days: Maximum segment length in days (default: 7)

        Returns:
            List of TimeSegment objects with transition events
        """
        if track_planets is None:
            # Default: Track Moon (changes ~every 2.5 days) and Sun (changes ~every 30 days)
            track_planets = [Planet.MOON, Planet.SUN]

        # Find all transition events in the date range
        transitions = self._find_all_transitions(
            start_date,
            end_date,
            natal_chart,
            track_planets,
            max_segment_days
        )

        # Create segments from transitions
        segments = self._create_segments_from_transitions(
            start_date,
            end_date,
            transitions
        )

        return segments

    def _find_all_transitions(
        self,
        start_date: datetime,
        end_date: datetime,
        natal_chart: NatalChart,
        track_planets: List[Planet],
        max_segment_days: float
    ) -> List[TransitionEvent]:
        """
        Find all planetary sign changes in the date range.

        Uses intelligent sampling based on planetary speeds:
        - Moon: Check every 1 day (changes sign ~every 2.5 days)
        - Sun: Check every 7 days (changes sign ~every 30 days)

        Args:
            start_date: Start of range
            end_date: End of range
            natal_chart: Natal chart
            track_planets: Planets to track
            max_segment_days: Maximum days between checks

        Returns:
            Sorted list of TransitionEvent objects
        """
        transitions = []

        for planet in track_planets:
            # Determine sampling interval based on planet speed
            if planet == Planet.MOON:
                # Moon changes sign every ~2.5 days, check daily
                sample_interval = timedelta(days=1)
            elif planet == Planet.SUN:
                # Sun changes sign every ~30 days, check weekly
                sample_interval = timedelta(days=7)
            else:
                # For other planets, use max_segment_days
                sample_interval = timedelta(days=max_segment_days)

            # Sample the date range
            current = start_date
            while current < end_date:
                next_check = min(current + sample_interval, end_date)

                # Check for sign change in this interval
                transition = self.find_sign_change(
                    planet,
                    current,
                    next_check,
                    natal_chart,
                    precision_hours=1.0
                )

                if transition:
                    transitions.append(transition)

                current = next_check

        # Sort transitions by timestamp
        transitions.sort(key=lambda t: t.timestamp)

        return transitions

    def _create_segments_from_transitions(
        self,
        start_date: datetime,
        end_date: datetime,
        transitions: List[TransitionEvent]
    ) -> List[TimeSegment]:
        """
        Create time segments from transition events.

        Each segment runs from one transition to the next, with the first
        segment starting at start_date and the last ending at end_date.

        Args:
            start_date: Timeline start
            end_date: Timeline end
            transitions: Sorted list of transitions

        Returns:
            List of TimeSegment objects
        """
        segments = []

        if not transitions:
            # No transitions - create single segment
            return [TimeSegment(start=start_date, end=end_date, transition_event=None)]

        # First segment: start_date to first transition
        segments.append(TimeSegment(
            start=start_date,
            end=transitions[0].timestamp,
            transition_event=None
        ))

        # Middle segments: between transitions
        for i in range(len(transitions) - 1):
            segments.append(TimeSegment(
                start=transitions[i].timestamp,
                end=transitions[i + 1].timestamp,
                transition_event=transitions[i]
            ))

        # Last segment: last transition to end_date
        segments.append(TimeSegment(
            start=transitions[-1].timestamp,
            end=end_date,
            transition_event=transitions[-1]
        ))

        return segments

