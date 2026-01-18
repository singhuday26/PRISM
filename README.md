# PRISM (Predictive Risk Intelligence & Surveillance Model)

Early outbreak warning and hotspot forecasting prototype using Python + MongoDB + FastAPI + Streamlit.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)

## Features

✅ **Real-time Risk Assessment** - Compute risk scores based on case data  
✅ **Automated Alerts** - Generate alerts for high-risk regions  
✅ **Hotspot Detection** - Identify regions with highest case counts  
✅ **Forecasting** - Predict future trends with configurable horizon  
✅ **RESTful API** - Comprehensive API with automatic documentation  
✅ **Interactive Dashboard** - Streamlit-based visualization  
✅ **Comprehensive Logging** - Detailed logs with rotation  
✅ **Error Handling** - Robust error handling throughout  
✅ **Health Monitoring** - Database connectivity checks

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

### 3. Run API Server

```bash
uvicorn backend.app:app --reload
```

Visit http://localhost:8000/docs for API documentation.

### 4. Run Dashboard (Optional)

```bash
streamlit run backend/dashboard/app.py
```

## Project Structure

- `backend/app.py` – FastAPI application with CORS and error handling
- `backend/config.py` – Environment-driven settings with validation
- `backend/db.py` – MongoDB client with connection pooling and retries
- `backend/logging_config.py` – Centralized logging configuration
- `backend/schemas/` – Pydantic models for data validation
- `backend/services/` – Business logic for ingestion, analytics, and forecasting
- `backend/routes/` – API endpoints with error handling
- `backend/dashboard/` – Streamlit UI
- `backend/scripts/` – Database seeding and CSV loading utilities

## Documentation

- [Security Best Practices](SECURITY.md) - Security guidelines and configuration
- [Development Guide](DEVELOPMENT.md) - Setup, testing, and development workflow

## API Endpoints

### Health

- `GET /health/ping` - Simple health check
- `GET /health/` - Comprehensive health check with DB status

### Regions

- `GET /regions/` - List all regions with counts

### Risk Assessment

- `POST /risk/compute?target_date=YYYY-MM-DD` - Compute risk scores
- `GET /risk/latest?region_id=<id>` - Get latest risk scores

### Alerts

- `POST /alerts/generate?date=YYYY-MM-DD` - Generate alerts from risk scores
- `GET /alerts/latest?region_id=<id>&limit=20` - Get latest alerts

### Hotspots

- `GET /hotspots/?limit=5` - Get top regions by confirmed cases

### Forecasts

- `POST /forecasts/generate?date=YYYY-MM-DD&horizon=7` - Generate forecasts
- `GET /forecasts/latest?region_id=<id>&horizon=7` - Get latest forecasts

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
