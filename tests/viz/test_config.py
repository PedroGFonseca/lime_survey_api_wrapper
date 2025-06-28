"""Tests for the config module."""

import pytest
from lime_survey_analyzer.viz.config import get_config, validate_config, DEFAULT_CONFIG


def test_get_config_default():
    """Test getting default configuration."""
    config = get_config()
    assert config == DEFAULT_CONFIG
    assert config is not DEFAULT_CONFIG  # Should be a copy


def test_get_config_with_custom():
    """Test getting configuration with custom overrides."""
    custom = {
        'chart_style': {'font_family': 'Arial'},
        'output_settings': {'default_format': 'png'}
    }
    
    config = get_config(custom)
    
    # Should have custom values
    assert config['chart_style']['font_family'] == 'Arial'
    assert config['output_settings']['default_format'] == 'png'
    
    # Should still have default values for non-overridden keys
    assert config['chart_style']['primary_color'] == DEFAULT_CONFIG['chart_style']['primary_color']
    assert config['ranking_settings'] == DEFAULT_CONFIG['ranking_settings']


def test_validate_config_valid():
    """Test validation with valid config."""
    config = get_config()
    validate_config(config)  # Should not raise


def test_validate_config_missing_key():
    """Test validation with missing required key."""
    config = {'chart_style': {}}
    
    with pytest.raises(ValueError, match="Missing required config key"):
        validate_config(config)


def test_validate_config_invalid_format():
    """Test validation with invalid output format."""
    config = get_config({
        'output_settings': {
            'default_format': 'invalid',
            'supported_formats': ['html', 'png']
        }
    })
    
    with pytest.raises(ValueError, match="Default format must be in supported formats"):
        validate_config(config) 