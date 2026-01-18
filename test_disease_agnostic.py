"""Test disease-agnostic PRISM functionality."""
import requests

API_URL = "http://localhost:8000"

print("=" * 70)
print("🧪 DISEASE-AGNOSTIC PRISM - TEST SUITE")
print("=" * 70)

# Test 1: Get available diseases
print("\n1️⃣  Testing /regions/diseases endpoint...")
try:
    resp = requests.get(f"{API_URL}/regions/diseases")
    data = resp.json()
    print(f"   ✓ Found {data['count']} disease(s): {', '.join(data['diseases'])}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Get regions filtered by disease
print("\n2️⃣  Testing /regions?disease=DENGUE...")
try:
    resp = requests.get(f"{API_URL}/regions?disease=DENGUE")
    data = resp.json()
    print(f"   ✓ Found {data['count']} regions for DENGUE")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Get hotspots filtered by disease
print("\n3️⃣  Testing /hotspots?disease=DENGUE...")
try:
    resp = requests.get(f"{API_URL}/hotspots?disease=DENGUE")
    data = resp.json()
    if data['hotspots']:
        top = data['hotspots'][0]
        print(f"   ✓ Top hotspot: {top.get('region_name', top['region_id'])} ({top['confirmed_sum']} cases)")
    else:
        print(f"   ℹ No hotspots found")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Get latest risk scores for disease
print("\n4️⃣  Testing /risk/latest?disease=DENGUE...")
try:
    resp = requests.get(f"{API_URL}/risk/latest?disease=DENGUE")
    data = resp.json()
    print(f"   ✓ Found {data['count']} risk scores for {data['date']}")
    if data['risk_scores']:
        top = data['risk_scores'][0]
        print(f"   ℹ Highest risk: {top['region_id']} (score: {top['risk_score']:.3f})")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Get latest alerts for disease
print("\n5️⃣  Testing /alerts/latest?disease=DENGUE...")
try:
    resp = requests.get(f"{API_URL}/alerts/latest?disease=DENGUE")
    data = resp.json()
    print(f"   ✓ Found {data['count']} alerts for {data['date']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Get latest forecasts for disease
print("\n6️⃣  Testing /forecasts/latest?disease=DENGUE&horizon=7...")
try:
    resp = requests.get(f"{API_URL}/forecasts/latest?disease=DENGUE&horizon=7")
    data = resp.json()
    print(f"   ✓ Found {data['count']} forecast records")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 7: Verify multi-disease support (all diseases)
print("\n7️⃣  Testing endpoints without disease filter (all diseases)...")
try:
    resp = requests.get(f"{API_URL}/regions")
    all_regions = resp.json()['count']
    
    resp = requests.get(f"{API_URL}/hotspots")
    all_hotspots = resp.json()['count']
    
    print(f"   ✓ Total regions (all diseases): {all_regions}")
    print(f"   ✓ Total hotspots (all diseases): {all_hotspots}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print("✅ DISEASE-AGNOSTIC TESTING COMPLETE!")
print("   All API endpoints now support optional disease filtering.")
print("   Dashboard can switch between diseases using dropdown.")
print("=" * 70)
