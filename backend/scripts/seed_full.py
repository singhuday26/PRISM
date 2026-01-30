import os
import sys
import random
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://prism_user:prism240818@cluster0.kesugwh.mongodb.net/?appName=Cluster0")
DB_NAME = "prism_db"

REGIONS = [
    {"region_id": "IN-MH", "region_name": "Maharashtra", "population": 112374333, "lat": 19.7515, "lon": 75.7139},
    {"region_id": "IN-DL", "region_name": "Delhi", "population": 16787941, "lat": 28.7041, "lon": 77.1025},
    {"region_id": "IN-KA", "region_name": "Karnataka", "population": 61095297, "lat": 15.3173, "lon": 75.7139},
    {"region_id": "IN-TN", "region_name": "Tamil Nadu", "population": 72147030, "lat": 11.1271, "lon": 78.6569},
    {"region_id": "IN-WB", "region_name": "West Bengal", "population": 91276115, "lat": 22.9868, "lon": 87.8550},
    {"region_id": "IN-UP", "region_name": "Uttar Pradesh", "population": 199812341, "lat": 26.8467, "lon": 80.9462},
    {"region_id": "IN-GJ", "region_name": "Gujarat", "population": 60439692, "lat": 22.2587, "lon": 71.1924},
    {"region_id": "IN-RJ", "region_name": "Rajasthan", "population": 68548437, "lat": 27.0238, "lon": 74.2179}
]

DISEASES = ["DENGUE", "MALARIA", "CHIKUNGUNYA"]

def generate_curve(x, amplitude, frequency, phase, noise_level):
    return amplitude * np.sin(frequency * x + phase) + amplitude + np.random.normal(0, noise_level, len(x))

