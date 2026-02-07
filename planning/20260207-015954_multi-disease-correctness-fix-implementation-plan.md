<!-- Session Manager Metadata
session_id: 20260207-015954_multi-disease-correctness-fix-implementation-plan
original_file: glistening-brewing-feigenbaum.md
saved_at: 2026-02-07T01:59:54.731631
original_modified: 2026-02-06T14:53:49.495807
-->

# Multi-Disease Correctness Fix - Implementation Plan

## Problem Summary

The system currently stores disease fields in documents but has critical data collision bugs:

- **Database indexes**: Missing `disease` in unique constraints, causing overwrites
- **Upsert operations**: All missing `disease` in query filters across 5 service files
- **Regions collection**: Unique index on `region_id` alone blocks multi-disease support
- **Schemas**: Data models missing disease field definitions

**Result**: Different diseases with same (region_id, date) overwrite each other's data.

## Architecture Decisions (User Confirmed)

1. **Regions**: Hybrid approach - one region document per region_id with optional disease field for disease-specific metadata
2. **Migration**: Assign existing data to "DENGUE" as default disease
3. **API**: Disease parameter optional everywhere (filter when provided, return all when omitted)

## Implementation Phases

### Phase 1: Database Schema & Indexes

**File**: `backend/db.py` (lines 76-119, `ensure_indexes()` function)

**Changes**:

1. **regions collection** - Change from unique `region_id` to compound:

```python
# BEFORE:
db["regions"].create_index("region_id", unique=True)

# AFTER:
db["regions"].create_index([
    ("region_id", ASCENDING),
    ("disease", ASCENDING)
], unique=True, sparse=True)
```

2. **cases_daily** - Ensure disease is in unique constraint:

```python
db["cases_daily"].create_index([
    ("region_id", ASCENDING),
    ("date", ASCENDING),
    ("disease", ASCENDING)
], unique=True, sparse=True)
```

3. **risk_scores** - Add disease-aware indexes:

```python
# Unique constraint for isolation
db["risk_scores"].create_index([
    ("region_id", ASCENDING),
    ("date", ASCENDING),
    ("disease", ASCENDING)
], unique=True, sparse=True)

# Performance index for queries
db["risk_scores"].create_index([
    ("date", ASCENDING),
    ("disease", ASCENDING),
    ("risk_score", ASCENDING)
])
```

4. **alerts** - Add disease-aware indexes:

```python
# Unique constraint
db["alerts"].create_index([
    ("region_id", ASCENDING),
    ("date", ASCENDING),
    ("disease", ASCENDING),
    ("reason", ASCENDING)
], unique=True, sparse=True)

# Performance index
db["alerts"].create_index([
    ("date", ASCENDING),
    ("disease", ASCENDING),
    ("risk_score", ASCENDING)
])
```

5. **forecasts_daily** - Add disease to unique constraint:

```python
db["forecasts_daily"].create_index([
    ("region_id", ASCENDING),
    ("date", ASCENDING),
    ("disease", ASCENDING),
    ("model_version", ASCENDING)
], unique=True, sparse=True)
```

**Note**: Use `sparse=True` to allow null disease values (backward compatibility)

---

### Phase 2: Schema Definitions

Add `disease: Optional[str]` field to all data models:

**Files to update**:

1. `backend/schemas/region.py`:

```python
class Region(BaseModel):
    region_id: str = Field(description="Unique region identifier")
    region_name: str = Field(description="Human readable name")
    disease: Optional[str] = Field(default=None, description="Disease-specific region metadata (null = disease-agnostic)")
```

2. `backend/schemas/case.py`:

```python
class CaseDaily(BaseModel):
    # ... existing fields ...
    disease: Optional[str] = Field(default=None, description="Disease identifier (e.g., DENGUE, COVID)")
```

3. `backend/schemas/risk_score.py`:

```python
class RiskScore(BaseModel):
    # ... existing fields ...
    disease: Optional[str] = Field(default=None, description="Disease identifier")
```

4. `backend/schemas/forecast_daily.py`:

```python
class ForecastDaily(BaseModel):
    # ... existing fields ...
    disease: Optional[str] = Field(default=None, description="Disease identifier")
```

---

### Phase 3: Service Layer - Fix Upsert Operations

**Critical**: All upserts must include `disease` in query filter to prevent cross-disease overwrites.

#### 3.1 ingestion.py (lines 9-52)

**File**: `backend/services/ingestion.py`

**Function**: `upsert_regions()` (lines ~13-29)

```python
def upsert_regions(regions: Iterable[Dict]) -> int:
    """Upsert region documents with disease isolation."""
    # ... existing code ...
    for region in regions:
        # Build query filter
        query_filter = {"region_id": region["region_id"]}
        # Include disease if present
        if "disease" in region and region["disease"] is not None:
            query_filter["disease"] = region["disease"]

        res = db["regions"].update_one(
            query_filter,  # Changed from just {"region_id": ...}
            {"$setOnInsert": region},
            upsert=True,
        )
```

