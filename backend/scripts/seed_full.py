"""
PRISM Full Database Seeder
==========================
Seeds MongoDB with epidemiologically realistic disease surveillance data
for Indian states. Uses known seasonal patterns for vector-borne diseases
(dengue, malaria, chikungunya) calibrated to published NVBDCP case counts.

Usage:
    python -m backend.scripts.seed_full
    python backend/scripts/seed_full.py
"""

import os
import sys
import random
import logging
import math
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Config
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://prism_user:prism240818@cluster0.kesugwh.mongodb.net/?appName=Cluster0"
)
DB_NAME = os.getenv("DB_NAME", "prism_db")

# ──────────────────────────────────────────────────────────────────────────────
# Region definitions (ISO 3166-2:IN)
# ──────────────────────────────────────────────────────────────────────────────
REGIONS = [
    {"region_id": "IN-MH", "region_name": "Maharashtra",   "population": 112374333, "lat": 19.7515, "lon": 75.7139},
    {"region_id": "IN-DL", "region_name": "Delhi",          "population": 16787941,  "lat": 28.7041, "lon": 77.1025},
    {"region_id": "IN-KA", "region_name": "Karnataka",      "population": 61095297,  "lat": 15.3173, "lon": 75.7139},
    {"region_id": "IN-TN", "region_name": "Tamil Nadu",     "population": 72147030,  "lat": 11.1271, "lon": 78.6569},
    {"region_id": "IN-WB", "region_name": "West Bengal",    "population": 91276115,  "lat": 22.9868, "lon": 87.8550},
    {"region_id": "IN-UP", "region_name": "Uttar Pradesh",  "population": 199812341, "lat": 26.8467, "lon": 80.9462},
    {"region_id": "IN-GJ", "region_name": "Gujarat",        "population": 60439692,  "lat": 22.2587, "lon": 71.1924},
    {"region_id": "IN-RJ", "region_name": "Rajasthan",      "population": 68548437,  "lat": 27.0238, "lon": 74.2179},
    {"region_id": "IN-KL", "region_name": "Kerala",         "population": 33406061,  "lat": 10.8505, "lon": 76.2711},
    {"region_id": "IN-AP", "region_name": "Andhra Pradesh",  "population": 49577103,  "lat": 15.9129, "lon": 79.7400},
]

DISEASES = ["DENGUE", "MALARIA", "CHIKUNGUNYA"]

# ──────────────────────────────────────────────────────────────────────────────
# Epidemiological seasonal profiles
# Monthly multipliers based on Indian disease patterns (NVBDCP data)
# Index 0 = January, 11 = December. Values are relative multipliers.
# ──────────────────────────────────────────────────────────────────────────────

# Dengue: peaks July–November, driven by post-monsoon Aedes mosquitoes
DENGUE_MONTHLY = [0.08, 0.05, 0.06, 0.08, 0.12, 0.25, 0.55, 0.80, 1.00, 0.90, 0.60, 0.20]

# Malaria: peaks June–September during monsoon (Anopheles breeding)
MALARIA_MONTHLY = [0.10, 0.08, 0.10, 0.15, 0.25, 0.60, 0.90, 1.00, 0.85, 0.50, 0.25, 0.12]

# Chikungunya: mirrors dengue pattern but lower overall
CHIKUNGUNYA_MONTHLY = [0.05, 0.04, 0.05, 0.07, 0.10, 0.20, 0.45, 0.70, 0.85, 1.00, 0.55, 0.15]

DISEASE_SEASONALITY = {
    "DENGUE": DENGUE_MONTHLY,
    "MALARIA": MALARIA_MONTHLY,
    "CHIKUNGUNYA": CHIKUNGUNYA_MONTHLY,
}

