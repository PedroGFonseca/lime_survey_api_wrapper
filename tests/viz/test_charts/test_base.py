"""Tests for base chart functionality."""

from lime_survey_analyzer.viz.charts.base import should_show_internal_text, get_chart_layout_base
from lime_survey_analyzer.viz.config import get_config


def test_should_show_internal_text_true():
    """Test internal text display decision - should show."""
    config = get_config()
    
    # Value and percentage both above thresholds
    assert should_show_internal_text(20, 10, config) is True


def test_should_show_internal_text_false_low_value():
    """Test internal text display decision - low value."""
    config = get_config()
    
    # Value below threshold
    assert should_show_internal_text(5, 15, config) is False


def test_should_show_internal_text_false_low_percentage():
    """Test internal text display decision - low percentage."""
    config = get_config()
    
    # Percentage below threshold
    assert should_show_internal_text(20, 5, config) is False


def test_get_chart_layout_base():
    """Test base chart layout generation."""
    config = get_config()
    title = "Test Chart Title"
    
    layout = get_chart_layout_base(title, config)
    
    assert layout['title']['text'] == title
    assert layout['title']['x'] == 0.5
    assert layout['font']['family'] == config['chart_style']['font_family']
    assert layout['width'] == config['chart_style']['chart_width']


def test_get_chart_layout_base_with_html():
    """Test base chart layout with HTML in title."""
    config = get_config()
    title = "<p>Test Chart Title</p>"
    
    layout = get_chart_layout_base(title, config)
    
    assert layout['title']['text'] == "Test Chart Title"  # HTML should be cleaned 