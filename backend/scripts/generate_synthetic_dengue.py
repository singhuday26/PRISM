"""
Synthetic Monthly/Weekly Dengue Data Generator
Expands yearly dengue data into monthly granularity using seasonality weights.

Dengue Seasonality Pattern (India):
- Pre-monsoon (Mar-May): Low, building up (10% of annual)
- Monsoon (Jun-Sep): Peak season (60% of annual)
- Post-monsoon (Oct-Nov): High continuation (20% of annual)
- Winter (Dec-Feb): Low activity (10% of annual)
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict
import random
from backend.db import get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dengue seasonality weights by month (India monsoon pattern)
# Higher weights during monsoon months (June-September)
MONTHLY_WEIGHTS = {
    1: 0.03,   # January - Winter (Low)
    2: 0.03,   # February - Winter (Low)
    3: 0.04,   # March - Pre-monsoon (Building)
    4: 0.05,   # April - Pre-monsoon (Building)
    5: 0.06,   # May - Pre-monsoon (Building)
    6: 0.15,   # June - Monsoon (Peak)
    7: 0.18,   # July - Monsoon (Peak)
    8: 0.17,   # August - Monsoon (Peak)
    9: 0.14,   # September - Monsoon (Peak)
    10: 0.09,  # October - Post-monsoon (High)
    11: 0.04,  # November - Post-monsoon (Declining)
    12: 0.02,  # December - Winter (Low)
}

# Verify weights sum to 1.0
assert abs(sum(MONTHLY_WEIGHTS.values()) - 1.0) < 0.01, "Monthly weights must sum to 1.0"


def generate_monthly_data(year: int, region_id: str, annual_cases: int, annual_deaths: int) -> List[Dict]:
    """
    Generate monthly case records from yearly totals using seasonality weights.
    
    Args:
        year: Year for data generation
        region_id: Region identifier
        annual_cases: Total confirmed cases for the year
        annual_deaths: Total deaths for the year
    
    Returns:
        List of monthly case records
    """
    monthly_records = []
    
    for month in range(1, 13):
        weight = MONTHLY_WEIGHTS[month]
        
        # Distribute cases with some randomness (±20%)
        base_cases = int(annual_cases * weight)
        randomness = random.uniform(0.8, 1.2)
        monthly_cases = max(0, int(base_cases * randomness))
        
        # Distribute deaths proportionally
        base_deaths = int(annual_deaths * weight)
        monthly_deaths = max(0, int(base_deaths * randomness))
        
        # Create date for mid-month (15th)
        date = f"{year}-{month:02d}-15"
        
        monthly_records.append({
            "region_id": region_id,
            "date": date,
            "confirmed": monthly_cases,
            "deaths": monthly_deaths,
            "recovered": 0,
            "disease": "DENGUE",
            "granularity": "monthly"
        })
    
    return monthly_records


def generate_weekly_data(year: int, region_id: str, annual_cases: int, annual_deaths: int) -> List[Dict]:
    """
    Generate weekly case records from yearly totals using seasonality weights.
    
    Args:
        year: Year for data generation
        region_id: Region identifier
        annual_cases: Total confirmed cases for the year
        annual_deaths: Total deaths for the year
    
    Returns:
        List of weekly case records (52 weeks)
    """
    weekly_records = []
    # Start from Jan 4 to avoid conflicts with monthly data (which uses 15th of month)
    start_date = datetime(year, 1, 4)
    
    # Generate 52 weeks directly from monthly weights
    for week_num in range(1, 53):
        # Calculate which month this week falls into (roughly 4.33 weeks per month)
        month = ((week_num - 1) // 4) + 1
        if month > 12:
            month = 12
        
        # Get monthly weight and divide by 4 for weekly
        monthly_weight = MONTHLY_WEIGHTS[month]
        weekly_weight = monthly_weight / 4.33  # More accurate weeks per month
        
        # Add randomness (±30% for weekly variability)
        randomness = random.uniform(0.7, 1.3)
        
        weekly_cases = max(0, int(annual_cases * weekly_weight * randomness))
        weekly_deaths = max(0, int(annual_deaths * weekly_weight * randomness))
        
        # Calculate week date
        week_date = start_date + timedelta(weeks=week_num - 1)
        
        weekly_records.append({
            "region_id": region_id,
            "date": week_date.strftime("%Y-%m-%d"),
            "confirmed": weekly_cases,
            "deaths": weekly_deaths,
            "recovered": 0,
            "disease": "DENGUE",
            "granularity": "weekly"
        })
    
    return weekly_records


def load_synthetic_monthly_dengue(granularity: str = "monthly", reset: bool = False):
    """
    Load synthetic monthly/weekly dengue data by expanding yearly data.
    
    Args:
        granularity: 'monthly' or 'weekly'
        reset: If True, delete existing synthetic data before loading
    """
    logger.info(f"🔬 Starting synthetic {granularity} dengue data generation...")
    
    db = get_db()
    cases_col = db["cases_daily"]
    
    if reset:
        logger.info("🗑️  Resetting synthetic data...")
        deleted = cases_col.delete_many({"disease": "DENGUE", "granularity": granularity})
        logger.info(f"✓ Deleted {deleted.deleted_count} existing {granularity} records")
    
    # Fetch yearly dengue data (our original loaded data)
    yearly_data = list(cases_col.find({
        "disease": "DENGUE",
        "granularity": {"$exists": False}  # Original yearly data doesn't have granularity field
    }))
    
    if not yearly_data:
        logger.error("No yearly dengue data found. Please run load_dengue_data.py first.")
        return
    
    logger.info(f"📊 Found {len(yearly_data)} yearly records to expand")
    
    # Group by region and year
    records_by_region_year = {}
    for record in yearly_data:
        region_id = record["region_id"]
        year = int(record["date"].split("-")[0])
        key = (region_id, year)
        records_by_region_year[key] = record
    
    # Generate synthetic data
    all_synthetic_records = []
    
    for (region_id, year), yearly_record in records_by_region_year.items():
        annual_cases = yearly_record.get("confirmed", 0)
        annual_deaths = yearly_record.get("deaths", 0)
        
        if granularity == "monthly":
            synthetic_records = generate_monthly_data(year, region_id, annual_cases, annual_deaths)
        elif granularity == "weekly":
            synthetic_records = generate_weekly_data(year, region_id, annual_cases, annual_deaths)
        else:
            logger.error(f"Invalid granularity: {granularity}. Use 'monthly' or 'weekly'")
            return
        
        all_synthetic_records.extend(synthetic_records)
    
    # Insert into database
    if all_synthetic_records:
        logger.info(f"💾 Inserting {len(all_synthetic_records)} {granularity} records...")
        
        # Use insert_many for efficiency (records should be unique due to date offsets)
        try:
            result = cases_col.insert_many(all_synthetic_records, ordered=False)
            logger.info(f"✅ Successfully loaded {len(result.inserted_ids)} {granularity} dengue records")
        except Exception as e:
            # If some duplicates, continue with what was inserted
            logger.warning(f"⚠️ Some duplicates encountered, but continuing: {e}")
            # Count what was actually inserted
            inserted_count = cases_col.count_documents({
                "disease": "DENGUE",
                "granularity": granularity
            })
            logger.info(f"✅ Successfully loaded {inserted_count} {granularity} dengue records")
        
        # Show sample statistics
        sample_region = all_synthetic_records[0]["region_id"]
        sample_year = int(all_synthetic_records[0]["date"].split("-")[0])
        
        sample_records = [r for r in all_synthetic_records 
                         if r["region_id"] == sample_region and r["date"].startswith(str(sample_year))]
        
        total_cases = sum(r["confirmed"] for r in sample_records)
        peak_month = max(sample_records, key=lambda x: x["confirmed"])
        
        logger.info(f"\n📈 Sample Statistics ({sample_region}, {sample_year}):")
        logger.info(f"   Total {granularity} records: {len(sample_records)}")
        logger.info(f"   Total cases: {total_cases:,}")
        logger.info(f"   Peak period: {peak_month['date']} ({peak_month['confirmed']:,} cases)")
        
        if granularity == "monthly":
            monsoon_months = [r for r in sample_records if int(r["date"].split("-")[1]) in [6, 7, 8, 9]]
            monsoon_cases = sum(r["confirmed"] for r in monsoon_months)
            logger.info(f"   Monsoon season (Jun-Sep): {monsoon_cases:,} cases ({monsoon_cases/total_cases*100:.1f}%)")
    else:
        logger.warning("No synthetic records generated")


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    granularity = sys.argv[1] if len(sys.argv) > 1 else "monthly"
    reset = "--reset" in sys.argv
    
    if granularity not in ["monthly", "weekly"]:
        print("Usage: python backend/scripts/generate_synthetic_dengue.py [monthly|weekly] [--reset]")
        print("\nExamples:")
        print("  python -m backend.scripts.generate_synthetic_dengue monthly")
        print("  python -m backend.scripts.generate_synthetic_dengue weekly --reset")
        sys.exit(1)
    
    load_synthetic_monthly_dengue(granularity, reset)
