import logging
import time
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, status
from pymongo.errors import PyMongoError

from backend.db import get_db, ensure_indexes
from backend.services.risk import compute_risk_scores
from backend.services.alerts import generate_alerts
from backend.services.arima_forecasting import generate_arima_forecasts

logger = logging.getLogger(__name__)
router = APIRouter()


def _step_result(name: str, *, status: str = "success", duration_ms: int = 0,
                 records_created: int = 0, total_records: int = 0,
                 detail: str = "") -> dict:
    """Build a structured step-result dict."""
    return {
        "name": name,
        "status": status,
        "duration_ms": duration_ms,
        "records_created": records_created,
        "total_records": total_records,
        "detail": detail,
    }


@router.post("/run")
def run_full_pipeline(
    disease: str = Query("DENGUE", description="Disease to process (e.g., 'DENGUE', 'COVID')"),
    reset: bool = Query(False, description="Delete existing derived data for this disease before running"),
    horizon: int = Query(7, description="Forecast horizon in days"),
    granularity: str = Query("monthly", description="Forecast data granularity (yearly/monthly/weekly)")
):
    """
    Run the full PRISM pipeline in one call: risk scores → alerts → forecasts.

    Returns a detailed step-by-step execution report with per-step timing,
    record counts, and status so the frontend can render a rich progress UI.
    """
    pipeline_start = time.time()
    steps: list[dict] = []

    try:
        db = get_db()

        # Step 0: Ensure indexes
        logger.info("Ensuring database indexes...")
        ensure_indexes()

        # ── Step 1: Reset ──────────────────────────────────────────────────
        t0 = time.time()
        if reset:
            logger.info(f"Reset requested: deleting derived data for disease={disease}")
            filt = {"disease": disease}
            r_del = db.risk_scores.delete_many(filt).deleted_count
            a_del = db.alerts.delete_many(filt).deleted_count
            f_del = db.forecasts_daily.delete_many(filt).deleted_count
            total_deleted = r_del + a_del + f_del
            logger.info(f"Deleted {r_del} risk scores, {a_del} alerts, {f_del} forecasts")
            steps.append(_step_result(
                "reset", status="success",
                duration_ms=int((time.time() - t0) * 1000),
                records_created=0, total_records=total_deleted,
                detail=f"Deleted {r_del} risk, {a_del} alerts, {f_del} forecasts",
            ))
        else:
            steps.append(_step_result(
                "reset", status="skipped",
                duration_ms=0, detail="Reset not requested",
            ))

        # ── Step 2: Risk scores ────────────────────────────────────────────
        t0 = time.time()
        logger.info(f"Step 1/3: Computing risk scores for disease={disease}")
        try:
            risk_date, risk_results = compute_risk_scores(target_date=None, disease=disease)
            risk_count = len(risk_results)
            total_risk = db.risk_scores.count_documents({"disease": disease})
            logger.info(f"✓ Created {risk_count} risk scores for {risk_date}")
            steps.append(_step_result(
                "risk_scores", status="success",
                duration_ms=int((time.time() - t0) * 1000),
                records_created=risk_count, total_records=total_risk,
                detail=f"Computed for {risk_count} regions on {risk_date}",
            ))
        except Exception as e:
            logger.error(f"Risk score computation failed: {e}", exc_info=True)
            risk_count = 0
            total_risk = db.risk_scores.count_documents({"disease": disease})
            steps.append(_step_result(
                "risk_scores", status="error",
                duration_ms=int((time.time() - t0) * 1000),
                detail=str(e)[:200],
            ))

        # ── Step 3: Alerts ─────────────────────────────────────────────────
        t0 = time.time()
        logger.info(f"Step 2/3: Generating alerts for disease={disease}")
        try:
            alert_date, alert_results = generate_alerts(target_date=None, disease=disease)
            alert_count = len(alert_results)
            total_alerts = db.alerts.count_documents({"disease": disease})
            logger.info(f"✓ Created {alert_count} alerts for {alert_date}")
            steps.append(_step_result(
                "alerts", status="success",
                duration_ms=int((time.time() - t0) * 1000),
                records_created=alert_count, total_records=total_alerts,
                detail=f"Generated {alert_count} alerts for {alert_date}",
            ))
        except Exception as e:
            logger.error(f"Alert generation failed: {e}", exc_info=True)
            alert_count = 0
            total_alerts = db.alerts.count_documents({"disease": disease})
            steps.append(_step_result(
                "alerts", status="error",
                duration_ms=int((time.time() - t0) * 1000),
                detail=str(e)[:200],
            ))

        # ── Step 4: Forecasts ──────────────────────────────────────────────
        t0 = time.time()
        logger.info(f"Step 3/3: Generating forecasts for disease={disease}, horizon={horizon}, granularity={granularity}")
        try:
            forecast_date, forecast_results = generate_arima_forecasts(
                target_date=None,
                horizon=horizon,
                disease=disease,
                granularity=granularity,
            )
            forecast_count = len(forecast_results)
            total_forecasts = db.forecasts_daily.count_documents({"disease": disease})
            logger.info(f"✓ Created {forecast_count} forecasts for {forecast_date}")
            steps.append(_step_result(
                "forecasts", status="success",
                duration_ms=int((time.time() - t0) * 1000),
                records_created=forecast_count, total_records=total_forecasts,
                detail=f"ARIMA {horizon}-day forecast for {forecast_count} regions",
            ))
        except Exception as e:
            logger.warning(f"Forecast generation failed: {e}", exc_info=True)
            forecast_count = 0
            total_forecasts = db.forecasts_daily.count_documents({"disease": disease})
            steps.append(_step_result(
                "forecasts", status="error",
                duration_ms=int((time.time() - t0) * 1000),
                detail=str(e)[:200],
            ))

        # ── Build response ─────────────────────────────────────────────────
        total_duration = time.time() - pipeline_start
        any_errors = any(s["status"] == "error" for s in steps)

        response = {
            "success": not any_errors,
            "disease": disease,
            "reset": reset,
            "horizon": horizon,
            "granularity": granularity,
            "execution_date": risk_date if risk_count else None,
            "duration_seconds": round(total_duration, 2),
            "steps": steps,
            "created": {
                "risk_scores": risk_count,
                "alerts": alert_count,
                "forecasts": forecast_count,
            },
            "total": {
                "risk_scores": total_risk,
                "alerts": total_alerts,
                "forecasts": total_forecasts,
            },
        }

        logger.info(f"Pipeline completed for disease={disease} in {total_duration:.1f}s "
                     f"(errors={'yes' if any_errors else 'none'})")
        return response

    except PyMongoError as e:
        logger.error(f"Database error in pipeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline execution failed: {str(e)}"
        )


@router.get("/status")
def get_pipeline_status(disease: Optional[str] = Query(None, description="Filter by disease")):
    """
    Get current pipeline data counts.
    
    Args:
        disease: Optional disease filter
    
    Returns:
        Counts of risk_scores, alerts, forecasts (total or filtered by disease)
    """
    try:
        db = get_db()
        
        query_filter = {"disease": disease} if disease else {}
        
        risk_count = db.risk_scores.count_documents(query_filter)
        alert_count = db.alerts.count_documents(query_filter)
        forecast_count = db.forecasts_daily.count_documents(query_filter)
        
        response = {
            "risk_scores": risk_count,
            "alerts": alert_count,
            "forecasts": forecast_count
        }
        
        if disease:
            response["disease"] = disease
        
        return response
        
    except PyMongoError as e:
        logger.error(f"Database error getting status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
