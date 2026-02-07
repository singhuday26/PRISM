<!-- Session Manager Metadata
session_id: 20260207-015954_prism-product-development-overview
original_file: radiant-stargazing-dijkstra.md
saved_at: 2026-02-07T01:59:54.779475
original_modified: 2026-02-06T18:49:16.663461
-->

# PRISM Product Development Overview

## What is PRISM?

**PRISM (Predictive Risk Intelligence & Surveillance Model)** is a full-stack disease surveillance and early warning system designed to detect, forecast, and alert on disease outbreaks across geographic regions.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACES                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────┐ │
│  │ React Frontend   │  │ Streamlit Dash   │  │ REST API  │ │
│  │ (Vite + TS)      │  │ (Analytics)      │  │ (FastAPI) │ │
│  │ Port: 5173/3000  │  │ Port: 8501       │  │ Swagger   │ │
│  └──────────────────┘  └──────────────────┘  └───────────┘ │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│               FASTAPI BACKEND (Port 8000)                   │
│  13 Route Modules: health, regions, hotspots, risk,         │
│  alerts, forecasts, pipeline, diseases, notifications,      │
│  reports, geojson, resources, evaluation                    │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                 SERVICES LAYER (12 modules)                 │
│  risk.py, alerts.py, forecasting.py, arima_forecasting.py,  │
│  ingestion.py, email.py, reports.py, resources.py, etc.     │
└────────────────────────────┬────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────┐
│                    MONGODB DATABASE                         │
│  Collections: regions, cases_daily, risk_scores, alerts,    │
│               forecasts_daily, disease_profiles, resources  │
│  Compound Indexes: (region_id, date, disease) for isolation │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Modules & Files

### Backend (`backend/`)

| Component          | Key Files                  | Purpose                             |
| ------------------ | -------------------------- | ----------------------------------- |
| **Entry Point**    | `app.py`                   | FastAPI app factory with middleware |
| **Configuration**  | `config.py`                | Pydantic settings, env variables    |
| **Database**       | `db.py`                    | MongoDB client, index management    |
| **Routes**         | `routes/*.py` (13 files)   | REST API endpoints                  |
| **Services**       | `services/*.py` (12 files) | Business logic layer                |
| **Schemas**        | `schemas/*.py` (6 files)   | Pydantic validation models          |
| **Disease Config** | `disease_config.py`        | 10 pre-configured diseases          |
| **Dashboard**      | `dashboard/app.py`         | Streamlit analytics UI              |

### Frontend (`frontend/`)

| Component      | Key Files              | Purpose                            |
| -------------- | ---------------------- | ---------------------------------- |
| **Entry**      | `src/main.tsx`         | React app bootstrap                |
| **Routing**    | `src/App.tsx`          | React Router configuration         |
| **API Client** | `src/lib/api.ts`       | Typed API functions (373 lines)    |
| **Pages**      | `src/pages/*.tsx`      | Dashboard, Analysis, Reports, etc. |
| **Components** | `src/components/*.tsx` | Map, widgets, layout               |
| **Build**      | `vite.config.ts`       | Vite + React + Tailwind            |

---

## Key Business Logic

### 1. Risk Scoring (`services/risk.py`)

- **Algorithm**: Weighted combination of growth rate (65%), volatility (25%), death ratio (10%)
- **Climate-Aware**: Monsoon multipliers (0.5-1.8) adjust risk by season
- **Levels**: LOW (<0.4) | MEDIUM (0.4-0.7) | HIGH (>=0.7)
- **Drivers**: Explains factors contributing to risk score

### 2. Forecasting (`services/forecasting.py`, `arima_forecasting.py`)

- **Naive Model v2**: Simple mean-based prediction with confidence bounds
- **ARIMA Model**: Auto-fitted time-series with seasonality support
- **Granularity**: Yearly (3yr), Monthly (6mo), Weekly (12wk)
- **Horizon**: 1-30 days forecast (default 7)

### 3. Alert System (`services/alerts.py`, `email.py`)

- **Threshold**: Triggers when risk_score >= 0.7 (configurable)
- **Channels**: Console, Email (SMTP), SMS
- **Subscriptions**: Region/disease-based subscriber management

### 4. Multi-Disease Support

