"""
Base chart functionality and common utilities.

Shared functions and utilities used across different chart types.
"""

from typing import Dict, Any


def should_show_internal_text(value: int, percentage: float, config: Dict[str, Any]) -> bool:
    """
    Determine if internal text should be shown based on value and percentage thresholds.
    
    Args:
        value: The numeric value to potentially display
        percentage: The percentage this value represents of the total
        config: Configuration dictionary containing ranking_settings
        
    Returns:
        True if text should be shown, False otherwise
    """
    settings = config['ranking_settings']
    return value >= settings['text_threshold_min'] and percentage >= settings['text_threshold_percent']


def get_chart_layout_base(title: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get base layout configuration for charts.
    
    Args:
        title: Chart title
        config: Configuration dictionary
        
    Returns:
        Base layout dictionary
    """
    from ..utils.text import clean_html_tags
    
    style = config['chart_style']
    
    return {
        'title': {
            'text': clean_html_tags(title),
            'x': 0.5,
            'font': {
                'size': style['font_size_title'], 
                'family': style['font_family'], 
                'color': style['title_color']
            }
        },
        'plot_bgcolor': style['background_color'],
        'width': style['chart_width'],
        'font': {'family': style['font_family']}
    } 