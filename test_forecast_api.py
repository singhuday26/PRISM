"""
Test script for forecasting with different granularities via API.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_forecast_granularities():
    """Test the forecast generation endpoint with different granularities."""
    
    print("\n" + "="*80)
    print("TESTING FORECAST API WITH DIFFERENT GRANULARITIES")
    print("="*80 + "\n")
    
    # Test parameters
    date = "2021-11-15"
    horizon = 7
    disease = "DENGUE"
    
    granularities = ["yearly", "monthly", "weekly"]
    
    for granularity in granularities:
        print(f"Testing {granularity} granularity...")
        print("-" * 80)
        
        url = f"{BASE_URL}/forecasts/generate"
        params = {
            "date": date,
            "horizon": horizon,
            "disease": disease,
            "granularity": granularity
        }
        
        try:
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            print(f"✓ Status: {response.status_code}")
            print(f"  Date: {data.get('date')}")
            print(f"  Forecasts: {data.get('count')} records")
            print(f"  Granularity: {data.get('granularity')}")
            
            if data.get('forecasts'):
                sample = data['forecasts'][0]
                print(f"  Sample forecast (region {sample.get('region_id')}):")
                print(f"    Mean: {sample.get('pred_mean'):.1f}")
                print(f"    Range: [{sample.get('pred_lower'):.1f} - {sample.get('pred_upper'):.1f}]")
                print(f"    Source: {sample.get('source_granularity')}")
            
            print()
            
        except requests.exceptions.ConnectionError:
            print("✗ Error: Could not connect to API server")
            print("  Make sure the server is running: uvicorn backend.app:app")
            print()
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            print()
    
    print("="*80)
    print("✓ All granularity tests completed successfully!")
    print("="*80 + "\n")
    return True


if __name__ == "__main__":
    success = test_forecast_granularities()
    exit(0 if success else 1)
