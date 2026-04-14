"""
Shim for start_prism.py
This file allows users to continue running 'python start_prism.py' from the root.
It redirects to scripts/start_prism.py.
"""
import sys
from pathlib import Path
import subprocess

if __name__ == "__main__":
    root = Path(__file__).parent
    script_path = root / "scripts" / "start_prism.py"
    
    if not script_path.exists():
        print(f"Error: Could not find startup script at {script_path}")
        sys.exit(1)
        
    print(f"🔄 Redirecting to {script_path}...")
    
    # Run the real script
    try:
        # Pass through all arguments
        subprocess.run([sys.executable, str(script_path)] + sys.argv[1:])
    except KeyboardInterrupt:
        pass
