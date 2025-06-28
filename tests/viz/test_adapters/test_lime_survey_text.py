"""
Tests for text question handling in LimeSurvey adapter.
"""

import pytest
from unittest.mock import Mock, patch
from src.lime_survey_analyzer.viz.adapters.lime_survey import extract_question_data
import pandas as pd


class TestTextQuestionExtraction:
    """Test text question data extraction from LimeSurvey."""
    
    def setup_method(self):
        """Set up mock analysis object for tests."""
        self.mock_analysis = Mock()
        self.mock_analysis.questions = pd.DataFrame([
            {
                'qid': 57,
                'type': 'Q',
                'question_theme_name': '',
                'question': '<p>Freguesia e concelho de residência</p>'
            },
            {
                'qid': 75,
                'type': 'S',
                'question_theme_name': '',
                'question': 'Se respondeu "outro", qual?'
            },
            {
                'qid': 96,
                'type': 'T',
                'question_theme_name': '',
                'question': 'ID storage'
            }
        ])
        self.mock_analysis.processed_responses = {}
    
    def test_extract_multiple_short_text_question(self):
        """Test extraction of multiple short text question (type Q)."""
        # Mock the processing method
        mock_responses = {
            'Freguesia': ['Lisboa', 'Porto', 'Coimbra'],
            'Concelho': ['Lisboa', 'Porto', 'Coimbra']
        }
        self.mock_analysis._process_multiple_short_text.return_value = None
        self.mock_analysis.processed_responses[57] = mock_responses
        
        result = extract_question_data(self.mock_analysis, 57, verbose=True)
        
        assert result is not None
        assert result['chart_type'] == 'multiple_short_text'
        assert result['data'] == mock_responses
        assert result['title'] == 'Freguesia e concelho de residência'  # HTML tags cleaned
        assert result['question_id'] == 57
        assert result['question_type'] == 'Q'
        
        # Verify the processing method was called
        self.mock_analysis._process_multiple_short_text.assert_called_once_with(57)
    
    def test_extract_short_text_question(self):
        """Test extraction of short text question (type S)."""
        mock_responses = ['Response 1', 'Response 2', 'Response 3']
        self.mock_analysis._process_text_question.return_value = None
        self.mock_analysis.processed_responses[75] = mock_responses
        
        result = extract_question_data(self.mock_analysis, 75, verbose=True)
        
        assert result is not None
        assert result['chart_type'] == 'text_responses'
        assert result['data'] == mock_responses
        assert result['title'] == 'Se respondeu "outro", qual?'
        assert result['question_id'] == 75
        assert result['question_type'] == 'S'
        
        # Verify the processing method was called
        self.mock_analysis._process_text_question.assert_called_once_with(75)
    
    def test_extract_long_text_question(self):
        """Test extraction of long text question (type T)."""
        mock_responses = ['Long response 1', 'Long response 2']
        self.mock_analysis._process_text_question.return_value = None
        self.mock_analysis.processed_responses[96] = mock_responses
        
        result = extract_question_data(self.mock_analysis, 96, verbose=True)
        
        assert result is not None
        assert result['chart_type'] == 'text_responses'
        assert result['data'] == mock_responses
        assert result['title'] == 'ID storage'
        assert result['question_id'] == 96
        assert result['question_type'] == 'T'
    
    def test_extract_question_not_found(self):
        """Test extraction with non-existent question ID."""
        with pytest.raises(ValueError, match="Question 999 not found"):
            extract_question_data(self.mock_analysis, 999)
    
    def test_extract_multiple_short_text_processing_error(self):
        """Test handling of processing errors for multiple short text."""
        self.mock_analysis._process_multiple_short_text.side_effect = Exception("Processing failed")
        
        result = extract_question_data(self.mock_analysis, 57, verbose=True)
        
        assert result is None
    
    def test_extract_text_question_processing_error(self):
        """Test handling of processing errors for text questions."""
        self.mock_analysis._process_text_question.side_effect = Exception("Processing failed")
        
        result = extract_question_data(self.mock_analysis, 75, verbose=True)
        
        assert result is None
    
    def test_extract_unsupported_question_type(self):
        """Test extraction of unsupported question type."""
        # Add an unsupported question type
        unsupported_question = pd.DataFrame([{
            'qid': 999,
            'type': 'X',  # Unsupported type
            'question_theme_name': '',
            'question': 'Unsupported question'
        }])
        self.mock_analysis.questions = pd.concat([self.mock_analysis.questions, unsupported_question])
        
        result = extract_question_data(self.mock_analysis, 999, verbose=True)
        
        assert result is None
    
    def test_extract_question_verbose_output(self):
        """Test that verbose mode produces expected output."""
        mock_responses = ['Response 1']
        self.mock_analysis._process_text_question.return_value = None
        self.mock_analysis.processed_responses[75] = mock_responses
        
        # Test with verbose=True (should not raise errors)
        result = extract_question_data(self.mock_analysis, 75, verbose=True)
        assert result is not None
        
        # Test with verbose=False (should also work)
        result = extract_question_data(self.mock_analysis, 75, verbose=False)
        assert result is not None


class TestTextQuestionIntegration:
    """Integration tests for text question handling."""
    
    def test_html_tag_cleaning_integration(self):
        """Test that HTML tags are properly cleaned from question titles."""
        mock_analysis = Mock()
        mock_analysis.questions = pd.DataFrame([{
            'qid': 57,
            'type': 'Q',
            'question_theme_name': '',
            'question': '<p dir="ltr">Freguesia e concelho de <strong>residência</strong></p>'
        }])
        mock_analysis.processed_responses = {57: {'Sub1': ['Response']}}
        mock_analysis._process_multiple_short_text.return_value = None
        
        result = extract_question_data(mock_analysis, 57)
        
        assert result is not None
        # HTML tags should be cleaned
        assert '<p' not in result['title']
        assert '<strong>' not in result['title']
        assert 'Freguesia e concelho de residência' in result['title']
    
    def test_question_type_priority_handling(self):
        """Test that question type detection works correctly."""
        mock_analysis = Mock()
        
        # Test multiple short text (type Q) takes precedence over theme
        mock_analysis.questions = pd.DataFrame([{
            'qid': 1,
            'type': 'Q',
            'question_theme_name': 'listradio',  # This should be ignored for type Q
            'question': 'Multiple short text question'
        }])
        mock_analysis.processed_responses = {1: {'Sub1': ['Response']}}
        mock_analysis._process_multiple_short_text.return_value = None
        
        result = extract_question_data(mock_analysis, 1)
        
        assert result is not None
        assert result['chart_type'] == 'multiple_short_text'  # Should be multiple_short_text, not horizontal_bar
    
    def test_empty_responses_handling(self):
        """Test handling of empty responses from processing."""
        mock_analysis = Mock()
        mock_analysis.questions = pd.DataFrame([{
            'qid': 1,
            'type': 'S',
            'question_theme_name': '',
            'question': 'Text question'
        }])
        
        # Test with empty list
        mock_analysis.processed_responses = {1: []}
        mock_analysis._process_text_question.return_value = None
        
        result = extract_question_data(mock_analysis, 1)
        
        assert result is not None
        assert result['data'] == []
        
        # Test with None
        mock_analysis.processed_responses = {1: None}
        
        result = extract_question_data(mock_analysis, 1)
        
        assert result is not None
        assert result['data'] is None 