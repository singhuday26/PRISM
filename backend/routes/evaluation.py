"""Evaluation routes for model performance metrics."""
import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, status
from pymongo.errors import PyMongoError

from backend.db import get_db
from backend.services.evaluation import evaluate_forecast
from backend.utils.validators import validate_disease, validate_region_id
from backend.exceptions import DiseaseValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/forecast")
def get_forecast_evaluation(
    region_id: str = Query(..., description="Region ID to evaluate"),
    date: Optional[str] = Query(None, description="Starting date (YYYY-MM-DD)"),
    horizon: int = Query(7, ge=1, le=30, description="Forecast horizon in days"),
):
    """
    Evaluate forecast accuracy for a region.
    
    Compares forecast predictions with actual observed values and returns
    MAE (Mean Absolute Error) and MAPE (Mean Absolute Percentage Error).
    """
    try:
        validated_region = validate_region_id(region_id) or region_id.strip().upper()
        logger.info(f"Evaluating forecast for region {validated_region}, horizon {horizon}")
        
        result = evaluate_forecast(validated_region, date, horizon)
        
        if result.get("error"):
            logger.warning(f"Evaluation returned error: {result['error']}")
        
        return result
        
    except PyMongoError as e:
        logger.error(f"Database error during evaluation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred during evaluation",
        )
    except Exception as e:
        logger.error(f"Unexpected error during evaluation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during evaluation",
        )


@router.get("/compare")
def compare_models(
    region_id: str = Query(..., description="Region to compare models"),
    date: Optional[str] = Query(None, description="Base date for comparison"),
    horizon: int = Query(7, ge=1, le=14, description="Number of periods"),
    disease: Optional[str] = Query(None, description="Filter by disease"),
    granularity: str = Query("monthly", description="Data granularity")
):
    """
    Compare naive vs ARIMA forecast accuracy.
    
    Generates forecasts using both methods and compares against actual values.
    """
    try:
        from backend.services.arima_forecasting import compare_forecast_models
        
        validated_region = validate_region_id(region_id) or region_id.strip().upper()
        validated_disease = validate_disease(disease)
        
        # Get actual values from database
        db = get_db()
        cases_col = db["cases_daily"]
        
        case_filter = {"region_id": validated_region}
        if date:
            case_filter["date"] = {"$gt": date}
        if validated_disease:
            case_filter["disease"] = validated_disease
        if granularity != "yearly":
            case_filter["granularity"] = granularity
            
        actual_docs = list(
            cases_col.find(case_filter)
            .sort("date", 1)
            .limit(horizon)
        )
        
        if not actual_docs:
            return {
                "error": "No actual data found for comparison",
                "region_id": validated_region,
                "date": date,
            }
        
        actual_values = [int(doc.get("confirmed", 0) or 0) for doc in actual_docs]
        base_date = date or actual_docs[0].get("date")
        
        result = compare_forecast_models(
            region_id=validated_region,
            target_date=base_date,
            actual_values=actual_values,
            disease=validated_disease,
            granularity=granularity,
        )
        
        return result
        
    except ImportError:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="ARIMA comparison requires pmdarima. Run: pip install pmdarima",
        )
    except DiseaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict(),
        )
    except Exception as e:
        logger.error(f"Error comparing models: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during comparison",
        )


@router.get("/summary")
def evaluation_summary(
    disease: Optional[str] = Query(None, description="Filter by disease"),
    horizon: int = Query(7, ge=1, le=30, description="Horizon to evaluate")
):
    """
    Get evaluation summary across all regions.
    
    Returns aggregate accuracy metrics for each model version.
    """
    try:
        validated_disease = validate_disease(disease)
        
        db = get_db()
        regions_col = db["regions"]
        
        region_filter = {"disease": validated_disease} if validated_disease else {}
        regions = list(regions_col.find(region_filter, {"region_id": 1, "_id": 0}))
        
        results = []
        for region in regions[:20]:  # Limit to 20 for performance
            region_id = region["region_id"]
            eval_result = evaluate_forecast(region_id=region_id, horizon=horizon)
            if eval_result.get("mae") is not None:
                results.append(eval_result)
        
        if not results:
            return {"summary": "No evaluations available", "regions_evaluated": 0}
        
        maes = [r["mae"] for r in results if r.get("mae")]
        mapes = [r["mape"] for r in results if r.get("mape")]
        
        return {
            "regions_evaluated": len(results),
            "horizon": horizon,
            "aggregate_mae": round(sum(maes) / len(maes), 2) if maes else None,
            "aggregate_mape": round(sum(mapes) / len(mapes), 2) if mapes else None,
            "disease": validated_disease,
            "top_regions": sorted(results, key=lambda x: x.get("mae", float("inf")))[:5],
        }
        
    except DiseaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict(),
        )
    except Exception as e:
        logger.error(f"Error generating evaluation summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
