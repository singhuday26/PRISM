"""API routes for disease management."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from backend.disease_config import get_disease_registry
from backend.db import get_db

router = APIRouter()


@router.get("/diseases")
async def list_diseases(
    transmission_mode: Optional[str] = Query(None, description="Filter by transmission mode"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    vaccine_available: Optional[bool] = Query(None, description="Filter by vaccine availability")
):
    """
    List all configured diseases with their metadata.
    
    Can filter by transmission mode, severity, or vaccine availability.
    """
    registry = get_disease_registry()
    diseases = list(registry.diseases.values())
    
    # Apply filters
    if transmission_mode:
        diseases = [d for d in diseases if d.transmission_mode == transmission_mode.lower()]
    
    if severity:
        diseases = [d for d in diseases if d.severity == severity.lower()]
    
    if vaccine_available is not None:
        diseases = [d for d in diseases if d.vaccine_available == vaccine_available]
    
    return {
        "count": len(diseases),
        "diseases": [d.model_dump() for d in diseases]
    }


@router.get("/diseases/{disease_id}")
async def get_disease_profile(disease_id: str):
    """
    Get detailed profile for a specific disease.
    """
    registry = get_disease_registry()
    profile = registry.get_disease(disease_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"Disease '{disease_id}' not found")
    
    return profile.model_dump()


@router.get("/diseases/{disease_id}/stats")
async def get_disease_stats(disease_id: str):
    """
    Get database statistics for a specific disease.
    
    Returns:
    - Total cases
    - Total deaths
    - Total recovered
    - Affected regions
    - Date range
    - Latest data date
    """
    registry = get_disease_registry()
    profile = registry.get_disease(disease_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"Disease '{disease_id}' not found")
    
    db = get_db()
    cases_col = db["cases_daily"]
    
    # Get case statistics
    pipeline = [
        {"$match": {"disease": disease_id.upper()}},
        {
            "$group": {
                "_id": None,
                "total_cases": {"$sum": "$confirmed"},
                "total_deaths": {"$sum": "$deaths"},
                "total_recovered": {"$sum": "$recovered"},
                "affected_regions": {"$addToSet": "$region_id"},
                "min_date": {"$min": "$date"},
                "max_date": {"$max": "$date"},
                "record_count": {"$sum": 1}
            }
        }
    ]
    
    result = list(cases_col.aggregate(pipeline))
    
    if not result:
        return {
            "disease_id": disease_id.upper(),
            "disease_name": profile.name,
            "data_available": False,
            "message": f"No data found for {profile.name}"
        }
    
    stats = result[0]
    
    return {
        "disease_id": disease_id.upper(),
        "disease_name": profile.name,
        "data_available": True,
        "statistics": {
            "total_cases": stats["total_cases"],
            "total_deaths": stats["total_deaths"],
            "total_recovered": stats["total_recovered"],
            "affected_regions_count": len(stats["affected_regions"]),
            "affected_regions": sorted(stats["affected_regions"]),
            "date_range": {
                "start": stats["min_date"],
                "end": stats["max_date"]
            },
            "total_records": stats["record_count"]
        },
        "profile": {
            "transmission_mode": profile.transmission_mode,
            "severity": profile.severity,
            "incubation_period_days": profile.incubation_period_days,
            "case_fatality_rate": profile.case_fatality_rate,
            "vaccine_available": profile.vaccine_available
        }
    }


@router.get("/diseases/compare/multiple")
async def compare_diseases(
    disease_ids: str = Query(..., description="Comma-separated disease IDs to compare")
):
    """
    Compare multiple diseases side by side.
    
    Example: ?disease_ids=DENGUE,COVID,MALARIA
    """
    registry = get_disease_registry()
    disease_list = [d.strip().upper() for d in disease_ids.split(",")]
    
    comparison = []
    db = get_db()
    cases_col = db["cases_daily"]
    
    for disease_id in disease_list:
        profile = registry.get_disease(disease_id)
        
        if not profile:
            comparison.append({
                "disease_id": disease_id,
                "status": "not_configured",
                "error": f"Disease '{disease_id}' not in registry"
            })
            continue
        
        # Get basic stats
        stats = cases_col.aggregate([
            {"$match": {"disease": disease_id}},
            {
                "$group": {
                    "_id": None,
                    "total_cases": {"$sum": "$confirmed"},
                    "total_deaths": {"$sum": "$deaths"},
                    "affected_regions": {"$addToSet": "$region_id"}
                }
            }
        ])
        
        stats_result = list(stats)
        
        if stats_result:
            s = stats_result[0]
            comparison.append({
                "disease_id": disease_id,
                "name": profile.name,
                "total_cases": s["total_cases"],
                "total_deaths": s["total_deaths"],
                "affected_regions": len(s["affected_regions"]),
                "case_fatality_rate": profile.case_fatality_rate,
                "r0_estimate": profile.r0_estimate,
                "severity": profile.severity,
                "transmission_mode": profile.transmission_mode,
                "vaccine_available": profile.vaccine_available
            })
        else:
            comparison.append({
                "disease_id": disease_id,
                "name": profile.name,
                "status": "no_data",
                "severity": profile.severity,
                "transmission_mode": profile.transmission_mode
            })
    
    return {
        "comparison": comparison,
        "disease_count": len(comparison)
    }


@router.get("/diseases/transmission/{mode}")
async def list_diseases_by_transmission(mode: str):
    """
    List all diseases by transmission mode.
    
    Modes: vector, airborne, waterborne, contact, foodborne, zoonotic
    """
    registry = get_disease_registry()
    
    try:
        from backend.schemas.disease import TransmissionMode
        transmission_mode = TransmissionMode(mode.lower())
        diseases = registry.list_by_transmission(transmission_mode)
    except ValueError:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid transmission mode. Valid options: {', '.join([m.value for m in TransmissionMode])}"
        )
    
    return {
        "transmission_mode": mode.lower(),
        "count": len(diseases),
        "diseases": [
            {
                "disease_id": d.disease_id,
                "name": d.name,
                "severity": d.severity
            }
            for d in diseases
        ]
    }
