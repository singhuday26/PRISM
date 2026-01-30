# 🤖 PRISM AI Agent Prompts

> Copy-paste these prompts when starting a new AI agent session to provide rich context for PRISM development.

---

## Quick Context Injection

Use this at the start of any PRISM development session:

```
I'm building PRISM (Predictive Risk Intelligence & Surveillance Model) - an open-source disease surveillance platform.

**Location**: C:\0001_Project\PRISM
**Stack**: FastAPI + MongoDB + Streamlit + Python 3.9+

**Key Files**:
- Main app: backend/app.py
- Config: backend/config.py  
- Exceptions: backend/exceptions.py
- Response schemas: backend/schemas/responses.py
- Tests: tests/unit/ and tests/integration/

**Current Features**: Risk scoring, alerts, ARIMA forecasting, multi-disease support
**Run Tests**: pytest
**Start API**: python -m uvicorn backend.app:app --reload
```

---

## Feature Implementation Prompts

### P0: Interactive Risk Heatmap

```
In PRISM (C:\0001_Project\PRISM), implement an interactive risk heatmap.

Requirements:
1. Create a new route GET /risk/geojson that returns risk scores as GeoJSON
2. Build an HTML page with Leaflet.js showing a map
3. Color-code regions by risk level (green/yellow/orange/red)
4. Add click handlers to show region details
5. Add a time slider for historical data

Technical constraints:
- Use existing risk_scores collection in MongoDB
- Follow patterns in backend/routes/risk.py
- Add response model in backend/schemas/responses.py
- Write tests in tests/integration/

Serve the HTML via FastAPI static files or as a new Streamlit page.
```

### P0: Email Notifications

```
In PRISM (C:\0001_Project\PRISM), add email notification support.

Requirements:
1. Add SMTP configuration to backend/config.py
2. Create backend/services/email.py for sending emails
3. Create subscriber management endpoints:
   - POST /notifications/subscribe
   - DELETE /notifications/unsubscribe  
   - GET /notifications/preferences
4. Create MongoDB collection 'subscribers'
5. Trigger emails when alerts are generated (modify backend/services/alerts.py)

Use fastapi-mail or aiosmtplib. Create HTML email templates in backend/templates/.
Add to requirements.txt as needed.
```

### P0: PDF Report Generation

```
In PRISM (C:\0001_Project\PRISM), implement PDF report generation.

Requirements:
1. Create backend/services/reports.py
2. Add endpoints:
   - POST /reports/generate (params: region_id, disease, period)
   - GET /reports/{report_id}
   - GET /reports/list
3. Use weasyprint or reportlab for PDF generation
4. Create Jinja2 templates in backend/templates/reports/
5. Store reports in 'reports' MongoDB collection with file paths

Reports should include: risk summary, case trends chart, alert history, forecast.
```

---

## Code Quality Requirements

Include these expectations in prompts:

```
Code Quality Requirements:
- Use custom exceptions from backend/exceptions.py
- Add Pydantic response models to backend/schemas/responses.py
- Write unit tests in tests/unit/
- Write integration tests in tests/integration/
- Follow existing code patterns in the codebase
- Run pytest before considering complete
```

---

## Verification Commands

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Type checking (if mypy configured)
mypy backend/

# Start and test API manually
python -m uvicorn backend.app:app --reload

```

---

## 🎯 Strategic Feature Prompts (PRISM Command)

### [Backend] P0: Resource Intelligence

```
I'm working on PRISM Command (Product A).
Context: C:\0001_Project\PRISM
Spec: docs/planning/FEATURE_RESOURCE_INTELLIGENCE.md

Task: Implement the Resource Allocation Service.
1. Create `backend/services/resources.py`: Implement the math `Demand = Active_Cases * Rate`.
2. Create `backend/routes/resources.py`: Endpoints for prediction and config.
3. Update `backend/schemas/responses.py`: Add ResourceDemand models.
4. Run `backend/scripts/seed_resources.py` to load medical config.
5. Verify with `pytest tests/unit/test_resource_service.py`.

