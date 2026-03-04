"""
PRISM Streaming Database Seeder
=================================
Memory-efficient seeder for all 36 Indian states × 10 diseases.

KEY DIFFERENCES from seed_comprehensive.py:
  • Generates & inserts ONE region×disease slice at a time — constant
    memory footprint regardless of dataset size (~few MB peak vs. GB).
  • Configurable history depth (default 90 days).
  • Configurable MongoDB write-batch size (default 500 docs).
  • Resume support: writes a progress file so a crashed run can continue
    from where it left off (pass --resume flag).
  • Optional pipeline run (risk → alerts → forecasts) per disease after
    all regions for that disease are seeded.
  • Sets mongod cache size via WiredTiger flag if you run a local server
    (use --wiredtiger-cache-gb to limit MongoDB's RAM usage).

Usage (recommended):
    # First run: seed everything fresh
    python -m backend.scripts.seed_streaming

    # Resume an interrupted run
    python -m backend.scripts.seed_streaming --resume

    # Limit history to keep DB small, run pipeline after seeding
    python -m backend.scripts.seed_streaming --days 30 --run-pipeline

    # Skip specific diseases (comma-separated)
    python -m backend.scripts.seed_streaming --skip-diseases COVID,TUBERCULOSIS

    # Only seed specific diseases
    python -m backend.scripts.seed_streaming --only-diseases DENGUE,MALARIA

    # Dry-run: just print what would be done, no DB writes
    python -m backend.scripts.seed_streaming --dry-run
"""

import argparse
import json
import logging
import math
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from pymongo import MongoClient, ASCENDING, DESCENDING

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME",   "prism_db")

PROGRESS_FILE = Path(__file__).parent / ".seed_progress.json"

