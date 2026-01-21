# 🧪 Verification: Resource Allocation Intelligence

> **Component**: PRISM Command Backend (Product A)
> **Goal**: Verify that "Cases" are correctly translated into "Hospital Beds".

## Prerequisite: Seed the Database
We created a new collection `disease_config` with medical constants. Use the script to populate it.

```powershell
python -m backend.scripts.seed_resources
```
*Expected Output*: "Resource seeding complete."

---

## 1. Verify Logic (Unit Tests)
Run the new test suite which mocks the database to ensure the math is perfect.

```powershell
pytest tests/unit/test_resource_service.py -v
```
*Expected*: 2 passed tests (`test_get_config_defaults`, `test_predict_demand_math`).

---

## 2. Verify API (Manual Forecast)
Start the server and test the live prediction endpoint.

**Start Server:**
```powershell
python -m uvicorn backend.app:app --reload
```

**Test Request (PowerShell):**
```powershell
$body = @{
    region_id = "IN-MH"
    date = "2024-02-01" # Target date
    disease = "dengue"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/resources/predict?region_id=IN-MH&date=2024-02-01&disease=dengue" -Method Post -Body $body -ContentType "application/json"
```

**Expected Response:**
```json
{
  "region_id": "IN-MH",
  "forecasted_cases": 0,  // (Likely 0 if no forecasts in local DB yet)
  "resources": {
    "general_beds": 0,
    "icu_beds": 0,
    ...
  }
}
```
*(Note: Since we haven't generated forecasts for 2024-02-01 in your local DB yet, it might return 0. That's expected! The logic works if the API responds 200 OK).*
