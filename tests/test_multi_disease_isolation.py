"""
Test multi-disease data isolation to ensure different diseases don't overwrite each other.
"""

import pytest
from datetime import datetime
from backend.db import get_db
from backend.services.ingestion import upsert_cases, upsert_regions
from backend.services.risk import compute_risk_scores
from backend.services.alerts import generate_alerts
from backend.services.forecasting import generate_forecasts
from backend.services.arima_forecasting import generate_arima_forecasts


@pytest.fixture
def clean_test_data():
    """Clean up test data before and after tests."""
    db = get_db()
    test_region = "TEST_REGION_MULTI"
    test_date = "2024-01-01"

    # Clean before
    db["regions"].delete_many({"region_id": test_region})
    db["cases_daily"].delete_many({"region_id": test_region})
    db["risk_scores"].delete_many({"region_id": test_region})
    db["alerts"].delete_many({"region_id": test_region})
    db["forecasts_daily"].delete_many({"region_id": test_region})

    yield

    # Clean after
    db["regions"].delete_many({"region_id": test_region})
    db["cases_daily"].delete_many({"region_id": test_region})
    db["risk_scores"].delete_many({"region_id": test_region})
    db["alerts"].delete_many({"region_id": test_region})
    db["forecasts_daily"].delete_many({"region_id": test_region})


def test_cases_disease_isolation(clean_test_data):
    """Verify cases for different diseases are properly isolated."""
    db = get_db()
    test_region = "TEST_REGION_MULTI"
    test_date = "2024-01-01"

    # Insert DENGUE case
    upsert_cases([{
        "region_id": test_region,
        "date": test_date,
        "confirmed": 100,
        "deaths": 5,
        "recovered": 90,
        "disease": "DENGUE"
    }])

    # Insert COVID case (same region, same date, different disease)
    upsert_cases([{
        "region_id": test_region,
        "date": test_date,
        "confirmed": 200,
        "deaths": 10,
        "recovered": 180,
        "disease": "COVID"
    }])

    # Verify both exist independently
    dengue_doc = db["cases_daily"].find_one({
        "region_id": test_region,
        "date": test_date,
        "disease": "DENGUE"
    })
    covid_doc = db["cases_daily"].find_one({
        "region_id": test_region,
        "date": test_date,
        "disease": "COVID"
    })

    assert dengue_doc is not None, "DENGUE case should exist"
    assert covid_doc is not None, "COVID case should exist"
    assert dengue_doc["confirmed"] == 100, "DENGUE confirmed count should be 100 (not overwritten)"
    assert covid_doc["confirmed"] == 200, "COVID confirmed count should be 200"
    assert dengue_doc["deaths"] == 5
    assert covid_doc["deaths"] == 10


def test_risk_scores_disease_isolation(clean_test_data):
    """Verify risk scores for different diseases are properly isolated."""
    db = get_db()
    test_region = "TEST_REGION_MULTI"
    test_date = "2024-01-15"

    # Setup: Insert cases for both diseases
    upsert_regions([{"region_id": test_region, "region_name": "Test Multi Region"}])

    for disease in ["DENGUE", "COVID"]:
        for day in range(1, 15):
            upsert_cases([{
                "region_id": test_region,
                "date": f"2024-01-{day:02d}",
                "confirmed": 50 + day * 5,
                "deaths": day,
                "recovered": 40 + day * 4,
                "disease": disease
            }])

    # Compute risk scores for DENGUE
    _, dengue_results = compute_risk_scores(target_date=test_date, disease="DENGUE")

    # Compute risk scores for COVID
    _, covid_results = compute_risk_scores(target_date=test_date, disease="COVID")

    # Verify both exist in database
    dengue_risk = db["risk_scores"].find_one({
        "region_id": test_region,
        "date": test_date,
        "disease": "DENGUE"
    })
    covid_risk = db["risk_scores"].find_one({
        "region_id": test_region,
        "date": test_date,
        "disease": "COVID"
    })

    assert dengue_risk is not None, "DENGUE risk score should exist"
    assert covid_risk is not None, "COVID risk score should exist"
    assert dengue_risk["disease"] == "DENGUE"
    assert covid_risk["disease"] == "COVID"
    # Risk scores should be different or same based on algorithm, but both should exist independently
    assert "_id" in dengue_risk
    assert "_id" in covid_risk
    assert dengue_risk["_id"] != covid_risk["_id"], "Should be separate documents"


