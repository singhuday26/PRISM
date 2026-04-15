from pathlib import Path
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status, APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pymongo.errors import PyMongoError

from .config import get_settings
from .db import ensure_indexes, get_client
from .services.cache import ensure_cache_indexes
from .logging_config import setup_logging
from .routes.health import router as health_router
from .routes.regions import router as regions_router
from .routes.hotspots import router as hotspots_router
from .routes.risk import router as risk_router
from .routes.alerts import router as alerts_router
from .routes.forecasts import router as forecasts_router
from .routes.evaluation import router as evaluation_router
from .routes.pipeline import router as pipeline_router
from .routes.diseases import router as diseases_router
from .routes.geojson import router as geojson_router
from .routes.notifications import router as notifications_router
from .routes.reports import router as reports_router
from .routes.resources import router as resources_router
from .routes.auth import router as auth_router
from .routes.news import router as news_router
from .routes.ecosystem import router as ecosystem_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    settings = get_settings()
    
    # Setup logging
    setup_logging(log_level=settings.log_level)
    logger.info(f"Starting PRISM API v0.1.0 with log level: {settings.log_level}")
    
    try:
        ensure_indexes()
        ensure_cache_indexes()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    try:
        client = get_client()
        client.close()
        logger.info("MongoDB connection closed")
    except Exception as e:
        logger.warning(f"Error during shutdown: {e}")
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title="PRISM API",
        version="0.1.0",
        description="Predictive Risk Intelligence & Surveillance Model",
        lifespan=lifespan,
    )
    
    # Add CORS middleware
    if settings.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.get_cors_origins_list(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS enabled for origins: {settings.get_cors_origins_list()}")
    
    # Global exception handlers
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation error on {request.url.path}: {exc.errors()}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "details": exc.errors(),
                "message": "Invalid request parameters",
            },
        )
    
    @app.exception_handler(PyMongoError)
    async def mongodb_exception_handler(request: Request, exc: PyMongoError):
        logger.error(f"Database error on {request.url.path}: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "error": "Database Error",
                "message": "The database is currently unavailable. Please try again later.",
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
            },
        )
    
    # Create an API router to group all endpoints
    api_router = APIRouter(prefix="/api")
    
    # Include routers into the API router
    api_router.include_router(news_router, prefix="/intelligence", tags=["news"])
    api_router.include_router(health_router, prefix="/health", tags=["health"])
    api_router.include_router(regions_router, prefix="/regions", tags=["regions"])
    api_router.include_router(hotspots_router, prefix="/hotspots", tags=["hotspots"])
    api_router.include_router(risk_router, prefix="/risk", tags=["risk"])
    api_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
    api_router.include_router(forecasts_router, prefix="/forecasts", tags=["forecasts"])
    api_router.include_router(pipeline_router, prefix="/pipeline", tags=["pipeline"])
    api_router.include_router(evaluation_router, prefix="/evaluation", tags=["evaluation"])
    api_router.include_router(diseases_router, prefix="/diseases", tags=["diseases"])
    api_router.include_router(geojson_router, prefix="/risk", tags=["geojson"])
    api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
    api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
    api_router.include_router(resources_router, prefix="/resources", tags=["resources"])
    api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
    api_router.include_router(ecosystem_router, prefix="/ecosystem", tags=["ecosystem"])
    
    # Mount the API router to the app
    app.include_router(api_router)

    # Serve frontend static files
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        # First, ensure API and Docs take priority (already included above)
        
        # SPA Catch-all and Static Serving
        @app.get("/{full_path:path}", include_in_schema=False)
        async def _serve_frontend(full_path: str):
            # Prioritize API routes - they are already handled by routers above, 
            # so if we are here, it's either a static file or an SPA route.
            
            # Check if it looks like a file (assets, favicon, etc.)
            if "." in full_path:
                file_path = frontend_dist / full_path
                if file_path.exists():
                    from fastapi.responses import FileResponse
                    return FileResponse(file_path)
            
            # Otherwise, serve index.html for SPA routing (like /app)
            index_file = frontend_dist / "index.html"
            if index_file.exists():
                from fastapi.responses import FileResponse
                return FileResponse(index_file)
            
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND, 
                content={"detail": "Frontend assets not found"}
            )

        logger.info(f"Serving frontend from {frontend_dist} at root")

    return app


app = create_app()
