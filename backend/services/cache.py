"""
Persistent caching service for PRISM.
Uses MongoDB as a Tier 2 (Warm) cache layer.
"""
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Any, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from backend.db import get_db

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class CacheService:
    """
    Manages Tier 2 persistent caching.
    
    FAANG-Standard:
    - O(1) retrieval via indexed keys.
    - TTL support for automatic cleanup.
    - Type-safe serialization using Pydantic.
    """
    
    COLLECTION = "internal_cache"
    
    @staticmethod
    def _generate_key(prefix: str, identifier: str) -> str:
        """Generate a stable cache key."""
        raw = f"{prefix}:{identifier}"
        return hashlib.sha256(raw.encode()).hexdigest()

    @classmethod
    def get(cls, prefix: str, identifier: str, model: Optional[Type[T]] = None) -> Optional[Union[Dict, T]]:
        """Retrieve an item from the cache."""
        try:
            db = get_db()
            key = cls._generate_key(prefix, identifier)
            
            doc = db[cls.COLLECTION].find_one({"key": key})
            
            if not doc:
                return None
                
            # Check expiration (fallback if TTL index hasn't run)
            if doc.get("expires_at") < datetime.utcnow():
                db[cls.COLLECTION].delete_one({"key": key})
                return None
            
            data = doc.get("data")
            if model and data:
                return model.model_validate(data)
            return data
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
            return None

    @classmethod
    def set(cls, prefix: str, identifier: str, data: Any, ttl_seconds: int = 3600):
        """Store an item in the cache."""
        try:
            db = get_db()
            key = cls._generate_key(prefix, identifier)
            
            # Prepare data for storage
            serializable_data = data
            if isinstance(data, BaseModel):
                serializable_data = data.model_dump()
            
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            
            db[cls.COLLECTION].update_one(
                {"key": key},
                {
                    "$set": {
                        "key": key,
                        "prefix": prefix,
                        "identifier": identifier,
                        "data": serializable_data,
                        "expires_at": expires_at,
                        "created_at": datetime.utcnow()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Cache storage error: {e}")

    @classmethod
    def invalidate(cls, prefix: Optional[str] = None):
        """Invalidate cache entries."""
        try:
            db = get_db()
            query = {"prefix": prefix} if prefix else {}
            db[cls.COLLECTION].delete_many(query)
        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")

def ensure_cache_indexes():
    """Ensure TTL index exists for the cache collection."""
    try:
        db = get_db()
        db["internal_cache"].create_index("key", unique=True)
        db["internal_cache"].create_index("expires_at", expireAfterSeconds=0)
        db["internal_cache"].create_index("prefix")
    except Exception as e:
        logger.error(f"Failed to create cache indexes: {e}")
