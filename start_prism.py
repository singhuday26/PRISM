"""Start both API and Streamlit Dashboard for PRISM"""
import subprocess
import sys
import time
import os
from pathlib import Path

def check_port_available(port):
    """Check if a port is available."""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def main():
    print("=" * 80)
    print("🚀 PRISM - Starting Web Services")
    print("=" * 80)
    
    # Check if ports are available
    if not check_port_available(8000):
        print("⚠️  Port 8000 is already in use (API)")
        print("   If you want to restart, stop the existing API server first.")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    if not check_port_available(8501):
        print("⚠️  Port 8501 is already in use (Dashboard)")
        print("   If you want to restart, stop the existing dashboard first.")
        response = input("   Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Exiting...")
            return
    
    print("\n🔌 Step 1: Starting API Server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    
    # Start API in background
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app:app", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Path(__file__).parent
    )
    
    print("   ✓ API server starting in background...")
    print("   ⏳ Waiting for API to be ready...")
    
    # Actively wait for API to be ready
    import urllib.request
    api_ready = False
    for attempt in range(20):  # Try for up to 20 seconds
        try:
            urllib.request.urlopen("http://localhost:8000/health/ping", timeout=2)
            api_ready = True
            break
        except Exception:
            time.sleep(1)
            print(f"   ... waiting ({attempt + 1}s)")
    
    if not api_ready:
        print("   ⚠️ API may not be fully ready, continuing anyway...")
    else:
        print("   ✓ API is ready!")
    
    print("📊 Step 2: Starting Streamlit Dashboard...")
    print("   URL: http://localhost:8501\n")
    
    print("=" * 80)
    print("✅ PRISM is now running!")
    print("=" * 80)
    print("\n🌐 Access URLs:")
    print("   📊 Dashboard:  http://localhost:8501")
    print("   🔌 API:        http://localhost:8000")
    print("   📖 API Docs:   http://localhost:8000/docs")
    print("\n⚠️  To stop PRISM:")
    print("   Press Ctrl+C in this window")
    print("=" * 80)
    print()
    
    # Start Streamlit (blocking)
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "backend/dashboard/app.py",
            "--server.port=8501",
            "--server.address=localhost"
        ])
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping PRISM...")
        api_process.terminate()
        api_process.wait()
        print("✓ API stopped")
        print("✓ Dashboard stopped")
        print("\nGoodbye! 👋")

if __name__ == "__main__":
    main()
