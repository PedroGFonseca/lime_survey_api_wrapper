#!/usr/bin/env python3
"""
Test script for the new modular viz structure.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lime_survey_analyzer.viz import create_survey_visualizations


def main():
    """Test the new viz module."""
    # Get credentials path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    credentials_path = os.path.join(project_root, 'secrets', 'credentials.ini')
    
    # Create visualizations with verbose output
    charts_created = create_survey_visualizations(
        credentials_path=credentials_path,
        verbose=True
    )
    
    print(f"\n🎉 Test complete! Created {charts_created} charts using the new modular structure.")


if __name__ == "__main__":
    main() 