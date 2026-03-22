"""Test script for the Analysis Pipeline."""
from datetime import datetime
from api.services.analysis_pipeline import AnalysisPipeline
from api.models.pipeline import QuickAnalysisRequest, AnalysisRequest
from api.services.natal_chart_service import NatalChartService
from api.services.scoring_engine import ScoringEngine
from api.services.house_activation_service import HouseActivationService
from api.services.domain_service import DomainService
from api.services.dasha_service import DashaService
from api.services.transit_service import TransitService
from api.services.strength_service import StrengthService
from api.services.aspect_service import AspectService
from api.services.motion_service import MotionService
from api.services.time_segmentation_service import TimeSegmentationService

# Initialize services
print("Initializing services...")
natal_chart_service = NatalChartService()
scoring_engine = ScoringEngine()
house_activation_service = HouseActivationService()
time_segmentation_service = TimeSegmentationService()
domain_service = DomainService(
    scoring_engine=scoring_engine,
    house_activation_service=house_activation_service,
    time_segmentation_service=time_segmentation_service
)

pipeline = AnalysisPipeline(
    natal_chart_service=natal_chart_service,
    scoring_engine=scoring_engine,
    house_activation_service=house_activation_service,
    domain_service=domain_service
)

print("✅ Services initialized\n")

# Test 1: Quick Analysis
print("=" * 60)
print("TEST 1: Quick Analysis")
print("=" * 60)

request = QuickAnalysisRequest(
    chart_id='04ecf146-d0e1-4e72-8c30-fb8bba03e2e5'
)

print('Running quick analysis...')
result = pipeline.run_quick_analysis(request)

print(f'\n✅ Quick Analysis Results:')
print(f'Chart ID: {result.chart_id}')
print(f'Overall Life Quality: {result.overall_life_quality:.1f}/100')
print(f'Strongest Domain: {result.strongest_domain} ({result.strongest_domain_score:.1f})')
print(f'Weakest Domain: {result.weakest_domain} ({result.weakest_domain_score:.1f})')
print(f'\nTop Insights:')
for i, insight in enumerate(result.top_insights, 1):
    print(f'{i}. {insight}')
print(f'\nAll Domain Scores:')
for domain, score in result.domain_scores.items():
    print(f'  {domain}: {score:.1f}')

# Test 2: Full Analysis (without timeline for speed)
print("\n" + "=" * 60)
print("TEST 2: Full Analysis (No Timeline)")
print("=" * 60)

full_request = AnalysisRequest(
    chart_id='04ecf146-d0e1-4e72-8c30-fb8bba03e2e5',
    calculation_date=datetime(2026, 3, 22),
    include_timeline=False,
    include_subdomains=True
)

print('Running full analysis...')
full_result = pipeline.run_full_analysis(full_request)

print(f'\n✅ Full Analysis Results:')
print(f'Chart ID: {full_result.chart_id}')
print(f'Natal Chart ID: {full_result.natal_chart.chart_id}')
print(f'Calculation Date: {full_result.calculation_date}')
print(f'Generated At: {full_result.generated_at}')
print(f'\nPlanet Scores: {len(full_result.current_planet_scores.scores)} planets')
print(f'House Activation: {len(full_result.current_house_activation.house_activations)} houses')
print(f'Domain Analysis: {len(full_result.current_domain_analysis.domains)} domains')
print(f'\nSummary:')
print(f'  Overall Life Quality: {full_result.summary["overall_life_quality"]:.1f}')
print(f'  Strongest: {full_result.summary["strongest_domain"]} ({full_result.summary["strongest_domain_score"]:.1f})')
print(f'  Weakest: {full_result.summary["weakest_domain"]} ({full_result.summary["weakest_domain_score"]:.1f})')

print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)

