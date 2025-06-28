#!/usr/bin/env python3
"""
Simple script to run the survey dashboard.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lime_survey_analyzer.viz import run_survey_dashboard


def main():
    """Run the survey dashboard."""
    # Get credentials path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    credentials_path = os.path.join(project_root, 'secrets', 'credentials.ini')
    
    print("🚀 Starting Survey Dashboard...")
    print("📊 Loading charts in survey order...")
    print("🌐 Dashboard will be available at: http://127.0.0.1:8050")
    print("⏹️  Press Ctrl+C to stop")
    
    # Run dashboard
    run_survey_dashboard(
        credentials_path=credentials_path,
        verbose=True,
        debug=False  # Set to True for development
    )


if __name__ == "__main__":
    main() 