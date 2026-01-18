# Multi-Disease Support Guide

## 🎯 Overview

PRISM now supports comprehensive multi-disease surveillance and forecasting. The system comes pre-configured with **10 diseases** and can easily be extended to support additional diseases.

## 📋 Pre-Configured Diseases

### Vector-Borne Diseases

- **Dengue Fever** - Mosquito-borne viral disease
- **Malaria** - Parasitic disease transmitted by Anopheles mosquitoes
- **Chikungunya** - Viral disease causing fever and joint pain
- **Japanese Encephalitis** - Viral brain infection

### Airborne Diseases

- **COVID-19** - SARS-CoV-2 respiratory illness
- **Tuberculosis** - Bacterial lung infection
- **Influenza** - Seasonal flu
- **Measles** - Highly contagious viral disease

### Waterborne Diseases

- **Cholera** - Bacterial diarrheal disease
- **Typhoid Fever** - Salmonella typhi infection

## 🏗️ Architecture

### Disease Schema

Each disease has a comprehensive profile including:

- **Identification**: ID, name, ICD code
- **Epidemiology**: R₀, case fatality rate, incubation period
- **Transmission**: Mode (vector, airborne, waterborne, etc.)
- **Climate Sensitivity**: Temperature, rainfall, humidity
- **Medical Info**: Vaccine and treatment availability
- **Alert Configuration**: Risk thresholds

### Registry System

All diseases are registered in a central `DiseaseRegistry` that provides:

- Lookup by ID
- Filtering by transmission mode
- Filtering by severity
- Metadata management

## 🛠️ Using the Disease Manager CLI

### List All Diseases

```bash
python disease_manager.py list
```

Shows all configured diseases grouped by transmission mode with severity indicators.

### Get Disease Details

```bash
python disease_manager.py info DENGUE
```

Shows comprehensive disease profile including:

- Epidemiological parameters
- Climate sensitivity
- Current database status
- Data availability

### Load Disease Data

```bash
# Example: Load COVID data
python disease_manager.py load COVID data/covid.csv \
  --region "State/UT" \
  --confirmed "Confirmed" \
  --deaths "Deaths" \
  --recovered "Recovered" \
  --date "Date"

# Example: Load Malaria data (yearly)
python disease_manager.py load MALARIA data/malaria.csv \
  --region "State" \
  --confirmed "Cases" \
  --deaths "Deaths" \
  --year "Year"
```

### Compare All Diseases

```bash
python disease_manager.py compare
```

Shows side-by-side comparison of all diseases with available data.

## 📡 API Endpoints

### Disease Management

#### List All Diseases

```http
GET /diseases
```

**Query Parameters:**

- `transmission_mode` - Filter by transmission (vector, airborne, waterborne, etc.)
- `severity` - Filter by severity (low, moderate, high, critical)
- `vaccine_available` - Filter by vaccine availability (true/false)

**Example:**

```bash
curl "http://localhost:8000/diseases?transmission_mode=vector&vaccine_available=true"
```

#### Get Disease Profile

```http
GET /diseases/{disease_id}
```

**Example:**

```bash
curl http://localhost:8000/diseases/DENGUE
```

**Response:**

```json
{
  "disease_id": "DENGUE",
  "name": "Dengue Fever",
  "description": "Mosquito-borne viral disease causing fever, rash, and joint pain",
  "transmission_mode": "vector",
  "severity": "moderate",
  "r0_estimate": 2.5,
  "case_fatality_rate": 0.01,
  "temperature_sensitive": true,
  "vaccine_available": true
}
```

#### Get Disease Statistics

```http
GET /diseases/{disease_id}/stats
```

Returns database statistics including:

- Total cases, deaths, recovered
- Affected regions
- Date range
- Data availability status

**Example:**

```bash
curl http://localhost:8000/diseases/DENGUE/stats
```

#### Compare Multiple Diseases

```http
GET /diseases/compare/multiple?disease_ids=DENGUE,COVID,MALARIA
```

Side-by-side comparison with epidemiological data and current case counts.

#### List by Transmission Mode

```http
GET /diseases/transmission/{mode}
```

Modes: `vector`, `airborne`, `waterborne`, `contact`, `foodborne`, `zoonotic`

**Example:**

```bash
curl http://localhost:8000/diseases/transmission/vector
```

### Disease Filtering in Existing Endpoints

All existing PRISM endpoints now support the `?disease=DISEASE_ID` parameter:

```http
GET /risk/latest?disease=COVID
GET /alerts/latest?disease=MALARIA
GET /forecasts/latest?disease=DENGUE&horizon=7
GET /hotspots?disease=CHOLERA
GET /regions?disease=TUBERCULOSIS
```

## 🔧 Adding a New Disease

### 1. Add Disease Profile

Edit `backend/config/disease_config.py`:

```python
registry.add_disease(DiseaseProfile(
    disease_id="EBOLA",
    name="Ebola Virus Disease",
    description="Severe viral hemorrhagic fever",
    transmission_mode=TransmissionMode.CONTACT,
    incubation_period_days=10,
    severity=Severity.CRITICAL,
    r0_estimate=2.0,
    case_fatality_rate=0.50,
    temperature_sensitive=False,
    rainfall_sensitive=False,
    humidity_sensitive=False,
    alert_threshold_multiplier=1.1,
    high_risk_case_threshold=10,
    data_sources=["WHO Ebola Database"],
    icd_code="A98.4",
    vaccine_available=True,
    treatment_available=True
))
```

