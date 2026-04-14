from backend.db import get_db
import json

def list_users():
    db = get_db()
    users = list(db["users"].find({}, {"_id": 0, "hashed_password": 0}))
    print(json.dumps(users, indent=2))

if __name__ == "__main__":
    list_users()
