#!/usr/bin/env python3
"""
Simple script to run the survey dashboard with real data.
"""

import os
import sys

# Add the src directory to the path so we can import lime_survey_analyzer
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from lime_survey_analyzer.viz.dashboard import run_survey_dashboard


def main():
    """Run the dashboard with real survey data."""
    
    # Get credentials path
    credentials_path = os.path.join(project_root, 'secrets', 'credentials.ini')
    
    if not os.path.exists(credentials_path):
        print(f"❌ Credentials file not found: {credentials_path}")
        print("Please ensure you have set up your credentials.ini file")
        sys.exit(1)
    
    print(f"🔑 Using credentials: {credentials_path}")
    print("🚀 Starting dashboard with real survey data...")
    print("📱 Dashboard will be available at: http://127.0.0.1:8050")
    print("🛑 Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        # Run dashboard with real data
        run_survey_dashboard(
            credentials_path=credentials_path,
            host='127.0.0.1',
            port=8050,
            debug=False,
            verbose=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 