"""Disease data management CLI tool."""
import sys
import argparse
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.scripts.load_multi_disease import (
    DiseaseDataLoader,
    load_generic_disease_data
)
from backend.disease_config import get_disease_registry
from backend.db import get_db


def list_diseases():
    """List all configured diseases."""
    registry = get_disease_registry()
    diseases = registry.diseases.values()
    
    print("\n" + "=" * 80)
    print("📋 CONFIGURED DISEASES IN PRISM")
    print("=" * 80)
    
    # Group by transmission mode
    from collections import defaultdict
    by_transmission = defaultdict(list)
    
    for disease in diseases:
        by_transmission[disease.transmission_mode].append(disease)
    
    for transmission_mode, disease_list in sorted(by_transmission.items()):
        print(f"\n🦠 {transmission_mode.upper()}")
        print("-" * 80)
        
        for disease in sorted(disease_list, key=lambda d: d.name):
            vaccine_status = "💉 Vaccine" if disease.vaccine_available else "❌ No vaccine"
            severity_emoji = {
                "low": "🟢",
                "moderate": "🟡",
                "high": "🟠",
                "critical": "🔴"
            }
            
            print(
                f"  {severity_emoji.get(disease.severity, '⚪')} {disease.disease_id:<20} "
                f"| {disease.name:<30} | {vaccine_status} | CFR: {disease.case_fatality_rate:.1%}"
            )
    
    print("\n" + "=" * 80)
    print(f"Total: {len(diseases)} diseases configured")
    print("=" * 80 + "\n")


def show_disease_info(disease_id: str):
    """Show detailed information about a disease."""
    registry = get_disease_registry()
    profile = registry.get_disease(disease_id)
    
    if not profile:
        print(f"❌ Disease '{disease_id}' not found in registry")
        return
    
    print("\n" + "=" * 80)
    print(f"📊 DISEASE PROFILE: {profile.name}")
    print("=" * 80)
    
    print(f"\n🆔 Disease ID: {profile.disease_id}")
    print(f"📝 Description: {profile.description}")
    print(f"🔬 ICD Code: {profile.icd_code or 'N/A'}")
    
    print(f"\n🦠 Transmission & Severity:")
    print(f"   Mode: {profile.transmission_mode.upper()}")
    print(f"   Severity: {profile.severity.upper()}")
    print(f"   Incubation: {profile.incubation_period_days} days")
    
    print(f"\n📈 Epidemiological Parameters:")
    print(f"   R₀: {profile.r0_estimate or 'N/A'}")
    print(f"   Case Fatality Rate: {profile.case_fatality_rate:.2%}" if profile.case_fatality_rate else "   Case Fatality Rate: N/A")
    
    print(f"\n🌡️ Climate Sensitivity:")
    print(f"   Temperature: {'Yes ✓' if profile.temperature_sensitive else 'No ✗'}")
    print(f"   Rainfall: {'Yes ✓' if profile.rainfall_sensitive else 'No ✗'}")
    print(f"   Humidity: {'Yes ✓' if profile.humidity_sensitive else 'No ✗'}")
    
    print(f"\n💊 Medical Interventions:")
    print(f"   Vaccine: {'Available ✓' if profile.vaccine_available else 'Not Available ✗'}")
    print(f"   Treatment: {'Available ✓' if profile.treatment_available else 'Not Available ✗'}")
    
    print(f"\n⚠️ Alert Configuration:")
    print(f"   Threshold Multiplier: {profile.alert_threshold_multiplier}x")
    print(f"   High Risk Case Count: {profile.high_risk_case_threshold}")
    
    if profile.data_sources:
        print(f"\n📚 Data Sources:")
        for source in profile.data_sources:
            print(f"   • {source}")
    
    # Check database for actual data
    db = get_db()
    cases_col = db["cases_daily"]
    
    case_count = cases_col.count_documents({"disease": profile.disease_id})
    
    print(f"\n💾 Database Status:")
    if case_count > 0:
        # Get stats
        pipeline = [
            {"$match": {"disease": profile.disease_id}},
            {
                "$group": {
                    "_id": None,
                    "total_cases": {"$sum": "$confirmed"},
                    "total_deaths": {"$sum": "$deaths"},
                    "regions": {"$addToSet": "$region_id"},
                    "min_date": {"$min": "$date"},
                    "max_date": {"$max": "$date"}
                }
            }
        ]
        
        stats = list(cases_col.aggregate(pipeline))[0]
        
        print(f"   ✓ Data Available")
        print(f"   Records: {case_count:,}")
        print(f"   Total Cases: {stats['total_cases']:,}")
        print(f"   Total Deaths: {stats['total_deaths']:,}")
        print(f"   Regions: {len(stats['regions'])}")
        print(f"   Date Range: {stats['min_date']} to {stats['max_date']}")
    else:
        print(f"   ✗ No data loaded")
        print(f"   Use: python disease_manager.py load {profile.disease_id} <csv_path>")
    
    print("\n" + "=" * 80 + "\n")


