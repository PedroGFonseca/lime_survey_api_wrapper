"""
Tests for core text visualization functionality.
"""

import pytest
from unittest.mock import Mock, patch
import plotly.graph_objects as go
from src.lime_survey_analyzer.viz.core import create_chart_from_data


class TestTextVisualizationCore:
    """Test core text visualization functionality."""
    
    def test_create_chart_from_data_text_responses(self):
        """Test creating text responses chart from data."""
        data = {
            'chart_type': 'text_responses',
            'data': ['Response 1', 'Response 2', 'Response 3'],
            'title': 'Text Question',
            'question_id': 75,
            'question_type': 'S'
        }
        config = {
            'font_family': 'Ubuntu',
            'title_font_size': 18,
            'text_color': '#2C3E50',
            'primary_color': '#82D0F4'
        }
        
        fig = create_chart_from_data(data, config, verbose=True)
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'Text Question'
    
    def test_create_chart_from_data_multiple_short_text(self):
        """Test creating multiple short text chart from data."""
        data = {
            'chart_type': 'multiple_short_text',
            'data': {
                'Freguesia': ['Lisboa', 'Porto'],
                'Concelho': ['Lisboa', 'Porto']
            },
            'title': 'Location Question',
            'question_id': 57,
            'question_type': 'Q'
        }
        config = {
            'font_family': 'Ubuntu',
            'title_font_size': 18,
            'text_color': '#2C3E50',
            'primary_color': '#82D0F4'
        }
        
        fig = create_chart_from_data(data, config, verbose=True)
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'Location Question'
    
    def test_create_chart_from_data_unsupported_type(self):
        """Test error handling for unsupported chart type."""
        data = {
            'chart_type': 'unsupported_type',
            'data': ['Response'],
            'title': 'Unsupported Question'
        }
        config = {'font_family': 'Ubuntu'}
        
        with pytest.raises(ValueError, match="Unsupported chart type: unsupported_type"):
            create_chart_from_data(data, config)
    
    def test_create_chart_from_data_missing_title(self):
        """Test chart creation with missing title."""
        data = {
            'chart_type': 'text_responses',
            'data': ['Response 1'],
            # Missing title
        }
        config = {'font_family': 'Ubuntu'}
        
        fig = create_chart_from_data(data, config)
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'Survey Question'  # Default title
    
    def test_create_chart_from_data_default_config(self):
        """Test chart creation with default config."""
        data = {
            'chart_type': 'text_responses',
            'data': ['Response 1'],
            'title': 'Test Question'
        }
        
        # Call without config parameter
        fig = create_chart_from_data(data, verbose=False)
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'Test Question'
    
    def test_create_chart_from_data_verbose_mode(self):
        """Test chart creation in verbose mode."""
        data = {
            'chart_type': 'text_responses',
            'data': ['Response 1'],
            'title': 'Verbose Test Question'
        }
        config = {'font_family': 'Ubuntu'}
        
        # Should not raise errors with verbose=True
        fig = create_chart_from_data(data, config, verbose=True)
        assert isinstance(fig, go.Figure)
    
    def test_create_chart_from_data_empty_responses(self):
        """Test chart creation with empty response data."""
        data = {
            'chart_type': 'text_responses',
            'data': [],
            'title': 'Empty Question'
        }
        config = {'font_family': 'Ubuntu'}
        
        fig = create_chart_from_data(data, config)
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'Empty Question'
    
    def test_create_chart_from_data_empty_multiple_short_text(self):
        """Test chart creation with empty multiple short text data."""
        data = {
            'chart_type': 'multiple_short_text',
            'data': {},
            'title': 'Empty Multiple Question'
        }
        config = {'font_family': 'Ubuntu'}
        
        fig = create_chart_from_data(data, config)
        
        assert isinstance(fig, go.Figure)
        assert fig.layout.title.text == 'Empty Multiple Question'


class TestTextVisualizationIntegration:
    """Integration tests for text visualization."""
    
    @patch('src.lime_survey_analyzer.viz.core.create_text_responses_chart')
    def test_text_responses_chart_integration(self, mock_create_chart):
        """Test integration with text responses chart creation."""
        mock_fig = Mock(spec=go.Figure)
        mock_create_chart.return_value = mock_fig
        
        data = {
            'chart_type': 'text_responses',
            'data': ['Response 1', 'Response 2'],
            'title': 'Integration Test'
        }
        config = {'font_family': 'Ubuntu'}
        
        result = create_chart_from_data(data, config, verbose=True)
        
        assert result == mock_fig
        mock_create_chart.assert_called_once_with(
            ['Response 1', 'Response 2'], 
            'Integration Test', 
            config, 
            True
        )
    
    @patch('src.lime_survey_analyzer.viz.core.create_multiple_short_text_chart')
    def test_multiple_short_text_chart_integration(self, mock_create_chart):
        """Test integration with multiple short text chart creation."""
        mock_fig = Mock(spec=go.Figure)
        mock_create_chart.return_value = mock_fig
        
        data = {
            'chart_type': 'multiple_short_text',
            'data': {'Sub1': ['Response 1'], 'Sub2': ['Response 2']},
            'title': 'Integration Test'
        }
        config = {'font_family': 'Ubuntu'}
        
        result = create_chart_from_data(data, config, verbose=False)
        
        assert result == mock_fig
        mock_create_chart.assert_called_once_with(
            {'Sub1': ['Response 1'], 'Sub2': ['Response 2']}, 
            'Integration Test', 
            config, 
            False
        )
    
    def test_chart_type_consistency(self):
        """Test that chart types are consistently handled."""
        # Test all supported text chart types
        text_chart_types = ['text_responses', 'multiple_short_text']
        
        for chart_type in text_chart_types:
            if chart_type == 'text_responses':
                test_data = ['Response 1']
            else:  # multiple_short_text
                test_data = {'Sub1': ['Response 1']}
            
            data = {
                'chart_type': chart_type,
                'data': test_data,
                'title': f'Test {chart_type}'
            }
            config = {'font_family': 'Ubuntu'}
            
            # Should not raise errors
            fig = create_chart_from_data(data, config)
            assert isinstance(fig, go.Figure)
    
    def test_config_parameter_propagation(self):
        """Test that config parameters are properly propagated to chart functions."""
        data = {
            'chart_type': 'text_responses',
            'data': ['Test response'],
            'title': 'Config Test'
        }
        custom_config = {
            'font_family': 'Arial',
            'title_font_size': 24,
            'text_color': '#FF0000',
            'primary_color': '#00FF00'
        }
        
        fig = create_chart_from_data(data, custom_config)
        
        assert isinstance(fig, go.Figure)
        # Verify config was applied
        assert fig.layout.font.family == 'Arial'
        assert fig.layout.title.font.size == 24
        assert fig.layout.title.font.color == '#FF0000' 