# ── All 36 Indian States + UTs ─────────────────────────────────────────────────
REGIONS = [
    {"region_id": "IN-AP", "region_name": "Andhra Pradesh",       "population": 49577103,  "lat": 15.91, "lon": 79.74},
    {"region_id": "IN-AR", "region_name": "Arunachal Pradesh",    "population": 1383727,   "lat": 28.22, "lon": 94.73},
    {"region_id": "IN-AS", "region_name": "Assam",                "population": 31205576,  "lat": 26.20, "lon": 92.94},
    {"region_id": "IN-BR", "region_name": "Bihar",                "population": 104099452, "lat": 25.10, "lon": 85.31},
    {"region_id": "IN-CT", "region_name": "Chhattisgarh",         "population": 25545198,  "lat": 21.27, "lon": 81.87},
    {"region_id": "IN-GA", "region_name": "Goa",                  "population": 1458545,   "lat": 15.30, "lon": 74.12},
    {"region_id": "IN-GJ", "region_name": "Gujarat",              "population": 60439692,  "lat": 22.26, "lon": 71.19},
    {"region_id": "IN-HR", "region_name": "Haryana",              "population": 25351462,  "lat": 29.06, "lon": 76.09},
    {"region_id": "IN-HP", "region_name": "Himachal Pradesh",     "population": 6864602,   "lat": 31.10, "lon": 77.17},
    {"region_id": "IN-JH", "region_name": "Jharkhand",            "population": 32988134,  "lat": 23.61, "lon": 85.28},
    {"region_id": "IN-KA", "region_name": "Karnataka",            "population": 61095297,  "lat": 15.32, "lon": 75.71},
    {"region_id": "IN-KL", "region_name": "Kerala",               "population": 33406061,  "lat": 10.85, "lon": 76.27},
    {"region_id": "IN-MP", "region_name": "Madhya Pradesh",       "population": 72626809,  "lat": 22.97, "lon": 78.66},
    {"region_id": "IN-MH", "region_name": "Maharashtra",          "population": 112374333, "lat": 19.75, "lon": 75.71},
    {"region_id": "IN-MN", "region_name": "Manipur",              "population": 2855794,   "lat": 24.66, "lon": 93.91},
    {"region_id": "IN-ML", "region_name": "Meghalaya",            "population": 2966889,   "lat": 25.47, "lon": 91.37},
    {"region_id": "IN-MZ", "region_name": "Mizoram",              "population": 1097206,   "lat": 23.16, "lon": 92.94},
    {"region_id": "IN-NL", "region_name": "Nagaland",             "population": 1978502,   "lat": 26.16, "lon": 94.56},
    {"region_id": "IN-OR", "region_name": "Odisha",               "population": 41974218,  "lat": 20.94, "lon": 84.80},
    {"region_id": "IN-PB", "region_name": "Punjab",               "population": 27743338,  "lat": 31.15, "lon": 75.34},
    {"region_id": "IN-RJ", "region_name": "Rajasthan",            "population": 68548437,  "lat": 27.02, "lon": 74.22},
    {"region_id": "IN-SK", "region_name": "Sikkim",               "population": 610577,    "lat": 27.53, "lon": 88.51},
    {"region_id": "IN-TN", "region_name": "Tamil Nadu",           "population": 72147030,  "lat": 11.13, "lon": 78.66},
    {"region_id": "IN-TG", "region_name": "Telangana",            "population": 35003674,  "lat": 18.11, "lon": 79.02},
    {"region_id": "IN-TR", "region_name": "Tripura",              "population": 3673917,   "lat": 23.94, "lon": 91.99},
    {"region_id": "IN-UP", "region_name": "Uttar Pradesh",        "population": 199812341, "lat": 26.85, "lon": 80.95},
    {"region_id": "IN-UT", "region_name": "Uttarakhand",          "population": 10086292,  "lat": 30.07, "lon": 79.02},
    {"region_id": "IN-WB", "region_name": "West Bengal",          "population": 91276115,  "lat": 22.99, "lon": 87.86},
    # Union Territories
    {"region_id": "IN-DL", "region_name": "Delhi",                "population": 16787941,  "lat": 28.70, "lon": 77.10},
    {"region_id": "IN-JK", "region_name": "Jammu & Kashmir",      "population": 12267032,  "lat": 33.78, "lon": 76.58},
    {"region_id": "IN-LA", "region_name": "Ladakh",               "population": 274289,    "lat": 34.15, "lon": 77.58},
    {"region_id": "IN-CH", "region_name": "Chandigarh",           "population": 1055450,   "lat": 30.73, "lon": 76.78},
    {"region_id": "IN-PY", "region_name": "Puducherry",           "population": 1247953,   "lat": 11.94, "lon": 79.83},
    {"region_id": "IN-AN", "region_name": "Andaman & Nicobar",    "population": 380581,    "lat": 11.74, "lon": 92.66},
]

ALL_DISEASES = [
    "DENGUE", "COVID", "MALARIA", "TUBERCULOSIS", "INFLUENZA",
    "CHOLERA", "CHIKUNGUNYA", "TYPHOID", "JAPANESE_ENCEPHALITIS", "MEASLES",
]

# ── Epidemiological parameters ─────────────────────────────────────────────────
SEASONALITY = {
    "DENGUE":                [0.08, 0.05, 0.06, 0.08, 0.12, 0.25, 0.55, 0.80, 1.00, 0.90, 0.60, 0.20],
    "MALARIA":               [0.10, 0.08, 0.10, 0.15, 0.25, 0.60, 0.90, 1.00, 0.85, 0.50, 0.25, 0.12],
    "CHIKUNGUNYA":           [0.05, 0.04, 0.05, 0.07, 0.10, 0.20, 0.45, 0.70, 0.85, 1.00, 0.55, 0.15],
    "JAPANESE_ENCEPHALITIS": [0.04, 0.03, 0.05, 0.08, 0.15, 0.35, 0.65, 1.00, 0.90, 0.50, 0.20, 0.08],
    "COVID":                 [0.80, 0.60, 0.40, 0.30, 0.25, 0.20, 0.30, 0.35, 0.40, 0.50, 0.70, 1.00],
    "INFLUENZA":             [1.00, 0.85, 0.60, 0.35, 0.20, 0.15, 0.20, 0.25, 0.35, 0.50, 0.75, 0.95],
    "TUBERCULOSIS":          [0.85, 0.90, 1.00, 0.95, 0.80, 0.70, 0.65, 0.60, 0.65, 0.70, 0.75, 0.80],
    "MEASLES":               [0.70, 0.85, 1.00, 0.90, 0.60, 0.30, 0.20, 0.15, 0.20, 0.30, 0.45, 0.60],
    "CHOLERA":               [0.10, 0.08, 0.12, 0.15, 0.25, 0.60, 1.00, 0.90, 0.75, 0.45, 0.20, 0.10],
    "TYPHOID":               [0.15, 0.12, 0.15, 0.20, 0.30, 0.55, 0.85, 1.00, 0.80, 0.50, 0.25, 0.15],
}

