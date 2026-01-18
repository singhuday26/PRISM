"""
Compare Forecast Quality Across Different Granularities
--------------------------------------------------------
Shows how monthly, weekly, and yearly data affect forecast accuracy.
"""

import logging
from backend.db import get_db
from backend.services.forecasting import generate_forecast

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def compare_granularities():
    """
    Compare forecast results using different data granularities.
    """
    logger.info("📊 Comparing Forecast Quality Across Granularities")
    
    # Test parameters
    region_id = "IN-AP"  # Andhra Pradesh
    target_date = "2021-08-15"  # Monsoon peak month
    horizon = 7
    disease = "DENGUE"
    
    print("\n" + "="*80)
    print("FORECAST GRANULARITY COMPARISON")
    print("="*80)
    print(f"\nTest Region:  {region_id}")
    print(f"Target Date:  {target_date}")
    print(f"Horizon:      {horizon} days")
    print(f"Disease:      {disease}\n")
    
    granularities = ["yearly", "monthly", "weekly"]
    results = {}
    
    for granularity in granularities:
        logger.info(f"Generating forecast with {granularity} data...")
        
        try:
            forecasts = generate_forecast(
                region_id=region_id,
                target_date=target_date,
                horizon=horizon,
                disease=disease,
                granularity=granularity
            )
            
            if forecasts:
                pred_mean = forecasts[0]["pred_mean"]
                pred_lower = forecasts[0]["pred_lower"]
                pred_upper = forecasts[0]["pred_upper"]
                
                results[granularity] = {
                    "mean": pred_mean,
                    "lower": pred_lower,
                    "upper": pred_upper,
                    "count": len(forecasts)
                }
            else:
                results[granularity] = None
                
        except Exception as e:
            logger.error(f"Error with {granularity}: {e}")
            results[granularity] = None
    
    # Display results
    print("-"*80)
    print(f"{'Granularity':<15} {'Mean Forecast':<20} {'Range':<35} {'Data Points':<15}")
    print("-"*80)
    
    for granularity in granularities:
        result = results.get(granularity)
        if result:
            mean = result["mean"]
            lower = result["lower"]
            upper = result["upper"]
            count = result["count"]
            
            # Create simple bar visualization
            bar_length = int(mean / 10) if mean > 0 else 0
            bar = "█" * min(bar_length, 30)
            
            print(f"{granularity:<15} {mean:>8.1f} {bar:<30} [{lower:.1f} - {upper:.1f}] {count:>10} forecasts")
        else:
            print(f"{granularity:<15} {'No data':>8} {'':<30} {'N/A':<35} {'0':>10} forecasts")
    
    print("-"*80)
    
    # Show lookback information
    print("\n📋 Lookback Configuration:")
    print("   Yearly:  3 data points (3 years)")
    print("   Monthly: 6 data points (6 months)")
    print("   Weekly:  12 data points (12 weeks)")
    
    # Analysis
    print("\n💡 Analysis:")
    if results.get("monthly") and results.get("weekly"):
        monthly_mean = results["monthly"]["mean"]
        weekly_mean = results["weekly"]["mean"]
        diff_pct = abs(monthly_mean - weekly_mean) / monthly_mean * 100 if monthly_mean > 0 else 0
        
        print(f"   Monthly vs Weekly difference: {diff_pct:.1f}%")
        
        if diff_pct < 10:
            print("   ✓ Monthly and weekly forecasts are consistent")
        elif diff_pct < 25:
            print("   ⚠ Moderate variance between monthly and weekly")
        else:
            print("   ⚠ High variance - weekly data may have more noise")
    
    if results.get("monthly"):
        print(f"   ✓ Monthly data recommended for best balance of signal/noise")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    compare_granularities()