# Region-disease baseline (avg monthly cases at multiplier=1.0)
# Based on approximate NVBDCP/IDSP annual figures divided by peak months
REGION_BASELINES = {
    # High-burden states for dengue
    "IN-MH": {"DENGUE": 3200, "MALARIA": 800,  "CHIKUNGUNYA": 450},
    "IN-DL": {"DENGUE": 2800, "MALARIA": 200,  "CHIKUNGUNYA": 350},
    "IN-KA": {"DENGUE": 2500, "MALARIA": 600,  "CHIKUNGUNYA": 400},
    "IN-TN": {"DENGUE": 2200, "MALARIA": 300,  "CHIKUNGUNYA": 380},
    "IN-WB": {"DENGUE": 1800, "MALARIA": 1200, "CHIKUNGUNYA": 250},
    "IN-UP": {"DENGUE": 1500, "MALARIA": 900,  "CHIKUNGUNYA": 200},
    "IN-GJ": {"DENGUE": 1200, "MALARIA": 500,  "CHIKUNGUNYA": 180},
    "IN-RJ": {"DENGUE": 1000, "MALARIA": 1500, "CHIKUNGUNYA": 150},
    "IN-KL": {"DENGUE": 2000, "MALARIA": 150,  "CHIKUNGUNYA": 500},
    "IN-AP": {"DENGUE": 1600, "MALARIA": 400,  "CHIKUNGUNYA": 300},
}

# Case fatality rates by disease (approximate)
CFR = {
    "DENGUE": 0.005,       # ~0.5%
    "MALARIA": 0.003,      # ~0.3%
    "CHIKUNGUNYA": 0.001,  # ~0.1%
}

# Recovery rate
RECOVERY_RATE = {
    "DENGUE": 0.92,
    "MALARIA": 0.95,
    "CHIKUNGUNYA": 0.97,
}