def test_alerts_disease_isolation(clean_test_data):
    """Verify alerts for different diseases are properly isolated."""
    db = get_db()
    test_region = "TEST_REGION_MULTI"
    test_date = "2024-01-15"

    # Setup: Insert risk scores for both diseases with HIGH risk
    db["risk_scores"].insert_one({
        "region_id": test_region,
        "date": test_date,
        "risk_score": 0.8,
        "risk_level": "HIGH",
        "drivers": ["increasing_cases"],
        "updated_at": datetime.utcnow(),
        "disease": "DENGUE"
    })

    db["risk_scores"].insert_one({
        "region_id": test_region,
        "date": test_date,
        "risk_score": 0.75,
        "risk_level": "HIGH",
        "drivers": ["increasing_deaths"],
        "updated_at": datetime.utcnow(),
        "disease": "COVID"
    })

    # Generate alerts for DENGUE
    _, dengue_alerts = generate_alerts(target_date=test_date, disease="DENGUE")

    # Generate alerts for COVID
    _, covid_alerts = generate_alerts(target_date=test_date, disease="COVID")

    # Verify both exist in database
    dengue_alert = db["alerts"].find_one({
        "region_id": test_region,
        "date": test_date,
        "disease": "DENGUE"
    })
    covid_alert = db["alerts"].find_one({
        "region_id": test_region,
        "date": test_date,
        "disease": "COVID"
    })

    assert dengue_alert is not None, "DENGUE alert should exist"
    assert covid_alert is not None, "COVID alert should exist"
    assert dengue_alert["disease"] == "DENGUE"
    assert covid_alert["disease"] == "COVID"
    assert dengue_alert["risk_score"] == 0.8
    assert covid_alert["risk_score"] == 0.75
    assert dengue_alert["_id"] != covid_alert["_id"], "Should be separate documents"


def test_forecasts_disease_isolation(clean_test_data):
    """Verify forecasts for different diseases are properly isolated."""
    db = get_db()
    test_region = "TEST_REGION_MULTI"
    test_date = "2024-01-15"
    forecast_date = "2024-01-16"

    # Setup: Insert historical cases for both diseases
    for disease in ["DENGUE", "COVID"]:
        for day in range(1, 16):
            upsert_cases([{
                "region_id": test_region,
                "date": f"2024-01-{day:02d}",
                "confirmed": 50 + day * 5,
                "deaths": day,
                "recovered": 40 + day * 4,
                "disease": disease
            }])

    # Generate forecasts for DENGUE
    _, dengue_forecasts = generate_forecasts(
        target_date=test_date,
        disease="DENGUE",
        horizon=7
    )

    # Generate forecasts for COVID
    _, covid_forecasts = generate_forecasts(
        target_date=test_date,
        disease="COVID",
        horizon=7
    )

    # Verify both exist in database for the first forecast date
    dengue_forecast = db["forecasts_daily"].find_one({
        "region_id": test_region,
        "date": forecast_date,
        "disease": "DENGUE"
    })
    covid_forecast = db["forecasts_daily"].find_one({
        "region_id": test_region,
        "date": forecast_date,
        "disease": "COVID"
    })

    assert dengue_forecast is not None, "DENGUE forecast should exist"
    assert covid_forecast is not None, "COVID forecast should exist"
    assert dengue_forecast["disease"] == "DENGUE"
    assert covid_forecast["disease"] == "COVID"
    assert dengue_forecast["_id"] != covid_forecast["_id"], "Should be separate documents"


