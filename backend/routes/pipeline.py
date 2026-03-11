import logging
import time
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, status, Depends, BackgroundTasks
from pymongo.errors import PyMongoError

from backend.db import get_db, ensure_indexes
from backend.services.risk import compute_risk_scores
from backend.services.alerts import generate_alerts
from backend.services.arima_forecasting import generate_arima_forecasts
from backend.routes.auth import get_current_user

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


def _run_pipeline_task(task_id: str, disease: str, reset: bool, horizon: int, granularity: str):
    """Background task to run the full pipeline and update database status."""
    pipeline_start = time.time()
    steps: list[dict] = []
    db = get_db()

    try:
        # Initial status update
        db.pipeline_status.update_one(
            {"task_id": task_id},
            {"$set": {"status": "processing", "started_at": datetime.utcnow()}}
        )

        # Step 0: Ensure indexes
        ensure_indexes()

        # ── Step 1: Reset ──────────────────────────────────────────────────
        t0 = time.time()
        if reset:
            filt = {"disease": disease}
            r_del = db.risk_scores.delete_many(filt).deleted_count
            a_del = db.alerts.delete_many(filt).deleted_count
            f_del = db.forecasts_daily.delete_many(filt).deleted_count
            total_deleted = r_del + a_del + f_del
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
        
        db.pipeline_status.update_one({"task_id": task_id}, {"$set": {"steps": steps}})

        # ── Step 2: Risk scores ────────────────────────────────────────────
        t0 = time.time()
        try:
            risk_date, risk_results = compute_risk_scores(target_date=None, disease=disease)
            risk_count = len(risk_results)
            total_risk = db.risk_scores.count_documents({"disease": disease})
            steps.append(_step_result(
                "risk_scores", status="success",
                duration_ms=int((time.time() - t0) * 1000),
                records_created=risk_count, total_records=total_risk,
                detail=f"Computed for {risk_count} regions on {risk_date}",
            ))
        except Exception as e:
            logger.error(f"Risk score computation failed: {e}")
            steps.append(_step_result("risk_scores", status="error", detail=str(e)[:200]))

        db.pipeline_status.update_one({"task_id": task_id}, {"$set": {"steps": steps}})

        # ── Step 3: Alerts ─────────────────────────────────────────────────
        t0 = time.time()
        try:
            alert_date, alert_results = generate_alerts(target_date=None, disease=disease)
            alert_count = len(alert_results)
            total_alerts = db.alerts.count_documents({"disease": disease})
            steps.append(_step_result(
                "alerts", status="success",
                duration_ms=int((time.time() - t0) * 1000),
                records_created=alert_count, total_records=total_alerts,
                detail=f"Generated {alert_count} alerts for {alert_date}",
            ))
        except Exception as e:
            logger.error(f"Alert generation failed: {e}")
            steps.append(_step_result("alerts", status="error", detail=str(e)[:200]))

        db.pipeline_status.update_one({"task_id": task_id}, {"$set": {"steps": steps}})

        # ── Step 4: Forecasts ──────────────────────────────────────────────
        t0 = time.time()
        try:
            forecast_date, forecast_results = generate_arima_forecasts(
                target_date=None, horizon=horizon, disease=disease, granularity=granularity
            )
            forecast_count = len(forecast_results)
            total_forecasts = db.forecasts_daily.count_documents({"disease": disease})
            steps.append(_step_result(
                "forecasts", status="success",
                duration_ms=int((time.time() - t0) * 1000),
                records_created=forecast_count, total_records=total_forecasts,
                detail=f"ARIMA {horizon}-day forecast for {forecast_count} regions",
            ))
        except Exception as e:
            logger.warning(f"Forecast generation failed: {e}")
            steps.append(_step_result("forecasts", status="error", detail=str(e)[:200]))

        # Final update
        total_duration = time.time() - pipeline_start
        any_errors = any(s["status"] == "error" for s in steps)
        
        db.pipeline_status.update_one(
            {"task_id": task_id},
            {
                "$set": {
                    "status": "completed" if not any_errors else "failed",
                    "completed_at": datetime.utcnow(),
                    "duration_seconds": round(total_duration, 2),
                    "steps": steps,
                    "progress": 100
                }
            }
        )

    except Exception as e:
        logger.error(f"Fatal error in background pipeline task: {e}", exc_info=True)
        db.pipeline_status.update_one(
            {"task_id": task_id},
            {"$set": {"status": "failed", "error": str(e), "completed_at": datetime.utcnow()}}
        )


@router.post("/run", status_code=status.HTTP_202_ACCEPTED)
async def run_full_pipeline(
    background_tasks: BackgroundTasks,
    disease: str = Query("DENGUE", description="Disease to process"),
    reset: bool = Query(False, description="Reset existing derived data"),
    horizon: int = Query(7, description="Forecast horizon"),
    granularity: str = Query("monthly", description="Data granularity"),
    current_user: dict = Depends(get_current_user)
):
    """
    Start the full PRISM pipeline as a background task.
    Returns a task_id for tracking status.
    """
    task_id = str(uuid.uuid4())
    db = get_db()
    
    # Initialize status in DB
    db.pipeline_status.insert_one({
        "task_id": task_id,
        "disease": disease,
        "status": "queued",
        "created_at": datetime.utcnow(),
        "params": {
            "reset": reset,
            "horizon": horizon,
            "granularity": granularity
        },
        "steps": [],
        "progress": 0
    })

    background_tasks.add_task(
        _run_pipeline_task, task_id, disease, reset, horizon, granularity
    )
    
    return {
        "task_id": task_id,
        "message": "Pipeline execution started in background",
        "status_url": f"/pipeline/status/{task_id}"
    }


@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """Get the status of a specific background pipeline task."""
    db = get_db()
    task = db.pipeline_status.find_one({"task_id": task_id}, {"_id": 0})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/status")
def get_pipeline_counts(disease: Optional[str] = Query(None, description="Filter by disease")):
    """Get current data counts in the system."""
    try:
        db = get_db()
        query_filter = {"disease": disease} if disease else {}
        
        return {
            "risk_scores": db.risk_scores.count_documents(query_filter),
            "alerts": db.alerts.count_documents(query_filter),
            "forecasts": db.forecasts_daily.count_documents(query_filter),
            "disease": disease
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