# ──────────────────────────────────────────────────────────────────────────────
# Disease configuration (resource planning parameters)
# ──────────────────────────────────────────────────────────────────────────────
DISEASE_CONFIGS = [
    {
        "_id": "dengue",
        "name": "DENGUE",
        "resource_params": {
            "hospitalization_rate": 0.20,    # 20% of cases need hospitalization
            "icu_rate": 0.03,                # 3% need ICU (dengue hemorrhagic)
            "avg_stay_days": 5,
            "nurse_ratio": 0.15,             # 1 nurse per ~7 hospitalized patients
            "oxygen_rate": 0.05,             # 5% need oxygen support
        }
    },
    {
        "_id": "malaria",
        "name": "MALARIA",
        "resource_params": {
            "hospitalization_rate": 0.15,    # 15% hospitalization
            "icu_rate": 0.02,                # 2% severe/cerebral malaria
            "avg_stay_days": 4,
            "nurse_ratio": 0.12,
            "oxygen_rate": 0.08,
        }
    },
    {
        "_id": "chikungunya",
        "name": "CHIKUNGUNYA",
        "resource_params": {
            "hospitalization_rate": 0.10,    # 10% hospitalization
            "icu_rate": 0.005,               # 0.5% ICU (rare complications)
            "avg_stay_days": 3,
            "nurse_ratio": 0.10,
            "oxygen_rate": 0.02,
        }
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Realistic news articles (Indian health context)
# ──────────────────────────────────────────────────────────────────────────────
def get_news_articles(today):
    """Generate realistic health news articles."""
    return [
        {
            "title": "Mumbai reports 45% spike in dengue cases as monsoon lingers",
            "source": "NVBDCP Weekly Bulletin",
            "published_at": today - timedelta(days=1),
            "url": "https://nvbdcp.gov.in/WriteReadData/dengue-weekly-report.pdf",
            "content": (
                "The National Vector Borne Disease Control Programme reports a significant uptick in "
                "dengue cases across the Mumbai Metropolitan Region. The BMC has recorded 2,847 confirmed "
                "cases in the last 30 days, a 45% increase over the corresponding period last year. "
                "Health officials attribute the surge to extended monsoon rainfall and stagnant water "
                "accumulation in suburban areas. Anti-larval spraying operations have been intensified."
            ),
            "extracted_diseases": ["DENGUE"],
            "extracted_locations": ["Mumbai", "Maharashtra"],
            "relevance_score": 0.92,
            "ingested_at": today,
        },
        {
            "title": "Rajasthan declares malaria alert in 12 districts after flood recedes",
            "source": "India IDSP Alert",
            "published_at": today - timedelta(days=2),
            "url": "https://idsp.nic.in/showfile.php?lid=4345",
            "content": (
                "Rajasthan's Directorate of Medical & Health Services has issued a malaria alert for "
                "12 districts following severe flooding. Post-flood stagnant water pools have created "
                "ideal breeding grounds for Anopheles mosquitoes. Over 1,500 positive smears were reported "
                "from Jodhpur, Barmer, and Jaisalmer districts in the past week alone. Rapid diagnostic "
                "kits and ACT supplies are being dispatched to affected PHCs."
            ),
            "extracted_diseases": ["MALARIA"],
            "extracted_locations": ["Rajasthan", "Jodhpur", "Barmer"],
            "relevance_score": 0.88,
            "ingested_at": today,
        },
        {
            "title": "WHO warns of chikungunya resurgence in South India amid climate anomalies",
            "source": "WHO South-East Asia Region",
            "published_at": today - timedelta(days=3),
            "url": "https://www.who.int/india/news/detail/chikungunya-advisory-2025",
            "content": (
                "The World Health Organization's Regional Office for South-East Asia has issued an "
                "advisory on elevated chikungunya transmission risk in Karnataka, Kerala, and Tamil Nadu. "
                "Above-normal temperatures combined with intermittent rainfall are driving Aedes aegypti "
                "proliferation. Seroprevalence surveys indicate low herd immunity in rural populations. "
                "State health departments are urged to activate integrated vector management protocols."
            ),
            "extracted_diseases": ["CHIKUNGUNYA", "DENGUE"],
            "extracted_locations": ["Karnataka", "Kerala", "Tamil Nadu"],
            "relevance_score": 0.85,
            "ingested_at": today,
        },
        {
            "title": "Delhi hospitals brace for post-monsoon dengue wave; beds filling up",
            "source": "Municipal Corporation of Delhi",
            "published_at": today - timedelta(days=4),
            "url": "https://health.delhi.gov.in/dengue-status-report",
            "content": (
                "Major hospitals across Delhi-NCR report a 60% occupancy surge in dengue wards over the "
                "past two weeks. The MCD has deployed 450 additional fogging machines across all zones. "
                "AIIMS and Safdarjung Hospital report daily admissions of 80-120 suspected dengue patients, "
                "with NS1 antigen positivity rate reaching 38%. Blood banks are on high alert for platelet "
                "demand."
            ),
            "extracted_diseases": ["DENGUE"],
            "extracted_locations": ["Delhi", "AIIMS"],
            "relevance_score": 0.90,
            "ingested_at": today,
        },
        {
            "title": "West Bengal reports concurrent dengue-malaria co-infections in flood-hit areas",
            "source": "State Health Department Bulletin",
            "published_at": today - timedelta(days=5),
            "url": "https://wbhealth.gov.in/surveillance-weekly-report",
            "content": (
                "Epidemiologists in West Bengal have flagged an unusual pattern of concurrent dengue and "
                "malaria co-infections in districts affected by recent Ganga basin flooding. At least 127 "
                "patients tested positive for both pathogens across Murshidabad, Nadia, and North 24 Parganas. "
                "Co-infections complicate treatment and increase ICU admission rates. The state has requested "
                "additional bivalent rapid diagnostic kits from the NVBDCP central store."
            ),
            "extracted_diseases": ["DENGUE", "MALARIA"],
            "extracted_locations": ["West Bengal", "Murshidabad", "Nadia"],
            "relevance_score": 0.87,
            "ingested_at": today,
        },
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Case data generation
# ──────────────────────────────────────────────────────────────────────────────

def generate_monthly_cases(region_id, disease, num_months=36):
    """
    Generate monthly case counts with realistic seasonal patterns.
    
    Uses the disease-specific monthly multiplier profile scaled by the
    region baseline, with calibrated noise (Poisson-like variance).
    
    Args:
        region_id: Region identifier
        disease: Disease name
        num_months: How many months of history to generate (default 36 = 3 years)
    
    Returns:
        List of (date_str, confirmed, deaths, recovered) tuples
    """
    baseline = REGION_BASELINES.get(region_id, {}).get(disease, 100)
    seasonality = DISEASE_SEASONALITY[disease]
    cfr = CFR[disease]
    recovery = RECOVERY_RATE[disease]
    
    today = datetime.now()
    records = []
    
    for m in range(num_months):
        # Work backwards from today
        month_offset = num_months - 1 - m
        target_date = today - timedelta(days=month_offset * 30)
        month_idx = target_date.month - 1  # 0-indexed
        
        # Seasonal multiplier
        multiplier = seasonality[month_idx]
        
        # Inter-annual variation (slight year-over-year trend)
        year_factor = 1.0 + 0.05 * (m / 12)  # 5% annual growth
        
        # Calculate expected cases
        expected = baseline * multiplier * year_factor
        
        # Add realistic noise (Poisson-like: std ≈ sqrt(mean))
        noise = np.random.normal(0, max(1, math.sqrt(expected) * 1.5))
        confirmed = max(0, int(expected + noise))
        
        # Derive deaths and recovered
        deaths = max(0, int(confirmed * cfr * random.uniform(0.5, 1.5)))
        recovered = max(0, int(confirmed * recovery * random.uniform(0.95, 1.0)))
        
        date_str = target_date.strftime("%Y-%m-%d")
        records.append((date_str, confirmed, deaths, recovered))
    
    return records


def generate_weekly_cases(region_id, disease, num_weeks=52):
    """
    Generate weekly case counts from monthly patterns (interpolated).
    
    Weekly data gives finer resolution for ARIMA and risk calculations.
    """
    baseline = REGION_BASELINES.get(region_id, {}).get(disease, 100)
    seasonality = DISEASE_SEASONALITY[disease]
    cfr = CFR[disease]
    recovery = RECOVERY_RATE[disease]
    
    today = datetime.now()
    records = []
    
    for w in range(num_weeks):
        week_offset = num_weeks - 1 - w
        target_date = today - timedelta(weeks=week_offset)
        month_idx = target_date.month - 1
        
        # Interpolate between months for smoother weekly data
        next_month_idx = (month_idx + 1) % 12
        day_of_month = target_date.day
        # Fraction through the month
        frac = day_of_month / 30.0
        multiplier = seasonality[month_idx] * (1 - frac) + seasonality[next_month_idx] * frac
        
        # Weekly baseline is monthly / 4.33
        weekly_baseline = baseline / 4.33
        expected = weekly_baseline * multiplier
        
        # Year-over-year growth
        year_factor = 1.0 + 0.05 * (w / 52)
        expected *= year_factor
        
        # Poisson-like noise
        noise = np.random.normal(0, max(1, math.sqrt(expected)))
        confirmed = max(0, int(expected + noise))
        
        deaths = max(0, int(confirmed * cfr * random.uniform(0.5, 1.5)))
        recovered = max(0, int(confirmed * recovery * random.uniform(0.95, 1.0)))
        
        date_str = target_date.strftime("%Y-%m-%d")
        records.append((date_str, confirmed, deaths, recovered))
    
    return records


# ──────────────────────────────────────────────────────────────────────────────
# Main seed function
# ──────────────────────────────────────────────────────────────────────────────

def run_seed():
    logger.info(f"Connecting to MongoDB: {MONGO_URI.split('@')[-1]}")
    client = MongoClient(
        MONGO_URI,
        connectTimeoutMS=30000,
        serverSelectionTimeoutMS=30000,
        socketTimeoutMS=60000,
    )
    db = client[DB_NAME]
    
    # ── Clean up derived data ──────────────────────────────────────────────
    logger.info("Dropping existing collections...")
    for col_name in ["regions", "cases_daily", "alerts", "forecasts_daily",
                     "resources_daily", "reports", "risk_scores", 
                     "disease_config", "news_articles"]:
        db[col_name].drop()
    
    # ── 1. Regions ─────────────────────────────────────────────────────────
    logger.info(f"Seeding {len(REGIONS)} regions...")
    db.regions.insert_many(REGIONS)
    
    # ── 2. Disease configuration ───────────────────────────────────────────
    logger.info(f"Seeding {len(DISEASE_CONFIGS)} disease configs...")
    for config in DISEASE_CONFIGS:
        db.disease_config.update_one(
            {"_id": config["_id"]},
            {"$set": config},
            upsert=True
        )
    
    # ── 3. Monthly case data (3 years) ─────────────────────────────────────
    logger.info("Generating monthly case data (36 months × 10 regions × 3 diseases)...")
    all_monthly_cases = []
    
    for region in REGIONS:
        rid = region["region_id"]
        for disease in DISEASES:
            monthly_records = generate_monthly_cases(rid, disease, num_months=36)
            for date_str, confirmed, deaths, recovered in monthly_records:
                all_monthly_cases.append({
                    "region_id": rid,
                    "date": date_str,
                    "disease": disease,
                    "confirmed": confirmed,
                    "deaths": deaths,
                    "recovered": recovered,
                    "granularity": "monthly",
                })
    
    logger.info(f"Inserting {len(all_monthly_cases)} monthly case records...")
    if all_monthly_cases:
        db.cases_daily.insert_many(all_monthly_cases)
    
    # ── 4. Weekly case data (52 weeks) ─────────────────────────────────────
    logger.info("Generating weekly case data (52 weeks × 10 regions × 3 diseases)...")
    all_weekly_cases = []
    
    for region in REGIONS:
        rid = region["region_id"]
        for disease in DISEASES:
            weekly_records = generate_weekly_cases(rid, disease, num_weeks=52)
            for date_str, confirmed, deaths, recovered in weekly_records:
                all_weekly_cases.append({
                    "region_id": rid,
                    "date": date_str,
                    "disease": disease,
                    "confirmed": confirmed,
                    "deaths": deaths,
                    "recovered": recovered,
                    "granularity": "weekly",
                })
    
    logger.info(f"Inserting {len(all_weekly_cases)} weekly case records...")
    if all_weekly_cases:
        db.cases_daily.insert_many(all_weekly_cases)
    
    # ── 5. News articles ───────────────────────────────────────────────────
    today = datetime.now()
    articles = get_news_articles(today)
    logger.info(f"Seeding {len(articles)} news articles...")
    for article in articles:
        db.news_articles.update_one(
            {"title": article["title"]},
            {"$set": article},
            upsert=True
        )
    
    # ── 6. Create indexes ──────────────────────────────────────────────────
    logger.info("Creating indexes...")
    db.cases_daily.create_index([("region_id", ASCENDING), ("disease", ASCENDING), ("date", ASCENDING)])
    db.cases_daily.create_index([("disease", ASCENDING), ("date", ASCENDING)])
    db.cases_daily.create_index([("granularity", ASCENDING)])
    db.risk_scores.create_index([("disease", ASCENDING), ("date", ASCENDING)])
    db.alerts.create_index([("disease", ASCENDING), ("date", ASCENDING)])
    db.forecasts_daily.create_index([("region_id", ASCENDING), ("disease", ASCENDING), ("date", ASCENDING)])
    db.news_articles.create_index([("extracted_diseases", ASCENDING)])
    db.news_articles.create_index([("published_at", -1)])
    
    # ── Summary ────────────────────────────────────────────────────────────
    logger.info("✅ Seeding Complete!")
    logger.info(f"  Regions:        {db.regions.count_documents({})}")
    logger.info(f"  Disease Config: {db.disease_config.count_documents({})}")
    logger.info(f"  Cases (monthly):{len(all_monthly_cases)}")
    logger.info(f"  Cases (weekly): {len(all_weekly_cases)}")
    logger.info(f"  Cases (total):  {db.cases_daily.count_documents({})}")
    logger.info(f"  News articles:  {db.news_articles.count_documents({})}")
    logger.info("")
    logger.info("📋 Next steps:")
    logger.info("  1. Start the API:  python start_prism.py")
    logger.info("  2. Run pipeline:   POST /api/pipeline/run?disease=DENGUE&reset=true")
    logger.info("  3. This will compute: risk scores → alerts → ARIMA forecasts")


if __name__ == "__main__":
    run_seed()
