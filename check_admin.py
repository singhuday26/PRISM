from backend.db import get_db
import json

def check_admin():
    db = get_db()
    user = db["users"].find_one({"username": "admin"})
    if user:
        user["_id"] = str(user["_id"])
        print(json.dumps(user, indent=2))
    else:
        print("Admin user not found")

if __name__ == "__main__":
    check_admin()
