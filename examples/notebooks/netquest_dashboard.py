#!/usr/bin/env python3
"""
Dashboard for the first available survey (Netquest survey).
Automatically detects and uses the first survey from your credentials.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lime_survey_analyzer.viz import run_survey_dashboard


def main():
    """Run dashboard for the first available survey."""
    # Get credentials path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    credentials_path = os.path.join(project_root, 'secrets', 'credentials.ini')
    
    print("🎯 Netquest Survey Dashboard")
    print("=" * 40)
    print("📡 Connecting to first available survey...")
    print("📊 Loading charts in survey order...")
    print("🌐 Dashboard will open at: http://127.0.0.1:8050")
    print("💡 The dashboard shows all supported question types:")
    print("   • Horizontal bar charts (listradio questions)")
    print("   • Stacked bar charts (ranking questions)")
    print("⏹️  Press Ctrl+C to stop")
    print()
    
    try:
        # Run dashboard - it will automatically use the first survey
        run_survey_dashboard(
            credentials_path=credentials_path,
            verbose=True,
            host='127.0.0.1',
            port=8050,
            debug=False
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        print("✅ Thanks for exploring the survey results!")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")
        print("💡 Make sure your credentials.ini file is properly configured")


if __name__ == "__main__":
    main() 