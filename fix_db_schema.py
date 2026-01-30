
import os
import logging
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connect to MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "prism_db"

def fix_forecast_schema():
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        collection = db["forecasts_daily"]
        
        # Check for legacy documents
        count = collection.count_documents({"cases": {"$exists": True}})
        if count == 0:
            logger.info("No legacy forecast documents found. Schema is clean.")
            return

        logger.info(f"Found {count} legacy forecast documents. Migrating...")

        # Rename fields
        result = collection.update_many(
            {"cases": {"$exists": True}},
            {
                "$rename": {
                    "cases": "pred_mean",
                    "lower_bound": "pred_lower",
                    "upper_bound": "pred_upper"
                }
            }
        )
        
        logger.info(f"Migration complete. Modified {result.modified_count} documents.")
        
        # Verify
        verify_count = collection.count_documents({"pred_mean": {"$exists": True}})
        logger.info(f"Total documents with correct schema: {verify_count}")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    fix_forecast_schema()
