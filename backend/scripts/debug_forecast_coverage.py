
import sys
from backend.db import get_db
from backend.disease_config import get_disease_registry

def check_coverage():
    db = get_db()
    registry = get_disease_registry()
    diseases = registry.list_diseases()
    regions = list(db["regions"].find({}, {"region_id": 1}))
    
    print(f"Checking coverage for {len(diseases)} diseases and {len(regions)} regions...")
    
    missing = []
    for disease in diseases:
        for region in regions:
            rid = region["region_id"]
            count = db["forecasts_daily"].count_documents({"region_id": rid, "disease": disease})
            if count == 0:
                missing.append((disease, rid))
    
    print(f"\nFound {len(missing)} combinations missing forecasts out of {len(diseases) * len(regions)}")
    
    if missing:
        print("\nAttempting manual forecast generation for first missing combination...")
        d, r = missing[0]
        from backend.services.arima_forecasting import generate_arima_forecast
        try:
            results = generate_arima_forecast(region_id=r, disease=d, granularity="daily", horizon=7)
            print(f"  Manual generation result: {len(results)} records")
        except Exception as e:
            print(f"  Manual generation FAILED: {e}")
            import traceback
            traceback.print_exc()
            
    return missing

if __name__ == "__main__":
    check_coverage()
