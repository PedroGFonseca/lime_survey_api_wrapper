#!/usr/bin/env python3
"""
Advanced example showing custom configuration and selective chart generation.
"""

import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from lime_survey_analyzer.viz import create_survey_visualizations, get_config


def main():
    """Demonstrate advanced viz features."""
    # Get credentials path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    credentials_path = os.path.join(project_root, 'secrets', 'credentials.ini')
    
    # Example 1: Custom styling with different colors and fonts
    print("🎨 Example 1: Custom styling")
    custom_style_config = {
        'chart_style': {
            'font_family': 'Arial',
            'primary_color': '#FF6B6B',  # Red theme
            'title_color': '#2C3E50',
            'font_size_title': 18,
            'chart_width': 1000,
            'chart_height': 500
        },
        'output_settings': {
            'plots_dir': 'plots_custom_style',
            'default_format': 'png'  # PNG instead of HTML
        }
    }
    
    charts_created = create_survey_visualizations(
        credentials_path=credentials_path,
        config=custom_style_config,
        question_types=['listradio'],  # Only horizontal bar charts
        verbose=True
    )
    print(f"Created {charts_created} charts with custom styling\n")
    
    # Example 2: Only ranking charts with verbose output
    print("📊 Example 2: Only ranking charts")
    ranking_config = {
        'output_settings': {
            'plots_dir': 'plots_ranking_only',
            'default_format': 'html'
        },
        'ranking_settings': {
            'text_threshold_min': 10,  # Lower threshold for showing text
            'wrap_length': 25,         # Shorter text wrapping
            'left_margin': 400         # More space for labels
        }
    }
    
    charts_created = create_survey_visualizations(
        credentials_path=credentials_path,
        config=ranking_config,
        question_types=['ranking'],  # Only ranking charts
        verbose=True
    )
    print(f"Created {charts_created} ranking charts\n")
    
    # Example 3: Silent mode with default settings
    print("🤫 Example 3: Silent mode")
    charts_created = create_survey_visualizations(
        credentials_path=credentials_path,
        verbose=False  # No output during processing
    )
    print(f"Silently created {charts_created} charts with default settings\n")
    
    print("🎉 Advanced examples complete!")


if __name__ == "__main__":
    main() 