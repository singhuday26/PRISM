from pymongo import MongoClient
from datetime import datetime, timedelta

MONGO_URI = "mongodb+srv://prism_user:prism240818@cluster0.kesugwh.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)
db = client["prism_db"]

regions_col = db["regions"]
cases_col = db["cases_daily"]

# -------------------------
# 1) Insert Regions (if not already present)
# -------------------------
regions = [
    {"region_id": "IN-AP", "region_name": "Andhra Pradesh"},
    {"region_id": "IN-TN", "region_name": "Tamil Nadu"}
]

for r in regions:
    regions_col.update_one(
        {"region_id": r["region_id"]},
        {"$setOnInsert": r},
        upsert=True
    )

print("✅ Regions inserted/verified.")

# -------------------------
# 2) Insert Sample Daily Cases (10 days)
# -------------------------
start_date = datetime(2021, 5, 1)

sample_data = []
for i in range(10):
    date_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")

    # Andhra Pradesh sample growth
    sample_data.append({
        "region_id": "IN-AP",
        "date": date_str,
        "confirmed": 1000 + i * 120,
        "deaths": 10 + i,
        "recovered": 400 + i * 90
    })

    # Tamil Nadu sample growth
    sample_data.append({
        "region_id": "IN-TN",
        "date": date_str,
        "confirmed": 1500 + i * 80,
        "deaths": 15 + i,
        "recovered": 600 + i * 70
    })

# Insert only if not already inserted
for doc in sample_data:
    cases_col.update_one(
        {"region_id": doc["region_id"], "date": doc["date"]},
        {"$setOnInsert": doc},
        upsert=True
    )

print("✅ Sample cases inserted/verified.")

# -------------------------
# 3) Quick Verification
# -------------------------
print("\n📌 Current Counts:")
print("Regions:", regions_col.count_documents({}))
print("Cases:", cases_col.count_documents({}))

print("\n📌 Sample Query (latest Andhra Pradesh record):")
latest_ap = cases_col.find({"region_id": "IN-AP"}).sort("date", -1).limit(1)
for x in latest_ap:
    print(x)
