
import asyncio
import logging
import sys
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.db import get_client, get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DISEASE_CONFIGS = [
    {
        "_id": "dengue",
        "name": "Dengue",
        "resource_params": {
            "hospitalization_rate": 0.20,  # 20% need hospital
            "icu_rate": 0.01,             # 1% need ICU
            "avg_stay_days": 4,           # 4 days avg stay
            "nurse_ratio": 0.1,           # 1 nurse per 10 patients
            "oxygen_rate": 0.05           # 5% need oxygen
        }
    },
    {
        "_id": "covid",
        "name": "COVID-19",
        "resource_params": {
            "hospitalization_rate": 0.05, # 5% (Omicron-like)
            "icu_rate": 0.005,            # 0.5%
            "avg_stay_days": 5,
            "nurse_ratio": 0.15,
            "oxygen_rate": 0.10
        }
    }
]

def seed_resources():
    settings = get_settings()
    logger.info(f"Connecting to database: {settings.db_name}")
    
    client = get_client()
    db = client[settings.db_name]
    config_col = db["disease_config"]
    
    for config in DISEASE_CONFIGS:
        result = config_col.update_one(
            {"_id": config["_id"]},
            {"$set": config},
            upsert=True
        )
        if result.upserted_id:
            logger.info(f"Created config for {config['name']}")
        else:
            logger.info(f"Updated config for {config['name']}")
            
    logger.info("Resource seeding complete.")

if __name__ == "__main__":
    try:
        seed_resources()
    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        sys.exit(1)
