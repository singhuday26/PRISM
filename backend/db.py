from functools import lru_cache
import logging
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from .config import get_settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_client() -> MongoClient:
    """Get MongoDB client with connection pooling and timeout settings."""
    settings = get_settings()
    try:
        client = MongoClient(
            settings.mongo_uri,
            connectTimeoutMS=settings.mongo_connect_timeout_ms,
            serverSelectionTimeoutMS=settings.mongo_server_selection_timeout_ms,
            maxPoolSize=50,
            minPoolSize=10,
            retryWrites=True,
            retryReads=True,
        )
        # Verify connection
        client.admin.command("ping")
        logger.info(f"MongoDB connection established to database: {settings.db_name}")
        return client
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise RuntimeError(
            f"Could not connect to MongoDB at {settings.mongo_uri}. "
            f"Please ensure MongoDB is running and the connection string is correct."
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error connecting to MongoDB: {e}")
        raise


def get_db():
    """Get database instance."""
    return get_client()[get_settings().db_name]


def check_db_health() -> dict:
    """Check database connectivity and return health status."""
    try:
        client = get_client()
        result = client.admin.command("ping")
        db = get_db()
        
        # Get collection stats
        collections = {}
        for coll_name in ["regions", "cases_daily", "risk_scores", "alerts", "forecasts_daily"]:
            try:
                count = db[coll_name].estimated_document_count()
                collections[coll_name] = count
            except Exception:
                collections[coll_name] = -1
        
        return {
            "status": "healthy",
            "database": get_settings().db_name,
            "collections": collections,
            "ping": result.get("ok") == 1.0,
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": get_settings().db_name,
        }


def ensure_indexes() -> None:
    """Create database indexes with error handling."""
    try:
        db = get_db()
        
        # Regions index
        db["regions"].create_index("region_id", unique=True)
        logger.info("Created index on regions.region_id")
        
        # Cases daily compound index
        db["cases_daily"].create_index([
            ("region_id", ASCENDING),
            ("date", ASCENDING),
        ], unique=True)
        logger.info("Created compound index on cases_daily")
        
        # Forecasts daily compound index
        db["forecasts_daily"].create_index([
            ("region_id", ASCENDING),
            ("date", ASCENDING),
        ])
        logger.info("Created compound index on forecasts_daily")
        
        # Additional indexes for performance
        db["risk_scores"].create_index([
            ("date", ASCENDING),
            ("risk_score", ASCENDING),
        ])
        logger.info("Created index on risk_scores")
        
        db["alerts"].create_index([
            ("date", ASCENDING),
            ("risk_score", ASCENDING),
        ])
        logger.info("Created index on alerts")
        
        logger.info("All database indexes created successfully")
    except OperationFailure as e:
        logger.error(f"Failed to create indexes: {e}")
        # Don't raise - indexes might already exist
    except Exception as e:
        logger.error(f"Unexpected error creating indexes: {e}")
        raise
