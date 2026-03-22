"""
Test script to verify Streamlit integration with pipeline endpoint.
"""
import requests
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_pipeline_integration():
    """Test that the pipeline endpoint works for Streamlit integration."""
    
    print("=" * 60)
    print("Testing Streamlit Pipeline Integration")
    print("=" * 60)
    
    # Test parameters
    chart_id = "04ecf146-d0e1-4e72-8c30-fb8bba03e2e5"
    calculation_datetime = datetime(2026, 3, 22, 12, 0, 0)
    start_date = datetime(2026, 3, 1, 0, 0, 0)
    end_date = datetime(2026, 3, 31, 23, 59, 59)
    
    print(f"\nTest Parameters:")
    print(f"  Chart ID: {chart_id}")
    print(f"  Calculation Date: {calculation_datetime}")
    print(f"  Timeline: {start_date.date()} to {end_date.date()}")
    
    # Call unified pipeline endpoint
    print(f"\n🔄 Calling unified pipeline endpoint...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/analyze/full",
            json={
                "chart_id": chart_id,
                "calculation_date": calculation_datetime.isoformat(),
                "include_timeline": True,
                "timeline_start_date": start_date.isoformat(),
                "timeline_end_date": end_date.isoformat(),
                "include_subdomains": True
            },
            timeout=120
        )
        response.raise_for_status()
        pipeline_data = response.json()
        
        print(f"✅ Pipeline response received!")
        
        # Verify structure
        print(f"\n📊 Response Structure:")
        print(f"  - Chart ID: {pipeline_data.get('chart_id')}")
        print(f"  - Calculation Date: {pipeline_data.get('calculation_date')}")
        print(f"  - Generated At: {pipeline_data.get('generated_at')}")
        
        # Check current state
        print(f"\n🌟 Current State:")
        planet_scores = pipeline_data.get('current_planet_scores', {})
        print(f"  - Planet Scores: {len(planet_scores.get('scores', {}))} planets")
        
        house_activation = pipeline_data.get('current_house_activation', {})
        print(f"  - House Activation: {len(house_activation.get('house_activations', {}))} houses")
        
        domain_analysis = pipeline_data.get('current_domain_analysis', {})
        print(f"  - Domain Analysis: {len(domain_analysis.get('domains', {}))} domains")
        print(f"  - Overall Life Quality: {domain_analysis.get('overall_life_quality', 0):.1f}/100")
        
        # Check summary
        summary = pipeline_data.get('summary', {})
        if summary:
            print(f"\n💡 Summary:")
            print(f"  - Overall Life Quality: {summary.get('overall_life_quality', 0):.1f}")
            print(f"  - Strongest Domain: {summary.get('strongest_domain')} ({summary.get('strongest_domain_score', 0):.1f})")
            print(f"  - Weakest Domain: {summary.get('weakest_domain')} ({summary.get('weakest_domain_score', 0):.1f})")
            
            insights = summary.get('key_insights', [])
            if insights:
                print(f"\n  Top Insights:")
                for i, insight in enumerate(insights[:3], 1):
                    print(f"    {i}. {insight}")
        
        # Check timeline
        timeline = pipeline_data.get('timeline_analysis')
        if timeline:
            print(f"\n📈 Timeline Analysis:")
            timeline_points = timeline.get('timeline', [])
            print(f"  - Timeline Points: {len(timeline_points)}")
            if timeline_points:
                print(f"  - First Point: {timeline_points[0].get('date')}")
                print(f"  - Last Point: {timeline_points[-1].get('date')}")
        
        # Simulate Streamlit data extraction
        print(f"\n🎨 Simulating Streamlit Data Extraction:")
        
        scoring_data = {
            "chart_id": pipeline_data["chart_id"],
            "planet_scores": pipeline_data["current_planet_scores"]
        }
        print(f"  ✅ Scoring data extracted")
        
        house_data = {
            "chart_id": pipeline_data["chart_id"],
            "house_activation": pipeline_data["current_house_activation"]
        }
        print(f"  ✅ House data extracted")
        
        domain_data = {
            "chart_id": pipeline_data["chart_id"],
            "domain_analysis": {
                "overall_life_quality": pipeline_data["current_domain_analysis"]["overall_life_quality"],
                "strongest_domain": pipeline_data["current_domain_analysis"]["strongest_domain"],
                "weakest_domain": pipeline_data["current_domain_analysis"]["weakest_domain"],
                "domains": pipeline_data["current_domain_analysis"]["domains"]
            }
        }
        print(f"  ✅ Domain data extracted")
        
        print(f"\n" + "=" * 60)
        print(f"✅ STREAMLIT INTEGRATION TEST PASSED!")
        print(f"=" * 60)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {str(e)}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pipeline_integration()
    exit(0 if success else 1)

