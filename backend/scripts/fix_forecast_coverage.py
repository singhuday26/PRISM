
import os
import sys
import logging
import time
from backend.disease_config import get_disease_registry
from backend.services.risk import compute_risk_scores
from backend.services.alerts import generate_alerts
from backend.services.arima_forecasting import generate_arima_forecasts

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def run_fix():
    registry = get_disease_registry()
    diseases = registry.list_diseases()
    
    print(f"🚀 Starting Pipeline Fix for {len(diseases)} diseases...")
    
    for disease in diseases:
        print(f"\nProcessing {disease}...")
        try:
            # 1. Risk
            risk_date, _ = compute_risk_scores(disease=disease)
            print(f"  ✓ Risk Scores computed for {risk_date}")
            
            # 2. Alerts
            _, alerts = generate_alerts(disease=disease)
            print(f"  ✓ Alerts generated: {len(alerts)}")
            
            # 3. Forecasts (using daily granularity and the new fallback)
            _, forecasts = generate_arima_forecasts(disease=disease, granularity="daily", horizon=7)
            print(f"  ✓ ARIMA Forecasts generated: {len(forecasts)}")
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")

if __name__ == "__main__":
    run_fix()
