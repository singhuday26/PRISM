"""Run PRISM Streamlit Dashboard"""
import subprocess
import sys
from pathlib import Path

# Get the dashboard path
dashboard_path = Path(__file__).parent / "backend" / "dashboard" / "app.py"

if not dashboard_path.exists():
    print(f"❌ Dashboard not found at: {dashboard_path}")
    sys.exit(1)

print("🚀 Starting PRISM Streamlit Dashboard...")
print("=" * 70)
print("📍 Dashboard will open in your browser at:")
print("   http://localhost:8501")
print("=" * 70)
print("\n⚠️  Make sure the API is running at http://localhost:8000")
print("   (Run: python -m uvicorn backend.app:app --reload)\n")
print("Press Ctrl+C to stop the dashboard")
print("=" * 70)

# Run Streamlit
subprocess.run([
    sys.executable,
    "-m",
    "streamlit",
    "run",
    str(dashboard_path),
    "--server.port=8501",
    "--server.address=localhost"
])
