import logging
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from ..db import check_db_health

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ping")
def ping():
    """Simple ping endpoint."""
    return {"status": "ok", "service": "PRISM API"}


@router.get("/")
def health_check():
    """Comprehensive health check including database connectivity."""
    try:
        db_health = check_db_health()
        
        if db_health.get("status") == "healthy":
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "healthy",
                    "service": "PRISM API",
                    "database": db_health,
                },
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "status": "unhealthy",
                    "service": "PRISM API",
                    "database": db_health,
                },
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "service": "PRISM API",
                "error": str(e),
            },
        )
