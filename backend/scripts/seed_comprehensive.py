"""
PRISM Comprehensive Database Seeder (NoSQL Showcase Edition)
=====================================
Generates 100% combinatorial coverage for 29 Indian States and 10 Diseases.
Injects rich NoSQL resources, and a 60-day historical time-series curve for ARIMA forecasting.

Usage:
    python -m backend.scripts.seed_comprehensive
    python backend/scripts/seed_comprehensive.py
"""

import os
import sys
import random
import logging
import math
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://prism_user:prism240818@cluster0.kesugwh.mongodb.net/?appName=Cluster0")
DB_NAME = os.getenv("DB_NAME", "prism_db")

# 1. Exactly 29 Indian States/UTs with realistic populations
REGIONS = [
    {"region_id": "IN-AP", "region_name": "Andhra Pradesh", "population": 49577103, "lat": 15.91, "lon": 79.74},
    {"region_id": "IN-AR", "region_name": "Arunachal Pradesh", "population": 1383727, "lat": 28.22, "lon": 94.73},
    {"region_id": "IN-AS", "region_name": "Assam", "population": 31205576, "lat": 26.20, "lon": 92.94},
    {"region_id": "IN-BR", "region_name": "Bihar", "population": 104099452, "lat": 25.10, "lon": 85.31},
    {"region_id": "IN-CT", "region_name": "Chhattisgarh", "population": 25545198, "lat": 21.27, "lon": 81.87},
    {"region_id": "IN-GA", "region_name": "Goa", "population": 1458545, "lat": 15.30, "lon": 74.12},
    {"region_id": "IN-GJ", "region_name": "Gujarat", "population": 60439692, "lat": 22.26, "lon": 71.19},
    {"region_id": "IN-HR", "region_name": "Haryana", "population": 25351462, "lat": 29.06, "lon": 76.09},
    {"region_id": "IN-HP", "region_name": "Himachal Pradesh", "population": 6864602, "lat": 31.10, "lon": 77.17},
    {"region_id": "IN-JH", "region_name": "Jharkhand", "population": 32988134, "lat": 23.61, "lon": 85.28},
    {"region_id": "IN-KA", "region_name": "Karnataka", "population": 61095297, "lat": 15.32, "lon": 75.71},
    {"region_id": "IN-KL", "region_name": "Kerala", "population": 33406061, "lat": 10.85, "lon": 76.27},
    {"region_id": "IN-MP", "region_name": "Madhya Pradesh", "population": 72626809, "lat": 22.97, "lon": 78.66},
    {"region_id": "IN-MH", "region_name": "Maharashtra", "population": 112374333, "lat": 19.75, "lon": 75.71},
    {"region_id": "IN-MN", "region_name": "Manipur", "population": 2855794, "lat": 24.66, "lon": 93.91},
    {"region_id": "IN-ML", "region_name": "Meghalaya", "population": 2966889, "lat": 25.47, "lon": 91.37},
    {"region_id": "IN-MZ", "region_name": "Mizoram", "population": 1097206, "lat": 23.16, "lon": 92.94},
    {"region_id": "IN-NL", "region_name": "Nagaland", "population": 1978502, "lat": 26.16, "lon": 94.56},
    {"region_id": "IN-OR", "region_name": "Odisha", "population": 41974218, "lat": 20.94, "lon": 84.80},
    {"region_id": "IN-PB", "region_name": "Punjab", "population": 27743338, "lat": 31.15, "lon": 75.34},
    {"region_id": "IN-RJ", "region_name": "Rajasthan", "population": 68548437, "lat": 27.02, "lon": 74.22},
    {"region_id": "IN-SK", "region_name": "Sikkim", "population": 610577, "lat": 27.53, "lon": 88.51},
    {"region_id": "IN-TN", "region_name": "Tamil Nadu", "population": 72147030, "lat": 11.13, "lon": 78.66},
    {"region_id": "IN-TG", "region_name": "Telangana", "population": 35003674, "lat": 18.11, "lon": 79.02},
    {"region_id": "IN-TR", "region_name": "Tripura", "population": 3673917, "lat": 23.94, "lon": 91.99},
    {"region_id": "IN-UP", "region_name": "Uttar Pradesh", "population": 199812341, "lat": 26.85, "lon": 80.95},
    {"region_id": "IN-UT", "region_name": "Uttarakhand", "population": 10086292, "lat": 30.07, "lon": 79.02},
    {"region_id": "IN-WB", "region_name": "West Bengal", "population": 91276115, "lat": 22.99, "lon": 87.86},
    {"region_id": "IN-DL", "region_name": "Delhi", "population": 16787941, "lat": 28.70, "lon": 77.10},
]

