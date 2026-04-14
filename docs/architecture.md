# PRISM Architecture Documentation

## 1. Overview
PRISM (Predictive Risk Intelligence & Surveillance Model) is a multi-disease epidemic surveillance and outbreak prediction platform. It is designed to provide real-time risk assessment, automated alerting, and predictive forecasting for various infectious diseases (e.g., Dengue, COVID, Malaria) with a focus on regional data isolation and climate awareness.

## 2. System Architecture
PRISM follows a modern, multi-tier architecture with a clear separation of concerns across four primary layers:

### 2.1 Layered Architecture
1.  **Presentation Layer**:
    *   **React Frontend**: A production-grade web application for interactive maps (Leaflet), resource planning, and reporting.
    *   **Streamlit Dashboard**: An analytics command center for data scientists and health officers to run pipelines and export data.
2.  **API Layer (FastAPI)**:
    *   RESTful API providing 20+ endpoints.
    *   Handles request validation (Pydantic), CORS, and error handling.
    *   Serves the React frontend as static files from `/ui`.
3.  **Service Layer**:
    *   Contains the core business logic: Risk scoring, Alert generation, ARIMA/SARIMA forecasting, Resource prediction, and PDF reporting.
    *   Independent of transport protocols (can be called by API or CLI).
4.  **Data Access Layer**:
    *   **MongoDB**: Primary data store using compound indexes for multi-disease isolation.
    *   **Disease Registry**: Configuration-driven management of disease-specific parameters.

## 3. Technology Stack
| Component | Technology |
| :--- | :--- |
| **Backend Framework** | FastAPI (Python 3.9+) |
| **Database** | MongoDB (PyMongo) |
| **Frontend Framework** | React 19, Vite 7, TypeScript 5 |
| **Styling** | TailwindCSS 4 |
| **Data Science/ML** | Pandas, NumPy, Statsmodels, Pmdarima |
| **Visualization** | Leaflet (Maps), Recharts (Frontend), Plotly (Dashboard) |
| **Reporting** | ReportLab (PDF Generation) |
| **Dashboard** | Streamlit |
| **Testing** | Pytest (Backend), Vitest (Frontend) |

## 4. Backend Architecture
The backend is structured for modularity and scalability:
*   `app.py`: Application factory, middleware registration, and route mounting.
*   `routes/`: Modular routers for Health, Risk, Alerts, Forecasts, Pipeline, etc.
*   `services/`: Pure business logic. Example: `risk.py` computes scores without knowing about HTTP requests.
*   `schemas/`: Pydantic v2 models ensuring type safety and automatic API documentation.
*   `db.py`: Centralized MongoDB client with connection pooling and automated index management.

## 5. Database Schema & Multi-Disease Isolation
PRISM uses a single MongoDB database (`prism_db`) with a multi-disease isolation strategy based on compound indexes.

### 5.1 Key Collections
*   `regions`: Metadata for geographic areas.
*   `cases_daily`: Historical epidemiological data (confirmed, deaths, recovered).
*   `risk_scores`: Computed scores with drivers and climate context.
*   `alerts`: High-risk notifications.
*   `forecasts_daily`: Time-series predictions.
*   `users`: Authentication and subscriber data.

### 5.2 Multi-Disease Isolation
Data isolation is enforced at the database level using compound unique indexes that always include the `disease` field:
`db["cases_daily"].create_index([("region_id", 1), ("date", 1), ("disease", 1)], unique=True)`
This ensures that queries for one disease (e.g., DENGUE) never leak data from another (e.g., COVID).

## 6. Core Algorithms
### 6.1 Risk Scoring
The risk score (0.0 to 1.0) is a weighted composite of three signals:
*   **Growth Rate (65%)**: Trajectory of new cases over a 7-day window.
*   **Volatility (25%)**: Standard deviation of case counts (detects erratic clusters).
*   **Death Ratio (10%)**: Severity signal.

**Weather-Aware Climate Boost**: For vector-borne diseases, a monsoon-season multiplier is applied to the base score, modeling India's seasonal transmission patterns.

### 6.2 Forecasting Engine
Two strategies are supported:
1.  **Naive Baseline**: Simple mean extrapolation for fast, low-data scenarios.
2.  **ARIMA/SARIMA**: Statistical time-series models using `pmdarima` for automated parameter selection (p, d, q). Captures trends and seasonality (SARIMA).

## 7. Data Flow (The Pipeline)
1.  **Ingestion**: CSV data is loaded via `disease_manager.py` or automated scripts into `cases_daily`.
2.  **Pipeline Orchestration**: A single API call (`/pipeline/run`) triggers:
    *   **Risk Computation**: Updates `risk_scores`.
    *   **Alert Generation**: Identifies regions > 0.7 risk and writes to `alerts`.
    *   **Forecasting**: Generates future trends into `forecasts_daily`.
3.  **Consumption**: Data is visualized in the React Map/Charts or the Streamlit analytics view.

## 8. Security & Reliability
*   **Environment Validation**: Pydantic Settings validates all `.env` variables on startup.
*   **Custom Exceptions**: A structured hierarchy (e.g., `PRISMException`, `ValidationError`) ensures consistent API error responses.
*   **Logging**: Rotating file logs for application events and a dedicated error log for debugging.
*   **Health Checks**: Comprehensive monitoring of database connectivity and collection health.
