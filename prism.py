"""
PRISM (Predictive Risk Intelligence & Surveillance Model) - Main Entry Point
Use this tool to setup, seed, and manage the PRISM platform.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path

# ANSI colors for better UI
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"

def print_banner():
    print(f"{BLUE}{BOLD}")
    print("=" * 60)
    print("   🌐 PRISM - Predictive Risk Intelligence & Surveillance")
    print("=" * 60)
    print(f"{RESET}")

def run_command(cmd, cwd=None, shell=False):
    try:
        if shell:
            return subprocess.run(cmd, cwd=cwd, shell=True, check=True)
        return subprocess.run(cmd, cwd=cwd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Error executing command: {e}{RESET}")
        return e

def check_env():
    print(f"\n{BLUE}🔍 Checking Environment...{RESET}")
    root = Path(__file__).parent
    
    # Check .env
    if not (root / ".env").exists():
        if (root / ".env.example").exists():
            print(f"{YELLOW}⚠️  .env file not found. Creating from .env.example...{RESET}")
            import shutil
            shutil.copy(".env.example", ".env")
            print(f"{GREEN}✅ .env created.{RESET}")
        else:
            print(f"{RED}❌ .env.example not found. Please create a .env file.{RESET}")
            return False
    else:
        print(f"{GREEN}✅ .env file found.{RESET}")
        
    # Check MongoDB (basic check for mongod in path)
    try:
        subprocess.run(["mongod", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}✅ MongoDB (mongod) found in PATH.{RESET}")
    except FileNotFoundError:
        print(f"{YELLOW}⚠️  'mongod' not found in PATH. You may need to start MongoDB manually or use Docker.{RESET}")
        
    return True

def setup_project(args):
    print_banner()
    print(f"{BOLD}Setting up PRISM...{RESET}\n")
    
    if not check_env():
        return
    
    # Install dependencies if requested or .venv missing
    if args.install or not Path(".venv").exists():
        print(f"\n{BLUE}📦 Installing Dependencies...{RESET}")
        run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print(f"{GREEN}✅ Dependencies installed.{RESET}")
    
    print(f"\n{BOLD}{GREEN}✨ Setup Complete!{RESET}")
    print(f"Run {BLUE}python prism.py start{RESET} to launch the platform.")

def start_project(args):
    print_banner()
    print(f"{GREEN}🚀 Starting PRISM Services...{RESET}")
    
    # Redirect to scripts/start_prism.py
    script_path = Path(__file__).parent / "scripts" / "start_prism.py"
    if not script_path.exists():
        print(f"{RED}❌ Error: {script_path} not found!{RESET}")
        return
        
    # Run the start script
    try:
        subprocess.run([sys.executable, str(script_path)])
    except KeyboardInterrupt:
        pass # Handle exit gracefully

def seed_data(args):
    print_banner()
    print(f"{BLUE}🌱 Seeding Database...{RESET}")
    
    seed_script = Path(__file__).parent / "backend" / "scripts" / "seed.py"
    if not seed_script.exists():
        # Maybe it's multi-disease seed
        seed_script = Path(__file__).parent / "backend" / "scripts" / "load_multi_disease.py"
    
    if seed_script.exists():
        run_command([sys.executable, "-m", "backend.scripts.seed"])
        print(f"{GREEN}✅ Database seeded successfully.{RESET}")
    else:
        print(f"{RED}❌ Seed script not found at {seed_script}{RESET}")

def check_status(args):
    print_banner()
    print(f"{BLUE}📊 Checking Service Status...{RESET}")
    
    import urllib.request
    services = {
        "API Server": "http://localhost:8000/health",
        "Dashboard": "http://localhost:8501",
        "React UI": "http://localhost:8000/ui/"
    }
    
    for name, url in services.items():
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    print(f" {GREEN}●{RESET} {name:<12}: RUNNING ({url})")
                else:
                    print(f" {YELLOW}●{RESET} {name:<12}: UNKNOWN (Status {response.status})")
        except Exception:
            print(f" {RED}○{RESET} {name:<12}: DOWN")

def main():
    parser = argparse.ArgumentParser(description="PRISM Control Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Initialize environment and dependencies")
    setup_parser.add_argument("--install", action="store_true", help="Force reinstall dependencies")
    
    # Start command
    subparsers.add_parser("start", help="Launch the full PRISM stack")
    
    # Seed command
    subparsers.add_parser("seed", help="Seed the database with sample data")
    
    # Status command
    subparsers.add_parser("status", help="Check status of running services")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_project(args)
    elif args.command == "start":
        start_project(args)
    elif args.command == "seed":
        seed_data(args)
    elif args.command == "status":
        check_status(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