# 2. Exactly 10 distinct diseases
DISEASES = [
    {"name": "DENGUE", "base_R0": 2.5, "severity": "Medium", "fatality_rate": 0.005},
    {"name": "COVID", "base_R0": 3.8, "severity": "High", "fatality_rate": 0.015},
    {"name": "MALARIA", "base_R0": 2.1, "severity": "Medium", "fatality_rate": 0.003},
    {"name": "NIPAH", "base_R0": 1.2, "severity": "Critical", "fatality_rate": 0.40},
    {"name": "TYPHOID", "base_R0": 1.8, "severity": "Medium", "fatality_rate": 0.008},
    {"name": "CHOLERA", "base_R0": 2.6, "severity": "High", "fatality_rate": 0.04},
    {"name": "TUBERCULOSIS", "base_R0": 1.5, "severity": "High", "fatality_rate": 0.10},
    {"name": "CHIKUNGUNYA", "base_R0": 1.9, "severity": "Medium", "fatality_rate": 0.001},
    {"name": "ZIKA", "base_R0": 1.4, "severity": "Medium", "fatality_rate": 0.002},
    {"name": "INFLUENZA", "base_R0": 2.2, "severity": "High", "fatality_rate": 0.01}, # Handled as H1N1 conceptually
]

def generate_daily_cases(region, disease, num_days=60):
    """
    Generate realistic timeseries: baseline + trend + noise (+/- 15%)
    """
    records = []
    base_cases = max(5, int((region["population"] / 1000000) * disease["base_R0"] * random.uniform(0.5, 2.0)))
    
    today = datetime.now()
    
    # Random walk trend factor to create realistic dynamic curves
    trend_factor = random.choice([1.015, 1.02, 0.985, 0.98])
    current_cases = float(base_cases)
    
    for d in range(num_days):
        day_offset = num_days - 1 - d
        target_date = today - timedelta(days=day_offset)
        date_str = target_date.strftime("%Y-%m-%d")
        
        # Inject randomized daily noise (+/- 15%)
        noise = random.uniform(0.85, 1.15)
        
        # Apply deterministic trend 
        current_cases = current_cases * trend_factor
        
        # Shift the trend randomly to create waves
        if random.random() < 0.1:
            trend_factor = 2.0 - trend_factor + random.uniform(-0.02, 0.02)
        
        confirmed = max(0, int(current_cases * noise))
        deaths = int(confirmed * disease["fatality_rate"] * random.uniform(0.5, 1.5))
        recovered = max(0, confirmed - deaths - random.randint(0, int(confirmed * 0.1)))
        
        records.append({
            "region_id": region["region_id"],
            "disease": disease["name"],
            "date": date_str,
            "confirmed": confirmed,
            "deaths": deaths,
            "recovered": recovered,
            "granularity": "daily"
        })
        
    return records


def generate_nosql_resources(region):
    """
    Generate deeply nested NoSQL documents for regional resources.
    Weighted heavily by the region's population.
    """
    multiplier = max(1, int(region["population"] / 1000000))
    
    icu_total = random.randint(50, 150) * multiplier
    icu_occ = int(icu_total * random.uniform(0.6, 0.95))
    icu_status = "Critical" if (icu_occ/icu_total) > 0.85 else "Warning" if (icu_occ/icu_total) > 0.70 else "Normal"
    
    vent_total = random.randint(15, 40) * multiplier
    vent_occ = int(vent_total * random.uniform(0.4, 0.90))
    vent_status = "Critical" if (vent_occ/vent_total) > 0.85 else "Warning" if (vent_occ/vent_total) > 0.70 else "Normal"
    
    n95_masks = random.randint(1000, 5000) * multiplier
    hazmat_suits = random.randint(200, 1000) * multiplier
    
    return {
        "region_id": region["region_id"],
        "region_name": region["region_name"],
        "population": region["population"],
        "infrastructure": {
            "icu_beds": {
                "total": icu_total,
                "occupied": icu_occ,
                "status": icu_status
            },
            "ventilators": {
                "total": vent_total,
                "occupied": vent_occ,
                "status": vent_status
            }
        },
        "ppe_inventory": {
            "n95_masks": n95_masks,
            "hazmat_suits": hazmat_suits
        },
        "last_updated": datetime.now().isoformat()
    }


