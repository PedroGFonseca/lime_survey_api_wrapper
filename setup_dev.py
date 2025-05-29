#!/usr/bin/env python3
"""
Development setup script for LimeSurvey Analyzer.

This script helps set up the development environment by:
1. Creating a virtual environment
2. Installing the package in development mode
3. Installing development dependencies
4. Setting up pre-commit hooks
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def run_command(cmd, check=True, shell=False):
    """Run a command and return the result."""
    print(f"Running: {cmd}")
    if isinstance(cmd, str) and not shell:
        cmd = cmd.split()
    
    result = subprocess.run(cmd, check=check, shell=shell, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def main():
    """Main setup function."""
    print("Setting up LimeSurvey Analyzer development environment...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Determine the correct venv activation script
    if platform.system() == "Windows":
        venv_activate = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        venv_activate = "venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    try:
        # Create virtual environment
        if not Path("venv").exists():
            print("\n1. Creating virtual environment...")
            run_command([sys.executable, "-m", "venv", "venv"])
        else:
            print("\n1. Virtual environment already exists.")
        
        # Upgrade pip
        print("\n2. Upgrading pip...")
        run_command([python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install the package in development mode with all dependencies
        print("\n3. Installing package in development mode...")
        run_command([pip_cmd, "install", "-e", ".[dev,docs]"])
        
        # Install pre-commit hooks (if available)
        print("\n4. Setting up pre-commit hooks...")
        try:
            run_command([python_cmd, "-m", "pre_commit", "install"])
        except subprocess.CalledProcessError:
            print("Pre-commit not available or failed to install hooks.")
        
        # Run tests to verify installation
        print("\n5. Running tests to verify installation...")
        try:
            run_command([python_cmd, "-m", "pytest", "--version"])
            run_command([python_cmd, "-m", "pytest", "tests/", "-v"])
        except subprocess.CalledProcessError:
            print("Tests failed or pytest not available.")
        
        print("\n" + "="*60)
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\nTo activate the virtual environment:")
        if platform.system() == "Windows":
            print("  venv\\Scripts\\activate")
        else:
            print("  source venv/bin/activate")
        
        print("\nTo run tests:")
        print("  pytest")
        
        print("\nTo build documentation:")
        print("  cd docs")
        print("  make html")
        
        print("\nTo format code:")
        print("  black src tests")
        print("  isort src tests")
        
        print("\nTo run type checking:")
        print("  mypy src")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during setup: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSetup cancelled by user.")
        sys.exit(1)


if __name__ == "__main__":
    main() 