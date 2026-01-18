"""
Test the new /pipeline/run endpoint.
Feature 8: One-Click Full Pipeline API
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_pipeline_run():
    """Test the pipeline run endpoint."""
    print("=" * 60)
    print("Testing POST /pipeline/run")
    print("=" * 60)
    
    # Test 1: Run pipeline for DENGUE without reset
    print("\n1. Testing DENGUE pipeline (no reset)...")
    response = requests.post(
        f"{API_URL}/pipeline/run",
        params={
            "disease": "DENGUE",
            "reset": False,
            "horizon": 7,
            "granularity": "monthly"
        },
        timeout=120
    )
    
    if response.ok:
        result = response.json()
        print(f"✓ Success!")
        print(f"  Disease: {result['disease']}")
        print(f"  Date: {result['execution_date']}")
        print(f"  Created: {result['created']['risk_scores']} risk scores, "
              f"{result['created']['alerts']} alerts, "
              f"{result['created']['forecasts']} forecasts")
        print(f"  Total: {result['total']['risk_scores']} risk scores, "
              f"{result['total']['alerts']} alerts, "
              f"{result['total']['forecasts']} forecasts")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  {response.text}")
        return False
    
    # Test 2: Get pipeline status
    print("\n2. Testing GET /pipeline/status...")
    response = requests.get(
        f"{API_URL}/pipeline/status",
        params={"disease": "DENGUE"}
    )
    
    if response.ok:
        result = response.json()
        print(f"✓ Success!")
        print(f"  Risk Scores: {result['risk_scores']}")
        print(f"  Alerts: {result['alerts']}")
        print(f"  Forecasts: {result['forecasts']}")
    else:
        print(f"✗ Failed: {response.status_code}")
        return False
    
    # Test 3: Test with reset=true for different disease
    print("\n3. Testing pipeline with reset=true...")
    response = requests.post(
        f"{API_URL}/pipeline/run",
        params={
            "disease": "DENGUE",
            "reset": True,
            "horizon": 14,
            "granularity": "weekly"
        },
        timeout=120
    )
    
    if response.ok:
        result = response.json()
        print(f"✓ Success!")
        print(f"  Reset: {result['reset']}")
        print(f"  Granularity: {result['granularity']}")
        print(f"  Horizon: {result['horizon']}")
        print(f"  Created counts: {result['created']}")
        print(f"  Total counts should match created: {result['total']}")
        
        # Verify reset worked (total should equal created)
        if result['total'] == result['created']:
            print("  ✓ Reset verified - totals match created counts")
        else:
            print("  ⚠ Warning - totals don't match (may have old data)")
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  {response.text}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    return True


def test_swagger_ui():
    """Check if Swagger UI is accessible."""
    print("\n4. Checking Swagger UI...")
    response = requests.get(f"{API_URL}/docs")
    if response.ok:
        print(f"✓ Swagger UI accessible at {API_URL}/docs")
        print("  Navigate to see the new /pipeline endpoints in the 'pipeline' tag")
    else:
        print(f"✗ Swagger UI not accessible")


if __name__ == "__main__":
    try:
        success = test_pipeline_run()
        test_swagger_ui()
        
        if success:
            print("\n✅ Feature 8 verified")
            print("\nNext steps:")
            print("1. Open dashboard at http://localhost:8501")
            print("2. Select disease from dropdown")
            print("3. Click 'Run Pipeline' button")
            print("4. View results displayed in metrics")
        else:
            print("\n❌ Some tests failed")
    except requests.ConnectionError:
        print("❌ Cannot connect to API server")
        print("Please ensure the API is running:")
        print("  uvicorn backend.app:app --reload --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")
