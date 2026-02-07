"""Migration script to add disease field to existing documents."""

import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import get_db


def migrate_existing_data(default_disease: str = "DENGUE"):
    """
    Add disease field to existing documents.

    Args:
        default_disease: Disease to assign to existing data (default: DENGUE)
    """
    db = get_db()

    print("=" * 60)
    print("Multi-Disease Migration Script")
    print("=" * 60)
    print(f"Default disease for existing data: {default_disease}\n")

    # 1. Regions: Set disease=null (disease-agnostic by default)
    print("1. Migrating regions collection...")
    result = db["regions"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": None}}
    )
    print(f"   ✓ Set disease=null for {result.modified_count} region documents\n")

    # 2. Cases: Assign to default disease
    print("2. Migrating cases_daily collection...")
    result = db["cases_daily"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"   ✓ Assigned disease={default_disease} to {result.modified_count} case documents\n")

    # 3. Risk scores: Assign to default disease
    print("3. Migrating risk_scores collection...")
    result = db["risk_scores"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"   ✓ Assigned disease={default_disease} to {result.modified_count} risk score documents\n")

    # 4. Alerts: Assign to default disease
    print("4. Migrating alerts collection...")
    result = db["alerts"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"   ✓ Assigned disease={default_disease} to {result.modified_count} alert documents\n")

    # 5. Forecasts: Assign to default disease
    print("5. Migrating forecasts_daily collection...")
    result = db["forecasts_daily"].update_many(
        {"disease": {"$exists": False}},
        {"$set": {"disease": default_disease}}
    )
    print(f"   ✓ Assigned disease={default_disease} to {result.modified_count} forecast documents\n")

    print("=" * 60)
    print("✓ Migration complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Deploy updated code with new upsert logic")
    print("2. Run: python -m backend.db (to update indexes)")
    print("3. Verify: Run tests to confirm data isolation")


if __name__ == "__main__":
    migrate_existing_data()
