"""Add missing model_version field to forecast documents."""
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["prism_db"]

# Add model_version to all documents missing it
result = db.forecasts_daily.update_many(
    {"model_version": {"$exists": False}},
    {"$set": {"model_version": "naive_v2"}}
)
print(f"Updated {result.modified_count} documents with model_version")

# Verify
sample = db.forecasts_daily.find_one({"region_id": "IN-MH"})
print(f"Sample document keys: {list(sample.keys())}")

client.close()
