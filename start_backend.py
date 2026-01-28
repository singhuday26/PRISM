import uvicorn
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.append(str(project_root))
    
    print("🚀 Starting PRISM Backend API...")
    print("   URL: http://localhost:8000")
    print("   Docs: http://localhost:8000/docs")
    
    # Run Uvicorn
    # reload=True allows auto-restart on code changes (Dev Experience!)
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True, reload_dirs=[str(project_root / "backend")])