Constraint: Ensure accurate math. This is a life-saving feature.
```

### [Frontend] P0: Command Dashboard

```
I'm working on PRISM Command (Product A).
Context: C:\0001_Project\PRISM
Spec: docs/planning/FEATURE_COMMAND_DASHBOARD.md
API Spec: docs/planning/FEATURE_RESOURCE_INTELLIGENCE.md

Task: Build the "Mission Control" Frontend.
1. Scaffold a React+Vite app in `frontend/`.
2. Install Shadcn UI, Tailwind, Lucide React, Recharts.
3. Create the "Bed Shortage Widget": 
   - Fetch data from `POST /resources/predict`
   - Show big red numbers if demand > capacity.
4. Use Dark Mode default.

Constraint: Must feel like an "Enterprise Operating System". High contrast, high density.
```

### [Frontend] P0: Operational Map Widget

```
I'm working on PRISM Command (Product A).
Context: C:\0001_Project\PRISM
Dashboard: frontend/ (already scaffolded with React+Vite+Tailwind)
API Spec: docs/planning/FEATURE_HEATMAP.md

Task: Add the Operational Map Widget to the Command Dashboard.
1. Install `react-leaflet` and `leaflet` in `frontend/`.
2. Create a new component `OperationalMap.tsx`.
3. Fetch GeoJSON from `GET /risk/geojson`.
4. Color regions by risk level (Green < 0.3, Yellow < 0.6, Orange < 0.8, Red >= 0.8).
5. Add click handler to show region details in a popup.
6. Integrate the map into the main dashboard layout (right panel).

Constraint: Map must be responsive. Use dark-themed tiles (e.g., CartoDB Dark Matter).
```

### [Backend] P0: Simulation Engine

```
I'm working on PRISM Command (Product A).
Context: C:\0001_Project\PRISM

Task: Build a Simulation Engine to generate realistic outbreak data for demos.
1. Create `backend/scripts/simulate_outbreak.py`.
2. Logic:
   - Generate 30 days of synthetic cases for 5 regions.
   - Use a sinusoidal wave with noise to mimic a realistic outbreak curve.
   - Peak should vary by region (randomized).
3. Insert data into `cases_daily` collection.
4. Re-run `POST /forecasts/generate` to create forecasts from this data.
5. Re-run `POST /risk/compute` to calculate risk scores.

Constraint: Data must look realistic enough for a faculty demo. No flat lines.
```

### [Frontend] P2: Public App (Product B)

```
I'm working on PRISM Public (Product B).
Context: C:\0001_Project\PRISM
Spec: docs/planning/FEATURE_PUBLIC_APP.md

Task: Build the "Health Weather App" for citizens.
1. Create a simplified layout `PublicLayout.tsx` (Mobile-First).
2. Create a "Traffic Light" Risk Component (Green/Yellow/Red).
3. Connect to `GET /risk/latest` (reusing existing API for now).
4. Add hardcoded advice logic: "If Red -> Show 'Avoid Outdoors'".

Constraint: ZERO graphs. ZERO tables. Only big text and colors.
```

### [Intelligence] P1: Digital Smoke Signals (BlueDot News)

```
I'm working on PRISM Command (Product A).
Context: C:\0001_Project\PRISM
Spec: docs/planning/FEATURE_NEWS_INGESTION.md

Task: Build the BlueDot-inspired Early Warning System.
1. Implement the Ingestion Worker (`backend/services/news/ingestion.py`) to fetch RSS/NewsAPI.
2. Build the NLP Engine using HuggingFace Transformers for Sentiment + spaCy for NER.
3. **CRITICAL**: Implement the Early Warning Score (EWS) logic:
   - Calculate EWS = (Mentions * 0.4) + (Sentiment * 0.4) + (OfficialLag * 0.2).
   - High score if: News mentions rising cases BUT official DB trend is flat.
4. Store results in `health_signals` collection.

Constraint: This must be "Predictive". We want to see signals *before* the charts spike.
```
