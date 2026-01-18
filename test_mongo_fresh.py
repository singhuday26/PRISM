from pymongo import MongoClient

MONGO_URI = "mongodb+srv://prism_user:prism240818@cluster0.kesugwh.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["prism_db"]
collection = db["test_collection"]

doc = {"project": "PRISM", "status": "fresh start working"}
result = collection.insert_one(doc)

print("✅ Insert successful!")
print("Inserted ID:", result.inserted_id)

read_back = collection.find_one({"_id": result.inserted_id})
print("✅ Read back:", read_back)
