"""
Seed an admin user into MongoDB for PRISM Command.

Usage:
    python -m backend.scripts.seed_admin
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.auth import get_password_hash
from backend.db import get_db


def seed_admin():
    db = get_db()
    
    # Check if admin already exists
    existing = db["users"].find_one({"username": "admin"})
    if existing:
        print("✅ Admin user already exists. Skipping.")
        return
    
    admin_user = {
        "username": "admin",
        "email": "admin@prism.org",
        "role": "admin",
        "hashed_password": get_password_hash("admin123"),
    }
    
    db["users"].insert_one(admin_user)
    print("✅ Admin user created successfully!")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Role:     admin")


if __name__ == "__main__":
    seed_admin()