def load_disease_data(
    disease_id: str,
    csv_path: Path,
    region_col: str,
    confirmed_col: str,
    deaths_col: str,
    date_col: Optional[str] = None,
    year_col: Optional[str] = None,
    recovered_col: Optional[str] = None
):
    """Load disease data from CSV."""
    print(f"\n📥 Loading {disease_id} data from {csv_path}...")
    
    try:
        result = load_generic_disease_data(
            disease_id=disease_id,
            csv_path=csv_path,
            region_col=region_col,
            date_col=date_col,
            year_col=year_col,
            confirmed_col=confirmed_col,
            deaths_col=deaths_col,
            recovered_col=recovered_col
        )
        
        print(f"\n✅ Successfully loaded {disease_id} data:")
        print(f"   Regions: {result['regions_loaded']} ({result['regions_new']} new)")
        print(f"   Cases: {result['cases_loaded']} ({result['cases_new']} new)")
        
    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        raise


def compare_diseases():
    """Compare all diseases with available data."""
    db = get_db()
    cases_col = db["cases_daily"]
    registry = get_disease_registry()
    
    print("\n" + "=" * 100)
    print("📊 DISEASE COMPARISON (Data Availability)")
    print("=" * 100)
    
    print(f"\n{'Disease':<25} {'Cases':<12} {'Deaths':<12} {'Regions':<10} {'Date Range':<25} {'Status'}")
    print("-" * 100)
    
    for disease_id in sorted(registry.list_diseases()):
        profile = registry.get_disease(disease_id)
        
        stats = list(cases_col.aggregate([
            {"$match": {"disease": disease_id}},
            {
                "$group": {
                    "_id": None,
                    "total_cases": {"$sum": "$confirmed"},
                    "total_deaths": {"$sum": "$deaths"},
                    "regions": {"$addToSet": "$region_id"},
                    "min_date": {"$min": "$date"},
                    "max_date": {"$max": "$date"}
                }
            }
        ]))
        
        if stats:
            s = stats[0]
            date_range = f"{s['min_date']} - {s['max_date']}"
            status = "✓ Loaded"
            print(
                f"{profile.name:<25} {s['total_cases']:<12,} {s['total_deaths']:<12,} "
                f"{len(s['regions']):<10} {date_range:<25} {status}"
            )
        else:
            print(f"{profile.name:<25} {'N/A':<12} {'N/A':<12} {'N/A':<10} {'N/A':<25} ✗ No data")
    
    print("\n" + "=" * 100 + "\n")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PRISM Disease Data Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all configured diseases
  python disease_manager.py list
  
  # Show disease details
  python disease_manager.py info DENGUE
  
  # Load disease data
  python disease_manager.py load COVID data/covid.csv --region State --confirmed Cases --deaths Deaths --date Date
  
  # Compare diseases
  python disease_manager.py compare
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List command
    subparsers.add_parser("list", help="List all configured diseases")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show detailed disease information")
    info_parser.add_argument("disease_id", help="Disease ID (e.g., DENGUE, COVID)")
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load disease data from CSV")
    load_parser.add_argument("disease_id", help="Disease ID")
    load_parser.add_argument("csv_path", type=Path, help="Path to CSV file")
    load_parser.add_argument("--region", required=True, help="Region column name")
    load_parser.add_argument("--confirmed", required=True, help="Confirmed cases column name")
    load_parser.add_argument("--deaths", required=True, help="Deaths column name")
    load_parser.add_argument("--date", help="Date column name")
    load_parser.add_argument("--year", help="Year column name")
    load_parser.add_argument("--recovered", help="Recovered column name")
    
    # Compare command
    subparsers.add_parser("compare", help="Compare all diseases")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "list":
        list_diseases()
    
    elif args.command == "info":
        show_disease_info(args.disease_id)
    
    elif args.command == "load":
        load_disease_data(
            disease_id=args.disease_id,
            csv_path=args.csv_path,
            region_col=args.region,
            confirmed_col=args.confirmed,
            deaths_col=args.deaths,
            date_col=args.date,
            year_col=args.year,
            recovered_col=args.recovered
        )
    
    elif args.command == "compare":
        compare_diseases()


if __name__ == "__main__":
    main()
