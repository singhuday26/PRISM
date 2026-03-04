"""
PRISM Seed Verification Script
================================
Checks every region × disease combination exists in MongoDB with expected
document counts. Reports missing or under-seeded pairs.

Usage:
    python -m backend.scripts.verify_seed
    python -m backend.scripts.verify_seed --expected-days 90
"""

import os
import sys
import argparse
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = os.getenv("DB_NAME",   "prism_db")

ALL_REGIONS = [
    "IN-AP", "IN-AR", "IN-AS", "IN-BR", "IN-CT", "IN-GA", "IN-GJ", "IN-HR",
    "IN-HP", "IN-JH", "IN-KA", "IN-KL", "IN-MP", "IN-MH", "IN-MN", "IN-ML",
    "IN-MZ", "IN-NL", "IN-OR", "IN-PB", "IN-RJ", "IN-SK", "IN-TN", "IN-TG",
    "IN-TR", "IN-UP", "IN-UT", "IN-WB",
    # Union Territories
    "IN-DL", "IN-JK", "IN-LA", "IN-CH", "IN-PY", "IN-AN",
]

ALL_DISEASES = [
    "DENGUE", "COVID", "MALARIA", "TUBERCULOSIS", "INFLUENZA",
    "CHOLERA", "CHIKUNGUNYA", "TYPHOID", "JAPANESE_ENCEPHALITIS", "MEASLES",
]

def main():
    parser = argparse.ArgumentParser(description="Verify PRISM seed data")
    parser.add_argument("--expected-days", type=int, default=90,
                        help="Expected number of daily records per region×disease")
    args = parser.parse_args()

    print("=" * 70)
    print("  PRISM Seed Verification")
    print("=" * 70)

    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]

    try:
        client.admin.command("ping")
        print("✅ MongoDB connection OK\n")
    except Exception as e:
        print(f"❌ Cannot connect to MongoDB: {e}")
        sys.exit(1)

    # 1. Check collections exist
    existing = db.list_collection_names()
    required = ["regions", "cases_daily", "disease_config", "news_articles"]
    print("── Collections ──")
    for col in required:
        status = "✅" if col in existing else "❌ MISSING"
        count = db[col].count_documents({}) if col in existing else 0
        print(f"  {status}  {col:20s}  ({count:,} docs)")
    print()

    # 2. Check regions
    print("── Regions ──")
    seeded_regions = set()
    for doc in db.regions.find({}, {"region_id": 1}):
        seeded_regions.add(doc["region_id"])

    missing_regions = set(ALL_REGIONS) - seeded_regions
    extra_regions   = seeded_regions - set(ALL_REGIONS)
    print(f"  Expected: {len(ALL_REGIONS)}")
    print(f"  Found:    {len(seeded_regions)}")
    if missing_regions:
        print(f"  ❌ Missing: {sorted(missing_regions)}")
    if extra_regions:
        print(f"  ⚠️  Extra:   {sorted(extra_regions)}")
    if not missing_regions and not extra_regions:
        print(f"  ✅ All {len(ALL_REGIONS)} regions present")
    print()

    # 3. Check disease_config
    print("── Disease Configs ──")
    seeded_configs = set()
    for doc in db.disease_config.find({}, {"name": 1}):
        seeded_configs.add(doc.get("name", ""))
    missing_configs = set(ALL_DISEASES) - seeded_configs
    if missing_configs:
        print(f"  ❌ Missing configs: {sorted(missing_configs)}")
    else:
        print(f"  ✅ All {len(ALL_DISEASES)} disease configs present")
    print()

    # 4. Check every region × disease combination
    print("── Region × Disease Case Data ──")
    print(f"  Expected combinations:  {len(ALL_REGIONS)} × {len(ALL_DISEASES)} = {len(ALL_REGIONS)*len(ALL_DISEASES)}")
    print(f"  Expected docs per pair: ~{args.expected_days}")
    print()

    total_ok     = 0
    total_low    = 0
    total_zero   = 0
    total_docs   = 0
    issues = []

    # Use aggregation pipeline for efficiency instead of N*M queries
    pipeline = [
        {"$match": {"granularity": "daily"}},
        {"$group": {
            "_id": {"region_id": "$region_id", "disease": "$disease"},
            "count": {"$sum": 1},
            "min_date": {"$min": "$date"},
            "max_date": {"$max": "$date"},
        }},
        {"$sort": {"_id.region_id": 1, "_id.disease": 1}},
    ]

    found_pairs = {}
    for doc in db.cases_daily.aggregate(pipeline, allowDiskUse=True):
        key = (doc["_id"]["region_id"], doc["_id"]["disease"])
        found_pairs[key] = {
            "count": doc["count"],
            "min_date": doc["min_date"],
            "max_date": doc["max_date"],
        }

    for region_id in ALL_REGIONS:
        for disease in ALL_DISEASES:
            key = (region_id, disease)
            if key not in found_pairs:
                total_zero += 1
                issues.append(f"❌ ZERO docs:  {region_id} × {disease}")
            else:
                info = found_pairs[key]
                count = info["count"]
                total_docs += count
                min_threshold = max(1, int(args.expected_days * 0.8))
                if count < min_threshold:
                    total_low += 1
                    issues.append(
                        f"⚠️  LOW count: {region_id} × {disease} = {count} "
                        f"(expected ~{args.expected_days})"
                    )
                else:
                    total_ok += 1

    total_expected = len(ALL_REGIONS) * len(ALL_DISEASES)
    print(f"  ✅ OK:            {total_ok}/{total_expected}")
    print(f"  ⚠️  Low count:     {total_low}/{total_expected}")
    print(f"  ❌ Missing (zero): {total_zero}/{total_expected}")
    print(f"  📊 Total docs:    {total_docs:,}")
    print()

    if issues:
        print("── Issues ──")
        for issue in issues[:50]:  # cap display
            print(f"  {issue}")
        if len(issues) > 50:
            print(f"  ... and {len(issues)-50} more")
        print()

    # 5. Check pipeline outputs (optional)
    print("── Pipeline Outputs ──")
    for col_name in ["risk_scores", "alerts", "forecasts_daily"]:
        count = db[col_name].count_documents({}) if col_name in existing else 0
        status = "✅" if count > 0 else "⚠️  (empty — run --run-pipeline)"
        print(f"  {status}  {col_name:20s}  ({count:,} docs)")
    print()

    # 6. Final verdict
    print("=" * 70)
    if total_zero == 0 and total_low == 0 and not missing_regions:
        print("  ✅ VERIFICATION PASSED — All combinations are fully seeded!")
    elif total_zero == 0 and total_low > 0:
        print("  ⚠️  PARTIAL — All combinations exist but some have low counts")
    else:
        print(f"  ❌ INCOMPLETE — {total_zero} missing + {total_low} low count pairs")
    print("=" * 70)

    return 0 if (total_zero == 0 and not missing_regions) else 1


if __name__ == "__main__":
    sys.exit(main())