- **10 Diseases**: COVID-19, Dengue, Malaria, Yellow Fever, Zika, Cholera, Ebola, Measles, Influenza, Leptospirosis
- **Metadata**: R0, CFR, incubation, transmission mode, climate sensitivity
- **Isolation**: Compound indexes prevent cross-disease data mixing

---

## Technology Stack

| Layer         | Technology                           |
| ------------- | ------------------------------------ |
| **Backend**   | Python 3.10+, FastAPI 0.110, Uvicorn |
| **Database**  | MongoDB 5.0+, PyMongo                |
| **Frontend**  | React 19, TypeScript 5.9, Vite 7.2   |
| **Styling**   | Tailwind CSS 4.1                     |
| **Charts**    | Recharts 3.7, Plotly 5.18            |
| **Maps**      | Leaflet, React-Leaflet               |
| **ML/Stats**  | statsmodels, pmdarima (ARIMA)        |
| **Reports**   | ReportLab (PDF), Pandas (CSV)        |
| **Dashboard** | Streamlit 1.31                       |
| **Testing**   | pytest, pytest-asyncio               |

---

## Current Development State

### Modified Files (In Progress - Multi-Disease Work)

- `backend/db.py` - Database index updates
- `backend/schemas/*.py` - Schema updates for disease field
- `backend/services/*.py` - Disease filtering in business logic

### New Files

- `backend/scripts/migrate_multi_disease.py` - Migration script
- `tests/test_multi_disease_isolation.py` - Isolation tests

### Cleanup Needed

- 60+ `tmpclaude-*` directories at project root (temporary files)

---

## Data Flow

```
CSV/API Data → Ingestion Service → MongoDB (cases_daily, regions)
                                          ↓
                    Risk Service ← Read 7-day window per region
                         ↓
                    Risk Scores → MongoDB (risk_scores)
                         ↓
              Alert Service ← Filter by threshold
                         ↓
                    Alerts → MongoDB (alerts) → Email/SMS
                         ↓
            Forecasting Service ← Historical data
                         ↓
                  Forecasts → MongoDB (forecasts_daily)
                         ↓
              API/Dashboard/Frontend ← Visualization
```

---

## API Endpoints Summary

| Category      | Endpoints                                           | Purpose                       |
| ------------- | --------------------------------------------------- | ----------------------------- |
| **Health**    | `GET /health/`, `/health/ping`                      | Service status                |
| **Regions**   | `GET /regions/`                                     | List regions (disease filter) |
| **Risk**      | `POST /risk/compute`, `GET /risk/latest`            | Risk scoring                  |
| **Alerts**    | `POST /alerts/generate`, `GET /alerts/latest`       | Alert management              |
| **Forecasts** | `POST /forecasts/generate`, `GET /forecasts/latest` | Predictions                   |
| **Hotspots**  | `GET /hotspots/`                                    | High-risk regions             |
| **Pipeline**  | `POST /pipeline/execute`                            | Full ETL workflow             |
| **Reports**   | `POST /reports/generate`                            | PDF/CSV reports               |
| **Diseases**  | `GET /diseases`, `GET /diseases/{id}`               | Disease profiles              |

---

## Development Recommendations

### Immediate Cleanup

1. Remove 60+ `tmpclaude-*` temporary directories
2. Complete the multi-disease isolation work (staged changes)
3. Run and fix any failing tests

### Technical Debt

1. No Docker/containerization setup
2. No CI/CD pipeline (GitHub Actions)
3. No frontend state management (Redux/Zustand)
4. Limited test coverage for frontend

### Feature Enhancements

1. Real-time WebSocket updates for alerts
2. Historical trend analysis dashboard
3. Export functionality for all data types
4. Role-based access control (RBAC)
5. API rate limiting and authentication
6. Comparative disease analytics

### Infrastructure

1. Add Docker Compose for local development
2. Add GitHub Actions for CI/CD
3. Add environment-specific configurations
4. Add database backup/restore scripts
5. Add monitoring and logging (e.g., Prometheus, Grafana)

---

## How to Run PRISM

### Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# 2. Set environment
export MONGO_URI="mongodb://localhost:27017"

# 3. Start all services
python start_prism.py
```

### Individual Services

```bash
# Backend API
uvicorn backend.app:app --reload --port 8000

