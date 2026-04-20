import requests
import json

BASE_URL = "http://localhost:8000/api"

def check_route(endpoint):
    try:
        r = requests.get(f"{BASE_URL}{endpoint}")
        print(f"GET {endpoint} status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Sample data from {endpoint}: {json.dumps(data, indent=2)[:500]}...")
            return data
    except Exception as e:
        print(f"Error checking {endpoint}: {e}")
    return None

if __name__ == "__main__":
    print("Verifying API alignment...")
    check_route("/diseases/")
    check_route("/regions/diseases")
    check_route("/regions/")