def run_seed():
    logger.info(f"Connecting to MongoDB: {MONGO_URI.split('@')[-1]}") # Hide credentials
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    logger.info("Dropping existing collections...")
    db.regions.drop()
    db.cases_daily.drop()
    db.alerts.drop()
    db.forecasts_daily.drop()
    db.resources_daily.drop()
    db.reports.drop()
    db.risk_scores.drop()
    
    # 1. Regions
    logger.info("Seeding Regions...")
    try:
        db.regions.insert_many(REGIONS)
    except Exception as e:
        logger.warning(f"Error seeding regions (might exist): {e}")
    
    # 2. Historical Data (90 days back to today)
    today = datetime.now()
    start_date = today - timedelta(days=90)
    
    all_cases = []
    all_risk = []
    all_alerts = []
    all_resources = []
    
    logger.info("Generating Historical Data (Cases, Risk, Alerts, Resources)...")
    
    for r in REGIONS:
        for d in DISEASES:
            # Generate cases curve
            days = np.arange(90)
            
            # Randomize curve params per region/disease for variety
            amp = random.randint(50, 500)
            freq = random.uniform(0.05, 0.15)
            phase = random.uniform(0, np.pi)
            noise = amp * 0.1
            
            cases_curve = generate_curve(days, amp, freq, phase, noise)
            cases_curve = np.maximum(cases_curve, 0).astype(int) # Verify non-negative
            
            for i, count in enumerate(cases_curve):
                date = start_date + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                # Cases
                all_cases.append({
                    "region_id": r["region_id"],
                    "date": date_str,
                    "disease": d,
                    "confirmed": int(count),
                    "deaths": int(count * random.uniform(0.001, 0.05)),
                    "recovered": int(count * random.uniform(0.8, 0.95))
                })
                
                # Risk Score (Normalized 0-1 based on simplified logic)
                # Cap roughly at 2*amp
                risk_score_val = min(float(count) / (amp * 2), 1.0)
                risk_score = float(risk_score_val)
                all_risk.append({
                    "region_id": r["region_id"],
                    "date": date_str,
                    "disease": d,
                    "risk_score": risk_score,
                    "risk_level": "CRITICAL" if risk_score > 0.7 else "HIGH" if risk_score > 0.5 else "MEDIUM" if risk_score > 0.3 else "LOW"
                })
                
                # Alerts (only for High/Critical)
                if risk_score > 0.5:
                    all_alerts.append({
                        "region_id": r["region_id"],
                        "date": date_str,
                        "disease": d,
                        "risk_score": risk_score,
                        "risk_level": "CRITICAL" if risk_score > 0.7 else "HIGH",
                        "message": f"{'Critical' if risk_score > 0.7 else 'High'} {d} outbreak risk detected in {r['region_name']}"
                    })
                
                # Resources
                if i == 89: # Only generate latest resource prediction for simplicity/current widget
                    all_resources.append({
                        "region_id": r["region_id"],
                        "date": date_str,
                        "disease": d,
                        "forecasted_cases": int(count * 1.1), # Assuming growth
                        "resources_needed": {
                            "general_beds": int(count * 0.2),
                            "icu_beds": int(count * 0.05),
                            "nurses": int(count * 0.1),
                            "oxygen_cylinders": int(count * 0.08)
                        },
                        "shortage_risk": bool(risk_score > 0.6)
                    })

    logger.info("Inserting Historical Data...")
    try:
        if all_cases: 
            # Use chunks if too large? 2000 is small.
            db.cases_daily.insert_many(all_cases).inserted_ids
        logger.info(f"Cases inserted: {len(all_cases)}")
    except Exception as e:
        logger.error(f"Error inserting cases: {e}")

    try:
        if all_risk: db.risk_scores.insert_many(all_risk)
        logger.info(f"Risk scores inserted: {len(all_risk)}")
    except Exception as e:
        logger.error(f"Error inserting risk scores: {e}")

    try:
        if all_alerts: db.alerts.insert_many(all_alerts)
        logger.info(f"Alerts inserted: {len(all_alerts)}")
    except Exception as e:
        logger.error(f"Error inserting alerts: {e}")
        
    try:
        if all_resources: db.resources_daily.insert_many(all_resources) 
        logger.info(f"Resources inserted: {len(all_resources)}")
    except Exception as e:
         logger.error(f"Error inserting resources: {e}")

    # 3. Forecasts
    logger.info("Generatng Forecasts...")
    forecast_generated_at = today.strftime("%Y-%m-%dT%H:%M:%S")
    past_forecast_generated_at = (today - timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%S")
    
    all_forecasts = []
    
    for r in REGIONS:
        for d in DISEASES:
            # A) Future Forecasts (Next 14 days from today)
            # Find the value at 'today' (approx 90th day in simulation)
            last_val_simulation = 100 # simplified, better if we tracked it in the loop above
            # For consistent charts, let's just assume a value
            
            # B) Historical Forecasts (Last 14 days, generated 14 days ago)
            # This allows "Evaluation" to compare these predictions against the "Actuals" we just inserted.
            # We want them to be slightly DIFFERENT from actuals to show non-zero MAE.
            
            # Reconstruct the curve segment for t=76 to t=90 (approx)
            # Actually easier: just take the actuals we generated and add noise.
            
            # Find actuals for this region/disease
            actuals_map = {x['date']: x['confirmed'] for x in all_cases if x['region_id'] == r['region_id'] and x['disease'] == d}
            
            # 1. Historical Forecasts (Targeting dates: today-14 to today-1)
            for i in range(1, 15):
                past_date = today - timedelta(days=i)
                past_date_str = past_date.strftime("%Y-%m-%d")
                
                if past_date_str in actuals_map:
                    actual_val = actuals_map[past_date_str]
                    # Prediction with some error
                    pred_val = int(actual_val * random.uniform(0.8, 1.2))
                    
                    all_forecasts.append({
                        "region_id": r["region_id"],
                        "disease": d,
                        "date": past_date_str,
                        "cases": pred_val,
                        "lower_bound": int(pred_val * 0.8),
                        "upper_bound": int(pred_val * 1.2),
                        "generated_at": past_forecast_generated_at, # Generated in the past
                        "granularity": "daily"
                    })

            # 2. Future Forecasts (Targeting dates: today to today+13)
            # Base off today's actual
            today_str = today.strftime("%Y-%m-%d")
            base_val = actuals_map.get(today_str, 100)
            
            for i in range(14):
                f_date = today + timedelta(days=i)
                f_date_str = f_date.strftime("%Y-%m-%d")
                
                # Simple projection
                val = int(base_val * (1 + (random.random()-0.4)*0.1*i)) # Slight drift
                val = max(0, val)
                
                all_forecasts.append({
                    "region_id": r["region_id"],
                    "disease": d,
                    "date": f_date_str,
                    "cases": val,
                    "lower_bound": int(val * 0.8),
                    "upper_bound": int(val * 1.2),
                    "generated_at": forecast_generated_at,
                    "granularity": "daily"
                })
                
    try:
        if all_forecasts: db.forecasts_daily.insert_many(all_forecasts)
        logger.info("Forecasts inserted.")
    except Exception as e:
        logger.error(f"Error inserting forecasts: {e}")

    # 4. Reports
    logger.info("Seeding Reports...")
    reports = [
        {
            "report_id": f"rep_{random.randint(1000,9999)}",
            "type": "weekly_summary",
            "status": "ready",
            "disease": "DENGUE",
            "generated_at": today - timedelta(days=1),
            "file_path": "/tmp/dummy.pdf" 
        },
        {
            "report_id": f"rep_{random.randint(1000,9999)}",
            "type": "disease_overview",
            "status": "processing",
            "disease": "MALARIA",
            "generated_at": today,
            "file_path": None
        }
    ]
    try:
        db.reports.insert_many(reports)
        logger.info("Reports inserted.")
    except Exception as e:
        logger.error(f"Error inserting reports: {e}")
    
    logger.info("✅ Seeding Complete!")
    logger.info(f"Regions: {db.regions.count_documents({})}")
    logger.info(f"Cases: {db.cases_daily.count_documents({})}")
    logger.info(f"Alerts: {db.alerts.count_documents({})}")
    logger.info(f"Forecasts: {db.forecasts_daily.count_documents({})}")

if __name__ == "__main__":
    run_seed()
