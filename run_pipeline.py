"""
Script to manually trigger the PRISM pipeline.
Useful for avoiding browser timeouts during long-running ARIMA training.
"""
import requests
import sys
import time

API_URL = "http://localhost:8000"

def run_pipeline(reset: bool = True, disease: str = "DENGUE"):
    print(f"🚀 Triggering PRISM Pipeline (Reset={reset}, Disease={disease})...")
    print("   This may take 2-5 minutes. Please wait.")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/pipeline/run",
            params={
                "reset": reset,
                "disease": disease,
                "horizon": 7,
                "granularity": "monthly"
            },
            timeout=600  # 10 minute timeout
        )
        
        duration = time.time() - start_time
        
        if response.ok:
            data = response.json()
            print(f"\n✅ Pipeline Completed in {duration:.1f}s!")
            print(f"   - Risk Scores: {data['created']['risk_scores']}")
            print(f"   - Alerts:      {data['created']['alerts']}")
            print(f"   - Forecasts:   {data['created']['forecasts']}")
            print("\nRefresh your dashboard to see the results.")
        else:
            print(f"\n❌ Pipeline Failed (HTTP {response.status_code})")
            print(f"   {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to API. Is 'python start_prism.py' running?")
    except requests.exceptions.Timeout:
        print("\n❌ Request timed out (API is still working in background).")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    reset_arg = "--no-reset" not in sys.argv
    disease_arg = "DENGUE"
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        disease_arg = sys.argv[1]
        
    run_pipeline(reset=reset_arg, disease=disease_arg)
