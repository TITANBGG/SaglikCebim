#!/usr/bin/env python3
"""
SaglikCebim Backend - Quick Start Script
Run from backend directory: python quick-start.py
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print("\n" + "="*70)
    print("  🏥 SaglikCebim Backend - Starting...")
    print("="*70 + "\n")

def check_venv():
    """Check if virtual environment exists, create if not"""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("⚠️  Virtual environment not found!")
        print("Creating venv...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ venv created\n")
    
    return venv_path

def activate_venv():
    """Activate virtual environment"""
    if os.name == 'nt':
        activate_script = "venv\\Scripts\\activate.bat"
    else:
        activate_script = "venv/bin/activate"
    
    print(f"Activating virtual environment: {activate_script}")
    return activate_script

def start_server():
    """Start the uvicorn server"""
    print("\n" + "="*70)
    print("✅ Starting API Server...")
    print("="*70)
    print("\n🌐 Access points:")
    print("   - API:    http://127.0.0.1:8000")
    print("   - Docs:   http://127.0.0.1:8000/docs  (Interactive)")
    print("   - ReDoc:  http://127.0.0.1:8000/redoc (Documentation)")
    print("\n⌚ Press CTRL+C to stop the server\n")
    print("="*70 + "\n")
    
    # Run the uvicorn server
    if os.name == 'nt':
        # Windows
        venv_python = "venv\\Scripts\\python.exe"
    else:
        # Unix-like
        venv_python = "venv/bin/python"
    
    try:
        subprocess.run([venv_python, "run.py"], check=False)
    except KeyboardInterrupt:
        print("\n\n⛔ Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

def main():
    clear_screen()
    print_banner()
    
    # Check and create venv if needed
    check_venv()
    
    # Activate venv
    activate_venv()
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
