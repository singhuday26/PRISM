# Synthetic Temporal Data Generation

## Overview

The PRISM system now supports **synthetic monthly and weekly data generation** to expand coarse yearly dengue data into realistic temporal granularity for meaningful outbreak forecasting.

## Problem Statement

- **Yearly dengue data is too coarse** for effective time-series forecasting
- Need **realistic temporal patterns** that reflect monsoon seasonality
- Original data: 144 yearly records (36 regions × 4 years)
- Required: Monthly/weekly granularity for forecasting algorithms

## Solution

Created `backend/scripts/generate_synthetic_dengue.py` that:

1. Expands yearly totals into monthly or weekly records
2. Applies **monsoon seasonality weights** based on India rainfall patterns
3. Adds realistic variance through randomization (±30%)
4. Preserves total annual case counts
5. Marks synthetic data with `granularity` field for filtering

## Seasonality Model

### Monthly Weights (Monsoon-Driven)

```python
MONTHLY_WEIGHTS = {
    # Winter (Low transmission)
    1: 0.03,  # January   - 3%
    2: 0.03,  # February  - 3%

    # Pre-monsoon (Building up)
    3: 0.04,  # March     - 4%
    4: 0.05,  # April     - 5%
    5: 0.06,  # May       - 6%

    # Monsoon (PEAK SEASON)
    6: 0.15,  # June      - 15% 🌧️
    7: 0.18,  # July      - 18% 🌧️ (PEAK)
    8: 0.17,  # August    - 17% 🌧️
    9: 0.13,  # September - 13% 🌧️

    # Post-monsoon (High activity continues)
    10: 0.09, # October   - 9%
    11: 0.04, # November  - 4%

    # Winter (Low transmission)
    12: 0.02  # December  - 2%
}
```

**Result**: **64.3% of annual cases occur during monsoon season** (Jun-Sep)

## Data Generated

### Monthly Data

```bash
python -m backend.scripts.generate_synthetic_dengue monthly --reset
```

- **1,728 records** (36 regions × 4 years × 12 months)
- Each month uses 15th as the date (e.g., `2018-01-15`)
- Monsoon peak in July-August (667.8 avg cases)
- Realistic variance through randomization

### Weekly Data

```bash
python -m backend.scripts.generate_synthetic_dengue weekly --reset
```

- **7,092 records** (36 regions × 4 years × 52 weeks)
- Week starts on the 4th of January (e.g., `2018-01-04`)
- 7-day intervals for consistent weekly data
- Higher variance (±30%) for weekly fluctuations

## Seasonality Visualization

Run the visualization script to see patterns:

```bash
python -m backend.scripts.visualize_seasonality
```

**Output:**

```
📈 Monthly Dengue Cases (Average per Region):

Jan     ██████  112.0 (  3.0%)
Feb     ██████  114.1 (  3.1%)
Mar     ████████  147.7 (  4.0%)
Apr     ██████████  182.4 (  4.9%)
May     █████████████  221.4 (  6.0%)
Jun 🌧️  ████████████████████████████████  563.0 ( 15.2%)
Jul 🌧️  ████████████████████████████████████████  667.8 ( 18.0%)
Aug 🌧️  ███████████████████████████████████████  659.7 ( 17.8%)
Sep 🌧️  █████████████████████████████  497.8 ( 13.4%)
Oct     ████████████████  330.8 (  8.9%)
Nov     ████████  146.7 (  3.9%)
Dec     ████   72.3 (  1.9%)

Peak Month:          Jul (667.8 avg cases)
Monsoon Season:      Jun-Sep (2388.2 cases, 64.3%)
Total Annual Avg:    3715.5 cases per region
```

## Database Structure

### Granularity Field

All synthetic records include a `granularity` field:

- **Yearly (original)**: No `granularity` field
- **Monthly**: `"granularity": "monthly"`
- **Weekly**: `"granularity": "weekly"`

### Filtering in API

Services and routes can filter by granularity:

```python
# Get only original yearly data
yearly_data = cases_col.find({
    "disease": "DENGUE",
    "granularity": {"$exists": False}
})

# Get monthly synthetic data
monthly_data = cases_col.find({
    "disease": "DENGUE",
    "granularity": "monthly"
})

# Get weekly synthetic data
weekly_data = cases_col.find({
    "disease": "DENGUE",
    "granularity": "weekly"
})
```

## Data Summary

| Granularity         | Records   | Coverage                         | Date Format  |
| ------------------- | --------- | -------------------------------- | ------------ |
| Yearly (original)   | 144       | 36 regions × 4 years             | `2018-01-01` |
| Monthly (synthetic) | 1,728     | 36 regions × 4 years × 12 months | `2018-01-15` |
| Weekly (synthetic)  | 7,092     | 36 regions × 4 years × 52 weeks  | `2018-01-04` |
| **Total**           | **8,964** |                                  |              |

## Use Cases

1. **Forecasting**: Monthly/weekly data provides meaningful time-series patterns
2. **Seasonality Analysis**: Visualize monsoon impact on dengue transmission
3. **Alert Systems**: Weekly granularity enables early outbreak detection
4. **Risk Modeling**: Temporal patterns improve risk score computation
5. **Dashboard**: Display realistic outbreak curves instead of flat yearly totals

## Technical Details

### Date Offsets

To avoid unique key conflicts in MongoDB:

- **Monthly**: Uses 15th of each month (`2018-01-15`)
- **Weekly**: Starts on Jan 4th (`2018-01-04`), increments by 7 days
- **Yearly**: Uses Jan 1st (`2018-01-01`)

### Randomness

- **Monthly**: ±20% variance
- **Weekly**: ±30% variance
- Ensures realistic fluctuations while preserving seasonality trends

### Database Index

Unique index on `(region_id, date)` prevents duplicates but allows different granularities at non-overlapping dates.

## Next Steps

1. ✅ Generate monthly synthetic data
2. ✅ Generate weekly synthetic data
3. ✅ Visualize seasonality patterns
4. 🔄 Update forecasting service to use monthly/weekly data
5. 🔄 Add granularity selector in dashboard
6. 🔄 Run pipeline on monthly data for better forecasts
7. 🔄 Create similar synthetic generators for COVID data

## References

- Seasonality weights based on India monsoon patterns (Jun-Sep peak)
- Dengue transmission peaks during and after rainfall
- Weekly variance reflects reporting delays and outbreak clusters
- Monthly data provides good balance between granularity and noise
