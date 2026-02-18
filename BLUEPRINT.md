# 🔬 PRISM — Complete Development Blueprint

> **Predictive Risk Intelligence & Surveillance Model**
>
> **Purpose of This Document:**
> This is your comprehensive guide to understanding every architectural decision,
> algorithm, and design pattern in PRISM. Read this FIRST before diving into code.
> It explains the WHY behind every choice so you can extend, debug, or rebuild
> any part of the system with confidence.

---

## Table of Contents

1. [Project Vision & Goals](#1-project-vision--goals)
2. [Tech Stack Decision Matrix](#2-tech-stack-decision-matrix)
3. [Architecture Deep Dive](#3-architecture-deep-dive)
4. [Project Structure Explained](#4-project-structure-explained)
5. [The Data Pipeline — End to End](#5-the-data-pipeline--end-to-end)
6. [Risk Scoring Algorithm](#6-risk-scoring-algorithm)
7. [Climate Boost System](#7-climate-boost-system)
8. [Forecasting Engine](#8-forecasting-engine)
9. [Alert & Notification System](#9-alert--notification-system)
10. [Multi-Disease Architecture](#10-multi-disease-architecture)
11. [API Design & Route Patterns](#11-api-design--route-patterns)
12. [Frontend Architecture](#12-frontend-architecture)
13. [Dashboard (Streamlit)](#13-dashboard-streamlit)
14. [Database Design](#14-database-design)
15. [Key Design Patterns](#15-key-design-patterns)
16. [Testing Strategy](#16-testing-strategy)
17. [Deployment & Operations](#17-deployment--operations)
18. [Security Model](#18-security-model)
19. [Production Checklist](#19-production-checklist)
20. [Extension Roadmap](#20-extension-roadmap)

---

## 1. Project Vision & Goals

### What PRISM Does

PRISM is a **multi-disease epidemic surveillance platform** for India that:

- Ingests epidemiological case data (CSV → MongoDB)
- Computes **risk scores** using growth rates, volatility, death ratios, and seasonal climate patterns
- Generates **automated alerts** when risk exceeds configurable thresholds
- Produces **time-series forecasts** using Naive and ARIMA/SARIMA models
- Predicts **hospital resource demand** (beds, ICU, nurses, oxygen) from forecast data
- Sends **email notifications** to subscribers matching region/disease/severity filters
- Visualizes everything through a **Streamlit dashboard** and a **React frontend** with interactive maps

### The Core Problem It Solves

```
Without PRISM:
  Epidemiologist downloads CSV → opens Excel → manually checks trends
  → writes email to health officials → weeks of delay

With PRISM:
  CSV loaded → risk auto-computed → alerts auto-generated → emails sent
  → dashboard shows heatmaps, forecasts, resource needs → minutes, not weeks
```

### Production Quality Means:

- **Type Safety**: Pydantic models validate every data boundary
- **Separation of Concerns**: Routes ≠ Services ≠ Schemas ≠ Database
- **Disease Isolation**: Every query is disease-scoped — no data leaks between diseases
- **Graceful Degradation**: Missing data produces empty results, not crashes
- **Comprehensive Logging**: Every operation is traced through rotating log files
- **Custom Exceptions**: Structured error hierarchy with serializable responses

---

## 2. Tech Stack Decision Matrix

### Why This Stack?

| Concern                | Choice                  | Why Not Alternatives?                                                                                                    |
| ---------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **API Framework**      | FastAPI                 | Auto-generates OpenAPI docs, async support, Pydantic integration. Flask is too bare-bones; Django is overkill for an API |
| **Database**           | MongoDB                 | Schema-flexible for evolving disease data. SQL would require migrations for every new disease field                      |
| **Data Validation**    | Pydantic v2             | Type-safe, auto-serialization, Settings integration. Marshmallow has weaker typing                                       |
| **Dashboard**          | Streamlit               | Zero-effort UI for data scientists. Dash requires more boilerplate. Gradio is ML-focused                                 |
| **Frontend**           | React 19 + Vite 7       | Component model, ecosystem, jobs. Vue/Svelte are great but React transfers broadly                                       |
| **CSS**                | TailwindCSS 4           | Utility-first, rapid prototyping, consistent design system. Bootstrap is heavier                                         |
| **Maps**               | Leaflet + React-Leaflet | Lightest interactive map library. Mapbox needs API keys; Google Maps costs money                                         |
| **Charts (Frontend)**  | Recharts                | React-native charting. D3 is too low-level. Chart.js needs wrappers                                                      |
| **Charts (Dashboard)** | Plotly                  | Interactive, publication-quality. Matplotlib is static only                                                              |
| **Forecasting**        | pmdarima + statsmodels  | Auto-ARIMA model selection. Prophet is heavier. Custom ML is premature                                                   |
| **PDF Reports**        | ReportLab               | Programmatic PDF generation. WeasyPrint needs system deps. FPDF is too basic                                             |
| **Testing**            | pytest                  | De facto Python standard. unittest is verbose. nose is deprecated                                                        |
| **Language**           | TypeScript (FE)         | Catches API contract bugs at compile time. Plain JS has no type safety                                                   |
| **Build Tool**         | Vite 7                  | 10–100× faster than Webpack. Native ESM. HMR in milliseconds                                                             |

### Alternatives Considered

```
Option A: Django + PostgreSQL + React
  ✅ Mature ORM, admin panel, auth built-in
  ❌ Heavy ORM for time-series data, rigid schema migrations
  ❌ Overkill for an API-first application
  Verdict: Great for CRUD apps, wrong fit for analytics

Option B: Flask + InfluxDB + Grafana
  ✅ Purpose-built time-series DB, zero-code dashboards
  ❌ InfluxDB query language is niche (Flux/InfluxQL)
  ❌ Grafana is view-only — no custom business logic UI
  Verdict: Great for monitoring, limited for domain-specific analytics

Option C: Node.js (Express) + PostgreSQL + Next.js
  ✅ Single language (JS/TS) across stack
  ❌ Python has far superior data science ecosystem (pandas, statsmodels)
  ❌ Time-series forecasting libraries in JS are immature
  Verdict: Good for web apps, wrong ecosystem for epidemiology

✅ Our Choice: FastAPI + MongoDB + React + Streamlit
  - FastAPI gives us auto-docs and Pydantic for free
  - MongoDB handles schema evolution across 10 diseases
  - Python's data science ecosystem (pandas, pmdarima) is unmatched
  - Streamlit for rapid analytics dashboards
  - React for production-quality interactive UI
  - Skills transfer: FastAPI/React are industry-standard
```

---

## 3. Architecture Deep Dive

### The Layered Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Presentation Layer                         │
│  React Frontend (maps, charts, reports)    :8000/ui/         │
│  Streamlit Dashboard (analytics, pipeline) :8501             │
├──────────────────────────────────────────────────────────────┤
│                      API Layer                               │
│  FastAPI Routes (13 routers, validation, error handling)      │
│  Shared helpers, Pydantic response models                    │
├──────────────────────────────────────────────────────────────┤
│                    Service Layer                             │
│  Business logic: risk scoring, alerting, forecasting,        │
│  email notifications, report generation, resource prediction │
├──────────────────────────────────────────────────────────────┤
│                    Utility Layer                             │
│  Validators, climate calculations, constants                 │
├──────────────────────────────────────────────────────────────┤
│                  Data Access Layer                           │
│  MongoDB client (connection pooling, retry, indexes)         │
│  Disease config registry, Pydantic schemas                   │
└──────────────────────────────────────────────────────────────┘
```

### Why This Layering Matters

**Scenario**: You want to add a new disease (e.g., Zika).

Without layering: You'd edit route files, database queries, dashboard code, and risk formulas all at once.

With layering:

1. Add Zika profile to `disease_config.py` (Data Layer)
2. Load Zika case data via `disease_manager.py load ZIKA zika_data.csv` (CLI)
3. Run the pipeline: `POST /pipeline/run?disease=ZIKA` (API Layer)
4. Services automatically compute risk, alerts, forecasts (Service Layer)
5. Dashboard and frontend auto-discover the new disease (Presentation Layer)

Each layer changes independently. **Adding a disease requires zero code changes** — just config and data.

### Data Flow (The Pipeline)

```
CSV File (Datasets/)
    │
    ├── python disease_manager.py load DENGUE data.csv
    │   └── scripts/load_dengue_data.py
    │         └── services/ingestion.py → upsert_cases() + upsert_regions()
    │
    ▼
MongoDB (cases_daily + regions)
    │
    ├── POST /pipeline/run?disease=DENGUE  ←── One-Click Pipeline
    │
    ▼
┌─ Step 1: Risk Scoring ──────────────────────────────────────────┐
│  services/risk.py → compute_risk_scores()                        │
│    ├── Query 7 days of cases_daily                               │
│    ├── Compute growth_rate, volatility, death_ratio              │
│    ├── Apply weighted formula → base_score                       │
│    ├── Apply climate multiplier (monsoon season) → adjusted_score│
│    └── Upsert to risk_scores collection                          │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ Step 2: Alert Generation ──────────────────────────────────────┐
│  services/alerts.py → generate_alerts()                          │
│    ├── Filter risk_scores ≥ threshold (0.7)                      │
│    ├── Create alert documents with reason + drivers              │
│    ├── Upsert to alerts collection                               │
│    ├── Email subscribers via services/email.py                   │
│    └── Multi-channel dispatch via services/notifications.py      │
└──────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─ Step 3: Forecasting ──────────────────────────────────────────┐
│  services/arima_forecasting.py → generate_arima_forecasts()     │
│    ├── Query historical cases (lookback by granularity)          │
│    ├── Fit ARIMA/SARIMA via pmdarima.auto_arima                  │
│    ├── Generate horizon-day predictions with 95% CI              │
│    └── Upsert to forecasts_daily collection                     │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
React Frontend / Streamlit Dashboard
    ├── GeoJSON risk heatmap (Leaflet / Plotly)
    ├── Forecast charts with confidence bands
    ├── Alert feed with severity badges
    ├── Resource demand predictions
    └── CSV / PDF report downloads
```

---

## 4. Project Structure Explained

```
PRISM/
│
├── BLUEPRINT.md                 ← You are here! The project bible.
├── README.md                    ← Quick-start guide
├── DEVELOPMENT.md               ← Developer setup & workflow
├── QUICKSTART.md                ← Fast track to running PRISM
├── SECURITY.md                  ← Security guidelines & API docs
├── CHANGES.md                   ← Changelog
│
├── requirements.txt             ← Python dependencies (42 packages)
├── pytest.ini                   ← Test configuration (markers, coverage)
├── .env.example                 ← Environment variable template
├── .gitignore                   ← Git exclusion rules
│
├── start_prism.py               ← 🚀 Main entry point (API + Dashboard)
├── disease_manager.py           ← 🦠 CLI for disease data management
├── run_pipeline.py              ← ⚡ HTTP client to trigger pipeline
├── kill_prism.ps1               ← 🛑 PowerShell script to stop services
│
├── Datasets/                    ← Raw epidemiological CSV data
│   └── Dengue_STATEWISE_DEATH_3yrs.csv
│
├── backend/                     ← ⚙️ All server-side code
│   ├── app.py                   ← FastAPI application factory
│   ├── config.py                ← Pydantic Settings (env-driven config)
│   ├── db.py                    ← MongoDB client & index management
│   ├── disease_config.py        ← Disease registry (10 diseases)
│   ├── exceptions.py            ← Custom exception hierarchy
│   ├── logging_config.py        ← Rotating file log configuration
│   │
│   ├── routes/                  ← API endpoint handlers
│   │   ├── helpers.py           ← Shared validation error handler
│   │   ├── health.py            ← GET /health/ping, /health/
│   │   ├── regions.py           ← GET /regions/
│   │   ├── hotspots.py          ← GET /hotspots/
│   │   ├── risk.py              ← POST /risk/compute, GET /risk/latest
│   │   ├── alerts.py            ← POST /alerts/generate, GET /alerts/latest
│   │   ├── forecasts.py         ← POST /forecasts/generate, GET /forecasts/latest
│   │   ├── pipeline.py          ← POST /pipeline/run (one-click)
│   │   ├── evaluation.py        ← GET /evaluation/forecast
│   │   ├── diseases.py          ← GET /diseases/
│   │   ├── notifications.py     ← POST /notifications/subscribe
│   │   ├── reports.py           ← POST /reports/generate, GET /reports/list
│   │   ├── resources.py         ← POST /resources/predict
│   │   └── geojson.py           ← GET /risk/geojson
│   │
│   ├── services/                ← Business logic (no HTTP awareness)
│   │   ├── risk.py              ← Risk scoring algorithm + climate boost
│   │   ├── alerts.py            ← Alert generation + notification trigger
│   │   ├── forecasting.py       ← Naive baseline forecaster
│   │   ├── arima_forecasting.py ← ARIMA/SARIMA forecaster
│   │   ├── analytics.py         ← Hotspot computation (aggregation)
│   │   ├── email.py             ← HTML email builder + SMTP sender
│   │   ├── notifications.py     ← Multi-channel dispatch (console/email/sms)
│   │   ├── evaluation.py        ← Forecast vs actuals (MAE, MAPE)
│   │   ├── geojson.py           ← Risk → GeoJSON feature conversion
│   │   ├── reports.py           ← PDF report generation (ReportLab)
│   │   ├── resources.py         ← Hospital resource demand prediction
│   │   └── ingestion.py         ← Data upsert (cases + regions)
│   │
│   ├── schemas/                 ← Pydantic data models
│   │   ├── case.py              ← CaseDaily model
│   │   ├── disease.py           ← DiseaseProfile, TransmissionMode enum
│   │   ├── forecast_daily.py    ← ForecastDaily model
│   │   ├── region.py            ← Region model
│   │   ├── risk_score.py        ← RiskScore model
│   │   └── responses.py         ← API response wrappers
│   │
│   ├── utils/                   ← Pure utility functions
│   │   ├── validators.py        ← Input validation (date, disease, granularity)
│   │   └── climate.py           ← Monsoon risk multiplier calculation
│   │
│   ├── dashboard/               ← Streamlit analytics dashboard
│   │   ├── app.py               ← Main dashboard (pipeline, risk, alerts, forecasts)
│   │   ├── charts.py            ← Plotly chart components
│   │   └── theme.py             ← CSS theme + color constants
│   │
│   ├── scripts/                 ← Data loading & maintenance utilities
│   │   ├── seed.py              ← Seed database with sample data
│   │   ├── seed_full.py         ← Comprehensive seeding
│   │   ├── seed_resources.py    ← Seed resource config
│   │   ├── load_csv.py          ← Generic CSV loader
│   │   ├── load_dengue_data.py  ← Dengue-specific loader
│   │   ├── load_covid_data.py   ← COVID-specific loader
│   │   ├── load_multi_disease.py← Multi-disease loader
│   │   ├── create_indexes.py    ← Manual index creation
│   │   ├── recompute_risk.py    ← Recompute all risk scores
│   │   ├── migrate_multi_disease.py ← Schema migration utility
│   │   ├── generate_synthetic_dengue.py ← Synthetic data generator
│   │   ├── simulate_outbreak.py ← Outbreak simulation
│   │   ├── compare_forecast_granularity.py ← Granularity analysis
│   │   ├── visualize_climate_risk.py ← Climate visualization
│   │   └── visualize_seasonality.py  ← Seasonality patterns
│   │
│   └── templates/               ← HTML report templates
│       └── reports/
│
├── frontend/                    ← 🎨 React web application
│   ├── package.json             ← Dependencies (React 19, Vite 7, Tailwind 4)
│   ├── vite.config.ts           ← Build config + API proxy
│   ├── tsconfig.json            ← TypeScript configuration
│   ├── index.html               ← Entry HTML
│   └── src/
│       ├── main.tsx             ← App bootstrap (StrictMode + ErrorBoundary)
│       ├── App.tsx              ← Router + Layout
│       ├── index.css            ← Global styles + CSS variables
│       ├── lib/
│       │   └── api.ts           ← Typed API client (all endpoints)
│       ├── components/
│       │   ├── layout/
│       │   │   ├── Layout.tsx   ← Sidebar + header + outlet
│       │   │   ├── Sidebar.tsx  ← Navigation menu
│       │   │   └── Header.tsx   ← Top bar
│       │   ├── OperationalMap.tsx    ← Leaflet risk heatmap
│       │   ├── BedShortageWidget.tsx ← Resource demand widget
│       │   └── ErrorBoundary.tsx     ← React error boundary
│       └── pages/
│           ├── Dashboard.tsx    ← Map + resource prediction
│           ├── Analysis.tsx     ← Forecasts + model evaluation
│           ├── Resources.tsx    ← Resource management
│           ├── Reports.tsx      ← PDF report generation
│           └── Settings.tsx     ← Configuration
│
├── tests/                       ← 🧪 Test suite
│   ├── conftest.py              ← Shared fixtures (app, client, mock_db)
│   ├── unit/                    ← Unit tests (no external deps)
│   │   ├── test_exceptions.py
│   │   ├── test_validators.py
│   │   ├── test_email_service.py
│   │   ├── test_geojson_service.py
│   │   ├── test_reports_service.py
│   │   └── test_resource_service.py
│   ├── integration/             ← Integration tests (require app)
│   │   ├── test_health_api.py
│   │   ├── test_alerts_api.py
│   │   ├── test_forecasts_api.py
│   │   └── test_risk_api.py
│   └── test_multi_disease_isolation.py
│
├── docs/                        ← 📚 Feature documentation
│   ├── MULTI_DISEASE_GUIDE.md
│   ├── WEB_INTERFACE_GUIDE.md
│   ├── WEATHER_AWARE_RISK.md
│   ├── CLIMATE_BOOST_QUICKSTART.md
│   ├── FORECASTING_GRANULARITY.md
│   ├── SYNTHETIC_DATA.md
│   ├── FEATURE_8_ONE_CLICK_PIPELINE.md
│   ├── FEATURE_9_RISK_HEATMAP.md
│   ├── FEATURE_10_CSV_EXPORT.md
│   └── planning/               ← Architectural planning docs
│
├── generated_reports/           ← PDF output (gitignored)
└── logs/                        ← Runtime logs (gitignored)
```

### Naming Conventions

| Type                | Convention                         | Example                            |
| ------------------- | ---------------------------------- | ---------------------------------- |
| Python modules      | snake_case                         | `arima_forecasting.py`             |
| Classes             | PascalCase                         | `NotificationService`              |
| Functions           | snake_case                         | `compute_risk_scores()`            |
| Constants           | UPPER_SNAKE_CASE                   | `DISEASE_REGISTRY`                 |
| Routes              | snake_case with RESTful prefixes   | `GET /risk/latest`                 |
| React components    | PascalCase                         | `OperationalMap.tsx`               |
| React hooks         | camelCase with `use` prefix        | `useState`, `useEffect`            |
| TypeScript types    | PascalCase                         | `ResourcePrediction`               |
| API client fns      | camelCase with verb prefix         | `fetchLatestForecasts()`           |
| CSS (Tailwind)      | Utility classes in JSX             | `className="bg-[#0f172a]"`         |
| CSS (Streamlit)     | BEM-inspired with component prefix | `.prism-card`, `.risk-badge--high` |
| Config keys         | snake_case (Pydantic fields)       | `risk_high_threshold`              |
| Env variables       | UPPER_SNAKE_CASE                   | `MONGO_URI`                        |
| MongoDB collections | snake_case plural                  | `cases_daily`, `risk_scores`       |
| Disease IDs         | UPPER_SNAKE_CASE                   | `DENGUE`, `COVID`, `MALARIA`       |

---

## 5. The Data Pipeline — End to End

### Stage 1: Data Ingestion

Data enters PRISM through CSV files loaded via scripts or the CLI:

```bash
# Option A: CLI tool (recommended)
python disease_manager.py load DENGUE Datasets/Dengue_STATEWISE_DEATH_3yrs.csv

# Option B: Direct script
python -m backend.scripts.load_dengue_data

# Option C: Generic CSV loader
python -m backend.scripts.load_csv Datasets/any_data.csv
```

**What happens internally:**

1. CSV is parsed with pandas
2. Each row maps to `region_id`, `date`, `confirmed`, `deaths`, `recovered`, `disease`
3. `ingestion.upsert_regions()` creates/updates region documents
4. `ingestion.upsert_cases()` upserts case documents with compound key `(region_id, date, disease)`
5. Duplicate rows are silently updated (upsert), not duplicated

### Stage 2: Pipeline Execution

The entire analytics pipeline runs with one API call:

```bash
curl -X POST "http://localhost:8000/pipeline/run?disease=DENGUE&horizon=7&granularity=monthly"
```

Or click **"▶️ Run Pipeline"** in the Streamlit dashboard.

**Pipeline steps** (sequential, order matters):

1. **(Optional)** Reset existing derived data for the disease
2. **Risk scoring** → writes to `risk_scores`
3. **Alert generation** → writes to `alerts`, triggers email notifications
4. **ARIMA forecasting** → writes to `forecasts_daily`

### Stage 3: Consumption

Results are consumed through three interfaces:

| Interface           | URL                          | Use Case                                       |
| ------------------- | ---------------------------- | ---------------------------------------------- |
| React Frontend      | `http://localhost:8000/ui/`  | Interactive maps, resource prediction, reports |
| Streamlit Dashboard | `http://localhost:8501`      | Analytics, pipeline control, CSV export        |
| REST API            | `http://localhost:8000/docs` | Programmatic access, integration               |

---

## 6. Risk Scoring Algorithm

### The Formula

The risk score is a weighted composite of three epidemiological signals:

```
base_score = 0.65 × growth_component
           + 0.25 × volatility_component
           + 0.10 × mortality_component
```

Each component is computed from a **7-day lookback window** of `cases_daily`:

| Component       | Calculation                                                             | Weight | Rationale                                                               |
| --------------- | ----------------------------------------------------------------------- | ------ | ----------------------------------------------------------------------- |
| **Growth Rate** | `(today_cases - 7d_ago_cases) / 7d_ago_cases`, clipped to [0, 1]        | 65%    | Most predictive of outbreak trajectory. Rapid growth = emerging hotspot |
| **Volatility**  | `stdev(confirmed) / mean(confirmed)`, normalized × 2, clipped to [0, 1] | 25%    | Erratic case counts signal unreliable data or emerging clusters         |
| **Death Ratio** | `sum(deaths) / sum(confirmed)`, scaled × 50, clipped to [0, 1]          | 10%    | High CFR indicates severe strain or overwhelmed healthcare              |

### Climate Adjustment

After computing the base score, PRISM applies a **monsoon-season multiplier**:

```
adjusted_score = min(1.0, base_score × climate_multiplier)
```

See [Section 7: Climate Boost System](#7-climate-boost-system) for details.

### Risk Levels

| Level        | Score Range | Color     | Action                              |
| ------------ | ----------- | --------- | ----------------------------------- |
| **CRITICAL** | ≥ 0.85      | 🔴 Red    | Immediate intervention required     |
| **HIGH**     | ≥ 0.70      | 🟠 Orange | Alert generated, notifications sent |
| **MEDIUM**   | ≥ 0.40      | 🟡 Yellow | Monitor closely                     |
| **LOW**      | < 0.40      | 🟢 Green  | Normal surveillance                 |

### Risk Drivers

Each risk score includes human-readable **drivers** explaining why it's high:

- `"High 7-day growth (≥30%)"` — growth_rate ≥ 0.30
- `"High case volatility"` — volatility ≥ 0.15
- `"Elevated death ratio"` — death_ratio ≥ 0.02
- `"Climate boost: +15%"` — climate multiplier raised score by >10%

### Why These Weights?

```
Growth (65%):
  The strongest predictor of an emerging outbreak. A region where
  cases doubled in a week is far more dangerous than one with
  stable high counts. Early warning systems must prioritize TREND
  over MAGNITUDE.

Volatility (25%):
  Stable case counts, even if high, indicate a known situation.
  Erratic swings suggest data quality issues, emerging clusters,
  or reporting delays — all of which warrant attention.

Death Ratio (10%):
  Kept low because CFR varies wildly by disease and is a LAGGING
  indicator. High deaths mean the outbreak is already advanced.
  We use it as a severity signal, not a primary predictor.
```

---

## 7. Climate Boost System

### What It Does

Vector-borne diseases (dengue, malaria, chikungunya) are heavily influenced by
monsoon seasons. PRISM applies month-based multipliers that model India's
climate patterns to boost or suppress risk scores seasonally.

### Monsoon Risk Multiplier Table

```
Month  │ Multiplier │ Season           │ Effect on Risk
───────┼────────────┼──────────────────┼─────────────────
Jan    │    0.6     │ Winter           │ 40% reduction
Feb    │    0.5     │ Winter           │ 50% reduction (lowest)
Mar    │    0.7     │ Pre-monsoon      │ 30% reduction
Apr    │    0.8     │ Pre-monsoon      │ 20% reduction
May    │    1.0     │ Pre-monsoon      │ No change
Jun    │    1.5     │ Monsoon onset    │ 50% boost
Jul    │    1.8     │ Peak monsoon     │ 80% boost (highest)
Aug    │    1.8     │ Peak monsoon     │ 80% boost
Sep    │    1.5     │ Monsoon retreat  │ 50% boost
Oct    │    1.2     │ Post-monsoon     │ 20% boost
Nov    │    0.8     │ Post-monsoon     │ 20% reduction
Dec    │    0.6     │ Winter           │ 40% reduction
```

### Why Monsoon Matters

```
Mosquitoes breed in stagnant water → monsoon creates ideal breeding grounds
  │
  ├── Dengue: Aedes mosquitoes breed in urban water collections
  ├── Malaria: Anopheles mosquitoes breed in rural standing water
  └── Chikungunya: Same Aedes vector as dengue

Peak monsoon (Jul–Aug) = peak vector density = peak transmission risk
Winter (Dec–Feb) = minimal breeding = minimal transmission
```

### How It's Implemented

```python
# utils/climate.py
MONSOON_RISK_MULTIPLIERS = {
    1: 0.6, 2: 0.5, 3: 0.7, 4: 0.8, 5: 1.0, 6: 1.5,
    7: 1.8, 8: 1.8, 9: 1.5, 10: 1.2, 11: 0.8, 12: 0.6,
}

def calculate_weather_aware_risk(base_risk, date_str, region_id):
    month = parse_date(date_str).month
    multiplier = MONSOON_RISK_MULTIPLIERS[month]
    adjusted = min(1.0, base_risk * multiplier)
    return adjusted, explanation, climate_info_dict
```

The climate info is stored alongside each risk score document, providing
full transparency into how the adjustment was applied.

---

## 8. Forecasting Engine

### Two Forecasting Models

PRISM offers two forecasting strategies, selectable per request:

| Model               | Endpoint                         | Strengths                                 | Limitations                        |
| ------------------- | -------------------------------- | ----------------------------------------- | ---------------------------------- |
| **Naive v2**        | `POST /forecasts/generate`       | Fast, works with minimal data (3+ points) | No trend/seasonality awareness     |
| **ARIMA/SARIMA v1** | `POST /forecasts/generate-arima` | Captures trends, seasonality, auto-tuned  | Needs more data, slower to compute |

### Naive Baseline (v2)

```
Algorithm:
  1. Query N most recent case records (N depends on granularity)
  2. Compute mean of confirmed values
  3. Prediction = mean for each future day
  4. Confidence interval = prediction ± 10%

Lookback by granularity:
  yearly  → 3 data points
  monthly → 6 data points
  weekly  → 12 data points
```

**Why keep a naive model?** It serves as the **performance baseline** for the
ARIMA model. If ARIMA can't beat the naive model, it means the data doesn't
have exploitable patterns — useful diagnostic information.

### ARIMA/SARIMA (v1)

```
Algorithm:
  1. Query extended historical data (yearly=5, monthly=24, weekly=52 points)
  2. Fit auto_arima with stepwise search (max p,q = 3; max P,Q = 2)
  3. Seasonal period: yearly=1, monthly=12, weekly=52
  4. Generate horizon-day forecasts with 95% confidence intervals
  5. Clamp predictions to ≥ 0 (cases can't be negative)

Model versions:
  sarima_v1 — when use_seasonal=True (default)
  arima_v1  — when use_seasonal=False
```

### Model Comparison

```bash
POST /forecasts/generate-arima?disease=DENGUE&horizon=7&use_seasonal=true
```

The evaluation endpoint compares predictions against actuals:

```bash
GET /evaluation/forecast?region_id=IN-MH&horizon=7
```

Returns: MAE (Mean Absolute Error), MAPE (Mean Absolute Percentage Error),
data points compared.

### Granularity System

PRISM supports three temporal granularities for case data:

```
yearly   ← Raw annual data (e.g., 3 years × 1 point = 3 data points)
monthly  ← Synthetic monthly data (more granular, recommended for forecasting)
weekly   ← Synthetic weekly data (most granular, requires sufficient history)
```

**Why "synthetic"?** Most Indian epidemiological data is reported annually.
PRISM can generate synthetic monthly/weekly breakdowns to enable higher-resolution
forecasting. See `docs/FORECASTING_GRANULARITY.md` for the methodology.

---

## 9. Alert & Notification System

### Alert Generation Flow

```
risk_scores (latest date)
    │
    ├── Filter: risk_score ≥ risk_high_threshold (0.7)
    │
    ▼
For each qualifying region:
    │
    ├── Create alert document:
    │   {
    │     region_id, date, disease,
    │     risk_score, risk_level,
    │     reason: "Risk score 0.85 ≥ threshold 0.70",
    │     drivers: ["High 7-day growth", "Climate boost: +15%"],
    │     created_at: datetime.utcnow()
    │   }
    │
    ├── Upsert to alerts collection
    │   (compound key: region_id + date + disease + reason)
    │
    ├── Email notifications ──→ services/email.py
    │   ├── Query subscribers matching region + disease + risk level
    │   ├── Build HTML email (branded template, risk badge, drivers list)
    │   ├── Build plain-text fallback
    │   └── Send via SMTP (TLS)
    │
    └── Multi-channel dispatch ──→ services/notifications.py
        ├── Console: logger.warning() with formatted message
        ├── Email: SMTP (same as above)
        └── SMS: Placeholder for Twilio integration
```

### Subscriber Model

Users subscribe to alerts via the API:

```bash
POST /notifications/subscribe
{
  "email": "doctor@hospital.org",
  "regions": ["IN-MH", "IN-KA"],
  "diseases": ["DENGUE"],
  "frequency": "immediate",
  "min_risk_level": "HIGH"
}
```

Subscribers are filtered per alert: only those matching the alert's region,
disease, and risk level receive notifications.

### Email Template

HTML emails include:

- PRISM branding header with gradient background
- Risk level badge (color-coded: red/orange/yellow)
- Region name and risk score
- List of risk drivers
- Link to dashboard
- One-click unsubscribe link (with token)
- Plain-text fallback for email clients without HTML support

---

## 10. Multi-Disease Architecture

### The Disease Registry

PRISM ships with **10 pre-configured disease profiles** in `disease_config.py`:

| Disease               | Transmission       | R₀   | CFR  | Climate Sensitive    |
| --------------------- | ------------------ | ---- | ---- | -------------------- |
| DENGUE                | Vector (Aedes)     | 2.5  | 1%   | Temp, Rain, Humidity |
| COVID                 | Airborne           | 5.0  | 2%   | Temp, Humidity       |
| MALARIA               | Vector (Anopheles) | 1.5  | 0.3% | Temp, Rain, Humidity |
| TUBERCULOSIS          | Airborne           | 10.0 | 15%  | Humidity             |
| INFLUENZA             | Airborne           | 1.3  | 0.1% | Temp, Humidity       |
| CHOLERA               | Waterborne         | 2.0  | 5%   | Temp, Rain           |
| CHIKUNGUNYA           | Vector (Aedes)     | 3.0  | 0.1% | Temp, Rain, Humidity |
| TYPHOID               | Waterborne         | 2.5  | 1%   | Temp, Rain           |
| JAPANESE_ENCEPHALITIS | Vector             | 1.5  | 30%  | Temp, Rain, Humidity |
| MEASLES               | Airborne           | 15.0 | 0.2% | None                 |

### Disease Isolation Principle

**Every data query in PRISM is disease-scoped.** This is the core architectural
guarantee that prevents data leaks between diseases:

```python
# ✅ Every MongoDB query includes disease filter
query = {"date": latest_date}
if disease:
    query["disease"] = disease

# ✅ Every compound index includes disease
db["risk_scores"].create_index(
    [("region_id", 1), ("date", 1), ("disease", 1)],
    unique=True
)

# ✅ Every API endpoint accepts disease parameter
@router.post("/compute")
def compute_risk(disease: Optional[str] = Query(None)):
    validated_disease = validate_disease(disease)
    ...
```

### Adding a New Disease (Zero Code Changes)

```bash
# 1. Add profile to disease_config.py (only if custom parameters needed)
#    Otherwise, PRISM uses sensible defaults for unknown diseases

# 2. Load data
python disease_manager.py load ZIKA zika_data.csv

# 3. Run pipeline
curl -X POST "http://localhost:8000/pipeline/run?disease=ZIKA"

# 4. View results — the disease auto-appears in dashboards
```

### Disease Manager CLI

```bash
python disease_manager.py list          # Show all 10 diseases + stats
python disease_manager.py info DENGUE   # Detailed profile + DB counts
python disease_manager.py compare       # Side-by-side data availability
python disease_manager.py load DENGUE data.csv  # Load CSV data
```

---

## 11. API Design & Route Patterns

### Router Registration

All 13 routers are registered in `app.py` with descriptive prefixes:

```python
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(risk_router, prefix="/risk", tags=["Risk Assessment"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(forecasts_router, prefix="/forecasts", tags=["Forecasts"])
app.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])
# ... 8 more routers
```

### Endpoint Pattern

Every route handler follows the same structure:

```python
@router.post("/compute", response_model=RiskScoreListResponse)
def compute_risk(
    target_date: Optional[str] = Query(None, description="ISO date YYYY-MM-DD"),
    disease: Optional[str] = Query(None, description="Filter by disease"),
):
    try:
        # 1. Validate inputs (raises typed exceptions)
        validated_date = validate_iso_date(target_date)
        validated_disease = validate_disease(disease)

        # 2. Call service layer (no HTTP awareness)
        used_date, results = compute_risk_scores(validated_date, validated_disease)

        # 3. Build response
        return {"date": used_date, "risk_scores": results, "count": len(results)}

    except (DateValidationError, DiseaseValidationError) as e:
        handle_validation_error(e)              # → 422
    except PyMongoError as e:
        raise HTTPException(503, "Database error")  # → 503
    except Exception as e:
        raise HTTPException(500, "Unexpected error") # → 500
```

### Shared Validation Helper

Validation error handling is centralized in `routes/helpers.py`:

```python
def handle_validation_error(e: Exception) -> None:
    """Convert validation exceptions to HTTP 422 responses."""
    if isinstance(e, PRISMException):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict()
        )
```

This eliminates the duplicated `_handle_validation_error()` pattern that would
otherwise be copy-pasted into every route file.

### API Response Format

All responses follow consistent Pydantic models:

```json
// Success — risk scores
{
  "date": "2024-07-15",
  "risk_scores": [...],
  "count": 28,
  "disease": "DENGUE"
}

// Error — validation failure
{
  "error": "DiseaseValidationError",
  "message": "Unknown disease: 'ZIKAA'. Valid options: DENGUE, COVID, ...",
  "details": {
    "field": "disease",
    "value": "ZIKAA"
  }
}
```

### Complete Endpoint Reference

| Method | Path                        | Purpose                                  |
| ------ | --------------------------- | ---------------------------------------- |
| `GET`  | `/health/ping`              | Simple liveness check                    |
| `GET`  | `/health/`                  | DB connectivity + collection stats       |
| `GET`  | `/regions/`                 | List all regions with counts             |
| `GET`  | `/regions/diseases`         | List available diseases                  |
| `GET`  | `/hotspots/`                | Top N hotspots by case count             |
| `POST` | `/risk/compute`             | Compute risk scores                      |
| `GET`  | `/risk/latest`              | Latest risk scores                       |
| `GET`  | `/risk/geojson`             | GeoJSON FeatureCollection for maps       |
| `POST` | `/alerts/generate`          | Generate alerts from risk scores         |
| `GET`  | `/alerts/latest`            | Latest alerts feed                       |
| `POST` | `/forecasts/generate`       | Naive forecasts                          |
| `POST` | `/forecasts/generate-arima` | ARIMA/SARIMA forecasts                   |
| `GET`  | `/forecasts/latest`         | Latest forecasts                         |
| `POST` | `/pipeline/run`             | **One-click: risk → alerts → forecasts** |
| `GET`  | `/evaluation/forecast`      | Forecast accuracy metrics                |
| `GET`  | `/diseases/`                | Disease registry listing                 |
| `POST` | `/notifications/subscribe`  | Subscribe to alerts                      |
| `POST` | `/reports/generate`         | Generate PDF report                      |
| `GET`  | `/reports/list`             | List generated reports                   |
| `POST` | `/resources/predict`        | Predict hospital resource demand         |

---

## 12. Frontend Architecture

### Stack

```
React 19 + Vite 7 + TypeScript 5.9 + TailwindCSS 4
├── Leaflet + React-Leaflet  — Interactive risk heatmaps
├── Recharts                 — Forecast line charts
├── Lucide React             — Icon library
└── React Router 7           — Client-side routing
```

### Routing

```
/              → Dashboard    (map + resource prediction)
/analysis      → Analysis     (forecasts + model evaluation)
/resources     → Resources    (resource management)
/reports       → Reports      (PDF generation + download)
/settings      → Settings     (configuration)
```

### Layout Pattern

```
┌─────────────────────────────────────────────────────┐
│  Sidebar  │              Header                      │
│  (nav)    │──────────────────────────────────────────│
│           │                                          │
│  🏠 Dash  │         <Outlet /> (page content)        │
│  📊 Anal  │                                          │
│  🏥 Res   │     Rendered by React Router based       │
│  📋 Rep   │     on current URL path                  │
│  ⚙️ Set   │                                          │
│           │                                          │
└───────────┴──────────────────────────────────────────┘
```

### Typed API Client

`lib/api.ts` provides a fully typed client for every backend endpoint:

```typescript
// Every API function is typed end-to-end
export async function fetchLatestForecasts(
  region_id?: string,
  disease?: string,
  horizon: number = 7,
): Promise<ForecastsResponse> {
  const params = new URLSearchParams();
  if (region_id) params.append("region_id", region_id);
  if (disease) params.append("disease", disease);
  params.append("horizon", horizon.toString());

  const response = await fetch(`${API_BASE}/forecasts/latest?${params}`);
  if (!response.ok) throw new Error(`Failed: ${response.statusText}`);
  return response.json();
}
```

### Key Components

| Component           | Purpose                                        | Key Technologies                     |
| ------------------- | ---------------------------------------------- | ------------------------------------ |
| `OperationalMap`    | Interactive risk heatmap overlaid on India map | Leaflet, GeoJSON, dynamic markers    |
| `BedShortageWidget` | Predicts hospital resource shortage by region  | API polling, threshold visualization |
| `ErrorBoundary`     | Catches React rendering errors gracefully      | React Error Boundary pattern         |
| `Layout/Sidebar`    | App shell with navigation                      | React Router `<Outlet>`              |

### Lazy Loading

The map component uses React `Suspense` for code-splitting — Leaflet is
a large library that shouldn't block initial page load:

```tsx
const OperationalMap = React.lazy(() => import("./OperationalMap"));

<Suspense fallback={<div>Loading map...</div>}>
  <OperationalMap disease={selectedDisease} />
</Suspense>;
```

---

## 13. Dashboard (Streamlit)

### What It Provides

The Streamlit dashboard at `:8501` is the **analytics command center**:

```
┌─────────────────────────────────────────────────┐
│  ⚙️ SIDEBAR                                     │
│  ├── Disease filter (dropdown)                  │
│  ├── 🗺️ Link to interactive heatmap             │
│  └── 🚀 One-Click Pipeline                      │
│       ├── Reset data checkbox                   │
│       ├── Horizon (1–30 days)                   │
│       ├── Granularity (yearly/monthly/weekly)   │
│       └── ▶️ Run Pipeline button                │
├─────────────────────────────────────────────────┤
│  MAIN CONTENT (5 sections)                      │
│                                                 │
│  🔥 Hotspots — Top regions by case count        │
│  ─────────────────────────────────────          │
│  🗺️ Risk Heatmap — Top 10 by risk score         │
│  ─────────────────────────────────────          │
│  📊 Risk Intelligence — All regions + CSV export │
│  ─────────────────────────────────────          │
│  🚨 Alerts Feed — Latest alerts + CSV export    │
│  ─────────────────────────────────────          │
│  📈 Forecast Viewer — Region selector + chart   │
│       ├── Confidence interval bands              │
│       ├── Forecast data table (expandable)       │
│       ├── CSV download                           │
│       └── 📐 Model Evaluation (MAE, MAPE)       │
└─────────────────────────────────────────────────┘
```

### Design Principles

1. **API-First**: Dashboard never queries MongoDB directly — all data comes
   through the REST API. This ensures consistency with the React frontend.

2. **Progressive Disclosure**: Summary views first (metrics, top-10), detailed
   tables behind expanders, CSV downloads for full data.

3. **Helper Extraction**: Repeated patterns (CSV download, alert formatting)
   are extracted into helper functions (`_csv_download()`, `_format_alert_rows()`).

---

## 14. Database Design

### MongoDB Collections

```
prism_db
├── regions             ← Region metadata (state name, disease, case counts)
├── cases_daily         ← Epidemiological case data (confirmed, deaths, recovered)
├── risk_scores         ← Computed risk scores with drivers & climate info
├── alerts              ← Generated alerts for high-risk regions
├── forecasts_daily     ← Forecast predictions with confidence intervals
├── subscribers         ← Email notification subscribers
├── reports             ← Generated report metadata (status, paths)
├── disease_config      ← Runtime disease configuration overrides
└── resource_config     ← Hospital resource multiplier configuration
```

### Index Strategy

All collections use **compound unique indexes** with the `disease` field
for multi-disease isolation:

```python
# Pattern: (region_id, date, disease) — unique per disease
db["cases_daily"].create_index(
    [("region_id", 1), ("date", 1), ("disease", 1)],
    unique=True, sparse=True
)

# Forecasts add model_version to allow multiple models per region/date
db["forecasts_daily"].create_index(
    [("region_id", 1), ("date", 1), ("disease", 1), ("model_version", 1)],
    unique=True, sparse=True
)

# Risk/alert sorting indexes for fast latest-first queries
db["risk_scores"].create_index([("date", -1), ("risk_score", -1)])
db["alerts"].create_index([("date", -1), ("risk_score", -1)])
```

### Document Shapes

```javascript
// cases_daily
{
  "region_id": "IN-MH",
  "date": "2024-07-15",
  "confirmed": 450,
  "deaths": 3,
  "recovered": 380,
  "disease": "DENGUE",
  "granularity": "monthly"
}

// risk_scores
{
  "region_id": "IN-MH",
  "date": "2024-07-15",
  "risk_score": 0.85,
  "risk_level": "HIGH",
  "drivers": ["High 7-day growth", "Climate boost: +15%"],
  "disease": "DENGUE",
  "climate_info": {
    "base_risk": 0.62,
    "climate_multiplier": 1.8,
    "adjusted_risk": 0.85,
    "season": "monsoon",
    "explanation": "Monsoon peak - high transmission risk"
  }
}

// forecasts_daily
{
  "region_id": "IN-MH",
  "date": "2024-07-22",
  "pred_mean": 485.3,
  "pred_lower": 412.5,
  "pred_upper": 558.1,
  "model_version": "sarima_v1",
  "source_granularity": "monthly",
  "disease": "DENGUE",
  "generated_at": "2024-07-15T10:30:00Z"
}
```

### Why MongoDB Over SQL?

```
1. Schema Flexibility:
   10 diseases × 28 states × 3 granularities × variable climate fields
   → SQL would require rigid migrations for every new disease attribute
   → MongoDB handles heterogeneous documents naturally

2. Upsert Pattern:
   PRISM's primary write pattern is UPSERT (update-or-insert)
   → MongoDB's update_one(filter, $set, upsert=True) is native and atomic
   → SQL requires ON CONFLICT DO UPDATE or MERGE (vendor-specific)

3. Time-Series Queries:
   Sorting by date descending and limiting to N documents is MongoDB's
   strength (cursor-based, index-backed). No JOINs needed.

4. Aggregation Pipeline:
   Hotspot computation uses MongoDB's aggregation framework
   ($group, $sum, $lookup, $sort, $limit) — SQL equivalent would need
   subqueries or CTEs.
```

---

## 15. Key Design Patterns

### Pattern 1: Application Factory

```python
# backend/app.py
def create_app() -> FastAPI:
    app = FastAPI(title="PRISM API", lifespan=lifespan)
    # Register middleware, exception handlers, routers
    return app

app = create_app()  # Module-level for uvicorn
```

**Why?** Testing creates a fresh app instance without side effects.
`TestClient(create_app())` gives each test suite a clean slate.

### Pattern 2: Settings Singleton

```python
# backend/config.py
@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

**Why?** Settings are parsed from `.env` once and cached. Every service
imports `get_settings()` — no global state, easily mockable in tests.

### Pattern 3: Connection Singleton

```python
# backend/db.py
@lru_cache()
def get_client() -> MongoClient:
    settings = get_settings()
    client = MongoClient(settings.mongo_uri, ...)
    client.admin.command("ping")  # Verify on first call
    return client
```

**Why?** MongoDB connection pooling (min=10, max=50) is managed by one client
instance. No connection leaks, no repeated handshakes.

### Pattern 4: Custom Exception Hierarchy

```
PRISMException (base)
├── .to_dict() → {"error": "...", "message": "...", "details": {...}}
│
├── ValidationError
│   ├── DateValidationError     → "Invalid date format: '2024-13-01'"
│   ├── DiseaseValidationError  → "Unknown disease: 'ZIKAA'"
│   └── GranularityValidationError → "Invalid granularity: 'hourly'"
│
├── DatabaseError               → "Failed to write risk scores"
└── DataNotFoundError           → "No cases found for region IN-MH"
```

**Why?** Routes catch typed exceptions and convert to appropriate HTTP codes.
Services throw domain exceptions without knowing about HTTP.

### Pattern 5: Service Layer Separation

```python
# ❌ BAD: Route does business logic
@router.post("/compute")
def compute_risk(date, disease):
    db = get_db()
    cases = list(db["cases_daily"].find({...}))
    # 50 lines of risk calculation here...
    db["risk_scores"].insert_many(results)
    return results

# ✅ GOOD: Route delegates to service
@router.post("/compute")
def compute_risk(date, disease):
    validated_date = validate_iso_date(date)
    validated_disease = validate_disease(disease)
    used_date, results = compute_risk_scores(validated_date, validated_disease)
    return {"date": used_date, "risk_scores": results}
```

**Why?** Services can be called from routes, CLI tools, scripts, or tests —
they have no HTTP dependency. This enabled `disease_manager.py` and
`run_pipeline.py` to reuse the same logic.

### Pattern 6: Upsert Repository

```python
# Every write operation uses upsert, not insert
collection.update_one(
    {"region_id": region, "date": date, "disease": disease},  # filter
    {"$set": document},                                        # update
    upsert=True                                                # create if missing
)
```

**Why?** Pipeline re-runs are idempotent. Running the pipeline twice for the
same date/disease produces the same results, not duplicate records. This is
critical for operational reliability.

### Pattern 7: Strategy (Forecasting)

```python
# Two forecasting strategies, same interface
def generate_forecasts(date, horizon, disease, granularity):
    """Naive baseline — simple mean extrapolation."""

def generate_arima_forecasts(date, horizon, disease, granularity):
    """ARIMA/SARIMA — statistical time-series model."""

# Routes select strategy based on endpoint:
# POST /forecasts/generate       → naive
# POST /forecasts/generate-arima → ARIMA
```

**Why?** New forecasting models (Prophet, LSTM) can be added as new services
without changing existing code. The pipeline can be configured to use any model.

### Pattern 8: Observer/Dispatch (Alerts → Notifications)

```python
# services/alerts.py — after generating alerts:
# 1. Email notifications for HIGH/CRITICAL
send_alert_notifications(alerts)

# 2. Multi-channel dispatch (console/email/sms)
dispatch_notifications(alerts)
```

**Why?** Alert generation and notification delivery are separate concerns.
Adding a new channel (Slack, webhook) requires only extending
`notifications.py`, not touching `alerts.py`.

---

## 16. Testing Strategy

### Test Pyramid

```
                    /\
                   /  \   Integration Tests
                  / ── \   (TestClient + mock DB)
                 /      \   api endpoints, error codes
                / ────── \
               / Unit Tests \  Pure logic, no I/O
              /  (88 tests)  \  validators, exceptions,
             /________________\  reports, geojson, email
```

### What We Test

| Layer                 | What                                                     | How                               |
| --------------------- | -------------------------------------------------------- | --------------------------------- |
| **Validators**        | Date parsing, disease validation, granularity checks     | Pure function calls, edge cases   |
| **Exceptions**        | Serialization, hierarchy, field propagation              | Instantiate → assert `.to_dict()` |
| **GeoJSON**           | Risk → Feature conversion, color mapping, geometry       | Service calls with mock data      |
| **Reports**           | PDF generation, chart creation, report builders          | Service calls with mock DB        |
| **Email**             | HTML/text building, subscriber matching, token inclusion | Template rendering assertions     |
| **Resources**         | Demand calculation, active case estimation               | Service with mock DB data         |
| **API endpoints**     | Status codes, response shapes, error handling            | FastAPI `TestClient`              |
| **Disease isolation** | Queries don't leak between diseases                      | Multi-disease insert + filter     |

### Running Tests

```bash
# All tests
python -m pytest

# Unit tests only (fast, no DB needed)
python -m pytest tests/unit/ -v

# Integration tests (need app instance)
python -m pytest tests/integration/ -v

# With coverage
python -m pytest --cov=backend --cov-report=html

# Specific marker
python -m pytest -m "unit" -v
```

### Test Configuration (pytest.ini)

```ini
[pytest]
testpaths = tests
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (require running services)
    slow: Slow tests (>1s)
```

### What We DON'T Test (and Why)

- **MongoDB queries directly**: We mock `get_db()` — testing PyMongo is testing PyMongo
- **Streamlit dashboard**: Streamlit has no testing framework; it's a visualization layer
- **CSS/styling**: Visual testing is a separate discipline
- **Third-party libraries**: pmdarima, ReportLab, etc. are tested upstream

### Fixtures

```python
# tests/conftest.py
@pytest.fixture(scope="session")
def app():
    """Create FastAPI application for testing."""
    return create_app()

@pytest.fixture(scope="session")
def client(app):
    """Test client for integration tests."""
    return TestClient(app)

@pytest.fixture
def mock_get_db(mock_db):
    """Patch get_db to return mock for unit tests."""
    with patch("backend.db.get_db", return_value=mock_db):
        yield mock_db
```

---

## 17. Deployment & Operations

### Starting PRISM

```bash
# Recommended: one command starts everything
python start_prism.py

# What it does:
# 1. Checks ports 8000 (API) and 8501 (Dashboard) are free
# 2. Starts uvicorn API server as background subprocess
# 3. Polls /health until API responds (up to 30 seconds)
# 4. Starts Streamlit dashboard (foreground/blocking)
# 5. Ctrl+C gracefully shuts down both services
```

### Manual Startup

```bash
# Terminal 1: API
python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Dashboard
python -m streamlit run backend/dashboard/app.py

# Terminal 3 (optional): Frontend dev server
cd frontend && npm run dev
```

### Production Deployment

```bash
# API with multiple workers
uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 4

# Build frontend
cd frontend && npm run build
# Built files are served by FastAPI from /ui/
```

### Environment Configuration

```bash
# Required
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net

# Recommended
DB_NAME=prism_db
LOG_LEVEL=INFO
RISK_HIGH_THRESHOLD=0.7

# SMTP (for email notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@prism.org
SMTP_PASSWORD=app_password
SMTP_FROM=PRISM Alert System

# CORS (production)
ENABLE_CORS=true
CORS_ORIGINS=https://prism.yourdomain.com
```

### Stopping PRISM

```powershell
# Windows
.\kill_prism.ps1

# Or manually
# Ctrl+C in the terminal running start_prism.py
```

### Log Management

```
logs/
├── prism.log         ← All logs (10MB rotation × 5 backups)
└── prism_errors.log  ← Errors only (10MB rotation × 5 backups)
```

Configure via `LOG_LEVEL` environment variable:
`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

---

## 18. Security Model

### Credentials Management

- **Never commit `.env` files** — `.gitignore` excludes them
- MongoDB credentials in `MONGO_URI` environment variable only
- SMTP passwords in `SMTP_PASSWORD` environment variable only
- No hardcoded secrets in any source file

### API Security

- **CORS**: Configurable via `CORS_ORIGINS` — use specific domains in production
- **Input Validation**: All inputs pass through `validators.py` before processing
- **Error Masking**: Internal errors return generic messages; details go to logs only
- **Status Codes**: Proper HTTP semantics (422 for validation, 503 for DB, 500 for unknown)

### MongoDB Security

- Connection pooling with timeouts (prevents hanging connections)
- Retry writes/reads enabled (survives transient failures)
- IP allowlisting recommended for Atlas deployments
- Minimal privileges — application user needs `readWrite` on `prism_db` only

### What's NOT Implemented (Future Work)

- Authentication/authorization (API is currently open)
- Rate limiting (add `slowapi` middleware for production)
- API key management
- HTTPS termination (handled by reverse proxy: nginx, Cloudflare)

---

## 19. Production Checklist

Before shipping, verify:

### Functionality

- [ ] Pipeline runs successfully for at least 2 diseases
- [ ] Risk scores, alerts, and forecasts are generated correctly
- [ ] Dashboard displays all 5 sections without errors
- [ ] React frontend loads maps, charts, and resource predictions
- [ ] CSV export produces valid files
- [ ] PDF reports generate and download correctly

### Data Integrity

- [ ] Disease isolation: DENGUE queries don't return COVID results
- [ ] Upsert idempotency: running pipeline twice produces same results
- [ ] Date validation rejects invalid formats
- [ ] Disease validation rejects unknown diseases

### Infrastructure

- [ ] MongoDB indexes created (`ensure_indexes()` runs at startup)
- [ ] Health endpoint responds (`GET /health/`)
- [ ] Logs rotate at 10MB, 5 backups
- [ ] `.env` file configured, not committed to git
- [ ] CORS origins restricted for production

### Performance

- [ ] API responds within 2s for read endpoints
- [ ] Pipeline completes within 30s for single disease
- [ ] Dashboard loads within 5s
- [ ] Frontend bundle is optimized (`npm run build` succeeds)

### Testing

- [ ] All unit tests pass (`pytest tests/unit/ -v`)
- [ ] All integration tests pass (`pytest tests/integration/ -v`)
- [ ] No hardcoded credentials in any source file

---

## 20. Extension Roadmap

### What to Build Next (In Order of Impact)

1. **Authentication & RBAC**
   Add JWT-based auth with role levels (viewer, analyst, admin).
   Teaches: middleware, token management, permission decorators.

2. **Real-Time WebSocket Alerts**
   Push alerts to connected dashboards instantly instead of polling.
   Teaches: FastAPI WebSockets, event-driven architecture.

3. **ML-Based Forecasting (Prophet / LSTM)**
   Add Facebook Prophet or LSTM neural network forecasters.
   Teaches: extending the Strategy pattern, model versioning.

4. **Automated Data Ingestion**
   Scheduled ETL from government health APIs (IDSP, WHO).
   Teaches: APScheduler, background tasks, data pipelines.

5. **Geographic Drill-Down**
   District-level granularity instead of state-level.
   Teaches: hierarchical data, map zoom levels, GeoJSON detail.

6. **Outbreak Simulation**
   SIR/SEIR compartmental models for "what-if" scenario planning.
   Teaches: differential equations, parameter sensitivity analysis.

7. **Mobile App (Capacitor)**
   Wrap the React frontend for Android/iOS distribution.
   Teaches: Capacitor, push notifications, app store deployment.

8. **Multi-Tenant Deployment**
   Support multiple countries/organizations from one instance.
   Teaches: tenant isolation, database sharding, config per tenant.

### Skills This Project Teaches

```
✅ Python (FastAPI, Pydantic, type hints, async patterns)
✅ MongoDB (CRUD, aggregation pipeline, indexing, upserts)
✅ React (components, routing, lazy loading, error boundaries)
✅ TypeScript (interfaces, generics, API contracts)
✅ TailwindCSS (utility-first, responsive, dark mode)
✅ Data Science (pandas, time-series, ARIMA/SARIMA, pmdarima)
✅ Architecture (layered design, service layer, dependency injection)
✅ API Design (REST, OpenAPI, Pydantic response models)
✅ Testing (pytest, fixtures, mocking, test pyramid)
✅ DevOps (environment config, logging, health checks)
✅ Domain Modeling (epidemiology, risk scoring, climate factors)
✅ Notification Systems (email templates, subscriber matching, multi-channel)
✅ GeoJSON & Mapping (Leaflet, spatial data, choropleth visualization)
✅ PDF Generation (ReportLab, charts-to-PDF, programmatic documents)
```

---

> 💡 **Remember**: PRISM started as a simple risk calculator and grew into
> a multi-disease surveillance platform through disciplined layering.
> Each feature was added by extending a layer, not rewriting one.
> That's the power of architecture — the last 20% (alerts, climate,
> multi-disease, reports, maps) was possible because the first 80%
> was structured correctly.