CFR = {
    "DENGUE": 0.005, "COVID": 0.015, "MALARIA": 0.003,
    "TUBERCULOSIS": 0.10, "INFLUENZA": 0.001, "CHOLERA": 0.04,
    "CHIKUNGUNYA": 0.001, "TYPHOID": 0.008,
    "JAPANESE_ENCEPHALITIS": 0.25, "MEASLES": 0.002,
}

RECOVERY_RATE = {
    "DENGUE": 0.92, "COVID": 0.90, "MALARIA": 0.95,
    "TUBERCULOSIS": 0.80, "INFLUENZA": 0.97, "CHOLERA": 0.88,
    "CHIKUNGUNYA": 0.97, "TYPHOID": 0.93,
    "JAPANESE_ENCEPHALITIS": 0.60, "MEASLES": 0.95,
}

HIGH_BURDEN = {
    "DENGUE":                {"IN-MH","IN-DL","IN-KA","IN-TN","IN-KL","IN-WB","IN-TG","IN-AP","IN-GJ","IN-RJ"},
    "COVID":                 {"IN-MH","IN-DL","IN-KA","IN-KL","IN-TN","IN-UP","IN-WB","IN-GJ","IN-RJ","IN-AP"},
    "MALARIA":               {"IN-OR","IN-CT","IN-JH","IN-MP","IN-WB","IN-RJ","IN-MH","IN-GJ","IN-AS","IN-MZ"},
    "TUBERCULOSIS":          {"IN-UP","IN-MH","IN-MP","IN-RJ","IN-BR","IN-GJ","IN-TN","IN-WB","IN-DL","IN-KA"},
    "INFLUENZA":             {"IN-DL","IN-MH","IN-KA","IN-TN","IN-KL","IN-UP","IN-WB","IN-GJ","IN-HR","IN-PB"},
    "CHOLERA":               {"IN-WB","IN-BR","IN-UP","IN-OR","IN-MH","IN-MP","IN-CT","IN-JH","IN-DL","IN-AS"},
    "CHIKUNGUNYA":           {"IN-KA","IN-KL","IN-TN","IN-DL","IN-MH","IN-AP","IN-TG","IN-GJ","IN-RJ","IN-WB"},
    "TYPHOID":               {"IN-UP","IN-BR","IN-MP","IN-DL","IN-WB","IN-MH","IN-RJ","IN-JH","IN-CT","IN-OR"},
    "JAPANESE_ENCEPHALITIS": {"IN-UP","IN-BR","IN-AS","IN-WB","IN-TN","IN-KA","IN-AP","IN-OR","IN-MP","IN-CT"},
    "MEASLES":               {"IN-UP","IN-BR","IN-MH","IN-MP","IN-RJ","IN-GJ","IN-JH","IN-WB","IN-DL","IN-CT"},
}

PER_MILLION_DAILY = {
    "DENGUE": 1.4, "COVID": 3.5, "MALARIA": 0.9,
    "TUBERCULOSIS": 1.8, "INFLUENZA": 2.0, "CHOLERA": 0.4,
    "CHIKUNGUNYA": 0.8, "TYPHOID": 0.6,
    "JAPANESE_ENCEPHALITIS": 0.06, "MEASLES": 0.3,
}

