"""
Analysis Service for detecting peaks, events, and generating insights.
"""
from datetime import datetime, timedelta
from typing import List, Tuple

from api.models import (
    Planet,
    PlanetInfluenceTimeline,
    HouseActivationTimeline,
    PeakInfluence,
    SignificantEvent,
    AnalysisReport,
)


class AnalysisService:
    """Service for analyzing timelines and detecting significant patterns."""
    
    def __init__(self, peak_threshold: float = 15.0, significance_threshold: float = 70.0):
        """
        Initialize the analysis service.
        
        Args:
            peak_threshold: Minimum score to be considered a peak (default: 15.0)
            significance_threshold: Minimum significance for events (default: 70.0)
        """
        self.peak_threshold = peak_threshold
        self.significance_threshold = significance_threshold
    
    def detect_planet_peaks(
        self,
        timeline: PlanetInfluenceTimeline
    ) -> List[PeakInfluence]:
        """
        Detect peak influence periods for planets.
        
        Args:
            timeline: Planet influence timeline
        
        Returns:
            List of peak influence periods
        """
        peaks = []
        
        for planet, planet_timeline in timeline.timelines.items():
            # Only consider peaks above threshold
            if planet_timeline.peak_score >= self.peak_threshold:
                # Calculate duration of elevated influence
                # Count consecutive days above 80% of peak
                threshold = planet_timeline.peak_score * 0.8
                duration = self._calculate_duration(
                    planet_timeline.data_points,
                    planet_timeline.peak_time,
                    threshold
                )
                
                peaks.append(
                    PeakInfluence(
                        entity=planet.value,
                        peak_score=planet_timeline.peak_score,
                        peak_time=planet_timeline.peak_time,
                        duration_days=duration
                    )
                )
        
        # Sort by peak score (highest first)
        peaks.sort(key=lambda x: x.peak_score, reverse=True)
        return peaks
    
    def detect_house_peaks(
        self,
        timeline: HouseActivationTimeline
    ) -> List[PeakInfluence]:
        """
        Detect peak activation periods for houses.
        
        Args:
            timeline: House activation timeline
        
        Returns:
            List of peak activation periods
        """
        peaks = []
        
        for house_num, house_timeline in timeline.timelines.items():
            # Only consider peaks above threshold
            if house_timeline.peak_score >= self.peak_threshold:
                # Calculate duration of elevated activation
                threshold = house_timeline.peak_score * 0.8
                duration = self._calculate_duration(
                    house_timeline.data_points,
                    house_timeline.peak_time,
                    threshold
                )
                
                peaks.append(
                    PeakInfluence(
                        entity=f"House {house_num}",
                        peak_score=house_timeline.peak_score,
                        peak_time=house_timeline.peak_time,
                        duration_days=duration
                    )
                )
        
        # Sort by peak score (highest first)
        peaks.sort(key=lambda x: x.peak_score, reverse=True)
        return peaks
    
    def _calculate_duration(
        self,
        data_points: List,
        peak_time: datetime,
        threshold: float
    ) -> int:
        """
        Calculate duration of elevated scores around a peak.
        
        Args:
            data_points: List of data points
            peak_time: Time of peak
            threshold: Minimum score to count as elevated
        
        Returns:
            Duration in days
        """
        # Find the peak index
        peak_idx = None
        for i, dp in enumerate(data_points):
            if dp.timestamp == peak_time:
                peak_idx = i
                break
        
        if peak_idx is None:
            return 1
        
        # Count days before peak above threshold
        days_before = 0
        for i in range(peak_idx - 1, -1, -1):
            if data_points[i].score >= threshold:
                days_before += 1
            else:
                break
        
        # Count days after peak above threshold
        days_after = 0
        for i in range(peak_idx + 1, len(data_points)):
            if data_points[i].score >= threshold:
                days_after += 1
            else:
                break
        
        # Total duration (including peak day)
        return days_before + 1 + days_after
    
    def detect_significant_events(
        self,
        timeline: PlanetInfluenceTimeline
    ) -> List[SignificantEvent]:
        """
        Detect significant astrological events in the timeline.
        
        Args:
            timeline: Planet influence timeline
        
        Returns:
            List of significant events
        """
        events = []
        
        # Detect peak influence events
        for planet, planet_timeline in timeline.timelines.items():
            if planet_timeline.peak_score >= self.peak_threshold:
                # Calculate significance based on peak score
                significance = min(100.0, (planet_timeline.peak_score / 20.0) * 100)
                
                if significance >= self.significance_threshold:
                    events.append(
                        SignificantEvent(
                            event_type="peak_influence",
                            description=f"{planet.value} reaches peak influence of {planet_timeline.peak_score:.1f}",
                            timestamp=planet_timeline.peak_time,
                            entities=[planet.value],
                            significance=significance
                        )
                    )
        
        # Sort by significance (highest first)
        events.sort(key=lambda x: x.significance, reverse=True)
        return events

    def generate_analysis_report(
        self,
        timeline: PlanetInfluenceTimeline
    ) -> AnalysisReport:
        """
        Generate a complete analysis report for a planet timeline.

        Args:
            timeline: Planet influence timeline

        Returns:
            Complete analysis report with peaks, events, and summary
        """
        # Detect peaks and events
        peak_influences = self.detect_planet_peaks(timeline)
        significant_events = self.detect_significant_events(timeline)

        # Generate summary
        summary = self._generate_summary(timeline, peak_influences, significant_events)

        return AnalysisReport(
            chart_id=timeline.chart_id,
            start_date=timeline.start_date,
            end_date=timeline.end_date,
            peak_influences=peak_influences,
            significant_events=significant_events,
            summary=summary
        )

    def _generate_summary(
        self,
        timeline: PlanetInfluenceTimeline,
        peaks: List[PeakInfluence],
        events: List[SignificantEvent]
    ) -> str:
        """
        Generate a text summary of the analysis.

        Args:
            timeline: Planet influence timeline
            peaks: Detected peak influences
            events: Detected significant events

        Returns:
            Human-readable summary text
        """
        summary_parts = []

        # Overall period
        days = (timeline.end_date - timeline.start_date).days
        summary_parts.append(f"Analysis for {days}-day period from {timeline.start_date.strftime('%b %d, %Y')} to {timeline.end_date.strftime('%b %d, %Y')}.")

        # Most influential planet
        most_influential, score = timeline.get_most_influential_planet()
        summary_parts.append(f"{most_influential.value} shows the strongest average influence ({score:.1f}).")

        # Peak influences
        if peaks:
            top_peak = peaks[0]
            summary_parts.append(
                f"Peak influence occurs on {top_peak.peak_time.strftime('%b %d')} "
                f"with {top_peak.entity} reaching {top_peak.peak_score:.1f}, "
                f"sustained for {top_peak.duration_days} days."
            )

        # Significant events
        if events:
            summary_parts.append(f"Detected {len(events)} significant astrological events during this period.")

        return " ".join(summary_parts)

