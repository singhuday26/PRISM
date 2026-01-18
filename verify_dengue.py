"""Quick script to verify dengue data in MongoDB."""
from pymongo import MongoClient
import json

client = MongoClient('mongodb://localhost:27017/')
db = client.prism_db

print(f"📊 Database Statistics:")
print(f"   Total regions: {db.regions.count_documents({})}")
print(f"   Dengue regions: {db.regions.count_documents({'disease': 'DENGUE'})}")
print(f"   Total case records: {db.cases_daily.count_documents({})}")
print(f"   Dengue case records: {db.cases_daily.count_documents({'disease': 'DENGUE'})}")

print(f"\n🌏 Sample Dengue Regions:")
dengue_regions = list(db.regions.find({'disease': 'DENGUE'}).limit(5))
for r in dengue_regions:
    print(f"   {r.get('region_id', 'N/A')}: {r.get('region_name', 'N/A')}, Country: {r.get('country', 'N/A')}")

print(f"\n📈 Sample Case Records:")
cases = list(db.cases_daily.find({'disease': 'DENGUE'}).sort('date', -1).limit(5))
for c in cases:
    print(f"   {c['region_id']} on {c['date']}: {c['confirmed']} cases, {c['deaths']} deaths")

client.close()
print("\n✅ Verification complete!")
