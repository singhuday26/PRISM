# PRISM (Predictive Risk Intelligence & Surveillance Model)

Early outbreak warning and hotspot forecasting prototype using Python + MongoDB + FastAPI + React + Streamlit.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)
[![React 19](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Vite 7](https://img.shields.io/badge/Vite-7-646cff.svg)](https://vite.dev/)

## Features

✅ **Real-time Risk Assessment** — Compute risk scores based on case data  
✅ **Automated Alerts** — Generate alerts for high-risk regions  
✅ **Hotspot Detection** — Identify regions with highest case counts  
✅ **ARIMA Forecasting** — Predict future trends with configurable horizon  
✅ **Multi-Disease Support** — Isolate and manage DENGUE, COVID, and more  
✅ **RESTful API** — 20+ endpoints with automatic Swagger documentation  
✅ **React Frontend** — Interactive map (Leaflet), charts (Recharts), resource planning  
✅ **Streamlit Dashboard** — Pipeline runner, hotspot viewer, CSV export  
✅ **Resource Prediction** — Bed, ICU, nurse, and oxygen demand estimation  
✅ **PDF Reporting** — Automated weekly/monthly report generation  
✅ **Notification System** — Email + SMS (stub) alert dispatching  
✅ **Climate-Aware Risk** — Weather boost factors for seasonal diseases  
✅ **Comprehensive Logging** — Rotating logs with separate error file  
✅ **Health Monitoring** — Database connectivity and collection count checks

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and set MONGO_URI
```

### 3. Start PRISM (All Services)

**Option A - One Command (Recommended)**:

```bash
python start_prism.py
```

This starts both the API and Dashboard automatically!

**Option B - Separate Services**:

**Terminal 1 - API Server**:

```bash
python -m uvicorn backend.app:app --reload
```

**Terminal 2 - Dashboard**:

```bash
python run_dashboard.py
```

### 4. Access Web Interfaces

- **�️ React Frontend**: http://localhost:8000/ui/
- **📊 Streamlit Dashboard**: http://localhost:8501
- **🔌 API Documentation**: http://localhost:8000/docs
- **⚕️ Health Check**: http://localhost:8000/health

See [Web Interface Guide](docs/WEB_INTERFACE_GUIDE.md) for detailed instructions.

### 5. Build the React Frontend (optional — pre-built dist is committed)

```bash
cd frontend
npm install
npm run build
cd ..
```

The production build is served at `/ui/` by the FastAPI backend.

## Project Structure

- `backend/app.py` – FastAPI application with CORS, error handling, static mount
- `backend/config.py` – Environment-driven settings with validation
- `backend/db.py` – MongoDB client with connection pooling and retries
- `backend/disease_config.py` – Per-disease parameters (thresholds, seasonality)
- `backend/logging_config.py` – Centralized logging configuration
- `backend/schemas/` – Pydantic v2 models for data validation
- `backend/services/` – Business logic (risk, alerts, forecasting, ARIMA, resources, notifications, reports)
- `backend/routes/` – 13 API routers with 20+ endpoints
- `backend/dashboard/` – Streamlit UI (charts, theme)
- `backend/scripts/` – 15 database seeding, CSV loading, and maintenance utilities
- `backend/utils/` – Validators, climate boost factors
- `frontend/` – React 19 + Vite 7 + TypeScript 5 + TailwindCSS 4 + Leaflet + Recharts
- `tests/` – pytest unit and integration tests (Vitest for frontend)
- `docs/` – Feature documentation and planning

## Documentation

- **[Web Interface Guide](docs/WEB_INTERFACE_GUIDE.md)** - Dashboard and API access
- **[Multi-Disease Guide](docs/MULTI_DISEASE_GUIDE.md)** - Multi-disease support and management
- **[Security Best Practices](SECURITY.md)** - Security guidelines and configuration
- **[Development Guide](DEVELOPMENT.md)** - Setup, testing, and development workflow
- **[Quick Start](QUICKSTART.md)** - Fast track to get PRISM running

## API Endpoints

### Health

- `GET /health/ping` - Simple health check
- `GET /health/` - Comprehensive health check with DB status

### Regions

- `GET /regions/` - List all regions with counts

### Diseases

- `GET /diseases/` - List all loaded diseases with metadata

### Risk Assessment

- `POST /risk/compute?target_date=YYYY-MM-DD` - Compute risk scores
- `GET /risk/latest?region_id=<id>&disease=<d>` - Get latest risk scores
- `GET /risk/geojson?disease=<d>` - Risk scores as GeoJSON FeatureCollection

### Alerts

- `POST /alerts/generate?date=YYYY-MM-DD` - Generate alerts from risk scores
- `GET /alerts/latest?region_id=<id>&disease=<d>&limit=20` - Get latest alerts

### Hotspots

- `GET /hotspots/?limit=5&disease=<d>` - Get top regions by confirmed cases

### Forecasts

- `POST /forecasts/generate?date=YYYY-MM-DD&horizon=7` - Generate forecasts
- `GET /forecasts/latest?region_id=<id>&disease=<d>&horizon=7` - Get latest forecasts

### Pipeline

- `POST /pipeline/run?disease=DENGUE` - Run full compute pipeline
- `GET /pipeline/status` - Pipeline status and last run info

### Evaluation

- `GET /evaluation/forecast?region_id=<id>` - Forecast accuracy (MAE/MAPE)
- `GET /evaluation/summary` - Aggregate model evaluation

### Resources

- `POST /resources/predict` - Predict bed/ICU/nurse/oxygen demand
- `GET /resources/config?disease=<d>` - Resource allocation parameters

### Reports

- `POST /reports/generate` - Generate PDF report
- `GET /reports/list` - List generated reports

### Notifications

- `POST /notifications/subscribe` - Subscribe to alerts
- `POST /notifications/unsubscribe` - Unsubscribe
- `GET /notifications/preferences` - Get notification preferences

### GeoJSON

- `GET /geojson/regions` - Region boundaries as GeoJSON

## Environment Variables

### Required

- `MONGO_URI` - MongoDB connection string

### Optional

- `DB_NAME` - Database name (default: `prism_db`)
- `API_HOST` - Host to bind (default: `0.0.0.0`)
- `API_PORT` - Port to bind (default: `8000`)
- `LOG_LEVEL` - Logging level (default: `INFO`)
- `RISK_HIGH_THRESHOLD` - Alert threshold (default: `0.7`)
- `ENABLE_CORS` - Enable CORS (default: `true`)
- `CORS_ORIGINS` - Allowed origins (default: `*`)

See [.env.example](.env.example) for all options.

## Data Loading

### Seed Sample Data

```bash
python -m backend.scripts.seed
```

### Load CSV Data

```bash
python -m backend.scripts.load_csv Datasets/covid_19_data.csv
```

CSV format: `region_id,date,confirmed,deaths,recovered`

## Logging

Logs are written to:

- `logs/prism.log` - All application logs
- `logs/prism_errors.log` - Errors only

Configure via `LOG_LEVEL` environment variable.

## Error Handling

All endpoints include:

- Input validation with detailed error messages
- Database error handling with graceful degradation
- Comprehensive logging for debugging
- Appropriate HTTP status codes

## Database Indexes

Automatically created on startup for optimal performance:

- `regions.region_id` (unique)
- `cases_daily.region_id + date` (unique)
- `forecasts_daily.region_id + date`
- `risk_scores.date + risk_score`
- `alerts.date + risk_score`

## Security

- Environment variable validation on startup
- CORS configuration for cross-origin requests
- MongoDB connection pooling and timeouts
- No sensitive data in logs
- See [SECURITY.md](SECURITY.md) for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Submit a pull request

## License

MIT License - See LICENSE file for details
