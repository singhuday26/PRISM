"""View detailed pipeline results."""
from pymongo import MongoClient, DESCENDING

client = MongoClient()
db = client.prism_db

print("=" * 70)
print("📊 PIPELINE RESULTS - DETAILED VIEW")
print("=" * 70)

# Risk Scores
print("\n🎯 TOP 10 RISK SCORES:")
risk_scores = list(db.risk_scores.find({}).sort("risk_score", DESCENDING).limit(10))
for i, r in enumerate(risk_scores, 1):
    region_name = db.regions.find_one({"region_id": r['region_id']})
    name = region_name['region_name'] if region_name else r['region_id']
    print(f"   {i}. {name:30s} | Score: {r['risk_score']:.3f} | Level: {r['risk_level']}")

# Alerts
print("\n🚨 ALL ALERTS GENERATED:")
alerts = list(db.alerts.find({}).sort("risk_score", DESCENDING))
for i, a in enumerate(alerts, 1):
    region_name = db.regions.find_one({"region_id": a['region_id']})
    name = region_name['region_name'] if region_name else a['region_id']
    print(f"   {i}. {name:30s} | Score: {a['risk_score']:.3f} | {a['reason']}")

# Forecasts Summary
print("\n📈 FORECAST SUMMARY:")
forecast_count = db.forecasts_daily.count_documents({})
regions_with_forecasts = len(db.forecasts_daily.distinct("region_id"))
print(f"   Total forecasts: {forecast_count}")
print(f"   Regions with forecasts: {regions_with_forecasts}")
print(f"   Days per region: {forecast_count // regions_with_forecasts if regions_with_forecasts > 0 else 0}")

# Sample forecasts
print("\n📊 SAMPLE FORECASTS (Random Region):")
sample_region = db.forecasts_daily.find_one()
if sample_region:
    region_id = sample_region['region_id']
    region_name = db.regions.find_one({"region_id": region_id})
    name = region_name['region_name'] if region_name else region_id
    print(f"\n   Region: {name} ({region_id})")
    
    forecasts = list(db.forecasts_daily.find({"region_id": region_id}).sort("date", 1))
    for f in forecasts:
        pred = f.get('pred_mean', 0)
        lower = f.get('pred_lower', 0)
        upper = f.get('pred_upper', 0)
        print(f"      {f['date']}: {pred:.0f} cases [{lower:.0f}-{upper:.0f}] (model: {f.get('model_version', 'v1')})")

# Case Data Summary
print("\n📋 INPUT DATA SUMMARY:")
total_cases = sum([c.get('confirmed', 0) for c in db.cases_daily.find({})])
total_deaths = sum([c.get('deaths', 0) for c in db.cases_daily.find({})])
print(f"   Total confirmed cases: {total_cases:,}")
print(f"   Total deaths: {total_deaths:,}")
print(f"   Case fatality rate: {(total_deaths/total_cases*100):.2f}%" if total_cases > 0 else "   N/A")

client.close()
print("\n" + "=" * 70)
