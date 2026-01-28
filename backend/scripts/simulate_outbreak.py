"""
Outbreak Simulation Engine
Generates realistic synthetic outbreak data for demos using sinusoidal waves.

Creates 30 days of daily case data for 5 regions with:
- Sinusoidal outbreak curve with random noise
- Randomized peak timing per region
- Realistic case/death ratios

Usage:
    python backend/scripts/simulate_outbreak.py [--disease DENGUE|COVID] [--days 30]
"""

import logging
import math
import random
from datetime import datetime, timedelta
from typing import List, Dict

from backend.db import get_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default simulation parameters
DEFAULT_REGIONS = ["IN-MH", "IN-KA", "IN-TN", "IN-DL", "IN-WB"]
DEFAULT_DISEASE = "DENGUE"
DEFAULT_DAYS = 30

# Disease-specific parameters
DISEASE_PARAMS = {
    "DENGUE": {
        "base_cases": 50,       # Baseline cases per day
        "amplitude": 150,       # Peak amplitude above baseline
        "death_rate": 0.005,    # 0.5% CFR
        "recovery_rate": 0.85,  # 85% recovery
    },
    "COVID": {
        "base_cases": 200,
        "amplitude": 500,
        "death_rate": 0.02,     # 2% CFR
        "recovery_rate": 0.90,
    }
}


def generate_outbreak_curve(
    num_days: int,
    base_cases: int,
    amplitude: int,
    peak_day: int,
    noise_level: float = 0.25
) -> List[int]:
    """
    Generate a realistic outbreak curve using sinusoidal wave with noise.
    
    Args:
        num_days: Number of days to generate
        base_cases: Baseline number of daily cases
        amplitude: Maximum deviation from baseline (peak height)
        peak_day: Day when outbreak peaks (0-indexed)
        noise_level: Random noise as fraction of value (0-1)
    
    Returns:
        List of daily case counts
    """
    cases = []
    
    for day in range(num_days):
        # Sinusoidal wave: cases = base + amplitude * sin(phase)
        # Phase shifts so peak_day is at sin(π/2) = 1
        phase = math.pi * (day - peak_day + num_days / 4) / (num_days / 2)
        
        # Clamp the sine wave to create realistic growth/decline
        wave_value = math.sin(phase)
        wave_value = max(0, wave_value)  # No negative values
        
        # Calculate cases
        daily_cases = base_cases + int(amplitude * wave_value)
        
        # Add noise (Gaussian, clipped)
        noise = random.gauss(0, noise_level * daily_cases)
        daily_cases = max(1, int(daily_cases + noise))
        
        cases.append(daily_cases)
    
    return cases


def simulate_outbreak(
    regions: List[str] = DEFAULT_REGIONS,
    disease: str = DEFAULT_DISEASE,
    num_days: int = DEFAULT_DAYS,
    start_date: datetime = None,
    reset: bool = True
) -> List[Dict]:
    """
    Generate synthetic outbreak data for multiple regions.
    
    Args:
        regions: List of region IDs
        disease: Disease name (DENGUE or COVID)
        num_days: Number of days to simulate
        start_date: Start date (defaults to today - num_days)
        reset: If True, delete existing simulated data first
    
    Returns:
        List of generated records
    """
    logger.info(f"🦠 Starting outbreak simulation...")
    logger.info(f"   Disease: {disease}")
    logger.info(f"   Regions: {len(regions)}")
    logger.info(f"   Days: {num_days}")
    
    db = get_db()
    cases_col = db["cases_daily"]
    
    # Get disease parameters
    params = DISEASE_PARAMS.get(disease.upper(), DISEASE_PARAMS["DENGUE"])
    
    # Default start date: today minus num_days
    if start_date is None:
        start_date = datetime.now() - timedelta(days=num_days)
    
    # Reset existing simulation data
    if reset:
        logger.info("🗑️  Clearing existing simulation data...")
        deleted = cases_col.delete_many({
            "disease": disease.upper(),
            "granularity": "daily",
            "simulated": True
        })
        logger.info(f"✓ Deleted {deleted.deleted_count} existing records")
    
    all_records = []
    
    for region_id in regions:
        # Randomize peak day for this region (creates variety)
        peak_day = random.randint(num_days // 3, 2 * num_days // 3)
        
        # Add regional variation (±30%)
        regional_factor = random.uniform(0.7, 1.3)
        adj_base = int(params["base_cases"] * regional_factor)
        adj_amplitude = int(params["amplitude"] * regional_factor)
        
        # Generate outbreak curve
        daily_cases = generate_outbreak_curve(
            num_days=num_days,
            base_cases=adj_base,
            amplitude=adj_amplitude,
            peak_day=peak_day,
            noise_level=0.20
        )
        
        logger.info(f"📊 {region_id}: Peak on day {peak_day}, max cases: {max(daily_cases)}")
        
        # Create database records
        for day_offset, confirmed in enumerate(daily_cases):
            current_date = start_date + timedelta(days=day_offset)
            
            # Calculate deaths and recovered with some delay/smoothing
            deaths = max(0, int(confirmed * params["death_rate"] * random.uniform(0.5, 1.5)))
            recovered = max(0, int(confirmed * params["recovery_rate"] * random.uniform(0.8, 1.0)))
            
            record = {
                "region_id": region_id,
                "date": current_date.strftime("%Y-%m-%d"),
                "confirmed": confirmed,
                "deaths": deaths,
                "recovered": recovered,
                "disease": disease.upper(),
                "granularity": "daily",
                "simulated": True,  # Mark as synthetic for easy cleanup
            }
            all_records.append(record)
    
    # Insert all records
    if all_records:
        logger.info(f"💾 Inserting {len(all_records)} records...")
        result = cases_col.insert_many(all_records)
        logger.info(f"✅ Inserted {len(result.inserted_ids)} records")
    
    # Print summary statistics
    total_cases = sum(r["confirmed"] for r in all_records)
    total_deaths = sum(r["deaths"] for r in all_records)
    date_range = f"{all_records[0]['date']} to {all_records[-1]['date']}"
    
    logger.info(f"\n📈 Simulation Summary:")
    logger.info(f"   Date Range: {date_range}")
    logger.info(f"   Total Cases: {total_cases:,}")
    logger.info(f"   Total Deaths: {total_deaths:,}")
    logger.info(f"   Avg Daily Cases/Region: {total_cases // (len(regions) * num_days):,}")
    
    return all_records


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    disease = DEFAULT_DISEASE
    days = DEFAULT_DAYS
    
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--disease" and i < len(sys.argv) - 1:
            disease = sys.argv[i + 1].upper()
        elif arg == "--days" and i < len(sys.argv) - 1:
            try:
                days = int(sys.argv[i + 1])
            except ValueError:
                pass
    
    # Run simulation
    simulate_outbreak(
        regions=DEFAULT_REGIONS,
        disease=disease,
        num_days=days,
        reset=True
    )
    
    logger.info("\n✨ Outbreak simulation complete!")
    logger.info("   Next steps:")
    logger.info("   1. Run: POST /forecasts/generate (to create forecasts)")
    logger.info("   2. Run: POST /risk/compute (to calculate risk scores)")
