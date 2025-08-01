#!/usr/bin/env python3
"""
Simple deployment script for Banking Fraud Detection API
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)


def main():
    """Main deployment function."""
    print("🚀 Banking Fraud Detection API - Deployment Script")
    print("=" * 50)
    
    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Install dependencies
    run_command("pip install -e .", "Installing dependencies")
    
    # Run tests
    run_command("python -m pytest tests/ -v", "Running tests")
    
    # Start the API
    print("🌟 Starting Banking Fraud Detection API...")
    print("API will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            "uvicorn", 
            "src.banking_fraud_api.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 API server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start API: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
