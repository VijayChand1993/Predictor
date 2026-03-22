"""
Analysis Pipeline Service - Unified Orchestration

This service coordinates all analysis components into a single
end-to-end pipeline, providing a unified interface for complete
astrological analysis.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from api.models.pipeline import (
    AnalysisRequest,
    AnalysisResponse,
    QuickAnalysisRequest,
    QuickAnalysisResponse
)
from api.models.natal_chart import NatalChart
from api.services.natal_chart_service import NatalChartService
from api.services.scoring_engine import ScoringEngine
from api.services.house_activation_service import HouseActivationService
from api.services.domain_service import DomainService


class AnalysisPipeline:
    """
    End-to-end analysis pipeline that orchestrates all services.
    
    This service provides a unified interface for complete astrological
    analysis, coordinating:
    1. Natal chart generation/retrieval
    2. Planet scoring (Dasha + Transit + Strength + Aspect + Motion)
    3. House activation calculation
    4. Domain analysis (7 life domains + subdomains)
    5. Timeline generation with intelligent segmentation
    """
    
    def __init__(
        self,
        natal_chart_service: NatalChartService,
        scoring_engine: ScoringEngine,
        house_activation_service: HouseActivationService,
        domain_service: DomainService
    ):
        """
        Initialize the analysis pipeline.
        
        Args:
            natal_chart_service: Service for natal chart operations
            scoring_engine: Service for planet scoring
            house_activation_service: Service for house activation
            domain_service: Service for domain analysis
        """
        self.natal_chart_service = natal_chart_service
        self.scoring_engine = scoring_engine
        self.house_activation_service = house_activation_service
        self.domain_service = domain_service
    
    def run_full_analysis(
        self,
        request: AnalysisRequest
    ) -> AnalysisResponse:
        """
        Run complete end-to-end analysis.
        
        This is the main orchestration method that coordinates all
        analysis components in the correct order.
        
        Args:
            request: Analysis request with birth details and parameters
            
        Returns:
            Unified response with all analysis results
        """
        # Step 1: Get or generate natal chart
        natal_chart, chart_id = self._get_or_create_chart(request)

        # Step 2: Calculate current planet scores
        current_planet_scores = self.scoring_engine.calculate_planet_scores(
            natal_chart=natal_chart,
            calculation_date=request.calculation_date
        )
        
        # Step 3: Calculate current house activation
        current_house_activation = self.house_activation_service.calculate_house_activation(
            natal_chart=natal_chart,
            calculation_date=request.calculation_date
        )
        
        # Step 4: Calculate current domain analysis
        current_domain_analysis = self.domain_service.calculate_all_domains(
            chart_id=chart_id,
            calculation_date=request.calculation_date,
            include_subdomains=request.include_subdomains
        )
        
        # Step 5: Generate timeline (if requested)
        domain_timeline = None
        if request.include_timeline:
            timeline_start, timeline_end = self._get_timeline_range(request)
            
            domain_timeline = self.domain_service.calculate_domain_timeline(
                chart_id=chart_id,
                start_date=timeline_start,
                end_date=timeline_end,
                include_events=request.include_events,
                use_intelligent_segmentation=request.use_intelligent_segmentation
            )
        
        # Step 6: Generate summary insights
        summary = self._generate_summary(
            current_domain_analysis,
            current_planet_scores,
            current_house_activation
        )
        
        # Step 7: Build unified response
        return AnalysisResponse(
            chart_id=chart_id,
            calculation_date=request.calculation_date,
            generated_at=datetime.now(),
            natal_chart=natal_chart,
            current_planet_scores=current_planet_scores,
            current_house_activation=current_house_activation,
            current_domain_analysis=current_domain_analysis,
            domain_timeline=domain_timeline,
            summary=summary
        )
    
    def run_quick_analysis(
        self,
        request: QuickAnalysisRequest
    ) -> QuickAnalysisResponse:
        """
        Run quick analysis for existing chart.
        
        Optimized for speed - only calculates essential metrics.
        
        Args:
            request: Quick analysis request
            
        Returns:
            Simplified response with key insights
        """
        calculation_date = request.calculation_date or datetime.now()
        
        # Calculate domain analysis (core metric)
        domain_analysis = self.domain_service.calculate_all_domains(
            chart_id=request.chart_id,
            calculation_date=calculation_date,
            include_subdomains=False  # Skip for speed
        )
        
        # Extract key metrics
        domain_scores = {
            domain: score.score
            for domain, score in domain_analysis.domains.items()
        }
        
        # Find strongest and weakest
        strongest_domain = max(domain_scores.items(), key=lambda x: x[1])
        weakest_domain = min(domain_scores.items(), key=lambda x: x[1])
        
        # Collect top insights
        top_insights = []
        for domain, score_obj in domain_analysis.domains.items():
            if score_obj.explanations:
                top_insights.extend(score_obj.explanations[:2])  # Top 2 per domain
        
        # Limit to top 5 insights
        top_insights = top_insights[:5]
        
        return QuickAnalysisResponse(
            chart_id=request.chart_id,
            calculation_date=calculation_date,
            overall_life_quality=domain_analysis.overall_life_quality,
            strongest_domain=strongest_domain[0],
            strongest_domain_score=strongest_domain[1],
            weakest_domain=weakest_domain[0],
            weakest_domain_score=weakest_domain[1],
            top_insights=top_insights,
            domain_scores=domain_scores
        )

    def _get_or_create_chart(
        self,
        request: AnalysisRequest
    ) -> tuple[NatalChart, str]:
        """
        Get existing chart or create new one.

        Args:
            request: Analysis request

        Returns:
            Tuple of (natal_chart, chart_id)
        """
        from api.routes.chart import charts_db

        # If chart_id provided, try to load it
        if request.chart_id:
            if request.chart_id in charts_db:
                return charts_db[request.chart_id], request.chart_id
            else:
                raise ValueError(f"Chart {request.chart_id} not found")

        # Otherwise, create new chart
        if not all([request.name, request.birth_date, request.birth_time,
                   request.latitude, request.longitude, request.timezone]):
            raise ValueError(
                "Must provide either chart_id or complete birth details "
                "(name, birth_date, birth_time, latitude, longitude, timezone)"
            )

        # Generate new chart
        natal_chart = self.natal_chart_service.generate_natal_chart(
            name=request.name,
            birth_date=request.birth_date,
            birth_time=request.birth_time,
            latitude=request.latitude,
            longitude=request.longitude,
            timezone=request.timezone
        )

        return natal_chart, natal_chart.chart_id

    def _get_timeline_range(
        self,
        request: AnalysisRequest
    ) -> tuple[datetime, datetime]:
        """
        Determine timeline start and end dates.

        Args:
            request: Analysis request

        Returns:
            Tuple of (start_date, end_date)
        """
        if request.timeline_start and request.timeline_end:
            return request.timeline_start, request.timeline_end

        # Default: calculation_date ± timeline_days/2
        half_days = request.timeline_days // 2
        start_date = request.calculation_date - timedelta(days=half_days)
        end_date = request.calculation_date + timedelta(days=half_days)

        return start_date, end_date

    def _generate_summary(
        self,
        domain_analysis,
        planet_scores,
        house_activation
    ) -> Dict[str, Any]:
        """
        Generate high-level summary and insights.

        Args:
            domain_analysis: Domain analysis results
            planet_scores: Planet scores
            house_activation: House activation

        Returns:
            Summary dictionary with key insights
        """
        # Extract domain scores
        domain_scores = {
            domain: score.score
            for domain, score in domain_analysis.domains.items()
        }

        # Find strongest and weakest
        strongest = max(domain_scores.items(), key=lambda x: x[1])
        weakest = min(domain_scores.items(), key=lambda x: x[1])

        # Collect key insights from explanations
        key_insights = []

        # Add top domain insights
        if strongest[0] in domain_analysis.domains:
            strongest_explanations = domain_analysis.domains[strongest[0]].explanations
            if strongest_explanations:
                key_insights.append(strongest_explanations[0])

        # Add planet insights
        for planet, planet_score in planet_scores.scores.items():
            if planet_score.explanations and planet_score.score > 12:
                key_insights.append(planet_score.explanations[0])
                if len(key_insights) >= 5:
                    break

        return {
            "overall_life_quality": domain_analysis.overall_life_quality,
            "strongest_domain": strongest[0],
            "strongest_domain_score": strongest[1],
            "weakest_domain": weakest[0],
            "weakest_domain_score": weakest[1],
            "key_insights": key_insights[:5],  # Top 5
            "domain_scores": domain_scores,
            "analysis_timestamp": datetime.now().isoformat()
        }

