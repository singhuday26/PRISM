# 🏗️ Implementation Plan: PRISM Command (Resource Intelligence)

> **Objective**: Implement the backend core for "Product A" — translating forecasted cases into actionable resource demands (Beds, ICU, Staff).

## User Review Required
> [!IMPORTANT]
> This plan initiates the "PRISM Command" strategic pivot. We are prioritizing backend intelligence over frontend dashboards for this sprint.

## Proposed Changes

### Backend Core
#### [NEW] [resources.py](file:///C:/0001_Project/PRISM/backend/services/resources.py)
- Implement `ResourceService` class
- Logic to fetch active cases from `ForecastService`
- Formula: `Demand = Active_Cases * Rate` (as defined in spec)

#### [NEW] [resources.py](file:///C:/0001_Project/PRISM/backend/routes/resources.py)
- `POST /resources/predict`: Endpoint to generate demand forecasts
- `GET /resources/config`: Endpoint to view medical parameters

#### [MODIFY] [responses.py](file:///C:/0001_Project/PRISM/backend/schemas/responses.py)
- Add Pydantic models: `ResourceDemand`, `ResourceConfig`

#### [MODIFY] [app.py](file:///C:/0001_Project/PRISM/backend/app.py)
- Register new `resources_router`

### Database Seeding
#### [NEW] [seed_resources.py](file:///C:/0001_Project/PRISM/backend/scripts/seed_resources.py)
- Script to populate `disease_config` collection with initial medical rates (Hospitalization rates for Dengue/COVID)

---

## Verification Plan

### Automated Tests
- **Unit Tests**: Verify the math (calculator logic).
    - `pytest tests/unit/test_resource_service.py`
- **Integration Tests**: Verify API and DB connection.
    - `pytest tests/integration/test_resource_api.py`

### Manual Verification
1. Run `python -m backend.scripts.seed_resources` to load config.
2. Start API: `python -m uvicorn backend.app:app`
3. Call `POST /resources/predict` with a region/date.
4. Verify response contains `beds_needed` matching manual calculation.
