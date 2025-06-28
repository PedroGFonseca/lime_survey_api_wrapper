"""
Configuration module for visualization components.

All visualization settings and constants are centralized here.
"""

import copy
from typing import Dict, Any, List

# Default visualization configuration
DEFAULT_CONFIG: Dict[str, Any] = {
    'chart_style': {
        'font_family': 'Ubuntu',
        'primary_color': '#82D0F4',
        'text_color': 'black',
        'title_color': '#2C3E50',
        'border_color': 'rgba(0,0,0,0.3)',
        'background_color': 'rgba(0,0,0,0)',
        'font_size_title': 16,
        'font_size_text': 14,
        'font_size_axis': 12,
        'chart_width': 800,
        'chart_height': 400,
        'text_wrap_length': 40,
        # Ranking chart colors - darkest to lightest blue
        'ranking_colors': ['#1f4e79', '#2e6da4', '#428bca', '#5bc0de', '#d9edf7']
    },
    'ranking_settings': {
        'text_threshold_min': 15,        # Minimum value to show internal text
        'text_threshold_percent': 8,     # Minimum percentage of bar to show text
        'wrap_length': 30,               # Text wrapping for ranking charts
        'chart_height_per_row': 50,      # Height per option row
        'chart_height_min': 500,         # Minimum chart height
        'left_margin': 350,              # Left margin for long labels
        'right_margin': 120              # Right margin for legend
    },
    'output_settings': {
        'plots_dir': 'plots',
        'default_format': 'html',
        'filename_max_length': 100,
        'supported_formats': ['html', 'png']
    }
}


def get_config(custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Get configuration with optional custom overrides.
    
    Args:
        custom_config: Optional dictionary to override default settings
        
    Returns:
        Complete configuration dictionary
    """
    if custom_config is None:
        return copy.deepcopy(DEFAULT_CONFIG)
    
    # Deep merge custom config with defaults
    config = copy.deepcopy(DEFAULT_CONFIG)
    for key, value in custom_config.items():
        if key in config and isinstance(config[key], dict) and isinstance(value, dict):
            config[key].update(value)
        else:
            config[key] = value
    
    return config


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration to validate
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_keys = ['chart_style', 'ranking_settings', 'output_settings']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    # Validate output format
    if config['output_settings']['default_format'] not in config['output_settings']['supported_formats']:
        raise ValueError("Default format must be in supported formats") 