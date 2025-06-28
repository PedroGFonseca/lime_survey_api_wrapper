"""
Visualization module for lime_survey_analyzer.

This module provides clean, modular visualization capabilities with support for:
- Horizontal bar charts for listradio questions
- Stacked bar charts for ranking questions
- Configurable styling and output formats
- Library-agnostic chart creation functions
- Interactive Dash dashboard

Main API:
    create_survey_visualizations() - Main function to generate all charts
    run_survey_dashboard() - Run interactive Dash dashboard
    get_config() - Get configuration with optional overrides
    
Chart functions:
    create_horizontal_bar_chart() - Pure function for horizontal bar charts
    create_ranking_stacked_bar_chart() - Pure function for ranking charts
"""

from .core import create_survey_visualizations
from .config import get_config, validate_config, DEFAULT_CONFIG
from .charts.horizontal_bar import create_horizontal_bar_chart
from .charts.ranking_stacked import create_ranking_stacked_bar_chart
from .utils.files import save_chart
from .utils.text import clean_html_tags, wrap_text_labels, clean_filename
from .dashboard import run_survey_dashboard

# Public API
__all__ = [
    # Main functions
    'create_survey_visualizations',
    'run_survey_dashboard',
    
    # Configuration
    'get_config',
    'validate_config', 
    'DEFAULT_CONFIG',
    
    # Pure chart functions
    'create_horizontal_bar_chart',
    'create_ranking_stacked_bar_chart',
    
    # Utilities
    'save_chart',
    'clean_html_tags',
    'wrap_text_labels',
    'clean_filename'
] 