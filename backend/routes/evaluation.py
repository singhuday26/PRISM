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
    disease: Optional[str] = Query(None, description="Filter by disease"),
    granularity: str = Query("monthly", description="Data granularity"),
):
    """
    Evaluate forecast accuracy for a region using holdout validation.

    Uses historical cases_daily data: holds out the last `horizon` records
    and measures a seasonal-naive model's MAE / MAPE / MSE / RMSE / R².
    """
    try:
        validated_region = validate_region_id(region_id) or region_id.strip().upper()
        validated_disease = validate_disease(disease)

        logger.info(
            "Evaluating forecast for region %s, horizon %d, disease %s",
            validated_region, horizon, validated_disease,
        )

        result = evaluate_forecast(
            region_id=validated_region,
            date=date,
            horizon=horizon,
            disease=validated_disease,
            granularity=granularity,
        )

        if result.get("error"):
            logger.warning("Evaluation warning for %s: %s", validated_region, result["error"])

        return result

    except DiseaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict(),
        )
    except PyMongoError as e:
        logger.error("Database error during evaluation: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database error occurred during evaluation",
        )
    except Exception as e:
        logger.error("Unexpected error during evaluation: %s", e, exc_info=True)
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
    granularity: str = Query("monthly", description="Data granularity"),
):
    """
    Compare naive vs ARIMA forecast accuracy.

    Generates forecasts using both methods and compares against actual values.
    """
    try:
        from backend.services.arima_forecasting import compare_forecast_models

        validated_region = validate_region_id(region_id) or region_id.strip().upper()
        validated_disease = validate_disease(disease)

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
        logger.error("Error comparing models: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during comparison",
        )


@router.get("/summary")
def evaluation_summary(
    disease: Optional[str] = Query(None, description="Filter by disease"),
    horizon: int = Query(7, ge=1, le=30, description="Horizon to evaluate"),
    granularity: str = Query("monthly", description="Data granularity"),
    limit: int = Query(20, ge=1, le=50, description="Max regions to evaluate"),
):
    """
    Get evaluation summary across all regions.

    Returns aggregate accuracy metrics computed via walk-forward holdout
    on historical cases_daily data.  No stored forecasts are required.
    """
    try:
        validated_disease = validate_disease(disease)

        db = get_db()
        regions_col = db["regions"]

        # Fetch region list (disease-agnostic)
        regions = list(
            regions_col.find({}, {"region_id": 1, "_id": 0}).limit(limit)
        )

        results = []
        for region in regions:
            region_id = region["region_id"]
            eval_result = evaluate_forecast(
                region_id=region_id,
                horizon=horizon,
                disease=validated_disease,
                granularity=granularity,
            )
            if eval_result.get("mae") is not None:
                results.append(eval_result)

        if not results:
            return {
                "regions_evaluated": 0,
                "horizon": horizon,
                "aggregate_mae": None,
                "aggregate_mape": None,
                "disease": validated_disease,
                "top_regions": [],
            }

        maes  = [r["mae"]  for r in results if r.get("mae")  is not None]
        mapes = [r["mape"] for r in results if r.get("mape") is not None]

        # Top regions = lowest MAE (best performing)
        top_regions = sorted(results, key=lambda x: x.get("mae", float("inf")))[:5]

        return {
            "regions_evaluated": len(results),
            "horizon": horizon,
            "aggregate_mae":  round(sum(maes)  / len(maes),  2) if maes  else None,
            "aggregate_mape": round(sum(mapes) / len(mapes), 4) if mapes else None,
            "disease": validated_disease,
            "top_regions": top_regions,
        }

    except DiseaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict(),
        )
    except Exception as e:
        logger.error("Error generating evaluation summary: %s", e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