**Function**: `upsert_cases()` (lines ~38-52)

```python
def upsert_cases(cases: Iterable[Dict]) -> int:
    """Upsert case documents with disease isolation."""
    # ... existing code ...
    for case in cases:
        query_filter = {
            "region_id": case["region_id"],
            "date": case["date"],
        }
        # Include disease in filter for proper isolation
        if "disease" in case and case["disease"] is not None:
            query_filter["disease"] = case["disease"]

        res = db["cases_daily"].update_one(
            query_filter,  # Changed from just {"region_id": ..., "date": ...}
            {"$setOnInsert": case},
            upsert=True,
        )
```

#### 3.2 risk.py (line ~224)

**File**: `backend/services/risk.py`

**Function**: `compute_risk_scores()` - upsert operation

```python
# Build upsert filter including disease
upsert_filter = {"region_id": region_id, "date": target_date}
if disease:
    upsert_filter["disease"] = disease

risk_col.update_one(
    upsert_filter,  # Changed from {"region_id": region_id, "date": target_date}
    {"$set": doc},
    upsert=True
)
```

#### 3.3 alerts.py (line ~74-78)

**File**: `backend/services/alerts.py`

**Function**: `generate_alerts()` - upsert operation

```python
# Build upsert filter including disease
upsert_filter = {
    "region_id": alert["region_id"],
    "date": target_date,
    "reason": alert["reason"]
}
if disease:
    upsert_filter["disease"] = disease

alerts_col.update_one(
    upsert_filter,  # Changed
    {"$set": alert},
    upsert=True,
)
```

#### 3.4 forecasting.py (line ~136-140)

**File**: `backend/services/forecasting.py`

**Function**: `generate_forecast()` - upsert operation

```python
# Build upsert filter including disease
upsert_filter = {
    "region_id": region_id,
    "date": f_date,
    "model_version": MODEL_VERSION
}
if disease:
    upsert_filter["disease"] = disease

forecasts_col.update_one(
    upsert_filter,  # Changed
    {"$set": doc},
    upsert=True,
)
```

#### 3.5 arima_forecasting.py (line ~246-250)

**File**: `backend/services/arima_forecasting.py`

**Function**: `generate_arima_forecast()` - upsert operation

```python
# Build upsert filter including disease
upsert_filter = {
    "region_id": region_id,
    "date": f_date,
    "model_version": model_version
}
if disease:
    upsert_filter["disease"] = disease

forecasts_col.update_one(
    upsert_filter,  # Changed
    {"$set": doc},
    upsert=True,
)
```

---

### Phase 4: Data Migration

**File**: Create new `backend/scripts/migrate_multi_disease.py`

**Purpose**: Add disease field to existing documents before deploying new indexes

**Script content**:

```python
"""Migration script to add disease field to existing documents."""

from backend.db import get_db

def migrate_existing_data(default_disease: str = "DENGUE"):
    """
    Add disease field to existing documents.

    Args:
        default_disease: Disease to assign to existing data (default: DENGUE)
    """
    db = get_db()

    # 1. Regions: Set disease=null (disease-agnostic by default)
    result = db["regions"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": None}}
    )
    print(f"✓ Regions: Set disease=null for {result.modified_count} documents")

    # 2. Cases: Assign to default disease
    result = db["cases_daily"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"✓ Cases: Assigned disease={default_disease} to {result.modified_count} documents")

    # 3. Risk scores: Assign to default disease
    result = db["risk_scores"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"✓ Risk scores: Assigned disease={default_disease} to {result.modified_count} documents")

    # 4. Alerts: Assign to default disease
    result = db["alerts"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"✓ Alerts: Assigned disease={default_disease} to {result.modified_count} documents")

    # 5. Forecasts: Assign to default disease
    result = db["forecasts_daily"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"✓ Forecasts: Assigned disease={default_disease} to {result.modified_count} documents")

    print("\n✓ Migration complete!")

if __name__ == "__main__":
    migrate_existing_data()
```

**Migration Steps (Critical Order)**:

1. **Backup database**: `mongodump --db prism_db --out ./backup_before_migration`
2. **Run migration**: `python -m backend.scripts.migrate_multi_disease`
3. **Drop old indexes**: Run script to remove old single-field indexes
4. **Deploy code**: Update service code with new upsert logic
5. **Create new indexes**: Run updated `backend/db.py ensure_indexes()`
6. **Verify**: Run tests to confirm isolation

---

### Phase 5: Testing & Verification

**Create new test**: `tests/test_multi_disease_isolation.py`

**Test cases**:

1. **Test cases isolation**:

```python
def test_cases_disease_isolation():
    """Verify cases for different diseases don't overwrite."""
    # Insert DENGUE case
    upsert_cases([{
        "region_id": "TEST_REGION",
        "date": "2024-01-01",
        "confirmed": 100,
        "disease": "DENGUE"
    }])

    # Insert COVID case (same region, same date)
    upsert_cases([{
        "region_id": "TEST_REGION",
        "date": "2024-01-01",
        "confirmed": 200,
        "disease": "COVID"
    }])

    # Verify both exist independently
    db = get_db()
    dengue = db["cases_daily"].find_one({
        "region_id": "TEST_REGION",
        "date": "2024-01-01",
        "disease": "DENGUE"
    })
    covid = db["cases_daily"].find_one({
        "region_id": "TEST_REGION",
        "date": "2024-01-01",
        "disease": "COVID"
    })

    assert dengue["confirmed"] == 100  # Not overwritten
    assert covid["confirmed"] == 200
```

2. **Test risk scores isolation** (same pattern for risk_scores collection)
3. **Test alerts isolation** (same pattern for alerts collection)
4. **Test forecasts isolation** (same pattern for forecasts_daily collection)

**Run existing tests**:

```bash
pytest tests/ -v
```

**Expected outcome**: All existing tests pass + new isolation tests pass

---

## Critical Files to Modify

| File                                       | Purpose                | Key Changes                                      |
| ------------------------------------------ | ---------------------- | ------------------------------------------------ |
| `backend/db.py`                            | Database indexes       | Add disease to all unique indexes (lines 76-119) |
| `backend/services/ingestion.py`            | Case/region upserts    | Add disease to query filters (lines 9-52)        |
| `backend/services/risk.py`                 | Risk score upserts     | Add disease to query filter (line ~224)          |
| `backend/services/alerts.py`               | Alert upserts          | Add disease to query filter (line ~74)           |
| `backend/services/forecasting.py`          | Forecast upserts       | Add disease to query filter (line ~136)          |
| `backend/services/arima_forecasting.py`    | ARIMA forecast upserts | Add disease to query filter (line ~246)          |
| `backend/schemas/region.py`                | Region schema          | Add disease field                                |
| `backend/schemas/case.py`                  | Case schema            | Add disease field                                |
| `backend/schemas/risk_score.py`            | Risk score schema      | Add disease field                                |
| `backend/schemas/forecast_daily.py`        | Forecast schema        | Add disease field                                |
| `backend/scripts/migrate_multi_disease.py` | Data migration         | New file - migrate existing data                 |

---

## Implementation Sequence

**Recommended order**:

1. ✅ **Phase 2** (Schemas): Add disease field to data models - LOW RISK
2. ✅ **Phase 4** (Migration): Create migration script - PREP
3. ✅ **Phase 3** (Services): Fix upsert operations - CORE FIX
4. ✅ **Phase 1** (Database): Update indexes - REQUIRES MIGRATION
5. ✅ **Phase 5** (Testing): Verify isolation - VALIDATION

**Why this order?**

- Schema changes are additive (safe)
- Upsert fixes work with or without new indexes (forward compatible)
- Run migration before creating new indexes (avoids constraint violations)
- Test after all changes deployed

---

## Rollback Strategy

If issues arise during migration:

1. **Stop deployment**: Don't proceed to next phase
2. **Restore database**: `mongorestore --db prism_db ./backup_before_migration`
3. **Revert code**: `git revert <commit-hash>`
4. **Drop new indexes**: Remove disease-inclusive indexes if created
5. **Recreate old indexes**: Run old index creation script
6. **Document issue**: Record what failed and why

---

## Success Criteria

- [ ] Multiple diseases can coexist for same (region_id, date) in all collections
- [ ] Upsert operations include disease in query filters
- [ ] Database indexes include disease in unique constraints
- [ ] Data models include disease field
- [ ] Migration assigns "DENGUE" to existing data
- [ ] All existing tests pass
- [ ] New multi-disease isolation tests pass (4 new tests)
- [ ] Can run full pipeline for DENGUE and COVID simultaneously without collisions
- [ ] No data loss during migration

---

## Verification Checklist

After implementation, verify end-to-end:

1. **Database level**:

   ```bash
   mongo prism_db --eval "db.cases_daily.getIndexes()"
   # Should show compound index with disease field
   ```

2. **Service level**:

   ```bash
   # Run pipeline for DENGUE
   curl -X POST "http://localhost:8000/pipeline/run?disease=DENGUE"

   # Run pipeline for COVID
   curl -X POST "http://localhost:8000/pipeline/run?disease=COVID"

   # Verify both exist
   curl "http://localhost:8000/risk/latest?disease=DENGUE"
   curl "http://localhost:8000/risk/latest?disease=COVID"
   ```

3. **Data isolation**:

   ```bash
   mongo prism_db --eval "db.risk_scores.count({disease: 'DENGUE'})"
   mongo prism_db --eval "db.risk_scores.count({disease: 'COVID'})"
   # Both should return counts (not zero, not same documents)
   ```

4. **Run tests**:
   ```bash
   pytest tests/ -v -k multi_disease
   ```

---

## Estimated Effort

- Phase 1 (Database): 2 hours
- Phase 2 (Schemas): 1 hour
- Phase 3 (Services): 3 hours
- Phase 4 (Migration): 2 hours
- Phase 5 (Testing): 3 hours

**Total**: ~11 hours development + testing
