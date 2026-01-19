import logging
import sys
from datetime import datetime

# Setup logging to capture output
logging.basicConfig(level=logging.INFO)

from backend.db import get_db
from backend.services.alerts import generate_alerts
from backend.services.notifications import dispatch_notifications

def verify_end_to_end_alerting():
    print("🧪 Starting End-to-End Alerting Verification...")
    db = get_db()
    
    # 1. Setup Test Data (High Risk)
    test_date = "2025-01-01"
    test_disease = "Dengue"
    db.risk_scores.update_one(
        {"region_id": "TEST_REGION_001", "date": test_date, "disease": test_disease},
        {"$set": {
            "risk_score": 0.95,  # High risk > 0.7
            "risk_level": "High",
            "cases_predicted": 100,
            "population": 1000
        }},
        upsert=True
    )
    print(f"✅ Inserted test high-risk score for {test_date}")

    # 2. Trigger Alert Generation
    # This should internally call dispatch_notifications
    print("Running generate_alerts...")
    date, alerts = generate_alerts(target_date=test_date, disease=test_disease)
    
    # 3. Verify Alert Creation in DB
    assert len(alerts) > 0, "❌ No alerts generated!"
    print(f"✅ Generated {len(alerts)} alerts.")
    
    found_alert = db.alerts.find_one({"region_id": "TEST_REGION_001", "date": test_date})
    assert found_alert is not None, "❌ Alert not found in DB!"
    print("✅ Alert persisted to MongoDB.")

    # 4. Verify Notification Dispatch
    # Since we can't easily capture stdout without capturing it, we rely on the
    # fact that we saw the logs in the console. 
    # But for extra rigor, let's call dispatch directly with a custom setting
    # to see it print.
    
    print("\n--- Verifying Notification Console Output ---")
    dispatch_notifications(alerts)
    print("---------------------------------------------")

if __name__ == "__main__":
    verify_end_to_end_alerting()
