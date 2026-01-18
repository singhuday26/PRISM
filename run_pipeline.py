"""Script to run the full PRISM pipeline: risk → alerts → forecasts."""
import sys
from backend.services.risk import compute_risk_scores
from backend.services.alerts import generate_alerts
from backend.services.forecasting import generate_forecasts
from backend.db import get_db

def run_pipeline(target_date: str = "2021-01-01", horizon: int = 7, disease: str = None, granularity: str = "monthly"):
    """
    Run the complete pipeline.
    
    Args:
        target_date: Date to run pipeline for (ISO format)
        horizon: Forecast horizon in days
        disease: Disease filter (optional)
        granularity: Data granularity for forecasting ('yearly', 'monthly', 'weekly')
    """
    print("=" * 60)
    print("🚀 PRISM PIPELINE EXECUTION")
    if disease:
        print(f"   Disease Filter: {disease}")
    print(f"   Forecast Granularity: {granularity}")
    print("=" * 60)
    
    db = get_db()
    
    # Step 1: Compute Risk Scores
    disease_info = f" for disease: {disease}" if disease else ""
    print(f"\n📊 Step 1/3: Computing Risk Scores for {target_date}{disease_info}...")
    try:
        computed_date, scores = compute_risk_scores(target_date, disease)
        print(f"   ✓ Created {len(scores)} risk scores for {computed_date}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Generate Alerts
    print(f"\n🚨 Step 2/3: Generating Alerts for {target_date}{disease_info}...")
    try:
        alerts = generate_alerts(target_date, disease)
        print(f"   ✓ Created {len(alerts)} alerts")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Generate Forecasts
    print(f"\n📈 Step 3/3: Generating Forecasts (horizon={horizon} days, granularity={granularity}){disease_info}...")
    try:
        forecast_date, forecasts = generate_forecasts(target_date, horizon, disease, granularity)
        print(f"   ✓ Created {len(forecasts)} forecasts for {forecast_date} using {granularity} data")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Verify results
    print(f"\n✅ Pipeline Complete! Verifying...")
    risk_count = db.risk_scores.count_documents({})
    alert_count = db.alerts.count_documents({})
    forecast_count = db.forecasts_daily.count_documents({})
    
    print(f"   Risk Scores: {risk_count}")
    print(f"   Alerts: {alert_count}")
    print(f"   Forecasts: {forecast_count}")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "2021-01-01"
    horizon = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    disease = sys.argv[3] if len(sys.argv) > 3 else None
    granularity = sys.argv[4] if len(sys.argv) > 4 else "monthly"
    
    success = run_pipeline(target, horizon, disease, granularity)
    sys.exit(0 if success else 1)
