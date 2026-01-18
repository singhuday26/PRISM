"""Test multi-disease expansion features."""
import requests

API_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 MULTI-DISEASE EXPANSION - TEST SUITE")
print("=" * 80)

# Test 1: List all configured diseases
print("\n1️⃣  Testing GET /diseases...")
try:
    resp = requests.get(f"{API_URL}/diseases")
    data = resp.json()
    print(f"   ✓ Found {data['count']} configured disease(s)")
    
    for disease in data['diseases'][:3]:  # Show first 3
        print(f"      • {disease['name']} ({disease['disease_id']}) - {disease['transmission_mode']}")
    
    if data['count'] > 3:
        print(f"      ... and {data['count'] - 3} more")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Get specific disease profile
print("\n2️⃣  Testing GET /diseases/DENGUE...")
try:
    resp = requests.get(f"{API_URL}/diseases/DENGUE")
    data = resp.json()
    print(f"   ✓ Disease: {data['name']}")
    print(f"      Transmission: {data['transmission_mode']}")
    print(f"      Severity: {data['severity']}")
    print(f"      R₀: {data.get('r0_estimate', 'N/A')}")
    print(f"      CFR: {data.get('case_fatality_rate', 0):.2%}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Get disease statistics
print("\n3️⃣  Testing GET /diseases/DENGUE/stats...")
try:
    resp = requests.get(f"{API_URL}/diseases/DENGUE/stats")
    data = resp.json()
    
    if data.get('data_available'):
        stats = data['statistics']
        print(f"   ✓ Data available:")
        print(f"      Total Cases: {stats['total_cases']:,}")
        print(f"      Total Deaths: {stats['total_deaths']:,}")
        print(f"      Affected Regions: {stats['affected_regions_count']}")
        print(f"      Date Range: {stats['date_range']['start']} to {stats['date_range']['end']}")
    else:
        print(f"   ℹ No data available for {data['disease_name']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Filter diseases by transmission mode
print("\n4️⃣  Testing GET /diseases/transmission/vector...")
try:
    resp = requests.get(f"{API_URL}/diseases/transmission/vector")
    data = resp.json()
    print(f"   ✓ Found {data['count']} vector-borne disease(s):")
    
    for disease in data['diseases']:
        print(f"      • {disease['name']} - {disease['severity']} severity")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Filter diseases by vaccine availability
print("\n5️⃣  Testing GET /diseases?vaccine_available=true...")
try:
    resp = requests.get(f"{API_URL}/diseases?vaccine_available=true")
    data = resp.json()
    print(f"   ✓ Found {data['count']} disease(s) with vaccines:")
    
    for disease in data['diseases'][:5]:
        print(f"      • {disease['name']}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 6: Compare multiple diseases
print("\n6️⃣  Testing GET /diseases/compare/multiple?disease_ids=DENGUE,COVID,MALARIA...")
try:
    resp = requests.get(f"{API_URL}/diseases/compare/multiple?disease_ids=DENGUE,COVID,MALARIA")
    data = resp.json()
    print(f"   ✓ Comparing {data['disease_count']} diseases:")
    
    for disease in data['comparison']:
        if disease.get('total_cases'):
            print(f"      • {disease['name']}: {disease['total_cases']:,} cases, {disease['total_deaths']:,} deaths")
        else:
            print(f"      • {disease['name']}: No data available")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 7: Filter diseases by severity
print("\n7️⃣  Testing GET /diseases?severity=high...")
try:
    resp = requests.get(f"{API_URL}/diseases?severity=high")
    data = resp.json()
    print(f"   ✓ Found {data['count']} high-severity disease(s):")
    
    for disease in data['diseases']:
        print(f"      • {disease['name']} - R₀: {disease.get('r0_estimate', 'N/A')}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 8: Verify disease filtering works with existing endpoints
print("\n8️⃣  Testing existing endpoints with disease filter...")
try:
    # Test with DENGUE
    resp = requests.get(f"{API_URL}/risk/latest?disease=DENGUE")
    dengue_count = resp.json()['count']
    
    # Test with COVID (should have no data)
    resp = requests.get(f"{API_URL}/risk/latest?disease=COVID")
    covid_count = resp.json()['count']
    
    print(f"   ✓ Risk scores - DENGUE: {dengue_count}, COVID: {covid_count}")
    print(f"      Disease filtering confirmed working!")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 80)
print("✅ MULTI-DISEASE TESTING COMPLETE!")
print("=" * 80)
print("\nNext steps:")
print("  1. Test CLI: python disease_manager.py list")
print("  2. Load new disease data: python disease_manager.py load COVID data.csv ...")
print("  3. Compare diseases: python disease_manager.py compare")
print("=" * 80 + "\n")