### 2. Load Disease Data

```bash
python disease_manager.py load EBOLA data/ebola.csv \
  --region "Country" \
  --confirmed "Cases" \
  --deaths "Deaths" \
  --date "Date"
```

### 3. Verify Integration

```bash
# Check disease info
python disease_manager.py info EBOLA

# Test API
curl http://localhost:8000/diseases/EBOLA/stats

# Run pipeline
python run_pipeline.py 2024-01-01 7 EBOLA
```

## 📊 Data Format Requirements

### CSV Structure

Your disease data CSV should have:

- **Region column**: State, district, or region name
- **Date/Year column**: ISO format (YYYY-MM-DD) or year
- **Confirmed cases**: Numeric
- **Deaths**: Numeric
- **Recovered** (optional): Numeric

**Example (Daily Data):**

```csv
State/UT,Date,Confirmed,Deaths,Recovered
Maharashtra,2024-01-01,150,5,120
Delhi,2024-01-01,89,2,75
```

**Example (Yearly Data):**

```csv
State/UT,Year,Cases,Deaths
Maharashtra,2023,1500,50
Delhi,2023,890,20
```

## 🎨 Dashboard Integration

The PRISM dashboard automatically:

1. Fetches available diseases via `/regions/diseases`
2. Populates disease dropdown
3. Filters all visualizations by selected disease
4. Updates in real-time when disease selection changes

No dashboard code changes needed - it's fully automatic!

## 🔬 Disease-Specific Risk Modeling

Each disease uses its configured parameters for:

### Alert Generation

```python
threshold = baseline * alert_threshold_multiplier
if cases > threshold or cases > high_risk_case_threshold:
    generate_alert()
```

### Climate-Aware Risk

- Temperature-sensitive diseases get boosted risk in hot weather
- Rainfall-sensitive diseases get boosted risk in monsoon
- Humidity-sensitive diseases get adjusted risk scores

### Forecasting

- Uses disease-specific seasonality patterns
- Accounts for incubation period
- Adjusts for R₀ estimates

## 📈 Best Practices

### Data Loading

1. **Always verify disease exists first**: `python disease_manager.py list`
2. **Check data format matches**: Use `--help` for column options
3. **Load incrementally**: Start with small dataset to verify
4. **Monitor logs**: Check for warnings about invalid data

### Multi-Disease Analysis

1. **Use compare endpoint** for cross-disease insights
2. **Filter by transmission mode** to group similar diseases
3. **Check severity levels** when prioritizing resources
4. **Consider climate sensitivity** for seasonal planning

### Performance

- Index on `disease` field is automatically created
- Queries filtered by disease are highly efficient
- Use disease-specific endpoints when possible
- Batch load data rather than individual records

## 🧪 Testing

### Run Multi-Disease Test Suite

```bash
python test_multi_disease.py
```

Tests:

- Disease listing and filtering
- Profile retrieval
- Statistics computation
- Multi-disease comparison
- Integration with existing endpoints

### Manual Testing Checklist

- [ ] List all diseases
- [ ] Get disease profile
- [ ] Get disease statistics
- [ ] Filter by transmission mode
- [ ] Filter by severity
- [ ] Compare multiple diseases
- [ ] Load new disease data
- [ ] Verify filtering in dashboard
- [ ] Run pipeline for specific disease
- [ ] Export disease-specific reports

## 🚀 Advanced Features

### Custom Disease Profiles

Create disease-specific alerting rules:

```python
if disease.transmission_mode == TransmissionMode.VECTOR:
    # Check rainfall and temperature
    apply_vector_risk_model()
elif disease.transmission_mode == TransmissionMode.AIRBORNE:
    # Check humidity and population density
    apply_airborne_risk_model()
```

### Data Source Integration

Each disease can specify multiple data sources:

```python
data_sources=[
    "National Health Portal",
    "WHO Disease Database",
    "State Health Departments"
]
```

### Vaccine & Treatment Tracking

```python
if disease.vaccine_available:
    show_vaccination_recommendations()
if disease.treatment_available:
    show_treatment_guidelines()
```

## 📚 Related Documentation

- [DISEASE_AGNOSTIC_SUMMARY.md](../DISEASE_AGNOSTIC_SUMMARY.md) - Original disease-agnostic design
- [QUICKSTART.md](../QUICKSTART.md) - Getting started with PRISM
- [README.md](../README.md) - Full system documentation

## ❓ FAQ

**Q: Can I add a disease not in the pre-configured list?**
A: Yes! Add it to `disease_config.py` and load data using `disease_manager.py load`.

**Q: Do I need to restart the API after adding a disease?**
A: Yes, restart the backend to load the new disease profile.

**Q: Can I use the same region for multiple diseases?**
A: Yes! Regions can have data for multiple diseases simultaneously.

**Q: What if my disease doesn't fit the schema?**
A: Use default values for optional fields. The system is flexible.

**Q: How do I remove a disease?**
A: Remove from `disease_config.py` and restart. Historical data remains in DB.

## 🎯 Next Steps

1. ✅ Load data for additional diseases
2. ✅ Test multi-disease comparisons
3. ✅ Configure disease-specific alert rules
4. ✅ Set up automated data ingestion
5. ✅ Create disease-specific dashboards
6. ✅ Export multi-disease reports

---

**Need help?** Check the main README or run `python disease_manager.py --help`
