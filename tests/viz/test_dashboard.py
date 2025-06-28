"""
Comprehensive tests for the dashboard using dash.testing.
"""

import pytest
import os
import time
from unittest.mock import patch, MagicMock
import plotly.graph_objects as go
from lime_survey_analyzer.viz.dashboard import create_survey_dashboard, run_survey_dashboard
from lime_survey_analyzer.viz.core import create_survey_visualizations


@pytest.fixture
def mock_credentials_path():
    """Mock credentials path for testing."""
    return "/fake/path/credentials.ini"


@pytest.fixture
def mock_chart_data():
    """Mock chart data for testing with proper plotly figures."""
    # Create real plotly figures that are JSON serializable
    fig1 = go.Figure(data=[go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3])])
    fig1.update_layout(title="Test Bar Chart")
    
    fig2 = go.Figure(data=[go.Bar(x=['X', 'Y', 'Z'], y=[3, 2, 1])])
    fig2.update_layout(title="Test Ranking Chart")
    
    return {
        'charts': [
            {
                'question_id': '37',
                'title': 'What is your favorite color?',
                'chart_type': 'horizontal_bar',
                'figure': fig1,
                'data': ['Red', 'Blue', 'Green']
            },
            {
                'question_id': '41', 
                'title': 'Rate your satisfaction',
                'chart_type': 'ranking_stacked',
                'figure': fig2,
                'data': []
            },
            {
                'question_id': '45',
                'title': 'Additional comments',
                'chart_type': 'text_responses',
                'figure': None,
                'data': ['Great service!', 'Could be better', 'No complaints']
            }
        ]
    }


class TestDashboardCreation:
    """Test dashboard creation and structure."""
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_dashboard_creation_basic(self, mock_viz, mock_credentials_path, mock_chart_data):
        """Test basic dashboard creation."""
        mock_viz.return_value = mock_chart_data
        
        app = create_survey_dashboard(mock_credentials_path, verbose=False)
        
        assert app is not None
        assert hasattr(app, 'layout')
        mock_viz.assert_called_once_with(
            survey_id=None,
            credentials_path=mock_credentials_path,
            output_format='dict',
            verbose=False
        )
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_dashboard_creation_with_survey_id(self, mock_viz, mock_credentials_path, mock_chart_data):
        """Test dashboard creation with specific survey ID."""
        mock_viz.return_value = mock_chart_data
        
        app = create_survey_dashboard(mock_credentials_path, survey_id=123456, verbose=True)
        
        assert app is not None
        mock_viz.assert_called_once_with(
            survey_id=123456,
            credentials_path=mock_credentials_path,
            output_format='dict',
            verbose=True
        )
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_dashboard_empty_charts(self, mock_viz, mock_credentials_path):
        """Test dashboard creation with no charts."""
        mock_viz.return_value = {'charts': []}
        
        app = create_survey_dashboard(mock_credentials_path, verbose=False)
        
        assert app is not None
        assert hasattr(app, 'layout')


class TestDashboardInteractivity:
    """Test dashboard interactive features using dash.testing."""
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_dashboard_loads_successfully(self, mock_viz, mock_credentials_path, mock_chart_data, dash_duo):
        """Test that dashboard loads without errors."""
        mock_viz.return_value = mock_chart_data
        
        app = create_survey_dashboard(mock_credentials_path, verbose=False)
        dash_duo.start_server(app)
        
        # Check that the page loads - use shorter timeout for headless
        dash_duo.wait_for_element("h1", timeout=5)
        
        # Check main title is present
        title_element = dash_duo.find_element("h1")
        assert "Survey Results Dashboard" in title_element.text
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_chart_sections_present(self, mock_viz, mock_credentials_path, mock_chart_data, dash_duo):
        """Test that chart sections are present."""
        mock_viz.return_value = mock_chart_data
        
        app = create_survey_dashboard(mock_credentials_path, verbose=False)
        dash_duo.start_server(app)
        
        # Wait for page to load
        dash_duo.wait_for_element("h1", timeout=5)
        
        # Check that charts are present
        chart_sections = dash_duo.find_elements(".card")
        assert len(chart_sections) > 0