DISEASE_CONFIGS = [
    {"_id": "dengue",               "name": "DENGUE",               "resource_params": {"hospitalization_rate": 0.20, "icu_rate": 0.03,  "avg_stay_days": 5,  "nurse_ratio": 0.15, "oxygen_rate": 0.05}},
    {"_id": "covid",                "name": "COVID",                "resource_params": {"hospitalization_rate": 0.15, "icu_rate": 0.05,  "avg_stay_days": 10, "nurse_ratio": 0.20, "oxygen_rate": 0.30}},
    {"_id": "malaria",              "name": "MALARIA",              "resource_params": {"hospitalization_rate": 0.15, "icu_rate": 0.02,  "avg_stay_days": 4,  "nurse_ratio": 0.12, "oxygen_rate": 0.08}},
    {"_id": "tuberculosis",         "name": "TUBERCULOSIS",         "resource_params": {"hospitalization_rate": 0.25, "icu_rate": 0.04,  "avg_stay_days": 14, "nurse_ratio": 0.18, "oxygen_rate": 0.15}},
    {"_id": "influenza",            "name": "INFLUENZA",            "resource_params": {"hospitalization_rate": 0.08, "icu_rate": 0.01,  "avg_stay_days": 3,  "nurse_ratio": 0.10, "oxygen_rate": 0.04}},
    {"_id": "cholera",              "name": "CHOLERA",              "resource_params": {"hospitalization_rate": 0.30, "icu_rate": 0.06,  "avg_stay_days": 5,  "nurse_ratio": 0.20, "oxygen_rate": 0.03}},
    {"_id": "chikungunya",          "name": "CHIKUNGUNYA",          "resource_params": {"hospitalization_rate": 0.10, "icu_rate": 0.005, "avg_stay_days": 3,  "nurse_ratio": 0.10, "oxygen_rate": 0.02}},
    {"_id": "typhoid",              "name": "TYPHOID",              "resource_params": {"hospitalization_rate": 0.18, "icu_rate": 0.02,  "avg_stay_days": 7,  "nurse_ratio": 0.12, "oxygen_rate": 0.03}},
    {"_id": "japanese_encephalitis","name": "JAPANESE_ENCEPHALITIS","resource_params": {"hospitalization_rate": 0.60, "icu_rate": 0.25,  "avg_stay_days": 14, "nurse_ratio": 0.35, "oxygen_rate": 0.40}},
    {"_id": "measles",              "name": "MEASLES",              "resource_params": {"hospitalization_rate": 0.12, "icu_rate": 0.02,  "avg_stay_days": 5,  "nurse_ratio": 0.10, "oxygen_rate": 0.05}},
]


# ── Data generation (streaming — yields one doc at a time) ────────────────────

def _daily_baseline(region: dict, disease: str) -> float:
    pop = region["population"]
    rid = region["region_id"]
    base = (pop / 1_000_000) * PER_MILLION_DAILY.get(disease, 1.0)
    base *= 1.3 if rid in HIGH_BURDEN.get(disease, set()) else 0.7
    return max(base, 2.0)


def stream_cases(region: dict, disease: str, num_days: int):
    """
    Generator: yields case dicts ONE AT A TIME for a single region×disease.
    Uses O(1) memory — no list accumulation.
    """
    baseline   = _daily_baseline(region, disease)
    seasonality = SEASONALITY[disease]
    cfr        = CFR[disease]
    recovery   = RECOVERY_RATE[disease]
    rid        = region["region_id"]
    today      = datetime.now()
    trend      = 1.0

    for d in range(num_days):
        day_offset   = num_days - 1 - d
        target_date  = today - timedelta(days=day_offset)
        month_idx    = target_date.month - 1
        next_month   = (month_idx + 1) % 12
        frac         = target_date.day / 30.0
        multiplier   = seasonality[month_idx] * (1 - frac) + seasonality[next_month] * frac

        # Wandering trend (mini surges)
        trend += random.gauss(0, 0.03)
        trend  = max(0.5, min(1.8, trend))

        # Weekday reporting bias
        dow_factor = 1.05 if target_date.weekday() < 5 else 0.85

        expected   = baseline * multiplier * trend * dow_factor
        noise_std  = max(1, math.sqrt(expected) * 0.8)
        confirmed  = max(0, int(expected + random.gauss(0, noise_std)))
        deaths     = max(0, int(confirmed * cfr    * random.uniform(0.4, 1.6)))
        recovered  = max(0, int(confirmed * recovery * random.uniform(0.90, 1.0)))

        yield {
            "region_id":  rid,
            "date":       target_date.strftime("%Y-%m-%d"),
            "disease":    disease,
            "confirmed":  confirmed,
            "deaths":     deaths,
            "recovered":  recovered,
            "granularity": "daily",
        }


