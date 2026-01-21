# 🏥 Feature Spec: Resource Allocation Intelligence

> **Priority**: P0 (Strategic Core)
> **Product**: PRISM Command (Product A)
> **Goal**: Translate abstract "risk/cases" into concrete "resource demands" (Predicted Bed Shortage).

---

## 1. Overview
Authorities struggle not because they lack case counts, but because they can't translate counts into logistics. This feature fills that gap by calculating:
- **General Ward Beds Needed**
- **ICU Beds Needed**
- **Oxygen Supply Requirements**
- **Nursing Staff Ratio**

## 2. Intelligence Logic (The Math)

The `ResourceModel` applies configurable multipliers to forecasted cases:

$$
\text{Total Active Cases}_t = \sum_{d=t-14}^{t} (\text{New Cases}_d - \text{Recovered}_d - \text{Deceased}_d)
$$

$$
\text{Bed Demand}_t = \text{Active Cases}_t \times \text{Hospitalization Rate}_{\text{disease}}
$$

$$
\text{ICU Demand}_t = \text{Active Cases}_t \times \text{ICU Rate}_{\text{disease}}
$$

### Configurable Parameters (per Disease)

| Parameter | Dengue | COVID (Omicron) | COVID (Delta) |
|-----------|--------|-----------------|---------------|
| `hospitalization_rate` | 0.20 (20%) | 0.05 (5%) | 0.15 (15%) |
| `icu_rate` | 0.01 (1%) | 0.005 (0.5%) | 0.03 (3%) |
| `avg_length_of_stay` | 4 days | 5 days | 12 days |
| `oxygen_requirement` | Low | Low | High |

---

## 3. Database Schema

### `disease_config` collection (New)
*Stores the medical constants for calculation.*
```javascript
{
  "_id": "dengue",
  "name": "Dengue",
  "resource_params": {
    "hospitalization_rate": 0.20,
    "icu_rate": 0.01,
    "avg_stay_days": 4,
    "nurse_ratio": 0.1  // 1 nurse per 10 patients
  }
}
```

### `resource_forecasts` collection (New)
*Stores the output of the intelligence model.*
```javascript
{
  "region_id": "IN-MH",
  "date": "2024-02-01",
  "disease": "dengue",
  "demand": {
    "general_beds": 150,
    "icu_beds": 12,
    "nurses": 16,
    "oxygen_cylinders": 5
  },
  "capacity": {  // Optional: If we track capacity
    "general_beds": 200,
    "icu_beds": 20
  },
  "status": "SAFE" // SAFE, WARNING, CRITICAL
}
```

---

## 4. API Layer

### `POST /resources/predict`
Generate resource predictions for a region/date range.

**Request:**
```json
{
  "region_id": "IN-MH",
  "date": "2024-02-01",
  "disease": "dengue"
}
```

**Response:**
```json
{
  "date": "2024-02-01",
  "forecasted_cases": 750,
  "resources": {
    "beds_needed": 150,
    "icu_needed": 8,
    "shortage_risk": false
  }
}
```

### `GET /resources/config`
View/Edit the medical parameters (Admin only).

---

## 5. Implementation Plan

1. **Create `backend/services/resources.py`**:
   - Implement the calculation logic.
   - Fetch forecasts from `ForecastService`.
   - Fetch config from DB.

2. **Create `backend/routes/resources.py`**:
   - Endpoints for prediction and config management.

3. **Update Pydantic Models**:
   - Add `ResourceDemand` model.

4. **Unit Tests**:
   - Test "Calculate 100 cases -> 20 beds" logic.

---

## 6. Success Metric for Engineering
- **Accuracy**: Calculations must exactly match the medical formula.
- **Latency**: Prediction < 200ms.