def test_regions_disease_metadata_isolation(clean_test_data):
    """Verify regions can have disease-specific metadata."""
    db = get_db()
    test_region = "TEST_REGION_MULTI"

    # Insert disease-agnostic region (disease=None)
    upsert_regions([{
        "region_id": test_region,
        "region_name": "Test Multi Region",
        "disease": None
    }])

    # Insert disease-specific region metadata
    upsert_regions([{
        "region_id": test_region,
        "region_name": "Test Multi Region (DENGUE specific)",
        "disease": "DENGUE",
        "vector_control_program": "Active",
        "surveillance_level": "High"
    }])

    # Verify both exist
    generic_region = db["regions"].find_one({
        "region_id": test_region,
        "disease": None
    })
    dengue_region = db["regions"].find_one({
        "region_id": test_region,
        "disease": "DENGUE"
    })

    assert generic_region is not None, "Generic region should exist"
    assert dengue_region is not None, "DENGUE-specific region metadata should exist"
    assert generic_region["region_name"] == "Test Multi Region"
    assert dengue_region["region_name"] == "Test Multi Region (DENGUE specific)"
    assert "vector_control_program" in dengue_region
    assert generic_region["_id"] != dengue_region["_id"], "Should be separate documents"


def test_concurrent_disease_pipeline(clean_test_data):
    """Test that full pipeline can run for multiple diseases concurrently without conflicts."""
    db = get_db()
    test_region = "TEST_REGION_MULTI"
    test_date = "2024-01-15"

    # Setup region
    upsert_regions([{"region_id": test_region, "region_name": "Test Multi Region"}])

    # Run full pipeline for DENGUE
    for day in range(1, 16):
        upsert_cases([{
            "region_id": test_region,
            "date": f"2024-01-{day:02d}",
            "confirmed": 100 + day * 10,
            "deaths": day * 2,
            "recovered": 80 + day * 8,
            "disease": "DENGUE"
        }])

    dengue_date, dengue_risks = compute_risk_scores(target_date=test_date, disease="DENGUE")
    dengue_alert_date, dengue_alerts = generate_alerts(target_date=test_date, disease="DENGUE")
    _, dengue_forecasts = generate_forecasts(target_date=test_date, disease="DENGUE", horizon=3)

    # Run full pipeline for COVID
    for day in range(1, 16):
        upsert_cases([{
            "region_id": test_region,
            "date": f"2024-01-{day:02d}",
            "confirmed": 200 + day * 15,
            "deaths": day * 3,
            "recovered": 160 + day * 12,
            "disease": "COVID"
        }])

    covid_date, covid_risks = compute_risk_scores(target_date=test_date, disease="COVID")
    covid_alert_date, covid_alerts = generate_alerts(target_date=test_date, disease="COVID")
    _, covid_forecasts = generate_forecasts(target_date=test_date, disease="COVID", horizon=3)

    # Verify all data exists independently
    dengue_case_count = db["cases_daily"].count_documents({"region_id": test_region, "disease": "DENGUE"})
    covid_case_count = db["cases_daily"].count_documents({"region_id": test_region, "disease": "COVID"})

    dengue_risk_count = db["risk_scores"].count_documents({"region_id": test_region, "disease": "DENGUE"})
    covid_risk_count = db["risk_scores"].count_documents({"region_id": test_region, "disease": "COVID"})

    dengue_forecast_count = db["forecasts_daily"].count_documents({"region_id": test_region, "disease": "DENGUE"})
    covid_forecast_count = db["forecasts_daily"].count_documents({"region_id": test_region, "disease": "COVID"})

    # Assertions
    assert dengue_case_count == 15, f"Should have 15 DENGUE cases, got {dengue_case_count}"
    assert covid_case_count == 15, f"Should have 15 COVID cases, got {covid_case_count}"
    assert dengue_risk_count >= 1, "Should have at least 1 DENGUE risk score"
    assert covid_risk_count >= 1, "Should have at least 1 COVID risk score"
    assert dengue_forecast_count >= 3, "Should have at least 3 DENGUE forecasts"
    assert covid_forecast_count >= 3, "Should have at least 3 COVID forecasts"

    print(f"✓ Multi-disease pipeline isolation verified:")
    print(f"  DENGUE: {dengue_case_count} cases, {dengue_risk_count} risks, {dengue_forecast_count} forecasts")
    print(f"  COVID: {covid_case_count} cases, {covid_risk_count} risks, {covid_forecast_count} forecasts")