def run_seed():
    logger.info(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(
        MONGO_URI,
        connectTimeoutMS=30000,
        serverSelectionTimeoutMS=30000,
        socketTimeoutMS=120000,
    )
    db = client[DB_NAME]
    
    try:
        client.admin.command("ping")
        logger.info("✅ MongoDB connection OK")
    except Exception as e:
        logger.error(f"❌ Cannot connect to MongoDB: {e}")
        sys.exit(1)
        
    # Drop existing data
    logger.info("Dropping existing collections to rebuild NoSQL Showcase dataset...")
    for col in ["regions", "cases_daily", "alerts", "forecasts_daily",
                 "resources_daily", "reports", "risk_scores",
                 "disease_config", "ecosystem"]:
        db[col].drop()
        
    # 1. Seed regions
    logger.info(f"Seeding {len(REGIONS)} regions...")
    db.regions.insert_many(REGIONS)
    
    # 2. Seed diseases config
    db.disease_config.insert_many([
        {
            "_id": d["name"].lower(),
            "name": d["name"],
            "resource_params": {
                "hospitalization_rate": random.uniform(0.1, 0.3), 
                "icu_rate": random.uniform(0.01, 0.1), 
                "avg_stay_days": random.randint(3, 14)
            }
        } for d in DISEASES
    ])

    # 3. Seed combinatorial cases: 10 diseases x 29 regions = 290 combinations
    total_combinations = len(REGIONS) * len(DISEASES)
    logger.info(f"Generating 60 days of historical timeseries for {total_combinations} combinations...")
    
    all_cases = []
    for region in REGIONS:
        for disease in DISEASES:
            cases = generate_daily_cases(region, disease, num_days=60)
            all_cases.extend(cases)
            
    if all_cases:
        db.cases_daily.insert_many(all_cases)
    
    logger.info(f"Inserted {len(all_cases)} daily case records.")
    
    # 4. Seed dynamic nested NoSQL resources
    logger.info("Generating dynamic nested resource data for ALL regions...")
    all_resources = []
    for region in REGIONS:
        resource_doc = generate_nosql_resources(region)
        all_resources.append(resource_doc)
        
    db.resources_daily.insert_many(all_resources)
    logger.info(f"Inserted {len(all_resources)} deeply nested NoSQL region resource documents.")

    # 5. Create indexes
    logger.info("Creating indexes...")
    db.cases_daily.create_index([("region_id", ASCENDING), ("disease", ASCENDING), ("date", ASCENDING)])
    db.cases_daily.create_index([("disease", ASCENDING), ("date", ASCENDING)])
    db.resources_daily.create_index([("region_id", ASCENDING)])
    db.regions.create_index([("region_id", ASCENDING)], unique=True)
    db.forecasts_daily.create_index([("region_id", ASCENDING), ("disease", ASCENDING), ("date", ASCENDING)])
    
    # 6. Optional: Auto-run the pipeline
    logger.info("═══════════════════════════════════════════")
    logger.info("  AUTO-RUNNING PIPELINE FOR ALL DISEASES")
    logger.info("═══════════════════════════════════════════")
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, project_root)
        from backend.services.risk import compute_risk_scores
        from backend.services.alerts import generate_alerts
        from backend.services.arima_forecasting import generate_arima_forecasts
        
        for d in DISEASES:
            disease_name = d["name"]
            logger.info(f"Pipeline: {disease_name}")
            try:
                compute_risk_scores(target_date=None, disease=disease_name)
                generate_alerts(target_date=None, disease=disease_name)
                generate_arima_forecasts(target_date=None, horizon=7, disease=disease_name, granularity="daily")
            except Exception as pipe_e:
                logger.warning(f"Failed to run pipeline for {disease_name}: {pipe_e}")

    except ImportError as e:
        logger.warning(f"Could not import pipeline modules directly: {e}")
        logger.info("You can run the pipeline from the PRISM dashboard UI.")
        
    logger.info("✅ NoSQL Showcase dataset seeding complete.")


if __name__ == "__main__":
    run_seed()