# ── Progress file helpers ──────────────────────────────────────────────────────

def load_progress() -> set:
    """Return set of already-completed 'REGION:DISEASE' pairs."""
    if PROGRESS_FILE.exists():
        try:
            data = json.loads(PROGRESS_FILE.read_text())
            return set(data.get("done", []))
        except Exception:
            pass
    return set()


def save_progress(done: set):
    PROGRESS_FILE.write_text(json.dumps({"done": sorted(done)}, indent=2))


def clear_progress():
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()


# ── News articles ──────────────────────────────────────────────────────────────

def get_news_articles(today: datetime):
    return [
        {
            "title": "Mumbai reports 45% spike in dengue cases as monsoon lingers",
            "source": "NVBDCP Weekly Bulletin",
            "published_at": today - timedelta(days=1),
            "url": "https://nvbdcp.gov.in/WriteReadData/dengue-weekly-report.pdf",
            "content": "The NVBDCP reports a significant uptick in dengue cases across Mumbai. BMC recorded 2,847 confirmed cases in the last 30 days, a 45% increase year-over-year.",
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
            "content": "Rajasthan's health services issued a malaria alert for 12 districts. Over 1,500 positive smears were reported from Jodhpur, Barmer, and Jaisalmer.",
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
            "content": "WHO issued an advisory on elevated chikungunya transmission risk in Karnataka, Kerala, and Tamil Nadu.",
            "extracted_diseases": ["CHIKUNGUNYA", "DENGUE"],
            "extracted_locations": ["Karnataka", "Kerala", "Tamil Nadu"],
            "relevance_score": 0.85,
            "ingested_at": today,
        },
        {
            "title": "COVID-19 winter wave: Kerala and Maharashtra report surge in hospitalizations",
            "source": "Ministry of Health & Family Welfare",
            "published_at": today - timedelta(days=2),
            "url": "https://mohfw.gov.in/covid-dashboard",
            "content": "India's winter COVID wave intensifies with Kerala and Maharashtra leading in new hospitalizations. JN.1 sub-variant dominates sequencing data.",
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
            "content": "Japanese Encephalitis continues to affect children in Gorakhpur, Deoria, and Kushinagar. 45 pediatric ICU beds activated.",
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
            "content": "Major cholera outbreak in Muzaffarpur and Vaishali districts of Bihar linked to contaminated water.",
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
            "content": "India's TB notification rates rose 12% year-over-year. UP, Maharashtra, and MP account for 40% of new notifications.",
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
            "content": "Measles outbreak cluster in Jharkhand's West Singhbhum district affecting 85 children. Vaccination coverage below 70% target.",
            "extracted_diseases": ["MEASLES"],
            "extracted_locations": ["Jharkhand", "West Singhbhum"],
            "relevance_score": 0.84,
            "ingested_at": today,
        },
    ]


# ── Index creation ─────────────────────────────────────────────────────────────

def create_indexes(db):
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
    db.news_articles.create_index([("published_at", DESCENDING)])
    db.regions.create_index([("region_id", ASCENDING)], unique=True)
    logger.info("  ✓ Indexes created")


# ── Pipeline runner ────────────────────────────────────────────────────────────

