"""
PRISM Comprehensive Database Seeder
=====================================
Seeds MongoDB with epidemiologically realistic disease surveillance data
for ALL 28 Indian states and ALL 10 configured diseases.

Generates 90 days of daily case data, disease configs, news articles,
and then runs the full pipeline (risk → alerts → forecasts) for each disease.

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

# ── Setup ──────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "prism_db")

# ── All 28 Indian States + 8 UTs (36 total) with lat/lon & population ─────────
REGIONS = [
    {"region_id": "IN-AP", "region_name": "Andhra Pradesh",       "population": 49577103,  "lat": 15.91,  "lon": 79.74},
    {"region_id": "IN-AR", "region_name": "Arunachal Pradesh",    "population": 1383727,   "lat": 28.22,  "lon": 94.73},
    {"region_id": "IN-AS", "region_name": "Assam",                "population": 31205576,  "lat": 26.20,  "lon": 92.94},
    {"region_id": "IN-BR", "region_name": "Bihar",                "population": 104099452, "lat": 25.10,  "lon": 85.31},
    {"region_id": "IN-CT", "region_name": "Chhattisgarh",         "population": 25545198,  "lat": 21.27,  "lon": 81.87},
    {"region_id": "IN-GA", "region_name": "Goa",                  "population": 1458545,   "lat": 15.30,  "lon": 74.12},
    {"region_id": "IN-GJ", "region_name": "Gujarat",              "population": 60439692,  "lat": 22.26,  "lon": 71.19},
    {"region_id": "IN-HR", "region_name": "Haryana",              "population": 25351462,  "lat": 29.06,  "lon": 76.09},
    {"region_id": "IN-HP", "region_name": "Himachal Pradesh",     "population": 6864602,   "lat": 31.10,  "lon": 77.17},
    {"region_id": "IN-JH", "region_name": "Jharkhand",            "population": 32988134,  "lat": 23.61,  "lon": 85.28},
    {"region_id": "IN-KA", "region_name": "Karnataka",            "population": 61095297,  "lat": 15.32,  "lon": 75.71},
    {"region_id": "IN-KL", "region_name": "Kerala",               "population": 33406061,  "lat": 10.85,  "lon": 76.27},
    {"region_id": "IN-MP", "region_name": "Madhya Pradesh",       "population": 72626809,  "lat": 22.97,  "lon": 78.66},
    {"region_id": "IN-MH", "region_name": "Maharashtra",          "population": 112374333, "lat": 19.75,  "lon": 75.71},
    {"region_id": "IN-MN", "region_name": "Manipur",              "population": 2855794,   "lat": 24.66,  "lon": 93.91},
    {"region_id": "IN-ML", "region_name": "Meghalaya",            "population": 2966889,   "lat": 25.47,  "lon": 91.37},
    {"region_id": "IN-MZ", "region_name": "Mizoram",              "population": 1097206,   "lat": 23.16,  "lon": 92.94},
    {"region_id": "IN-NL", "region_name": "Nagaland",             "population": 1978502,   "lat": 26.16,  "lon": 94.56},
    {"region_id": "IN-OR", "region_name": "Odisha",               "population": 41974218,  "lat": 20.94,  "lon": 84.80},
    {"region_id": "IN-PB", "region_name": "Punjab",               "population": 27743338,  "lat": 31.15,  "lon": 75.34},
    {"region_id": "IN-RJ", "region_name": "Rajasthan",            "population": 68548437,  "lat": 27.02,  "lon": 74.22},
    {"region_id": "IN-SK", "region_name": "Sikkim",               "population": 610577,    "lat": 27.53,  "lon": 88.51},
    {"region_id": "IN-TN", "region_name": "Tamil Nadu",           "population": 72147030,  "lat": 11.13,  "lon": 78.66},
    {"region_id": "IN-TG", "region_name": "Telangana",            "population": 35003674,  "lat": 18.11,  "lon": 79.02},
    {"region_id": "IN-TR", "region_name": "Tripura",              "population": 3673917,   "lat": 23.94,  "lon": 91.99},
    {"region_id": "IN-UP", "region_name": "Uttar Pradesh",        "population": 199812341, "lat": 26.85,  "lon": 80.95},
    {"region_id": "IN-UT", "region_name": "Uttarakhand",          "population": 10086292,  "lat": 30.07,  "lon": 79.02},
    {"region_id": "IN-WB", "region_name": "West Bengal",          "population": 91276115,  "lat": 22.99,  "lon": 87.86},
    # Union Territories
    {"region_id": "IN-DL", "region_name": "Delhi",                "population": 16787941,  "lat": 28.70,  "lon": 77.10},
    {"region_id": "IN-JK", "region_name": "Jammu & Kashmir",      "population": 12267032,  "lat": 33.78,  "lon": 76.58},
    {"region_id": "IN-LA", "region_name": "Ladakh",               "population": 274289,    "lat": 34.15,  "lon": 77.58},
    {"region_id": "IN-CH", "region_name": "Chandigarh",           "population": 1055450,   "lat": 30.73,  "lon": 76.78},
    {"region_id": "IN-PY", "region_name": "Puducherry",           "population": 1247953,   "lat": 11.94,  "lon": 79.83},
    {"region_id": "IN-AN", "region_name": "Andaman & Nicobar",    "population": 380581,    "lat": 11.74,  "lon": 92.66},
]

ALL_DISEASES = [
    "DENGUE", "COVID", "MALARIA", "TUBERCULOSIS", "INFLUENZA",
    "CHOLERA", "CHIKUNGUNYA", "TYPHOID", "JAPANESE_ENCEPHALITIS", "MEASLES",
]

# ── Monthly seasonal multipliers (index 0 = Jan, 11 = Dec) ────────────────────
# Based on known Indian epidemiological patterns
SEASONALITY = {
    # Vector-borne: peaks during/after monsoon (Jul-Nov)
    "DENGUE":                [0.08, 0.05, 0.06, 0.08, 0.12, 0.25, 0.55, 0.80, 1.00, 0.90, 0.60, 0.20],
    "MALARIA":               [0.10, 0.08, 0.10, 0.15, 0.25, 0.60, 0.90, 1.00, 0.85, 0.50, 0.25, 0.12],
    "CHIKUNGUNYA":           [0.05, 0.04, 0.05, 0.07, 0.10, 0.20, 0.45, 0.70, 0.85, 1.00, 0.55, 0.15],
    "JAPANESE_ENCEPHALITIS": [0.04, 0.03, 0.05, 0.08, 0.15, 0.35, 0.65, 1.00, 0.90, 0.50, 0.20, 0.08],
    # Respiratory: peaks in winter (Nov-Feb)
    "COVID":                 [0.80, 0.60, 0.40, 0.30, 0.25, 0.20, 0.30, 0.35, 0.40, 0.50, 0.70, 1.00],
    "INFLUENZA":             [1.00, 0.85, 0.60, 0.35, 0.20, 0.15, 0.20, 0.25, 0.35, 0.50, 0.75, 0.95],
    "TUBERCULOSIS":          [0.85, 0.90, 1.00, 0.95, 0.80, 0.70, 0.65, 0.60, 0.65, 0.70, 0.75, 0.80],
    "MEASLES":               [0.70, 0.85, 1.00, 0.90, 0.60, 0.30, 0.20, 0.15, 0.20, 0.30, 0.45, 0.60],
    # Waterborne: peaks monsoon + post-monsoon (Jun-Oct)
    "CHOLERA":               [0.10, 0.08, 0.12, 0.15, 0.25, 0.60, 1.00, 0.90, 0.75, 0.45, 0.20, 0.10],
    "TYPHOID":               [0.15, 0.12, 0.15, 0.20, 0.30, 0.55, 0.85, 1.00, 0.80, 0.50, 0.25, 0.15],
}

# Case fatality rates by disease
CFR = {
    "DENGUE": 0.005,     "COVID": 0.015,    "MALARIA": 0.003,
    "TUBERCULOSIS": 0.10, "INFLUENZA": 0.001, "CHOLERA": 0.04,
    "CHIKUNGUNYA": 0.001, "TYPHOID": 0.008,  "JAPANESE_ENCEPHALITIS": 0.25,
    "MEASLES": 0.002,
}

# Recovery rates by disease
RECOVERY_RATE = {
    "DENGUE": 0.92,      "COVID": 0.90,     "MALARIA": 0.95,
    "TUBERCULOSIS": 0.80, "INFLUENZA": 0.97, "CHOLERA": 0.88,
    "CHIKUNGUNYA": 0.97,  "TYPHOID": 0.93,  "JAPANESE_ENCEPHALITIS": 0.60,
    "MEASLES": 0.95,
}

# ── Region-level disease burden tiers ──────────────────────────────────────────
# Population drives base daily cases. Burden tier adjusts.
# Tier: HIGH_BURDEN=1.2, MED_BURDEN=1.0, LOW_BURDEN=0.6
# Defines which states are high-burden for which diseases
HIGH_BURDEN = {
    "DENGUE":     {"IN-MH","IN-DL","IN-KA","IN-TN","IN-KL","IN-WB","IN-TG","IN-AP","IN-GJ","IN-RJ"},
    "COVID":      {"IN-MH","IN-DL","IN-KA","IN-KL","IN-TN","IN-UP","IN-WB","IN-GJ","IN-RJ","IN-AP"},
    "MALARIA":    {"IN-OR","IN-CT","IN-JH","IN-MP","IN-WB","IN-RJ","IN-MH","IN-GJ","IN-AS","IN-MZ"},
    "TUBERCULOSIS":{"IN-UP","IN-MH","IN-MP","IN-RJ","IN-BR","IN-GJ","IN-TN","IN-WB","IN-DL","IN-KA"},
    "INFLUENZA":  {"IN-DL","IN-MH","IN-KA","IN-TN","IN-KL","IN-UP","IN-WB","IN-GJ","IN-HR","IN-PB"},
    "CHOLERA":    {"IN-WB","IN-BR","IN-UP","IN-OR","IN-MH","IN-MP","IN-CT","IN-JH","IN-DL","IN-AS"},
    "CHIKUNGUNYA":{"IN-KA","IN-KL","IN-TN","IN-DL","IN-MH","IN-AP","IN-TG","IN-GJ","IN-RJ","IN-WB"},
    "TYPHOID":    {"IN-UP","IN-BR","IN-MP","IN-DL","IN-WB","IN-MH","IN-RJ","IN-JH","IN-CT","IN-OR"},
    "JAPANESE_ENCEPHALITIS":{"IN-UP","IN-BR","IN-AS","IN-WB","IN-TN","IN-KA","IN-AP","IN-OR","IN-MP","IN-CT"},
    "MEASLES":    {"IN-UP","IN-BR","IN-MH","IN-MP","IN-RJ","IN-GJ","IN-JH","IN-WB","IN-DL","IN-CT"},
}

def _get_daily_baseline(region, disease):
    """
    Compute a per-region, per-disease daily baseline scaled by population.
    Returns approximate average daily cases at peak multiplier=1.0.
    """
    pop = region["population"]
    rid = region["region_id"]
    
    # Population-driven base: per-million daily cases
    # These are hand-tuned to produce realistic numbers
    PER_MILLION_DAILY = {
        "DENGUE": 1.4,      "COVID": 3.5,       "MALARIA": 0.9,
        "TUBERCULOSIS": 1.8, "INFLUENZA": 2.0,   "CHOLERA": 0.4,
        "CHIKUNGUNYA": 0.8,  "TYPHOID": 0.6,     "JAPANESE_ENCEPHALITIS": 0.06,
        "MEASLES": 0.3,
    }
    
    base = (pop / 1_000_000) * PER_MILLION_DAILY.get(disease, 1.0)
    
    # Burden tier adjustment
    if rid in HIGH_BURDEN.get(disease, set()):
        base *= 1.3
    else:
        base *= 0.7
    
    # Small states floor — ensure at least some data
    return max(base, 2.0)


# ── Disease resource configuration ─────────────────────────────────────────────
DISEASE_CONFIGS = [
    {"_id": "dengue",               "name": "DENGUE",               "resource_params": {"hospitalization_rate": 0.20, "icu_rate": 0.03, "avg_stay_days": 5, "nurse_ratio": 0.15, "oxygen_rate": 0.05}},
    {"_id": "covid",                "name": "COVID",                "resource_params": {"hospitalization_rate": 0.15, "icu_rate": 0.05, "avg_stay_days": 10, "nurse_ratio": 0.20, "oxygen_rate": 0.30}},
    {"_id": "malaria",              "name": "MALARIA",              "resource_params": {"hospitalization_rate": 0.15, "icu_rate": 0.02, "avg_stay_days": 4, "nurse_ratio": 0.12, "oxygen_rate": 0.08}},
    {"_id": "tuberculosis",         "name": "TUBERCULOSIS",         "resource_params": {"hospitalization_rate": 0.25, "icu_rate": 0.04, "avg_stay_days": 14, "nurse_ratio": 0.18, "oxygen_rate": 0.15}},
    {"_id": "influenza",            "name": "INFLUENZA",            "resource_params": {"hospitalization_rate": 0.08, "icu_rate": 0.01, "avg_stay_days": 3, "nurse_ratio": 0.10, "oxygen_rate": 0.04}},
    {"_id": "cholera",              "name": "CHOLERA",              "resource_params": {"hospitalization_rate": 0.30, "icu_rate": 0.06, "avg_stay_days": 5, "nurse_ratio": 0.20, "oxygen_rate": 0.03}},
    {"_id": "chikungunya",          "name": "CHIKUNGUNYA",          "resource_params": {"hospitalization_rate": 0.10, "icu_rate": 0.005, "avg_stay_days": 3, "nurse_ratio": 0.10, "oxygen_rate": 0.02}},
    {"_id": "typhoid",              "name": "TYPHOID",              "resource_params": {"hospitalization_rate": 0.18, "icu_rate": 0.02, "avg_stay_days": 7, "nurse_ratio": 0.12, "oxygen_rate": 0.03}},
    {"_id": "japanese_encephalitis","name": "JAPANESE_ENCEPHALITIS","resource_params": {"hospitalization_rate": 0.60, "icu_rate": 0.25, "avg_stay_days": 14, "nurse_ratio": 0.35, "oxygen_rate": 0.40}},
    {"_id": "measles",              "name": "MEASLES",              "resource_params": {"hospitalization_rate": 0.12, "icu_rate": 0.02, "avg_stay_days": 5, "nurse_ratio": 0.10, "oxygen_rate": 0.05}},
]


# ── News articles ──────────────────────────────────────────────────────────────
def get_news_articles(today):
    return [
        {
            "title": "Mumbai reports 45% spike in dengue cases as monsoon lingers",
            "source": "NVBDCP Weekly Bulletin",
            "published_at": today - timedelta(days=1),
            "url": "https://nvbdcp.gov.in/WriteReadData/dengue-weekly-report.pdf",
            "content": "The National Vector Borne Disease Control Programme reports a significant uptick in dengue cases across the Mumbai Metropolitan Region. The BMC has recorded 2,847 confirmed cases in the last 30 days, a 45% increase over the corresponding period last year.",
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
            "content": "Rajasthan's Directorate of Medical & Health Services has issued a malaria alert for 12 districts following severe flooding. Over 1,500 positive smears were reported from Jodhpur, Barmer, and Jaisalmer districts in the past week.",
            "extracted_diseases": ["MALARIA"],
            "extracted_locations": ["Rajasthan", "Jodhpur", "Barmer"],
            "relevance_score": 0.88,
            "ingested_at": today,
        },
        {
            "title": "WHO warns of chikungunya resurgence in South India",
            "source": "WHO South-East Asia Region",
            "published_at": today - timedelta(days=3),
            "url": "https://www.who.int/india/news/detail/chikungunya-advisory-2025",
            "content": "The WHO has issued an advisory on elevated chikungunya transmission risk in Karnataka, Kerala, and Tamil Nadu. Above-normal temperatures combined with intermittent rainfall are driving Aedes aegypti proliferation.",
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
            "content": "Major hospitals across Delhi-NCR report a 60% occupancy surge in dengue wards. AIIMS and Safdarjung Hospital report daily admissions of 80-120 suspected dengue patients.",
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
            "content": "Epidemiologists in West Bengal have flagged concurrent dengue and malaria co-infections in flood-affected districts. At least 127 patients tested positive for both pathogens across Murshidabad, Nadia, and North 24 Parganas.",
            "extracted_diseases": ["DENGUE", "MALARIA"],
            "extracted_locations": ["West Bengal", "Murshidabad", "Nadia"],
            "relevance_score": 0.87,
            "ingested_at": today,
        },
        {
            "title": "COVID-19 winter wave: Kerala and Maharashtra report surge in hospitalizations",
            "source": "Ministry of Health & Family Welfare",
            "published_at": today - timedelta(days=2),
            "url": "https://mohfw.gov.in/covid-dashboard",
            "content": "India's winter COVID wave intensifies with Kerala and Maharashtra leading in new hospitalizations. JN.1 sub-variant dominates sequencing data. Health ministry advises booster doses for vulnerable populations.",
            "extracted_diseases": ["COVID"],
            "extracted_locations": ["Kerala", "Maharashtra"],
            "relevance_score": 0.91,
            "ingested_at": today,
        },
        {
            "title": "UP: Japanese Encephalitis claims 23 lives in eastern districts",
            "source": "Uttar Pradesh State Surveillance Unit",
            "published_at": today - timedelta(days=6),
            "url": "https://uphealth.up.nic.in/je-report",
            "content": "Japanese Encephalitis continues to affect children in Gorakhpur, Deoria, and Kushinagar districts. The state has activated 45 pediatric ICU beds and deployed rapid response teams.",
            "extracted_diseases": ["JAPANESE_ENCEPHALITIS"],
            "extracted_locations": ["Uttar Pradesh", "Gorakhpur"],
            "relevance_score": 0.89,
            "ingested_at": today,
        },
        {
            "title": "Cholera outbreak in Bihar: 400+ cases reported after contaminated water supply",
            "source": "Integrated Disease Surveillance Programme",
            "published_at": today - timedelta(days=3),
            "url": "https://idsp.nic.in/showfile.php?lid=4380",
            "content": "A major cholera outbreak in Muzaffarpur and Vaishali districts of Bihar has been linked to contaminated drinking water sources. ORS and IV fluid supplies are being airlifted.",
            "extracted_diseases": ["CHOLERA"],
            "extracted_locations": ["Bihar", "Muzaffarpur"],
            "relevance_score": 0.93,
            "ingested_at": today,
        },
        {
            "title": "TB notification rates rise 12% across India in latest NTEP quarterly report",
            "source": "National TB Elimination Programme",
            "published_at": today - timedelta(days=7),
            "url": "https://tbcindia.gov.in/quarterly-report",
            "content": "India's TB notification rates have risen 12% year-over-year. Uttar Pradesh, Maharashtra, and Madhya Pradesh account for 40% of all new notifications. Active case finding campaigns show success.",
            "extracted_diseases": ["TUBERCULOSIS"],
            "extracted_locations": ["India", "Uttar Pradesh", "Maharashtra"],
            "relevance_score": 0.86,
            "ingested_at": today,
        },
        {
            "title": "Measles vaccination coverage drops in tribal areas; Jharkhand reports cluster",
            "source": "Universal Immunization Programme",
            "published_at": today - timedelta(days=4),
            "url": "https://mohfw.gov.in/uip-report",
            "content": "A measles outbreak cluster has been identified in Jharkhand's West Singhbhum district affecting 85 children. Vaccination coverage in tribal areas has dropped below 70% target.",
            "extracted_diseases": ["MEASLES"],
            "extracted_locations": ["Jharkhand", "West Singhbhum"],
            "relevance_score": 0.84,
            "ingested_at": today,
        },
    ]


# ── Daily case generation ──────────────────────────────────────────────────────

def generate_daily_cases(region, disease, num_days=90):
    """
    Generate daily case data with realistic seasonal patterns and trends.
    
    Produces daily records going back `num_days` from today.
    Uses Poisson-like noise, seasonal multipliers, and regional burden tiers.
    Also introduces realistic multi-day trends (mini surges/declines).
    """
    baseline = _get_daily_baseline(region, disease)
    seasonality = SEASONALITY[disease]
    cfr = CFR[disease]
    recovery = RECOVERY_RATE[disease]
    
    today = datetime.now()
    records = []
    
    # Introduce a wandering trend factor for realistic jagged growth
    trend = 1.0
    
    for d in range(num_days):
        day_offset = num_days - 1 - d
        target_date = today - timedelta(days=day_offset)
        month_idx = target_date.month - 1
        
        # Interpolate between months for daily smoothness
        day_of_month = target_date.day
        next_month = (month_idx + 1) % 12
        frac = day_of_month / 30.0
        multiplier = seasonality[month_idx] * (1 - frac) + seasonality[next_month] * frac
        
        # Wandering trend: random walk (simulates mini-surges and declines)
        trend += random.gauss(0, 0.03)
        trend = max(0.5, min(1.8, trend))  # clamp
        
        # Day-of-week effect: Mon-Fri slightly higher reporting
        dow = target_date.weekday()
        dow_factor = 1.05 if dow < 5 else 0.85
        
        expected = baseline * multiplier * trend * dow_factor
        
        # Poisson-like noise
        noise_std = max(1, math.sqrt(expected) * 0.8)
        confirmed = max(0, int(expected + random.gauss(0, noise_std)))
        
        deaths = max(0, int(confirmed * cfr * random.uniform(0.4, 1.6)))
        recovered = max(0, int(confirmed * recovery * random.uniform(0.90, 1.0)))
        
        date_str = target_date.strftime("%Y-%m-%d")
        records.append({
            "region_id": region["region_id"],
            "date": date_str,
            "disease": disease,
            "confirmed": confirmed,
            "deaths": deaths,
            "recovered": recovered,
            "granularity": "daily",
        })
    
    return records


# ══════════════════════════════════════════════════════════════════════════════
# Main seed + pipeline runner
# ══════════════════════════════════════════════════════════════════════════════

def run_seed():
    logger.info(f"Connecting to MongoDB: {MONGO_URI}")
    client = MongoClient(
        MONGO_URI,
        connectTimeoutMS=30000,
        serverSelectionTimeoutMS=30000,
        socketTimeoutMS=120000,
    )
    db = client[DB_NAME]
    
    # Verify connection
    try:
        client.admin.command("ping")
        logger.info("✅ MongoDB connection OK")
    except Exception as e:
        logger.error(f"❌ Cannot connect to MongoDB: {e}")
        sys.exit(1)
    
    # ── 1. Drop existing data ──────────────────────────────────────────────
    logger.info("Dropping existing collections...")
    for col in ["regions", "cases_daily", "alerts", "forecasts_daily",
                 "resources_daily", "reports", "risk_scores",
                 "disease_config", "news_articles"]:
        db[col].drop()
    
    # ── 2. Seed regions ────────────────────────────────────────────────────
    logger.info(f"Seeding {len(REGIONS)} regions...")
    db.regions.insert_many(REGIONS)
    
    # ── 3. Seed disease configs ────────────────────────────────────────────
    logger.info(f"Seeding {len(DISEASE_CONFIGS)} disease resource configs...")
    for config in DISEASE_CONFIGS:
        db.disease_config.update_one(
            {"_id": config["_id"]},
            {"$set": config},
            upsert=True,
        )
    
    # ── 4. Generate daily case data ────────────────────────────────────────
    total_combinations = len(REGIONS) * len(ALL_DISEASES)
    logger.info(f"Generating 90 days of daily cases for {total_combinations} region×disease combos...")
    
    all_cases = []
    batch_size = 5000
    inserted = 0
    
    for i, region in enumerate(REGIONS):
        for disease in ALL_DISEASES:
            cases = generate_daily_cases(region, disease, num_days=90)
            all_cases.extend(cases)
            
            # Batch insert to avoid memory issues
            if len(all_cases) >= batch_size:
                db.cases_daily.insert_many(all_cases)
                inserted += len(all_cases)
                all_cases = []
        
        if (i + 1) % 10 == 0:
            logger.info(f"  ... {i+1}/{len(REGIONS)} regions processed")
    
    # Insert remaining
    if all_cases:
        db.cases_daily.insert_many(all_cases)
        inserted += len(all_cases)
    
    logger.info(f"Inserted {inserted} daily case records")
    
    # ── 5. Seed news articles ──────────────────────────────────────────────
    today = datetime.now()
    articles = get_news_articles(today)
    logger.info(f"Seeding {len(articles)} news articles...")
    for article in articles:
        db.news_articles.update_one(
            {"title": article["title"]},
            {"$set": article},
            upsert=True,
        )
    
    # ── 6. Create indexes ──────────────────────────────────────────────────
    logger.info("Creating indexes...")
    db.cases_daily.create_index([("region_id", ASCENDING), ("disease", ASCENDING), ("date", ASCENDING)])
    db.cases_daily.create_index([("disease", ASCENDING), ("date", ASCENDING)])
    db.cases_daily.create_index([("granularity", ASCENDING)])
    db.risk_scores.create_index([("disease", ASCENDING), ("date", ASCENDING)])
    db.risk_scores.create_index([("region_id", ASCENDING), ("disease", ASCENDING)])
    db.alerts.create_index([("disease", ASCENDING), ("date", ASCENDING)])
    db.alerts.create_index([("region_id", ASCENDING), ("disease", ASCENDING)])
    db.forecasts_daily.create_index([("region_id", ASCENDING), ("disease", ASCENDING), ("date", ASCENDING)])
    db.news_articles.create_index([("extracted_diseases", ASCENDING)])
    db.news_articles.create_index([("published_at", -1)])
    db.regions.create_index([("region_id", ASCENDING)], unique=True)
    
    # ── 7. Summary ─────────────────────────────────────────────────────────
    logger.info("")
    logger.info("═══════════════════════════════════════════")
    logger.info("  SEEDING COMPLETE")
    logger.info("═══════════════════════════════════════════")
    logger.info(f"  Regions:         {db.regions.count_documents({})}")
    logger.info(f"  Disease Configs: {db.disease_config.count_documents({})}")
    logger.info(f"  Cases (daily):   {db.cases_daily.count_documents({})}")
    logger.info(f"  News Articles:   {db.news_articles.count_documents({})}")
    logger.info("")
    
    # ── 8. Run pipeline for all diseases ───────────────────────────────────
    logger.info("═══════════════════════════════════════════")
    logger.info("  RUNNING PIPELINE FOR ALL DISEASES")
    logger.info("═══════════════════════════════════════════")
    
    # Import the pipeline functions (same ones the API uses)
    try:
        from backend.services.risk import compute_risk_scores
        from backend.services.alerts import generate_alerts
        from backend.services.arima_forecasting import generate_arima_forecasts
    except ImportError:
        # If running as standalone script, add project root to path
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        sys.path.insert(0, project_root)
        from backend.services.risk import compute_risk_scores
        from backend.services.alerts import generate_alerts
        from backend.services.arima_forecasting import generate_arima_forecasts
    
    pipeline_results = {}
    
    for disease in ALL_DISEASES:
        logger.info(f"")
        logger.info(f"──── Pipeline: {disease} ────")
        
        try:
            # Step 1: Risk scores
            risk_date, risk_results = compute_risk_scores(target_date=None, disease=disease)
            risk_count = len(risk_results)
            logger.info(f"  ✓ Risk scores:  {risk_count} regions")
            
            # Step 2: Alerts
            alert_date, alert_results = generate_alerts(target_date=None, disease=disease)
            alert_count = len(alert_results)
            logger.info(f"  ✓ Alerts:       {alert_count} generated")
            
            # Step 3: ARIMA Forecasts
            try:
                forecast_date, forecast_results = generate_arima_forecasts(
                    target_date=None, horizon=7, disease=disease, granularity="daily"
                )
                forecast_count = len(forecast_results)
                logger.info(f"  ✓ Forecasts:    {forecast_count} regions")
            except Exception as e:
                logger.warning(f"  ⚠ Forecasts failed for {disease}: {str(e)[:80]}...")
                forecast_count = 0
            
            pipeline_results[disease] = {
                "risk": risk_count,
                "alerts": alert_count,
                "forecasts": forecast_count,
            }
        except Exception as e:
            logger.error(f"  ✗ Pipeline failed for {disease}: {e}")
            pipeline_results[disease] = {"risk": 0, "alerts": 0, "forecasts": 0}
    
    # ── Final summary ──────────────────────────────────────────────────────
    logger.info("")
    logger.info("═══════════════════════════════════════════")
    logger.info("  FINAL DATABASE STATE")
    logger.info("═══════════════════════════════════════════")
    logger.info(f"  regions:         {db.regions.count_documents({})}")
    logger.info(f"  cases_daily:     {db.cases_daily.count_documents({})}")
    logger.info(f"  risk_scores:     {db.risk_scores.count_documents({})}")
    logger.info(f"  alerts:          {db.alerts.count_documents({})}")
    logger.info(f"  forecasts_daily: {db.forecasts_daily.count_documents({})}")
    logger.info(f"  disease_config:  {db.disease_config.count_documents({})}")
    logger.info(f"  news_articles:   {db.news_articles.count_documents({})}")
    logger.info("")
    
    logger.info("Pipeline results per disease:")
    logger.info(f"  {'Disease':<25} {'Risk':>6}  {'Alerts':>7}  {'Forecasts':>10}")
    logger.info(f"  {'─'*25} {'─'*6}  {'─'*7}  {'─'*10}")
    for disease, counts in pipeline_results.items():
        logger.info(f"  {disease:<25} {counts['risk']:>6}  {counts['alerts']:>7}  {counts['forecasts']:>10}")
    
    logger.info("")
    logger.info("🚀 PRISM is fully operational! Open http://localhost:5173 to use the dashboard.")


if __name__ == "__main__":
    run_seed()
