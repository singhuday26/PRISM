# Development Guide

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher (for React frontend)
- MongoDB 4.4 or higher (local or Atlas)
- Git

### Initial Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd PRISM
   ```

2. **Create virtual environment**

   ```bash
   python -m venv .venv

   # Windows
   .\.venv\Scripts\activate

   # Unix/MacOS
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env and set MONGO_URI
   ```

5. **Verify installation**

   ```bash
   python -c "import fastapi, pymongo, pydantic; print('All dependencies installed!')"
   ```

6. **Build React frontend**
   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

## Running the Application

### Development Server

```bash
uvicorn backend.app:app --reload --log-level debug
```

### Production Server

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4
```

### Dashboard

```bash
streamlit run backend/dashboard/app.py
```

## Database Setup

### MongoDB Atlas (Cloud)

1. Create free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create database user
3. Whitelist IP address
4. Copy connection string to `MONGO_URI`

### Local MongoDB

```bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data

# Set MONGO_URI in .env
MONGO_URI=mongodb://localhost:27017
```

## Loading Data

### Seed Sample Data

```bash
python -m backend.scripts.seed
```

### Load CSV Data

```bash
python -m backend.scripts.load_csv Datasets/covid_19_data.csv
```

CSV must have columns: `region_id,date,confirmed,deaths,recovered`

### Create Indexes

```bash
python -m backend.scripts.create_indexes
```

## Testing

### Backend Tests (pytest)

```bash
# Run all tests
python -m pytest tests/ -v

# Run unit tests only
python -m pytest tests/unit/ -v

# Run integration tests only
python -m pytest tests/integration/ -v

# Run with coverage
python -m pytest --cov=backend --cov-report=term-missing
```

Test structure:

- `tests/unit/` — Unit tests for services (risk, alerts, forecasting, ARIMA, analytics, notifications, etc.)
- `tests/integration/` — Integration tests for all API routes (health, regions, diseases, risk, alerts, forecasts, pipeline, reports, resources, notifications, evaluation)
- `tests/test_multi_disease_isolation.py` — Verifies disease isolation between DENGUE and COVID pipelines

### Frontend Tests (Vitest)

```bash
cd frontend
npm test          # Run once
npm run test:watch  # Watch mode
```

Frontend test files:

- `src/test/ErrorBoundary.test.tsx` — Error boundary component tests
- `src/test/api.test.ts` — API URL construction and fetch mock tests
- `src/test/pages.test.tsx` — Smoke tests for all page components

### Manual API Testing

Visit http://localhost:8000/docs for interactive API documentation (Swagger UI)

### Health Check

```bash
curl http://localhost:8000/health/
```

### Example API Calls

```bash
# List regions
curl http://localhost:8000/regions/

# Compute risk scores
curl -X POST http://localhost:8000/risk/compute

# Get latest risk scores
curl http://localhost:8000/risk/latest

# Generate alerts
curl -X POST http://localhost:8000/alerts/generate

# Get hotspots
curl http://localhost:8000/hotspots/?limit=10
```

## Code Style

### Python Standards

- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for functions and classes

### Import Order

1. Standard library imports
2. Third-party imports
3. Local application imports

Example:

```python
import logging
from typing import Optional

from fastapi import APIRouter
from pymongo import DESCENDING

from backend.db import get_db
```

## Common Tasks

### Adding a New Route

1. Create route file in `backend/routes/`
2. Import and register in `backend/app.py`
3. Add error handling and logging
4. Add input validation

### Adding a New Service

1. Create service file in `backend/services/`
2. Add comprehensive error handling
3. Add logging for key operations
4. Import and use in routes

### Adding a New Schema

1. Create schema in `backend/schemas/`
2. Use Pydantic models with validation
3. Add field descriptions and constraints

## Troubleshooting

### MongoDB Connection Issues

- Verify MongoDB is running
- Check connection string format
- Verify network access/firewall
- Check credentials

### Missing Dependencies

```bash
pip install -r requirements.txt --force-reinstall
```

### Port Already in Use

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Unix/MacOS
lsof -ti:8000 | xargs kill -9
```

### Import Errors

- Ensure virtual environment is activated
- Run from project root directory
- Use `python -m` for module execution

## Project Structure

```
PRISM/
├── backend/
│   ├── app.py              # FastAPI application (CORS, static mount, lifespan)
│   ├── config.py           # Environment-driven configuration
│   ├── db.py               # MongoDB client with connection pooling
│   ├── disease_config.py   # Per-disease parameters and thresholds
│   ├── exceptions.py       # Custom exception classes
│   ├── logging_config.py   # Rotating log configuration
│   ├── routes/             # 13 API routers (health, regions, diseases, risk, alerts, hotspots, forecasts, pipeline, evaluation, resources, reports, notifications, geojson)
│   ├── schemas/            # Pydantic v2 validation models
│   ├── services/           # Business logic (risk, alerts, forecasting, ARIMA, analytics, resources, notifications, reports, email, geojson, ingestion)
│   ├── scripts/            # 15 data loading and maintenance utilities
│   ├── dashboard/          # Streamlit UI (app, charts, theme)
│   ├── templates/          # Report templates
│   └── utils/              # Validators, climate boost factors
├── frontend/               # React 19 + Vite 7 + TypeScript 5.9 + TailwindCSS 4
│   ├── src/
│   │   ├── components/     # Reusable components (OperationalMap, BedShortageWidget, ErrorBoundary, Layout)
│   │   ├── pages/          # Page views (Dashboard, Analysis, Resources, Reports, Settings)
│   │   ├── lib/            # API client with typed interfaces
│   │   └── test/           # Vitest tests (ErrorBoundary, api, pages)
│   ├── vite.config.ts      # Build, dev proxy, and test configuration
│   └── dist/               # Production build (served at /ui/)
├── tests/                  # pytest test suite
│   ├── unit/               # Service-level unit tests
│   └── integration/        # API route integration tests
├── Datasets/               # Sample CSV data files
├── docs/                   # Feature documentation and planning
├── logs/                   # Application logs (auto-created)
├── generated_reports/      # PDF reports (auto-created)
├── .env                    # Environment variables (create from .env.example)
├── .env.example            # Example environment config
├── requirements.txt        # Python dependencies
├── start_prism.py          # One-command startup (API + Dashboard)
├── run_pipeline.py         # CLI pipeline runner
├── disease_manager.py      # Multi-disease data management CLI
└── README.md               # Project overview
```
