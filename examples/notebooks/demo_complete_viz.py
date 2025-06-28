#!/usr/bin/env python3
"""
Complete demonstration of lime_survey_analyzer.viz capabilities.
Shows both static chart generation and interactive dashboard.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lime_survey_analyzer.viz import create_survey_visualizations, run_survey_dashboard


def main():
    """Demonstrate complete viz functionality."""
    # Get credentials path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    credentials_path = os.path.join(project_root, 'secrets', 'credentials.ini')
    
    print("🎯 Complete Visualization Demo")
    print("=" * 50)
    
    # Option 1: Generate static charts
    print("\n📊 Option 1: Generate Static Charts")
    print("-" * 35)
    charts_created = create_survey_visualizations(
        credentials_path=credentials_path,
        verbose=True
    )
    print(f"✅ Created {charts_created} static charts in 'plots/' directory")
    
    # Option 2: Interactive dashboard
    print("\n🌐 Option 2: Interactive Dashboard")
    print("-" * 35)
    print("Starting interactive dashboard...")
    print("📊 Charts will be displayed in survey order")
    print("🔗 Open http://127.0.0.1:8050 in your browser")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print()
    
    try:
        run_survey_dashboard(
            credentials_path=credentials_path,
            verbose=True,
            debug=False
        )
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"\n❌ Dashboard error: {e}")


if __name__ == "__main__":
    main() 