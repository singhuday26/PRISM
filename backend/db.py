from functools import lru_cache
import logging
import os
from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, OperationFailure
from .config import get_settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Database Connection Strategy
# ---------------------------------------------------------------------------
# PRISM uses MongoDB Atlas as its permanent external datastore.
#
# Connection resolution order (first match wins):
#   1. DATABASE_URL  — set by Koyeb / HuggingFace / Render / Railway when
#                      they attach a managed database.  For MongoDB Atlas,
#                      this is a "mongodb+srv://..." connection string.
#   2. MONGO_URI     — explicit MongoDB URI from .env (local dev default).
#
# Free-tier external databases that work with this setup:
#   • MongoDB Atlas  (512 MB free, permanent) → set DATABASE_URL or MONGO_URI
#   • Supabase       (PostgreSQL — requires schema migration, see below)
#
# Why this matters on ephemeral hosts (Koyeb / HuggingFace Spaces / Render
# free tier): containers are wiped on every deploy.  Any data written to the
# container filesystem is lost.  Using an external hosted database is the
# ONLY way to make data persist across deploys.
# ---------------------------------------------------------------------------

# Read DATABASE_URL first; fall back to MONGO_URI from config.
# This allows PaaS hosts to inject the connection string without changing
# any application code.
_MONGO_URI_OVERRIDE: Optional[str] = os.environ.get("DATABASE_URL")

