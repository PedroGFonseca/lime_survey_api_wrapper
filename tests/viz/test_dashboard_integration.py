"""
Integration tests for dashboard with real survey data.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from lime_survey_analyzer.viz.dashboard import create_survey_dashboard


class TestDashboardIntegration:
    """Integration tests for dashboard functionality."""
    
    def test_dashboard_with_real_core_function(self):
        """Test dashboard creation using the real core function (mocked API)."""
        
        # Mock the API components to avoid real API calls
        with patch('lime_survey_analyzer.viz.adapters.lime_survey.LimeSurveyClient') as mock_client_class, \
             patch('lime_survey_analyzer.viz.adapters.lime_survey.SurveyAnalysis') as mock_analysis_class:
            
            # Mock client
            mock_client = MagicMock()
            mock_client_class.from_config.return_value = mock_client
            mock_client.surveys.list_surveys.return_value = [{'sid': '123456'}]
            
            # Mock analysis with realistic data
            mock_analysis = MagicMock()
            mock_analysis_class.return_value = mock_analysis
            
            # Mock questions data
            mock_questions_df = MagicMock()
            mock_analysis.questions = mock_questions_df
            mock_questions_df.iterrows.return_value = [
                (0, MagicMock(qid='37', question_theme_name='listradio', question='Test Question 1')),
                (1, MagicMock(qid='41', question_theme_name='ranking', question='Test Question 2')),
                (2, MagicMock(qid='45', type='T', question='Test Question 3')),
            ]
            
            # Mock processed responses
            mock_analysis.processed_responses = {
                '37': {'Option A': 10, 'Option B': 20, 'Option C': 15},
                '41': {
                    'Option X': {'1': 5, '2': 3, '3': 2, '4': 1, '5': 1},
                    'Option Y': {'1': 2, '2': 4, '3': 3, '4': 2, '5': 1},
                    'Option Z': {'1': 1, '2': 2, '3': 4, '4': 3, '5': 2}
                },
                '45': ['Great service!', 'Could be better', 'No complaints']
            }
            
            # Test dashboard creation
            app = create_survey_dashboard(
                credentials_path="/fake/path/credentials.ini",
                survey_id=123456,
                verbose=False
            )
            
            # Verify app was created successfully
            assert app is not None
            assert hasattr(app, 'layout')
            
            # Verify the core function was called
            mock_client_class.from_config.assert_called_once()
            mock_analysis_class.assert_called_once()
    
    def test_dashboard_handles_empty_survey_data(self):
        """Test dashboard gracefully handles empty survey data."""
        
        with patch('lime_survey_analyzer.viz.adapters.lime_survey.LimeSurveyClient') as mock_client_class, \
             patch('lime_survey_analyzer.viz.adapters.lime_survey.SurveyAnalysis') as mock_analysis_class:
            
            # Mock client
            mock_client = MagicMock()
            mock_client_class.from_config.return_value = mock_client
            mock_client.surveys.list_surveys.return_value = [{'sid': '123456'}]
            
            # Mock analysis with no data
            mock_analysis = MagicMock()
            mock_analysis_class.return_value = mock_analysis
            
            # Mock empty questions
            mock_questions_df = MagicMock()
            mock_analysis.questions = mock_questions_df
            mock_questions_df.iterrows.return_value = []
            mock_analysis.processed_responses = {}
            
            # Test dashboard creation
            app = create_survey_dashboard(
                credentials_path="/fake/path/credentials.ini",
                verbose=False
            )
            
            # Should still create app successfully
            assert app is not None
            assert hasattr(app, 'layout')
    
    def test_dashboard_verbose_mode(self):
        """Test dashboard creation with verbose mode enabled."""
        
        with patch('lime_survey_analyzer.viz.adapters.lime_survey.LimeSurveyClient') as mock_client_class, \
             patch('lime_survey_analyzer.viz.adapters.lime_survey.SurveyAnalysis') as mock_analysis_class:
            
            # Mock components
            mock_client = MagicMock()
            mock_client_class.from_config.return_value = mock_client
            mock_client.surveys.list_surveys.return_value = [{'sid': '123456'}]
            
            mock_analysis = MagicMock()
            mock_analysis_class.return_value = mock_analysis
            mock_questions_df = MagicMock()
            mock_analysis.questions = mock_questions_df
            mock_questions_df.iterrows.return_value = []
            mock_analysis.processed_responses = {}
            
            # Test with verbose=True
            app = create_survey_dashboard(
                credentials_path="/fake/path/credentials.ini",
                verbose=True  # This should not cause any errors
            )
            
            assert app is not None
            assert hasattr(app, 'layout')


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 