# Streamlit Dashboard
streamlit run backend/dashboard/app.py

# React Frontend (dev)
cd frontend && npm run dev
```

---

## Verification

1. **API Health**: `curl http://localhost:8000/health/ping`
2. **Swagger Docs**: http://localhost:8000/docs
3. **Frontend**: http://localhost:5173 (dev) or http://localhost:8000/ui (prod)
4. **Dashboard**: http://localhost:8501
5. **Tests**: `pytest tests/ -v`

---

## Implementation Plan: Complete In-Progress Work

The multi-disease isolation work is **~90% complete**. There's one critical bug to fix and cleanup needed.

---

### Step 1: Fix Critical Bug in Test File

**File**: `tests/test_multi_disease_isolation.py`

**Problem**: The test calls `generate_forecasts()` with an invalid `region_ids` parameter that doesn't exist in the actual function signature.

**Current (BROKEN)**:
```python
dengue_forecasts = generate_forecasts(
    region_ids=[test_region],  # WRONG - parameter doesn't exist
    target_date=test_date,
    disease="DENGUE",
    horizon=7
)
```

**Fixed**:
```python
dengue_forecasts = generate_forecasts(
    target_date=test_date,
    disease="DENGUE",
    horizon=7
)
```

**Lines to fix**: 207-212, 215-220, 302, 317

---

### Step 2: Verify the Migration Script

```bash
python -c "from backend.scripts.migrate_multi_disease import migrate_existing_data; print('Script loads correctly')"
```

The migration script sets:
- `disease=null` for existing regions (disease-agnostic)
- `disease=DENGUE` for existing cases, risk_scores, alerts, forecasts

---

### Step 3: Run Tests

```bash
pytest tests/test_multi_disease_isolation.py -v
```

Expected test coverage:
- `test_cases_disease_isolation`
- `test_risk_scores_disease_isolation`
- `test_alerts_disease_isolation`
- `test_forecasts_disease_isolation`
- `test_regions_disease_metadata_isolation`
- `test_concurrent_disease_pipeline`

---

### Step 4: Clean Up Temporary Directories

Remove 97 `tmpclaude-*-cwd` directories:

```powershell
Remove-Item -Recurse -Force tmpclaude-*-cwd
```

---

### Step 5: Commit the Changes

```bash
git add backend/db.py
git add backend/schemas/*.py
git add backend/services/*.py
git add backend/scripts/migrate_multi_disease.py
git add tests/test_multi_disease_isolation.py
git commit -m "Add multi-disease data isolation support

- Add disease field to all schemas (case, forecast, region, risk_score)
- Update database indexes to compound indexes including disease
- Update all service upsert operations to include disease in filter
- Add migration script for existing data
- Add comprehensive isolation tests"
```

---

### Step 6: Verify via API

```bash
# Start API
uvicorn backend.app:app --reload

# Test disease-specific endpoints
curl "http://localhost:8000/risk/latest?disease=DENGUE"
curl "http://localhost:8000/alerts/latest?disease=COVID"
curl "http://localhost:8000/pipeline/run?disease=DENGUE"
```

---

## Summary of What's Already Complete

| Component | Status | Files |
|-----------|--------|-------|
| **Schemas** | ✅ Complete | `case.py`, `forecast_daily.py`, `region.py`, `risk_score.py` |
| **Database Indexes** | ✅ Complete | `db.py` - compound indexes with disease |
| **Services** | ✅ Complete | `ingestion.py`, `risk.py`, `alerts.py`, `forecasting.py`, `arima_forecasting.py` |
| **API Routes** | ✅ Complete | All routes support `?disease=` parameter |
| **Dashboard** | ✅ Complete | Disease selector in sidebar |
| **Migration Script** | ✅ Complete | `migrate_multi_disease.py` |
| **Tests** | ⚠️ Bug Fix Needed | `test_multi_disease_isolation.py` |
| **Cleanup** | ❌ Pending | 97 `tmpclaude-*` directories |

---

## Critical Files for This Work

| File | Action |
|------|--------|
| `tests/test_multi_disease_isolation.py` | Fix function call signature bug |
| `backend/services/forecasting.py` | Reference for correct signature |
| `backend/db.py` | Contains compound index definitions |
| `backend/scripts/migrate_multi_disease.py` | Ready to use for data migration |
