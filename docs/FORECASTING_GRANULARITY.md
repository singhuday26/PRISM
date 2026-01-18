# Forecasting with Multiple Granularities

## Overview

The PRISM forecasting service now supports **multiple data granularities** for generating predictions:

- **Yearly**: Original yearly data (3 years lookback)
- **Monthly**: Synthetic monthly data (6 months lookback) - **RECOMMENDED**
- **Weekly**: Synthetic weekly data (12 weeks lookback)

## Why Granularity Matters

Different granularities provide different trade-offs:

| Granularity   | Lookback | Pros                           | Cons                           | Best For               |
| ------------- | -------- | ------------------------------ | ------------------------------ | ---------------------- |
| **Yearly**    | 3 years  | Long-term trends, stable       | Too coarse, misses seasonality | Annual planning        |
| **Monthly** ✓ | 6 months | Captures seasonality, balanced | -                              | Most forecasting tasks |
| **Weekly**    | 12 weeks | High resolution, recent trends | More noise, less stable        | Short-term alerts      |

## API Usage

### Generate Forecasts with Granularity

```bash
# Using monthly data (recommended)
POST /forecasts/generate?disease=DENGUE&granularity=monthly&horizon=7

# Using weekly data for high-resolution forecasts
POST /forecasts/generate?disease=DENGUE&granularity=weekly&horizon=7

# Using yearly data for long-term trends
POST /forecasts/generate?disease=DENGUE&granularity=yearly&horizon=7
```

### Response Format

```json
{
  "date": "2021-11-15",
  "forecasts": [
    {
      "region_id": "IN-AP",
      "date": "2021-11-16",
      "pred_mean": 435.8,
      "pred_lower": 392.2,
      "pred_upper": 479.4,
      "model_version": "naive_v2",
      "source_granularity": "monthly",
      "disease": "DENGUE"
    }
  ],
  "count": 252,
  "horizon": 7,
  "granularity": "monthly"
}
```

## CLI Usage

### Running Pipeline with Granularity

```bash
# Run pipeline with monthly data (default)
python run_pipeline.py 2021-11-15 7 DENGUE monthly

# Run pipeline with weekly data
python run_pipeline.py 2021-11-04 7 DENGUE weekly

# Run pipeline with yearly data
python run_pipeline.py 2021-01-01 7 DENGUE yearly
```

### CLI Arguments

```
python run_pipeline.py <target_date> <horizon> <disease> <granularity>

Arguments:
  target_date   Date to run pipeline for (YYYY-MM-DD), default: 2021-01-01
  horizon       Forecast horizon in days, default: 7
  disease       Disease filter (optional), e.g., DENGUE
  granularity   Data granularity (yearly|monthly|weekly), default: monthly
```

## Forecast Quality Comparison

### Sample Results (IN-AP, Dengue, Aug 2021)

```
Granularity     Mean Forecast        Range
yearly            3370.3 ██████████████████████████████ [3033.3 - 3707.4]
monthly            435.8 ██████████████████████████████ [392.2 - 479.4]  ✓ RECOMMENDED
weekly             152.8 ███████████████                [137.6 - 168.1]
```

**Analysis:**

- **Monthly forecasts** capture seasonal patterns from 6 months of history
- **Weekly forecasts** show more variance due to random fluctuations
- **Yearly forecasts** miss monthly seasonality, averaging across full year

### Running the Comparison

```bash
python -m backend.scripts.compare_forecast_granularity
```

## Model Updates

### Version 2 (Current)

- **Model Version**: `naive_v2`
- **Improvements**:
  - Added granularity parameter
  - Configurable lookback periods
  - Tracks source granularity in forecast records
  - Better handling of seasonal data

### Lookback Configuration

```python
LOOKBACK_CONFIG = {
    "yearly": 3,    # 3 years of history
    "monthly": 6,   # 6 months of history
    "weekly": 12,   # 12 weeks of history
}
```

## Implementation Details

### Service Layer (`backend/services/forecasting.py`)

```python
from backend.services.forecasting import generate_forecasts

# Generate forecasts with monthly data
date, forecasts = generate_forecasts(
    target_date="2021-11-15",
    horizon=7,
    disease="DENGUE",
    granularity="monthly"  # NEW parameter
)
```

### Route Layer (`backend/routes/forecasts.py`)

```python
@router.post("/generate")
def generate(
    date: Optional[str] = Query(None),
    horizon: int = Query(7, ge=1, le=30),
    disease: Optional[str] = Query(None),
    granularity: Literal["yearly", "monthly", "weekly"] = Query("monthly")
):
    # ... implementation
```

## Best Practices

### Choosing Granularity

1. **For most use cases**: Use `monthly` (default)
   - Captures seasonal patterns
   - Balanced signal-to-noise ratio
   - 6 months of history provides context

2. **For short-term alerts**: Use `weekly`
   - Recent trends emphasized
   - High temporal resolution
   - Good for outbreak detection

3. **For annual planning**: Use `yearly`
   - Long-term stable trends
   - Less affected by short-term noise
   - Useful for capacity planning

### Data Requirements

Ensure synthetic data is generated before using monthly/weekly granularities:

```bash
# Generate monthly data
python -m backend.scripts.generate_synthetic_dengue monthly --reset

# Generate weekly data
python -m backend.scripts.generate_synthetic_dengue weekly --reset
```

## Dashboard Integration

The dashboard automatically uses monthly granularity for forecasts when displaying dengue data. This provides users with:

- Realistic temporal patterns
- Seasonal outbreak curves
- More accurate predictions than yearly averages

## Future Improvements

Potential enhancements:

1. ✅ Add granularity parameter _(DONE)_
2. ✅ Configure lookback by granularity _(DONE)_
3. 🔄 Add granularity selector in dashboard UI
4. 🔄 Implement ARIMA/SARIMA models for monthly data
5. 🔄 Add ensemble forecasts combining multiple granularities
6. 🔄 Automatic granularity selection based on data availability

## References

- Synthetic data generation: [SYNTHETIC_DATA.md](SYNTHETIC_DATA.md)
- Monsoon seasonality patterns for dengue forecasting
- Model version tracking for forecast reproducibility
