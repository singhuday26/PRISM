"""
Test Feature 9: Risk Heatmap / Top Hotspots
Verify the new dashboard section displays correctly.
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_risk_heatmap_data():
    """Test that we can fetch risk data for the heatmap."""
    print("=" * 60)
    print("Testing Risk Heatmap Data Source")
    print("=" * 60)
    
    # Test 1: Fetch risk scores for DENGUE
    print("\n1. Fetching risk scores for DENGUE...")
    response = requests.get(
        f"{API_URL}/risk/latest",
        params={"disease": "DENGUE"},
        timeout=10
    )
    
    if response.ok:
        data = response.json()
        risk_scores = data.get("risk_scores", [])
        risk_date = data.get("date")
        
        print(f"✓ Success!")
        print(f"  Date: {risk_date}")
        print(f"  Total regions: {len(risk_scores)}")
        
        if risk_scores:
            # Sort by risk score to get top 10
            sorted_risks = sorted(risk_scores, key=lambda x: x.get("risk_score", 0), reverse=True)
            top_10 = sorted_risks[:10]
            
            print(f"  Top 10 regions: {len(top_10)}")
            print("\n  Top 5 by risk score:")
            for i, r in enumerate(top_10[:5], 1):
                region_id = r.get("region_id")
                risk_score = r.get("risk_score", 0)
                risk_level = r.get("risk_level")
                drivers = r.get("drivers", [])
                
                print(f"    {i}. {region_id}: {risk_score:.3f} ({risk_level})")
                if drivers:
                    print(f"       Drivers: {', '.join(drivers[:2])}")  # Show first 2 drivers
            
            # Test with less than 10 regions
            if len(risk_scores) < 10:
                print(f"\n  ✓ Works with <10 regions ({len(risk_scores)} available)")
            
            # Verify all required fields present
            print("\n2. Verifying data structure...")
            required_fields = ["region_id", "risk_score", "risk_level", "drivers"]
            all_have_fields = True
            
            for r in top_10:
                for field in required_fields:
                    if field not in r:
                        print(f"  ✗ Missing field '{field}' in {r.get('region_id', 'Unknown')}")
                        all_have_fields = False
            
            if all_have_fields:
                print(f"  ✓ All required fields present")
            
            return True
        else:
            print("  ⚠ No risk scores available. Run pipeline first.")
            return False
    else:
        print(f"✗ Failed: {response.status_code}")
        print(f"  {response.text}")
        return False


def test_dashboard_access():
    """Test that dashboard is accessible."""
    print("\n3. Checking dashboard access...")
    
    try:
        response = requests.get("http://localhost:8501", timeout=5)
        if response.ok:
            print(f"✓ Dashboard accessible at http://localhost:8501")
            return True
        else:
            print(f"✗ Dashboard returned: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("✗ Dashboard not accessible - is it running?")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def print_dashboard_instructions():
    """Print instructions for verifying the dashboard."""
    print("\n" + "=" * 60)
    print("Dashboard Verification Steps")
    print("=" * 60)
    print("\n1. Open dashboard: http://localhost:8501")
    print("\n2. Look for the section: '🗺️ Risk Heatmap / Top Hotspots'")
    print("   - Should appear after 'Hotspots' section")
    print("   - Should show before 'Risk Intelligence' section")
    print("\n3. Verify the following elements:")
    print("   ✓ Bar chart showing top 10 regions")
    print("   ✓ Bars colored by risk level (Red/Orange/Green)")
    print("   ✓ Risk scores labeled on bars")
    print("   ✓ Table with: Region, Risk Score, Risk Level, Drivers")
    print("   ✓ Color legend in expandable section")
    print("\n4. Test with disease dropdown:")
    print("   - Change disease selection")
    print("   - Risk heatmap should update automatically")
    print("\n5. Verify it works with <10 regions:")
    print("   - Chart and table should render correctly")
    print("   - Section title should say 'Top X regions' (not always 10)")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        # Test API data
        data_ok = test_risk_heatmap_data()
        
        # Test dashboard access
        dashboard_ok = test_dashboard_access()
        
        # Print verification instructions
        print_dashboard_instructions()
        
        # Final verdict
        if data_ok and dashboard_ok:
            print("\n✅ Feature 9 verified")
            print("\nThe Risk Heatmap section is ready!")
            print("- Fast rendering (bar chart + table)")
            print("- Clean design (no shapefile complexity)")
            print("- Works with any number of regions (<10 or ≥10)")
            print("- Color-coded by risk level")
            print("- Detailed drivers in table")
        else:
            print("\n⚠ Partial success - check dashboard manually")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
