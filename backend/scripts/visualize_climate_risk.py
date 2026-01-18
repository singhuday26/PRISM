"""
Visualize Climate Risk Impact
------------------------------
Shows how monsoon seasonality affects disease risk scores.
"""

import logging
from backend.utils.climate import MONSOON_RISK_MULTIPLIERS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def visualize_climate_multipliers():
    """Display climate risk multipliers across the year."""
    
    print("\n" + "="*90)
    print("CLIMATE RISK MULTIPLIERS - MONSOON SEASONALITY PATTERN")
    print("="*90 + "\n")
    
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Find max multiplier for scaling
    max_multiplier = max(MONSOON_RISK_MULTIPLIERS.values())
    
    print(f"{'Month':<12} {'Risk Multiplier':<20} {'Visualization':<35} {'Season':<20}")
    print("-"*90)
    
    for month in range(1, 13):
        multiplier = MONSOON_RISK_MULTIPLIERS[month]
        
        # Create bar visualization
        bar_length = int((multiplier / max_multiplier) * 30)
        bar = "█" * bar_length
        
        # Determine season and marker
        if month in [6, 7, 8, 9]:
            season = "MONSOON 🌧️"
            marker = " ⬆️"
        elif month in [10, 11]:
            season = "Post-monsoon"
            marker = ""
        elif month in [3, 4, 5]:
            season = "Pre-monsoon"
            marker = ""
        else:
            season = "Winter"
            marker = " ⬇️"
        
        # Color-code multiplier value
        if multiplier >= 1.5:
            mult_str = f"{multiplier:.1f}x 🔴"
        elif multiplier >= 1.0:
            mult_str = f"{multiplier:.1f}x 🟡"
        else:
            mult_str = f"{multiplier:.1f}x 🟢"
        
        print(f"{month_names[month-1]:<12} {mult_str:<20} {bar:<35} {season:<20}{marker}")
    
    print("-"*90)
    print("\nRisk Levels:")
    print("  🔴 Very High (1.5x+) - Peak monsoon transmission")
    print("  🟡 Moderate (1.0x)   - Baseline transmission")
    print("  🟢 Low (< 1.0x)      - Reduced transmission")
    print("\nSeasonal Periods:")
    print("  🌧️  Monsoon (Jun-Sep): Peak dengue transmission due to rainfall and humidity")
    print("  ⬆️  Post-monsoon (Oct-Nov): Elevated risk from standing water")
    print("  ⬇️  Winter (Dec-Feb): Reduced transmission due to cooler, drier conditions")
    print("="*90 + "\n")


def show_example_impact():
    """Show example of climate boost impact on risk scores."""
    
    print("\n" + "="*90)
    print("EXAMPLE: CLIMATE BOOST IMPACT ON RISK SCORES")
    print("="*90 + "\n")
    
    base_risk = 0.60  # Example base risk (MEDIUM level)
    
    print(f"Scenario: Region with base risk score of {base_risk:.2f} (MEDIUM)")
    print("-"*90)
    print(f"{'Month':<12} {'Base Risk':<12} {'Multiplier':<12} {'Adjusted Risk':<15} {'Risk Level':<15}")
    print("-"*90)
    
    for month in [1, 5, 7, 10]:
        multiplier = MONSOON_RISK_MULTIPLIERS[month]
        adjusted = min(1.0, base_risk * multiplier)
        
        # Determine risk level
        if adjusted >= 0.70:
            level = "HIGH 🔴"
        elif adjusted >= 0.40:
            level = "MEDIUM 🟡"
        else:
            level = "LOW 🟢"
        
        month_names_short = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        
        print(f"{month_names_short[month-1]:<12} {base_risk:<12.2f} {multiplier:<12.1f}x {adjusted:<15.2f} {level:<15}")
    
    print("-"*90)
    print("\nKey Insight:")
    print("  • Same outbreak intensity (base_risk=0.60) has different implications by season")
    print("  • July (monsoon peak): Risk elevated to 1.00 (capped) → HIGH alert")
    print("  • January (winter): Risk reduced to 0.30 → LOW concern")
    print("  • This reflects real-world dengue epidemiology in India")
    print("="*90 + "\n")


if __name__ == "__main__":
    visualize_climate_multipliers()
    show_example_impact()
