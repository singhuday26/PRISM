"""Start both API and Streamlit Dashboard for PRISM"""
import subprocess
import sys
import time
import os
import signal
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
    if not check_port_available(27017):
        print("⚠️  Port 27017 is already in use — MongoDB may already be running.")
        print("   Skipping MongoDB startup.")
        mongo_process = None
    else:
        mongo_process = None  # will be set below

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
    
    # Create logs directory
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------ #
    # Step 1: Start MongoDB
    # ------------------------------------------------------------------ #
    if not check_port_available(27017):
        print("\n🍃 Step 1: MongoDB already running on port 27017 — skipping.")
    else:
        print("\n🍃 Step 1: Starting MongoDB...")
        print("   Port: 27017")
        mongo_log_path = logs_dir / "mongodb.log"
        print(f"   Writing MongoDB logs to: {mongo_log_path}")
        mongo_log = open(mongo_log_path, "w")
        try:
            mongo_process = subprocess.Popen(
                ["mongod", "--port", "27017"],
                stdout=mongo_log,
                stderr=subprocess.STDOUT,
            )
            print("   ✓ MongoDB starting in background...")
            print("   ⏳ Waiting for MongoDB to be ready...")

            import socket
            mongo_ready = False
            for attempt in range(15):  # up to 15 seconds
                try:
                    s = socket.create_connection(("localhost", 27017), timeout=1)
                    s.close()
                    mongo_ready = True
                    break
                except OSError:
                    if mongo_process.poll() is not None:
                        print(f"   ❌ MongoDB process died with code {mongo_process.returncode}")
                        print("   Check logs/mongodb.log for details.")
                        break
                    time.sleep(1)
                    print(f"   ... waiting ({attempt + 1}s)")

            if mongo_ready:
                print("   ✓ MongoDB is ready!")
            else:
                print("   ⚠️  MongoDB may not be fully ready.")
                print("   Check logs/mongodb.log for details.")
                response = input("   Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    mongo_log.close()
                    return
        except FileNotFoundError:
            print("   ❌ 'mongod' not found. Is MongoDB installed and on your PATH?")
            response = input("   Continue without MongoDB? (y/n): ")
            if response.lower() != 'y':
                return
            mongo_process = None

    print("\n🔌 Step 2: Starting API Server...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    
    api_log_path = logs_dir / "api_startup.log"
    
    print(f"   Writing API logs to: {api_log_path}")
    api_log = open(api_log_path, "w")
    
    cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
    print(f"   Command: {' '.join(cmd)}")
    
    # Start API in background
    api_process = None
    try:
        api_process = subprocess.Popen(
            cmd,
            stdout=api_log,
            stderr=subprocess.STDOUT,
            cwd=Path(__file__).parent,
        )
        
        print("   ✓ API server starting in background...")
        print("   ⏳ Waiting for API to be ready...")
        
        # Actively wait for API to be ready
        import urllib.request
        api_ready = False
        for attempt in range(30):  # Try for up to 30 seconds
            try:
                urllib.request.urlopen("http://localhost:8000/health", timeout=2)
                api_ready = True
                break
            except Exception as e:
                if api_process.poll() is not None:
                    print(f"   ❌ API process died with code {api_process.returncode}")
                    break
                time.sleep(1)
                print(f"   ... waiting ({attempt + 1}s)")
        
        if not api_ready:
            print("   ⚠️ API may not be fully ready or failed to start.")
            print("   Check logs/api_startup.log for details.")
            response = input("   Continue to dashboard anyway? (y/n): ")
            if response.lower() != 'y':
                return
        else:
            print("   ✓ API is ready!")
        
        print("\n📊 Step 3: Starting Streamlit Dashboard...")
        print("   URL: http://localhost:8501\n")
        
        print("=" * 80)
        print("✅ PRISM is now running!")
        print("=" * 80)
        print("\n🌐 Access URLs:")
        print("   📊 Dashboard:      http://localhost:8501")
        print("   🔌 API:            http://localhost:8000")
        print("   📖 API Docs:       http://localhost:8000/docs")
        print("   🗺️ Heatmap:        http://localhost:8000/ui/heatmap/")
        print("\n⚠️  To stop PRISM:")
        print("   Press Ctrl+C in this window")
        print("=" * 80)
        print()
        
        # Start Streamlit (non-blocking so we can manage shutdown)
        streamlit_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run",
            "backend/dashboard/app.py",
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=true"
        ])
        
        # Wait for Streamlit to exit (or be killed)
        streamlit_process.wait()
    except KeyboardInterrupt:
        print("\n\n⏹️  Stopping PRISM (KeyboardInterrupt)...")
    except Exception as e:
        print(f"\n\n❌ Error occurred: {e}")
    finally:
        # Terminate Streamlit if still running
        if 'streamlit_process' in locals() and streamlit_process.poll() is None:
            print("⏹️  Shutting down Dashboard...")
            streamlit_process.terminate()
            try:
                streamlit_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                streamlit_process.kill()
            print("✓ Dashboard stopped")
        
        if api_process and api_process.poll() is None:
            print("⏹️  Shutting down API server...")
            api_process.terminate()
            try:
                api_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                api_process.kill()
            print("✓ API stopped")
        
        if mongo_process and mongo_process.poll() is None:
            print("⏹️  Shutting down MongoDB...")
            mongo_process.terminate()
            try:
                mongo_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                mongo_process.kill()
            print("✓ MongoDB stopped")
        
        if 'api_log' in locals() and not api_log.closed:
            api_log.close()
            
        print("✓ Dashboard stopped")
        print("\nGoodbye! 👋")

if __name__ == "__main__":
    main()
