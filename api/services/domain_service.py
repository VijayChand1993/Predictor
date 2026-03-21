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


class DomainService:
    """Service for calculating life domain scores and analysis."""
    
    def __init__(
        self,
        scoring_engine: ScoringEngine,
        house_activation_service: HouseActivationService
    ):
        """
        Initialize the domain service.
        
        Args:
            scoring_engine: Service for calculating planet scores
            house_activation_service: Service for calculating house activations
        """
        self.scoring_engine = scoring_engine
        self.house_activation_service = house_activation_service
    
    def calculate_domain_score(
        self,
        domain: str,
        house_activations: Dict[int, HouseActivation],
        planet_scores: Dict[Planet, float]
    ) -> DomainScore:
        """
        Calculate score for a single life domain.

        Combines:
        - House activation (60% weight)
        - Planet influence (40% weight)

        Args:
            domain: Domain name (e.g., "Career / Work")
            house_activations: House activation scores (house number -> HouseActivation)
            planet_scores: Planet scores (Planet -> score)

        Returns:
            DomainScore with complete breakdown
        """
        # Get domain configuration
        domain_houses = get_domain_houses(domain)

        # Calculate house component (60% weight)
        house_component = 0.0
        house_scores = {}
        for house_num in domain_houses:
            if house_num in house_activations:
                house_weight = get_domain_house_weight(domain, house_num)
                house_score = house_activations[house_num].score
                house_component += house_score * house_weight
                house_scores[house_num] = house_score

        # Calculate planet component (40% weight)
        planet_component = 0.0
        total_influence = 0.0

        for planet, score in planet_scores.items():
            influence = get_planet_domain_influence(planet, domain)
            if influence > 0:
                planet_component += score * influence
                total_influence += influence

        # Normalize planet component by total influence
        if total_influence > 0:
            planet_component = planet_component / total_influence

        # Combine components with weights
        house_weight = DOMAIN_CALCULATION_WEIGHTS["house_weight"]
        planet_weight = DOMAIN_CALCULATION_WEIGHTS["planet_weight"]

        final_score = (house_component * house_weight) + (planet_component * planet_weight)

        # Identify driving planets
        driving_planets = self.identify_driving_planets(domain, planet_scores)

        # Create domain score
        return DomainScore(
            domain=domain,
            score=final_score,
            house_contribution=house_component,
            planet_contribution=planet_component,
            driving_planets=driving_planets,
            house_scores=house_scores,
            subdomains={}  # Will be populated if requested
        )
    
    def calculate_subdomain_score(
        self,
        subdomain: str,
        house_activations: Dict[int, HouseActivation],
        planet_scores: Dict[Planet, float]
    ) -> SubdomainScore:
        """
        Calculate score for a specific subdomain.

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

        # Calculate house component
        house_component = 0.0
        total_house_weight = 0.0

        for house_num, weight in subdomain_config["houses"].items():
            if house_num in house_activations:
                house_score = house_activations[house_num].score
                house_component += house_score * weight
                total_house_weight += weight

        # Normalize house component
        if total_house_weight > 0:
            house_component = house_component / total_house_weight

        # Calculate planet component
        planet_component = 0.0
        total_planet_influence = 0.0

        for planet_str, influence in subdomain_config["planets"].items():
            planet = Planet(planet_str)
            if planet in planet_scores:
                planet_component += planet_scores[planet] * influence
                total_planet_influence += influence

        # Normalize planet component
        if total_planet_influence > 0:
            planet_component = planet_component / total_planet_influence

        # Combine components (60% house, 40% planet)
        house_weight = DOMAIN_CALCULATION_WEIGHTS["house_weight"]
        planet_weight = DOMAIN_CALCULATION_WEIGHTS["planet_weight"]

        final_score = (house_component * house_weight) + (planet_component * planet_weight)

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
        include_events: bool = True
    ) -> DomainTimeline:
        """
        Calculate domain scores over a time period.

        Args:
            chart_id: Chart identifier
            start_date: Start of timeline
            end_date: End of timeline
            interval_days: Days between data points (default: 7)
            include_events: Whether to include significant events

        Returns:
            DomainTimeline with scores at each interval
        """
        timeline_points = []

        # Calculate domain scores at each interval
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

