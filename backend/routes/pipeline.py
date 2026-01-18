import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, status
from pymongo.errors import PyMongoError

from backend.db import get_db, ensure_indexes
from backend.services.risk import compute_risk_scores
from backend.services.alerts import generate_alerts
from backend.services.forecasting import generate_forecasts

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run")
def run_full_pipeline(
    disease: str = Query("DENGUE", description="Disease to process (e.g., 'DENGUE', 'COVID')"),
    reset: bool = Query(False, description="Delete existing derived data for this disease before running"),
    horizon: int = Query(7, description="Forecast horizon in days"),
    granularity: str = Query("monthly", description="Forecast data granularity (yearly/monthly/weekly)")
):
    """
    Run the full PRISM pipeline in one call: risk scores → alerts → forecasts.
    
    Args:
        disease: Disease filter (default: DENGUE)
        reset: If true, delete existing risk_scores, alerts, forecasts for this disease
        horizon: Forecast horizon in days (default: 7)
        granularity: Data granularity for forecasting (default: monthly)
    
    Returns:
        JSON summary with counts of records created
    """
    try:
        db = get_db()
        
        # Step 0: Ensure indexes exist
        logger.info("Ensuring database indexes...")
        ensure_indexes()
        
        # Step 1: Reset if requested
        if reset:
            logger.info(f"Reset requested: deleting derived data for disease={disease}")
            delete_filter = {"disease": disease}
            
            risk_deleted = db.risk_scores.delete_many(delete_filter)
            alerts_deleted = db.alerts.delete_many(delete_filter)
            forecasts_deleted = db.forecasts_daily.delete_many(delete_filter)
            
            logger.info(
                f"Deleted {risk_deleted.deleted_count} risk scores, "
                f"{alerts_deleted.deleted_count} alerts, "
                f"{forecasts_deleted.deleted_count} forecasts"
            )
        
        # Step 2: Compute risk scores
        logger.info(f"Step 1/3: Computing risk scores for disease={disease}")
        risk_date, risk_results = compute_risk_scores(target_date=None, disease=disease)
        risk_count = len(risk_results)
        logger.info(f"✓ Created {risk_count} risk scores for {risk_date}")
        
        # Step 3: Generate alerts
        logger.info(f"Step 2/3: Generating alerts for disease={disease}")
        alert_date, alert_results = generate_alerts(target_date=None, disease=disease)
        alert_count = len(alert_results)
        logger.info(f"✓ Created {alert_count} alerts for {alert_date}")
        
        # Step 4: Generate forecasts
        logger.info(f"Step 3/3: Generating forecasts for disease={disease}, horizon={horizon}, granularity={granularity}")
        forecast_date, forecast_results = generate_forecasts(
            target_date=None, 
            horizon=horizon, 
            disease=disease,
            granularity=granularity
        )
        forecast_count = len(forecast_results)
        logger.info(f"✓ Created {forecast_count} forecasts for {forecast_date}")
        
        # Step 5: Get total counts from database
        total_risk = db.risk_scores.count_documents({"disease": disease})
        total_alerts = db.alerts.count_documents({"disease": disease})
        total_forecasts = db.forecasts_daily.count_documents({"disease": disease})
        
        # Build response
        response = {
            "success": True,
            "disease": disease,
            "reset": reset,
            "horizon": horizon,
            "granularity": granularity,
            "execution_date": risk_date,
            "created": {
                "risk_scores": risk_count,
                "alerts": alert_count,
                "forecasts": forecast_count
            },
            "total": {
                "risk_scores": total_risk,
                "alerts": total_alerts,
                "forecasts": total_forecasts
            }
        }
        
        logger.info(f"Pipeline completed successfully for disease={disease}")
        return response
        
    except PyMongoError as e:
        logger.error(f"Database error in pipeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