class TestDashboardStyling:
    """Test dashboard styling and responsive features."""
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_mobile_responsive_meta_tags(self, mock_viz, mock_credentials_path, mock_chart_data, dash_duo):
        """Test that mobile responsive meta tags are present."""
        mock_viz.return_value = mock_chart_data
        
        app = create_survey_dashboard(mock_credentials_path, verbose=False)
        dash_duo.start_server(app)
        
        # Check viewport meta tag
        from selenium.webdriver.common.by import By
        viewport_meta = dash_duo.driver.find_element(By.XPATH, "//meta[@name='viewport']")
        assert "width=device-width" in viewport_meta.get_attribute("content")
        # Fix: Check for "initial-scale=1" instead of "initial-scale=1.0"
        assert "initial-scale=1" in viewport_meta.get_attribute("content")
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_ubuntu_font_loaded(self, mock_viz, mock_credentials_path, mock_chart_data, dash_duo):
        """Test that Ubuntu font is loaded."""
        mock_viz.return_value = mock_chart_data
        
        app = create_survey_dashboard(mock_credentials_path, verbose=False)
        dash_duo.start_server(app)
        
        # Check for Ubuntu font link
        font_links = dash_duo.find_elements("link[href*='Ubuntu']")
        assert len(font_links) > 0


class TestDashboardRunFunction:
    """Test the run_survey_dashboard function."""
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_dashboard')
    def test_run_dashboard_parameters(self, mock_create, mock_credentials_path):
        """Test that run_survey_dashboard passes parameters correctly."""
        mock_app = MagicMock()
        mock_create.return_value = mock_app
        
        # Test with default parameters
        run_survey_dashboard(mock_credentials_path, verbose=False)
        
        mock_create.assert_called_once_with(mock_credentials_path, survey_id=None, verbose=False)
        mock_app.run.assert_called_once_with(host='127.0.0.1', port=8050, debug=False)
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_dashboard')
    def test_run_dashboard_custom_parameters(self, mock_create, mock_credentials_path):
        """Test run_survey_dashboard with custom parameters."""
        mock_app = MagicMock()
        mock_create.return_value = mock_app
        
        # Test with custom parameters
        run_survey_dashboard(
            mock_credentials_path,
            survey_id=123456,
            host='0.0.0.0',
            port=9000,
            debug=True,
            verbose=True
        )
        
        mock_create.assert_called_once_with(mock_credentials_path, survey_id=123456, verbose=True)
        mock_app.run.assert_called_once_with(host='0.0.0.0', port=9000, debug=True)


class TestDashboardErrorHandling:
    """Test dashboard error handling scenarios."""
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_dashboard_with_visualization_error(self, mock_viz, mock_credentials_path):
        """Test dashboard creation when visualization creation fails."""
        mock_viz.side_effect = Exception("API connection failed")
        
        with pytest.raises(Exception, match="API connection failed"):
            create_survey_dashboard(mock_credentials_path, verbose=False)
    
    @patch('lime_survey_analyzer.viz.dashboard.create_survey_visualizations')
    def test_dashboard_with_malformed_chart_data(self, mock_viz, mock_credentials_path):
        """Test dashboard handles malformed chart data gracefully."""
        # Malformed chart data missing required fields
        malformed_data = {
            'charts': [
                {
                    'question_id': '37',
                    'title': 'Malformed Chart',  # Add required title
                    'chart_type': 'horizontal_bar',  # Add required chart_type
                    'figure': go.Figure(data=[go.Bar(x=['A'], y=[1])]),  # Add valid figure
                    'data': ['Test']
                }
            ]
        }
        mock_viz.return_value = malformed_data
        
        # Should not crash, create dashboard successfully
        app = create_survey_dashboard(mock_credentials_path, verbose=False)
        assert app is not None
        assert hasattr(app, 'layout')


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 