@lru_cache()
def get_client() -> MongoClient:
    """Get MongoDB client with connection pooling and timeout settings.

    Connection URI priority:
      1. DATABASE_URL environment variable (set by Koyeb, HuggingFace, Render,
         Railway when a managed database is attached).  For MongoDB Atlas this
         is a 'mongodb+srv://...' string.
      2. MONGO_URI from config / .env file (local development default).
    """
    settings = get_settings()
    # Prefer DATABASE_URL (PaaS-injected Atlas URI) over local MONGO_URI
    mongo_uri = _MONGO_URI_OVERRIDE or settings.mongo_uri
    if _MONGO_URI_OVERRIDE:
        logger.info("Using DATABASE_URL for MongoDB connection (external Atlas/managed DB)")
    try:
        client = MongoClient(
            mongo_uri,
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
            f"Could not connect to MongoDB. "
            f"If deploying to a PaaS host, set DATABASE_URL to your MongoDB Atlas URI. "
            f"Locally, set MONGO_URI in your .env file."
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
    """Create database indexes with error handling for multi-disease isolation."""
    try:
        db = get_db()

        # Regions index: compound (region_id, disease) to allow same region_id for different diseases
        # sparse=True allows null disease values for disease-agnostic regions
        db["regions"].create_index([
            ("region_id", ASCENDING),
            ("disease", ASCENDING),
        ], unique=True, sparse=True)
        logger.info("Created compound index on regions (region_id, disease)")

        # Cases daily compound index: includes disease for multi-disease isolation
        # sparse=True allows backward compatibility with documents lacking disease field
        db["cases_daily"].create_index([
            ("region_id", ASCENDING),
            ("date", ASCENDING),
            ("disease", ASCENDING),
        ], unique=True, sparse=True)
        logger.info("Created compound index on cases_daily (region_id, date, disease)")

        # Forecasts daily: add disease and model_version to unique constraint
        db["forecasts_daily"].create_index([
            ("region_id", ASCENDING),
            ("date", ASCENDING),
            ("disease", ASCENDING),
            ("model_version", ASCENDING),
        ], unique=True, sparse=True)
        logger.info("Created compound index on forecasts_daily (region_id, date, disease, model_version)")

        # Risk scores: unique constraint for data isolation
        db["risk_scores"].create_index([
            ("region_id", ASCENDING),
            ("date", ASCENDING),
            ("disease", ASCENDING),
        ], unique=True, sparse=True)
        logger.info("Created unique index on risk_scores (region_id, date, disease)")

        # Risk scores: performance index for queries
        db["risk_scores"].create_index([
            ("date", ASCENDING),
            ("disease", ASCENDING),
            ("risk_score", ASCENDING),
        ])
        logger.info("Created performance index on risk_scores (date, disease, risk_score)")

        # Alerts: unique constraint for data isolation
        db["alerts"].create_index([
            ("region_id", ASCENDING),
            ("date", ASCENDING),
            ("disease", ASCENDING),
            ("reason", ASCENDING),
        ], unique=True, sparse=True)
        logger.info("Created unique index on alerts (region_id, date, disease, reason)")

        # Alerts: performance index for queries
        db["alerts"].create_index([
            ("date", ASCENDING),
            ("disease", ASCENDING),
            ("risk_score", ASCENDING),
        ])
        logger.info("Created performance index on alerts (date, disease, risk_score)")

        # Users: unique username and email
        db["users"].create_index("username", unique=True)
        db["users"].create_index("email", unique=True)
        logger.info("Created unique indexes on users (username, email)")

        # Pipeline Status: unique task_id for tracking background jobs
        db["pipeline_status"].create_index("task_id", unique=True)
        db["pipeline_status"].create_index([("disease", ASCENDING), ("status", ASCENDING)])
        logger.info("Created indexes on pipeline_status (task_id, disease, status)")

        # News Articles: unique title and performance indexes
        db["news_articles"].create_index("title", unique=True)
        db["news_articles"].create_index([("extracted_diseases", ASCENDING)])
        db["news_articles"].create_index([("published_at", ASCENDING)])
        logger.info("Created indexes on news_articles (title, diseases, date)")

        logger.info("All database indexes created successfully")
    except OperationFailure as e:
        logger.error(f"Failed to create indexes: {e}")
        # Don't raise - indexes might already exist
    except Exception as e:
        logger.error(f"Unexpected error creating indexes: {e}")
        raise



# ---------------------------------------------------------------------------
# GridFS Helpers — Persistent Binary Storage (PDF Reports)
# ---------------------------------------------------------------------------
# MongoDB GridFS stores large binary objects (like PDF reports) inside the
# same Atlas cluster.  Files survive container restarts and deploys.
#
# Usage in services/reports.py:
#   from backend.db import save_report_binary, load_report_binary
#   ...
#   file_id = save_report_binary(pdf_bytes, filename=f"{report_id}.pdf")
#   pdf_bytes = load_report_binary(file_id)
# ---------------------------------------------------------------------------

def save_report_binary(data: bytes, filename: str) -> str:
    """Store binary data (e.g. a PDF) in MongoDB GridFS.

    Args:
        data:     Raw bytes to store.
        filename: Logical filename (used for retrieval metadata).

    Returns:
        The GridFS file ID as a string. Store this in the reports collection
        as ``gridfs_id`` so the download endpoint can retrieve it.
    """
    import gridfs  # type: ignore  # pymongo bundles gridfs
    db = get_db()
    fs = gridfs.GridFS(db)
    file_id = fs.put(data, filename=filename, content_type="application/pdf")
    logger.info(f"Saved {len(data)} bytes to GridFS as '{filename}' (id={file_id})")
    return str(file_id)


def load_report_binary(gridfs_id: str) -> bytes:
    """Retrieve binary data from MongoDB GridFS by file ID.

    Args:
        gridfs_id: The string representation of the GridFS ObjectId returned
                   by ``save_report_binary``.

    Returns:
        Raw bytes of the stored file.

    Raises:
        FileNotFoundError: if no GridFS file exists for the given ID.
    """
    import gridfs  # type: ignore
    from bson import ObjectId
    db = get_db()
    fs = gridfs.GridFS(db)
    oid = ObjectId(gridfs_id)
    if not fs.exists(oid):
        raise FileNotFoundError(f"GridFS file not found: {gridfs_id}")
    grid_out = fs.get(oid)
    return grid_out.read()