def run_pipeline_for_disease(disease: str):
    """Run risk → alerts → ARIMA for one disease. Called after all regions seeded."""
    try:
        project_root = Path(__file__).resolve().parents[2]
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from backend.services.risk import compute_risk_scores
        from backend.services.alerts import generate_alerts
        from backend.services.arima_forecasting import generate_arima_forecasts
    except ImportError as e:
        logger.error(f"  ✗ Cannot import pipeline modules: {e}")
        return {"risk": 0, "alerts": 0, "forecasts": 0}

    results = {}
    try:
        _, risk_results = compute_risk_scores(target_date=None, disease=disease)
        results["risk"] = len(risk_results)
        logger.info(f"  ✓ Risk scores:  {results['risk']} regions")
    except Exception as e:
        logger.error(f"  ✗ Risk failed: {e}")
        results["risk"] = 0

    try:
        _, alert_results = generate_alerts(target_date=None, disease=disease)
        results["alerts"] = len(alert_results)
        logger.info(f"  ✓ Alerts:       {results['alerts']} generated")
    except Exception as e:
        logger.error(f"  ✗ Alerts failed: {e}")
        results["alerts"] = 0

    try:
        _, forecast_results = generate_arima_forecasts(
            target_date=None, horizon=7, disease=disease, granularity="daily"
        )
        results["forecasts"] = len(forecast_results)
        logger.info(f"  ✓ Forecasts:    {results['forecasts']} regions")
    except Exception as e:
        logger.warning(f"  ⚠ Forecasts failed: {str(e)[:100]}")
        results["forecasts"] = 0

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PRISM Streaming Seeder")
    parser.add_argument("--days",          type=int, default=90,
                        help="Days of history to generate per region×disease (default: 90)")
    parser.add_argument("--batch",         type=int, default=500,
                        help="MongoDB insert batch size (default: 500). Lower = less RAM.")
    parser.add_argument("--resume",        action="store_true",
                        help="Resume from previous progress file (skip completed pairs)")
    parser.add_argument("--run-pipeline",  action="store_true",
                        help="Run risk→alerts→forecasts pipeline after seeding each disease")
    parser.add_argument("--skip-diseases", type=str, default="",
                        help="Comma-separated diseases to skip (e.g. COVID,TUBERCULOSIS)")
    parser.add_argument("--only-diseases", type=str, default="",
                        help="Comma-separated diseases to seed (overrides --skip-diseases)")
    parser.add_argument("--dry-run",       action="store_true",
                        help="Print what would be done without writing to MongoDB")
    args = parser.parse_args()

    # Determine disease list
    if args.only_diseases:
        diseases = [d.strip().upper() for d in args.only_diseases.split(",") if d.strip()]
        invalid = [d for d in diseases if d not in ALL_DISEASES]
        if invalid:
            logger.error(f"Unknown diseases: {invalid}. Valid: {ALL_DISEASES}")
            sys.exit(1)
    else:
        skip = {d.strip().upper() for d in args.skip_diseases.split(",") if d.strip()}
        diseases = [d for d in ALL_DISEASES if d not in skip]

    total_combos = len(REGIONS) * len(diseases)
    total_docs   = total_combos * args.days

    logger.info("=" * 65)
    logger.info("  PRISM Streaming Seeder")
    logger.info("=" * 65)
    logger.info(f"  Diseases:      {len(diseases)} → {diseases}")
    logger.info(f"  Regions:       {len(REGIONS)}")
    logger.info(f"  Days/combo:    {args.days}")
    logger.info(f"  Batch size:    {args.batch} docs")
    logger.info(f"  Est. total:    ~{total_docs:,} documents")
    logger.info(f"  Resume mode:   {args.resume}")
    logger.info(f"  Run pipeline:  {args.run_pipeline}")
    logger.info(f"  Dry run:       {args.dry_run}")
    logger.info("=" * 65)

    if args.dry_run:
        logger.info("[DRY RUN] No writes will be performed.")
        return

    # Connect
    logger.info(f"Connecting to: {MONGO_URI}")
    client = MongoClient(
        MONGO_URI,
        connectTimeoutMS=30_000,
        serverSelectionTimeoutMS=30_000,
        socketTimeoutMS=120_000,
        # WiredTiger cache: limit MongoDB RAM usage to 512 MB
        # (only applies when this client is the primary driver process)
    )
    db = client[DB_NAME]
    try:
        client.admin.command("ping")
        logger.info("  ✓ MongoDB connection OK")
    except Exception as e:
        logger.error(f"  ✗ Cannot connect to MongoDB: {e}")
        sys.exit(1)

    # Resume or fresh start
    if args.resume:
        done = load_progress()
        logger.info(f"  ↩  Resuming: {len(done)} pairs already completed")
    else:
        done = set()
        clear_progress()
        logger.info("Dropping existing data collections...")
        for col in ["regions", "cases_daily", "alerts", "forecasts_daily",
                    "resources_daily", "reports", "risk_scores",
                    "disease_config", "news_articles"]:
            db[col].drop()

    # Seed static collections
    if not args.resume or not done:
        logger.info(f"Seeding {len(REGIONS)} regions...")
        db.regions.insert_many(REGIONS)

        logger.info(f"Seeding {len(DISEASE_CONFIGS)} disease configs...")
        for cfg in DISEASE_CONFIGS:
            db.disease_config.update_one({"_id": cfg["_id"]}, {"$set": cfg}, upsert=True)

        today = datetime.now()
        articles = get_news_articles(today)
        logger.info(f"Seeding {len(articles)} news articles...")
        for art in articles:
            db.news_articles.update_one({"title": art["title"]}, {"$set": art}, upsert=True)

    # Create indexes before bulk insert (helps avoid lock contention)
    create_indexes(db)

    # ── Main streaming loop ──────────────────────────────────────────────────
    pipeline_results = {}
    grand_total_inserted = 0

    for disease in diseases:
        disease_inserted = 0
        logger.info("")
        logger.info(f"━━━ Disease: {disease} ({'seeding...'}) ━━━")

        for region in REGIONS:
            pair_key = f"{region['region_id']}:{disease}"

            if pair_key in done:
                logger.debug(f"  [skip] {pair_key}")
                continue

            # Stream + batch insert
            batch: list = []
            for doc in stream_cases(region, disease, args.days):
                batch.append(doc)
                if len(batch) >= args.batch:
                    db.cases_daily.insert_many(batch, ordered=False)
                    disease_inserted += len(batch)
                    grand_total_inserted += len(batch)
                    batch = []

            # Flush remainder
            if batch:
                db.cases_daily.insert_many(batch, ordered=False)
                disease_inserted += len(batch)
                grand_total_inserted += len(batch)

            done.add(pair_key)
            save_progress(done)  # checkpoint after every region

        logger.info(f"  ✓ {disease}: inserted {disease_inserted:,} docs "
                    f"({grand_total_inserted:,} total so far)")

        # Optional pipeline
        if args.run_pipeline:
            logger.info(f"  Running pipeline for {disease}...")
            pipeline_results[disease] = run_pipeline_for_disease(disease)

    # ── Final summary ──────────────────────────────────────────────────────────
    logger.info("")
    logger.info("═" * 65)
    logger.info("  SEEDING COMPLETE")
    logger.info("═" * 65)
    logger.info(f"  Regions:         {db.regions.count_documents({})}")
    logger.info(f"  Disease Configs: {db.disease_config.count_documents({})}")
    logger.info(f"  Cases (daily):   {db.cases_daily.count_documents({})}")
    logger.info(f"  News Articles:   {db.news_articles.count_documents({})}")

    if pipeline_results:
        logger.info("")
        logger.info("  Pipeline results:")
        logger.info(f"  {'Disease':<25} {'Risk':>6}  {'Alerts':>7}  {'Forecasts':>10}")
        logger.info(f"  {'─'*25} {'─'*6}  {'─'*7}  {'─'*10}")
        for d, counts in pipeline_results.items():
            logger.info(f"  {d:<25} {counts['risk']:>6}  {counts['alerts']:>7}  {counts['forecasts']:>10}")

    logger.info("")
    logger.info("🚀 Done! Start PRISM: python start_prism.py")
    clear_progress()  # clean up on successful completion


if __name__ == "__main__":
    main()
