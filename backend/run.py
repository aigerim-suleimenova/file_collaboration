#!/usr/bin/env python3
"""
Script to run FastAPI app with automatic virtual environment management.
This script will create a venv if it doesn't exist, install dependencies, and run the app.
"""

import os
import sys
import subprocess
import venv
from pathlib import Path


def run_command(cmd, shell=True, check=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            cmd, shell=shell, check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return e


def create_venv(venv_path):
    """Create a virtual environment if it doesn't exist"""
    if not venv_path.exists():
        print("❌ Virtual environment not found. Creating one...")
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created!")
    else:
        print("✅ Virtual environment found!")


def get_venv_python(venv_path):
    """Get the path to the Python executable in the virtual environment"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        return venv_path / "bin" / "python"


def get_venv_pip(venv_path):
    """Get the path to the pip executable in the virtual environment"""
    if os.name == 'nt':  # Windows
        return venv_path / "Scripts" / "pip.exe"
    else:  # Unix/Linux/Mac
        return venv_path / "bin" / "pip"


def main():
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    venv_path = script_dir / "venv"

    print(f"🔧 Working directory: {script_dir}")
    print(f"🔧 Virtual environment path: {venv_path}")

    # Create virtual environment if it doesn't exist
    create_venv(venv_path)

    # Get paths to venv executables
    venv_python = get_venv_python(venv_path)
    venv_pip = get_venv_pip(venv_path)

    print(f"🔧 Using Python: {venv_python}")
    print(f"🔧 Using pip: {venv_pip}")

    # Install/update dependencies
    print("📦 Installing/updating dependencies...")
    requirements_file = script_dir / "requirements.txt"

    if requirements_file.exists():
        result = run_command(f'"{venv_pip}" install -r "{requirements_file}"')
        if result.returncode == 0:
            print("✅ Dependencies installed/updated!")
        else:
            print("❌ Failed to install dependencies")
            return 1
    else:
        print("⚠️ No requirements.txt found, skipping dependency installation")

    # Run the FastAPI app
    print("🚀 Starting FastAPI app...")
    print("🌐 App will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("🔄 Press Ctrl+C to stop the server")
    print("-" * 50)

    # Change to the script directory and run uvicorn
    os.chdir(script_dir)
    try:
        subprocess.run([
            str(venv_python), "-m", "uvicorn",
            "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
