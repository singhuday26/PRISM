
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query

from backend.services.resources import ResourceService
from backend.schemas.responses import (
    ResourcePredictionResponse, 
    ResourceConfig, 
    ErrorResponse
)
from backend.utils.validators import validate_iso_date, validate_disease
from backend.exceptions import (
    DateValidationError, 
    DiseaseValidationError, 
    DataNotFoundError
)

logger = logging.getLogger(__name__)
router = APIRouter()

def get_resource_service():
    return ResourceService()

@router.post(
    "/predict", 
    response_model=ResourcePredictionResponse,
    description="Generate resource demand forecast based on predicted active cases."
)
def predict_resources(
    region_id: str,
    date: str = Query(..., description="Target date (YYYY-MM-DD)"),
    disease: str = Query(..., description="Disease type"),
    service: ResourceService = Depends(get_resource_service)
):
    try:
        validated_date = validate_iso_date(date)
        validated_disease = validate_disease(disease)
        
        return service.predict_demand(
            region_id=region_id,
            target_date=validated_date,
            disease=validated_disease
        )
    except (DateValidationError, DiseaseValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Error predicting resources: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error generating resource prediction"
        )

@router.get(
    "/config/{disease}", 
    response_model=ResourceConfig,
    description="Get resource calculation parameters for a disease."
)
def get_config(
    disease: str,
    service: ResourceService = Depends(get_resource_service)
):
    try:
        validated_disease = validate_disease(disease)
        return service.get_config(validated_disease)
    except DiseaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict()
        )

@router.post(
    "/config",
    response_model=ResourceConfig,
    description="Update resource calculation parameters (Admin)."
)
def update_config(
    config: ResourceConfig,
    service: ResourceService = Depends(get_resource_service)
):
    try:
        validate_disease(config.disease)
        service.set_config(config)
        return config
    except DiseaseValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.to_dict()
        )
    except Exception as e:
        logger.error(f"Error updating config: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update configuration"
        )
