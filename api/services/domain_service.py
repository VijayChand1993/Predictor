"""
Domain Service for calculating life domain scores.

This service translates astrological data (planet scores and house activations)
into actionable insights about 7 key life domains.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from api.models.enums import Planet
from api.models.scoring import PlanetScores, PlanetScore
from api.models.house_activation import HouseActivationCalculation, HouseActivation
from api.models.domain_analysis import (
    DomainScore,
    SubdomainScore,
    PlanetContribution,
    DomainAnalysis,
    DomainTimeline,
    DomainTimePoint,
    SignificantEvent
)
from api.core.domain_config import (
    LIFE_DOMAINS,
    DOMAIN_HOUSE_MAPPING,
    PLANET_DOMAIN_INFLUENCE,
    SUBDOMAIN_MAPPING,
    DOMAIN_CALCULATION_WEIGHTS,
    get_domain_houses,
    get_domain_house_weight,
    get_planet_domain_influence,
    get_subdomain_parent
)
from api.services.scoring_engine import ScoringEngine
from api.services.house_activation_service import HouseActivationService
from api.services.time_segmentation_service import TimeSegmentationService


class DomainService:
    """Service for calculating life domain scores and analysis."""

    def __init__(
        self,
        scoring_engine: ScoringEngine,
        house_activation_service: HouseActivationService,
        time_segmentation_service: TimeSegmentationService = None
    ):
        """
        Initialize the domain service.

        Args:
            scoring_engine: Service for calculating planet scores
            house_activation_service: Service for calculating house activations
            time_segmentation_service: Service for intelligent time segmentation (optional)
        """
        self.scoring_engine = scoring_engine
        self.house_activation_service = house_activation_service
        self.time_segmentation_service = time_segmentation_service or TimeSegmentationService()
    
    def calculate_domain_score(
        self,
        domain: str,
        house_activations: Dict[int, HouseActivation],
        planet_scores: Dict[Planet, float]
    ) -> DomainScore:
        """
        Calculate score for a single life domain (Phase 6 - STRUCTURAL FIX).

        NEW APPROACH - ABSOLUTE SCORING (not normalized across domains):
        1. Calculate absolute domain score from planets and houses
        2. Apply house amplification if house score > 60
        3. Apply sigmoid scaling to map to 0-100 range
        4. Clamp to 100 max

        This fixes the "domain scores < 20" problem by removing global normalization.

        Args:
            domain: Domain name (e.g., "Career / Work")
            house_activations: House activation scores (house number -> HouseActivation)
            planet_scores: Planet scores (Planet -> score)

        Returns:
            DomainScore with complete breakdown
        """
        # Get domain configuration
        domain_houses = get_domain_houses(domain)

        # Step 1: Calculate ABSOLUTE domain score (sum, not average)
        # Each planet contributes: planetScore × domainWeight × houseActivation

        domain_score_raw = 0.0
        house_scores = {}

        # House contribution (direct sum, not normalized)
        house_component = 0.0
        for house_num in domain_houses:
            if house_num in house_activations:
                house_weight = get_domain_house_weight(domain, house_num)
                house_score = house_activations[house_num].score
                house_component += house_score * house_weight
                house_scores[house_num] = house_score

        # Planet contribution (direct sum, not normalized)
        planet_component = 0.0
        for planet, score in planet_scores.items():
            influence = get_planet_domain_influence(planet, domain)
            if influence > 0:
                # Absolute contribution (no normalization)
                planet_component += score * influence

        # Combine components (absolute sum, not weighted average)
        # Scale down to reasonable range (0-2 typically)
        house_weight = DOMAIN_CALCULATION_WEIGHTS["house_weight"]
        planet_weight = DOMAIN_CALCULATION_WEIGHTS["planet_weight"]

        domain_score_raw = (house_component * house_weight + planet_component * planet_weight) / 100.0

        # Step 2: House amplification - if primary houses are strong, boost domain
        avg_house_score = sum(house_scores.values()) / len(house_scores) if house_scores else 0
        if avg_house_score > 60:
            domain_score_raw *= 1.2

        # Step 3: Sigmoid scaling - map absolute score to 0-100 range
        # Formula: 100 × (1 - e^(-2 × score))
        # This maps: 0 → 0, 0.5 → 63, 1.0 → 86, 1.5 → 95, 2.0 → 98
        import math
        final_score = 100.0 * (1.0 - math.exp(-2.0 * domain_score_raw))

        # Step 4: Clamp to 100 max
        final_score = min(final_score, 100.0)

        # Identify driving planets
        driving_planets = self.identify_driving_planets(domain, planet_scores)

        # Create domain score (without explanations first)
        domain_score = DomainScore(
            domain=domain,
            score=final_score,
            house_contribution=house_component,
            planet_contribution=planet_component,
            driving_planets=driving_planets,
            house_scores=house_scores,
            subdomains={},  # Will be populated if requested
            explanations=[]
        )

        # Generate explanations
        explanations = self.generate_domain_explanations(domain, domain_score, house_activations)
        domain_score.explanations = explanations

        return domain_score
    
    def calculate_subdomain_score(
        self,
        subdomain: str,
        house_activations: Dict[int, HouseActivation],
        planet_scores: Dict[Planet, float]
    ) -> SubdomainScore:
        """
        Calculate score for a specific subdomain (Phase 6 - STRUCTURAL FIX).

        Uses same absolute scoring approach as domains.

        Args:
            subdomain: Subdomain name (e.g., "job", "promotion")
            house_activations: House activation scores
            planet_scores: Planet scores

        Returns:
            SubdomainScore with breakdown
        """
        # Get subdomain configuration
        if subdomain not in SUBDOMAIN_MAPPING:
            raise ValueError(f"Unknown subdomain: {subdomain}")

        subdomain_config = SUBDOMAIN_MAPPING[subdomain]

        # Calculate house component (absolute sum)
        house_component = 0.0
        for house_num, weight in subdomain_config["houses"].items():
            if house_num in house_activations:
                house_score = house_activations[house_num].score
                house_component += house_score * weight

        # Calculate planet component (absolute sum)
        planet_component = 0.0
        for planet_str, influence in subdomain_config["planets"].items():
            planet = Planet(planet_str)
            if planet in planet_scores:
                planet_component += planet_scores[planet] * influence

        # Combine components (absolute sum, scaled down)
        house_weight = DOMAIN_CALCULATION_WEIGHTS["house_weight"]
        planet_weight = DOMAIN_CALCULATION_WEIGHTS["planet_weight"]

        subdomain_score_raw = (house_component * house_weight + planet_component * planet_weight) / 100.0

        # Apply sigmoid scaling
        import math
        final_score = 100.0 * (1.0 - math.exp(-2.0 * subdomain_score_raw))
        final_score = min(final_score, 100.0)

        return SubdomainScore(
            subdomain=subdomain,
            score=final_score,
            house_contribution=house_component,
            planet_contribution=planet_component
        )
    
    def identify_driving_planets(
        self,
        domain: str,
        planet_scores: Dict[Planet, float]
    ) -> List[PlanetContribution]:
        """
        Identify which planets are most influential for a domain.

        Args:
            domain: Domain name
            planet_scores: Planet scores

        Returns:
            List of PlanetContribution sorted by contribution (highest first)
        """
        contributions = []

        for planet, score in planet_scores.items():
            influence = get_planet_domain_influence(planet, domain)

            if influence > 0:
                # Contribution is the product of planet score and influence
                contribution = score * influence

                contributions.append(PlanetContribution(
                    planet=planet,
                    planet_score=score,
                    influence=influence,
                    contribution=contribution
                ))

        # Sort by contribution (highest first)
        contributions.sort(key=lambda x: x.contribution, reverse=True)

        return contributions

    def generate_domain_explanations(
        self,
        domain: str,
        domain_score: DomainScore,
        house_activations: Dict[int, HouseActivation]
    ) -> List[str]:
        """
        Generate human-readable explanations for why a domain score is what it is.

        Args:
            domain: Domain name
            domain_score: The calculated domain score
            house_activations: House activation data for detailed explanations

        Returns:
            List of explanation strings
        """
        explanations = []

        # 1. Overall score interpretation
        score = domain_score.score
        if score >= 75:
            strength = "very strong"
        elif score >= 60:
            strength = "strong"
        elif score >= 45:
            strength = "moderate"
        elif score >= 30:
            strength = "weak"
        else:
            strength = "very weak"

        explanations.append(f"Overall {domain} score is {strength} at {score:.1f}/100")

        # 2. House contribution explanation
        house_contrib = domain_score.house_contribution
        if house_contrib >= 60:
            explanations.append(f"Houses are highly activated (contributing {house_contrib:.1f} points, 60% weight)")
        elif house_contrib >= 40:
            explanations.append(f"Houses are moderately activated (contributing {house_contrib:.1f} points, 60% weight)")
        else:
            explanations.append(f"Houses are weakly activated (contributing {house_contrib:.1f} points, 60% weight)")

        # 3. Top house explanation
        if domain_score.house_scores:
            top_house = max(domain_score.house_scores.items(), key=lambda x: x[1])
            house_num, house_score = top_house

            # Get house meaning
            house_meanings = {
                1: "self and personality",
                2: "wealth and resources",
                3: "communication and siblings",
                4: "home and mother",
                5: "creativity and children",
                6: "health and service",
                7: "partnerships and marriage",
                8: "transformation and inheritance",
                9: "higher learning and fortune",
                10: "career and status",
                11: "gains and aspirations",
                12: "losses and spirituality"
            }

            meaning = house_meanings.get(house_num, "life area")
            explanations.append(f"House {house_num} ({meaning}) is most active with score {house_score:.1f}")

        # 4. Planet contribution explanation
        planet_contrib = domain_score.planet_contribution
        if planet_contrib >= 60:
            explanations.append(f"Planetary influences are very strong (contributing {planet_contrib:.1f} points, 40% weight)")
        elif planet_contrib >= 40:
            explanations.append(f"Planetary influences are moderate (contributing {planet_contrib:.1f} points, 40% weight)")
        else:
            explanations.append(f"Planetary influences are weak (contributing {planet_contrib:.1f} points, 40% weight)")

        # 5. Top driving planets explanation
        if domain_score.driving_planets:
            top_planet = domain_score.driving_planets[0]
            planet_name = top_planet.planet.value

            # Planet characteristics
            planet_roles = {
                "Sun": "authority and vitality",
                "Moon": "emotions and mind",
                "Mars": "energy and action",
                "Mercury": "intellect and communication",
                "Jupiter": "wisdom and expansion",
                "Venus": "relationships and beauty",
                "Saturn": "discipline and structure",
                "Rahu": "ambition and innovation",
                "Ketu": "spirituality and detachment"
            }

            role = planet_roles.get(planet_name, "influence")
            explanations.append(
                f"{planet_name} ({role}) is the primary driver with score {top_planet.planet_score:.1f} "
                f"and {top_planet.influence*100:.0f}% natural influence on {domain}"
            )

            # Mention second planet if significantly contributing
            if len(domain_score.driving_planets) > 1:
                second_planet = domain_score.driving_planets[1]
                if second_planet.contribution >= top_planet.contribution * 0.6:  # At least 60% of top
                    planet_name_2 = second_planet.planet.value
                    role_2 = planet_roles.get(planet_name_2, "influence")
                    explanations.append(
                        f"{planet_name_2} ({role_2}) also significantly contributes with score {second_planet.planet_score:.1f}"
                    )

        # 6. Actionable insight based on score
        if score >= 60:
            explanations.append(f"This is a favorable time for {domain.lower()} activities")
        elif score >= 40:
            explanations.append(f"Moderate support for {domain.lower()} - proceed with balanced expectations")
        else:
            explanations.append(f"Exercise caution in {domain.lower()} matters - focus on preparation rather than action")

        return explanations

    def calculate_all_domains(
        self,
        chart_id: str,
        calculation_date: datetime,
        include_subdomains: bool = True
    ) -> DomainAnalysis:
        """
        Calculate scores for all 7 life domains.

        Args:
            chart_id: Chart identifier
            calculation_date: Date/time for calculation
            include_subdomains: Whether to include subdomain calculations

        Returns:
            DomainAnalysis with all domain scores
        """
        # Import charts_db from routes
        from api.routes.chart import charts_db

        # Get natal chart
        if chart_id not in charts_db:
            raise ValueError(f"Chart not found: {chart_id}")

        natal_chart = charts_db[chart_id]

        # Calculate planet scores
        planet_scores_result = self.scoring_engine.calculate_planet_scores(
            natal_chart=natal_chart,
            calculation_date=calculation_date
        )

        # Extract planet scores as dict
        planet_scores = {
            planet: score.score
            for planet, score in planet_scores_result.scores.items()
        }

        # Calculate house activations
        house_activation_result = self.house_activation_service.calculate_house_activation(
            natal_chart=natal_chart,
            calculation_date=calculation_date
        )

        # Extract house activations as dict (already a dict in the result)
        house_activations = house_activation_result.house_activations

        # Calculate all domains
        domains = {}
        for domain in LIFE_DOMAINS:
            domain_score = self.calculate_domain_score(
                domain=domain,
                house_activations=house_activations,
                planet_scores=planet_scores
            )

            # Add subdomains if requested
            if include_subdomains:
                subdomains = {}
                for subdomain_name, _ in SUBDOMAIN_MAPPING.items():
                    if get_subdomain_parent(subdomain_name) == domain:
                        subdomain_score = self.calculate_subdomain_score(
                            subdomain=subdomain_name,
                            house_activations=house_activations,
                            planet_scores=planet_scores
                        )
                        subdomains[subdomain_name] = subdomain_score

                domain_score.subdomains = subdomains

            domains[domain] = domain_score

        # Find strongest and weakest domains
        sorted_domains = sorted(domains.items(), key=lambda x: x[1].score, reverse=True)
        strongest_domain = sorted_domains[0][0] if sorted_domains else None
        weakest_domain = sorted_domains[-1][0] if sorted_domains else None

        # Calculate overall life quality as average of all domain scores
        overall_life_quality = sum(d.score for d in domains.values()) / len(domains) if domains else 0.0

        return DomainAnalysis(
            chart_id=chart_id,
            calculation_date=calculation_date,
            domains=domains,
            overall_life_quality=overall_life_quality,
            strongest_domain=strongest_domain,
            weakest_domain=weakest_domain
        )
    
    def detect_significant_events(
        self,
        chart_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[SignificantEvent]:
        """
        Identify significant astrological events in a time period.

        Detects:
        - Planet sign changes
        - Retrograde periods
        - Major aspects
        - House ingress

        Args:
            chart_id: Chart identifier
            start_date: Start of period
            end_date: End of period

        Returns:
            List of SignificantEvent sorted by date
        """
        from api.routes.chart import charts_db
        from api.services.transit_service import TransitService

        # Get natal chart
        if chart_id not in charts_db:
            raise ValueError(f"Chart not found: {chart_id}")

        natal_chart = charts_db[chart_id]
        transit_service = TransitService()

        events = []

        # Sample dates throughout the period to detect changes
        current_date = start_date
        interval = timedelta(days=1)  # Check daily

        previous_transit = None

        while current_date <= end_date:
            # Get transit data for this date
            transit_data = transit_service.get_transit_data(
                target_date=current_date,
                natal_chart=natal_chart,
                save_json=False
            )

            # Check for sign changes and retrograde status changes
            if previous_transit:
                for planet in Planet:
                    if planet in transit_data.planets and planet in previous_transit.planets:
                        current_planet = transit_data.planets[planet]
                        previous_planet = previous_transit.planets[planet]

                        # Detect sign change
                        if current_planet.sign != previous_planet.sign:
                            # Determine affected domains
                            affected_domains = []
                            for domain in LIFE_DOMAINS:
                                influence = get_planet_domain_influence(planet, domain)
                                if influence > 0.3:  # Significant influence threshold
                                    affected_domains.append(domain)

                            events.append(SignificantEvent(
                                date=current_date,
                                event_type="sign_change",
                                description=f"{planet.value} enters {current_planet.sign.value}",
                                affected_domains=affected_domains,
                                impact_score=influence * 100 if affected_domains else 50.0
                            ))

                        # Detect retrograde status change
                        if current_planet.is_retrograde != previous_planet.is_retrograde:
                            affected_domains = []
                            for domain in LIFE_DOMAINS:
                                influence = get_planet_domain_influence(planet, domain)
                                if influence > 0.3:
                                    affected_domains.append(domain)

                            status = "goes retrograde" if current_planet.is_retrograde else "goes direct"
                            events.append(SignificantEvent(
                                date=current_date,
                                event_type="retrograde_change",
                                description=f"{planet.value} {status}",
                                affected_domains=affected_domains,
                                impact_score=influence * 80 if affected_domains else 40.0
                            ))

            previous_transit = transit_data
            current_date += interval

        # Sort events by date
        events.sort(key=lambda x: x.date)

        return events
    
    def calculate_domain_timeline(
        self,
        chart_id: str,
        start_date: datetime,
        end_date: datetime,
        interval_days: int = 7,
        include_events: bool = True,
        use_intelligent_segmentation: bool = True
    ) -> DomainTimeline:
        """
        Calculate domain scores over a time period.

        Now supports intelligent segmentation based on Moon/Sun sign changes
        for more accurate timeline analysis.

        Args:
            chart_id: Chart identifier
            start_date: Start of timeline
            end_date: End of timeline
            interval_days: Days between data points (default: 7, used only if intelligent segmentation is disabled)
            include_events: Whether to include significant events
            use_intelligent_segmentation: Use Moon/Sun transitions instead of fixed intervals (default: True)

        Returns:
            DomainTimeline with scores at each interval
        """
        from api.routes.chart import charts_db

        timeline_points = []

        # Get natal chart for segmentation
        if chart_id not in charts_db:
            raise ValueError(f"Chart {chart_id} not found")

        natal_chart = charts_db[chart_id]

        if use_intelligent_segmentation:
            # Use intelligent segmentation based on Moon/Sun transitions
            segments = self.time_segmentation_service.generate_segments(
                start_date=start_date,
                end_date=end_date,
                natal_chart=natal_chart,
                track_planets=[Planet.MOON, Planet.SUN],
                max_segment_days=7.0
            )

            # Calculate domain scores at segment midpoints
            for segment in segments:
                calculation_date = segment.midpoint()

                # Calculate all domains for this date
                domain_analysis = self.calculate_all_domains(
                    chart_id=chart_id,
                    calculation_date=calculation_date,
                    include_subdomains=False  # Don't include subdomains in timeline for performance
                )

                # Create time point
                time_point = DomainTimePoint(
                    date=calculation_date,
                    domains={
                        domain: score.score
                        for domain, score in domain_analysis.domains.items()
                    }
                )

                timeline_points.append(time_point)
        else:
            # Use fixed interval (legacy mode)
            current_date = start_date
            interval = timedelta(days=interval_days)

            while current_date <= end_date:
                # Calculate all domains for this date
                domain_analysis = self.calculate_all_domains(
                    chart_id=chart_id,
                    calculation_date=current_date,
                    include_subdomains=False  # Don't include subdomains in timeline for performance
                )

                # Create time point
                time_point = DomainTimePoint(
                    date=current_date,
                    domains={
                        domain: score.score
                        for domain, score in domain_analysis.domains.items()
                    }
                )

                timeline_points.append(time_point)
                current_date += interval

        # Detect significant events if requested
        events = []
        if include_events:
            events = self.detect_significant_events(
                chart_id=chart_id,
                start_date=start_date,
                end_date=end_date
            )

        return DomainTimeline(
            chart_id=chart_id,
            start_date=start_date,
            end_date=end_date,
            interval_days=interval_days,
            timeline=timeline_points,
            significant_events=events
        )

