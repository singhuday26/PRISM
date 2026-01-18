"""
Visualize Dengue Seasonality Data
----------------------------------
Shows the monthly dengue case distribution to demonstrate seasonality patterns.
"""

import logging
from collections import defaultdict
from backend.db import get_db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def visualize_seasonality():
    """
    Display dengue seasonality patterns from synthetic monthly data.
    """
    logger.info("📊 Analyzing Dengue Seasonality Patterns")
    
    db = get_db()
    cases_col = db["cases_daily"]
    
    # Get monthly synthetic data for analysis
    monthly_records = list(cases_col.find({
        "disease": "DENGUE",
        "granularity": "monthly"
    }).sort("date", 1))
    
    if not monthly_records:
        logger.error("No monthly synthetic data found. Run generate_synthetic_dengue.py first.")
        return
    
    logger.info(f"Found {len(monthly_records)} monthly records")
    
    # Aggregate cases by month across all regions and years
    cases_by_month = defaultdict(int)
    count_by_month = defaultdict(int)
    
    for record in monthly_records:
        date_str = record.get("date", "")
        month = int(date_str.split("-")[1])  # Extract month
        cases = record.get("confirmed", 0)
        
        cases_by_month[month] += cases
        count_by_month[month] += 1
    
    # Calculate average cases per month
    avg_cases_by_month = {
        month: cases_by_month[month] / count_by_month[month]
        for month in range(1, 13)
    }
    
    # Find peak month
    peak_month = max(avg_cases_by_month.items(), key=lambda x: x[1])
    total_annual = sum(avg_cases_by_month.values())
    
    # Calculate monsoon season contribution
    monsoon_months = [6, 7, 8, 9]  # Jun, Jul, Aug, Sep
    monsoon_cases = sum(avg_cases_by_month[m] for m in monsoon_months)
    monsoon_percentage = (monsoon_cases / total_annual) * 100
    
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    
    print("\n" + "="*70)
    print("DENGUE SEASONALITY ANALYSIS")
    print("="*70)
    print(f"\n📈 Monthly Dengue Cases (Average per Region):\n")
    
    # Create a simple bar chart
    max_cases = max(avg_cases_by_month.values())
    
    for month in range(1, 13):
        avg_cases = avg_cases_by_month[month]
        percentage = (avg_cases / total_annual) * 100
        bar_length = int((avg_cases / max_cases) * 40)
        bar = "█" * bar_length
        
        # Mark monsoon months
        marker = " 🌧️ " if month in monsoon_months else "    "
        
        print(f"{month_names[month-1]}{marker} {bar} {avg_cases:6.1f} ({percentage:5.1f}%)")
    
    print(f"\n" + "-"*70)
    print(f"Peak Month:          {month_names[peak_month[0]-1]} ({peak_month[1]:.1f} avg cases)")
    print(f"Monsoon Season:      Jun-Sep ({monsoon_cases:.1f} cases, {monsoon_percentage:.1f}%)")
    print(f"Total Annual Avg:    {total_annual:.1f} cases per region")
    print("="*70 + "\n")
    
    # Show data granularity summary
    yearly_count = cases_col.count_documents({
        "disease": "DENGUE",
        "granularity": {"$exists": False}
    })
    monthly_count = cases_col.count_documents({
        "disease": "DENGUE",
        "granularity": "monthly"
    })
    weekly_count = cases_col.count_documents({
        "disease": "DENGUE",
        "granularity": "weekly"
    })
    
    print("📦 Data Granularity Summary:")
    print(f"   Yearly (original):     {yearly_count:,} records")
    print(f"   Monthly (synthetic):   {monthly_count:,} records")
    print(f"   Weekly (synthetic):    {weekly_count:,} records")
    print(f"   Total:                 {yearly_count + monthly_count + weekly_count:,} records\n")


if __name__ == "__main__":
    visualize_seasonality()
