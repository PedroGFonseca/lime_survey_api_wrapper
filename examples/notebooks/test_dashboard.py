#!/usr/bin/env python3
"""
Test script to verify dashboard creation works.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lime_survey_analyzer.viz.dashboard import create_survey_dashboard
from lime_survey_analyzer.viz import get_config


def main():
    """Test dashboard creation."""
    # Get credentials path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    credentials_path = os.path.join(project_root, 'secrets', 'credentials.ini')
    
    print('🧪 Testing dashboard creation...')
    
    try:
        app = create_survey_dashboard(credentials_path, get_config(), verbose=True)
        print(f'✅ Dashboard created successfully!')
        print(f'📊 Dashboard has {len(app.layout.children)} main components')
        print('🌐 Ready to run with run_survey_dashboard()')
        
    except Exception as e:
        print(f'❌ Dashboard creation failed: {e}')
        return False
        
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 