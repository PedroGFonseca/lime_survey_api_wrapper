#!/usr/bin/env python3
"""
Unit tests for ranking question functionality and max_answers handling.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from lime_survey_analyzer.analyser import SurveyAnalysis


class TestGetMaxAnswers:
    """Test the _get_max_answers method and its edge cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analysis = SurveyAnalysis("111111", verbose=False)
        self.analysis.api = Mock()
        
    def test_get_max_answers_valid_integer(self):
        """Test _get_max_answers with valid integer string."""
        # Mock API response
        mock_props = {
            'attributes': {
                'max_answers': '5'
            }
        }
        self.analysis.api.questions.get_question_properties.return_value = mock_props
        
        # Mock cache manager
        with patch('lime_survey_analyzer.analyser.get_cache_manager') as mock_cache_manager:
            mock_cache = Mock()
            mock_cache.get_cached.return_value = None  # Cache miss
            mock_cache_manager.return_value = mock_cache
            
            result = self.analysis._get_max_answers("222222")
            
            assert result == 5
            assert isinstance(result, int)
            mock_cache.set_cached.assert_called_once_with(5, '_get_max_answers', '111111', '222222')
    
    def test_get_max_answers_empty_string(self):
        """Test _get_max_answers with empty string (should default to 1000000)."""
        # Mock API response
        mock_props = {
            'attributes': {
                'max_answers': ''
            }
        }
        self.analysis.api.questions.get_question_properties.return_value = mock_props
        
        # Mock cache manager
        with patch('lime_survey_analyzer.analyser.get_cache_manager') as mock_cache_manager:
            mock_cache = Mock()
            mock_cache.get_cached.return_value = None  # Cache miss
            mock_cache_manager.return_value = mock_cache
            
            result = self.analysis._get_max_answers("test_question_id")
            
            assert result == 1000000
            assert isinstance(result, int)
    
    def test_get_max_answers_none_value(self):
        """Test _get_max_answers with None value (should default to 1000000)."""
        # Mock API response
        mock_props = {
            'attributes': {
                'max_answers': None
            }
        }
        self.analysis.api.questions.get_question_properties.return_value = mock_props
        
        # Mock cache manager
        with patch('lime_survey_analyzer.analyser.get_cache_manager') as mock_cache_manager:
            mock_cache = Mock()
            mock_cache.get_cached.return_value = None  # Cache miss
            mock_cache_manager.return_value = mock_cache
            
            result = self.analysis._get_max_answers("test_question_id")
            
            assert result == 1000000
            assert isinstance(result, int)
    
    def test_get_max_answers_invalid_string(self):
        """Test _get_max_answers with invalid string (should default to 1000000)."""
        # Mock API response
        mock_props = {
            'attributes': {
                'max_answers': 'invalid_number'
            }
        }
        self.analysis.api.questions.get_question_properties.return_value = mock_props
        
        # Mock cache manager
        with patch('lime_survey_analyzer.analyser.get_cache_manager') as mock_cache_manager:
            mock_cache = Mock()
            mock_cache.get_cached.return_value = None  # Cache miss
            mock_cache_manager.return_value = mock_cache
            
            result = self.analysis._get_max_answers("test_question_id")
            
            assert result == 1000000
            assert isinstance(result, int)
    
    def test_get_max_answers_cache_hit_valid(self):
        """Test _get_max_answers with valid cached value."""
        # Mock cache manager
        with patch('lime_survey_analyzer.analyser.get_cache_manager') as mock_cache_manager:
            mock_cache = Mock()
            mock_cache.get_cached.return_value = 10  # Cache hit
            mock_cache_manager.return_value = mock_cache
            
            result = self.analysis._get_max_answers("test_question_id")
            
            assert result == 10
            assert isinstance(result, int)
            # API should not be called on cache hit
            self.analysis.api.questions.get_question_properties.assert_not_called()
    
    def test_get_max_answers_cache_hit_invalid(self):
        """Test _get_max_answers with invalid cached value (should fetch fresh)."""
        # Mock API response for fresh fetch
        mock_props = {
            'attributes': {
                'max_answers': '7'
            }
        }
        self.analysis.api.questions.get_question_properties.return_value = mock_props
        
        # Mock cache manager
        with patch('lime_survey_analyzer.analyser.get_cache_manager') as mock_cache_manager:
            mock_cache = Mock()
            mock_cache.get_cached.return_value = 'invalid_cached_value'  # Invalid cache
            mock_cache_manager.return_value = mock_cache
            
            result = self.analysis._get_max_answers("test_question_id")
            
            assert result == 7
            assert isinstance(result, int)
            # API should be called to fetch fresh data
            self.analysis.api.questions.get_question_properties.assert_called_once()


class TestRankingQuestionProcessing:
    """Test ranking question processing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analysis = SurveyAnalysis("111111", verbose=False)
        self.analysis.api = Mock()
        
        # Mock required components
        self.analysis.questions = pd.DataFrame({
            'qid': ['5', '10'],
            'title': ['G01Q01', 'G02Q01'],
            'question': ['Test ranking question', 'Another test question']
        })
        
        self.analysis.options = pd.DataFrame({
            'qid': ['5', '5', '5'],
            'option_code': ['AO01', 'AO02', 'AO03'],
            'answer': ['Option 1', 'Option 2', 'Option 3'],
            'question_code': ['G01Q01', 'G01Q01', 'G01Q01']
        })
        
        self.analysis.response_column_codes = pd.DataFrame({
            'question_code': ['G01Q01', 'G01Q01', 'G01Q01'],
            'appendage': ['1', '2', '3']
        }, index=['G01Q01[1]', 'G01Q01[2]', 'G01Q01[3]'])
        
        self.analysis.responses_user_input = pd.DataFrame({
            'G01Q01[1]': ['AO01', 'AO02', 'AO01'],
            'G01Q01[2]': ['AO02', 'AO01', 'AO03'],
            'G01Q01[3]': ['AO03', 'AO03', 'AO02']
        })
    
    def test_process_ranking_question_with_max_answers(self):
        """Test processing ranking question with specific max_answers."""
        # Mock _get_max_answers to return 2
        with patch.object(self.analysis, '_get_max_answers', return_value=2):
            with patch.object(self.analysis, '_get_question_code', return_value='G01Q01'):
                with patch('lime_survey_analyzer.analyser._map_names_to_rank_responses') as mock_map:
                    # Create a mock result DataFrame with more rows than max_answers
                    mock_df = pd.DataFrame({
                        'Option 1': [2, 1, 0, 0, 0],
                        'Option 2': [1, 1, 1, 0, 0],
                        'Option 3': [0, 1, 2, 0, 0]
                    })
                    mock_map.return_value = mock_df
                    
                    self.analysis._process_ranking_question('5')
                    
                    # Check that result was limited to max_answers (2 rows)
                    result = self.analysis.processed_responses['5']
                    assert result.shape[0] == 2  # Limited to max_answers
                    assert result.shape[1] == 3  # All columns preserved
    
    def test_process_ranking_question_unlimited(self):
        """Test processing ranking question with unlimited max_answers."""
        # Mock _get_max_answers to return 1000000 (unlimited)
        with patch.object(self.analysis, '_get_max_answers', return_value=1000000):
            with patch.object(self.analysis, '_get_question_code', return_value='G01Q01'):
                with patch('lime_survey_analyzer.analyser._map_names_to_rank_responses') as mock_map:
                    # Create a mock result DataFrame
                    mock_df = pd.DataFrame({
                        'Option 1': [2, 1, 0],
                        'Option 2': [1, 1, 1],
                        'Option 3': [0, 1, 2]
                    })
                    mock_map.return_value = mock_df
                    
                    self.analysis._process_ranking_question('5')
                    
                    # Check that all rows are preserved (no limiting)
                    result = self.analysis.processed_responses['5']
                    assert result.shape[0] == 3  # All rows preserved
                    assert result.shape[1] == 3  # All columns preserved


class TestPandasIlocSafety:
    """Test that pandas iloc slicing works safely with large indices."""
    
    def test_iloc_with_large_index(self):
        """Test that iloc[:large_number, :] works safely."""
        # Create small DataFrame
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [4, 5, 6]
        })
        
        # Test with large index (should return all rows)
        result = df.iloc[:1000000, :]
        
        assert result.shape == (3, 2)  # Same as original
        pd.testing.assert_frame_equal(result, df)
    
    def test_iloc_with_exact_index(self):
        """Test that iloc[:exact_length, :] works correctly."""
        # Create DataFrame
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [6, 7, 8, 9, 10]
        })
        
        # Test with exact length
        result = df.iloc[:5, :]
        pd.testing.assert_frame_equal(result, df)
        
        # Test with smaller index
        result_partial = df.iloc[:3, :]
        expected = df.head(3)
        pd.testing.assert_frame_equal(result_partial, expected)


if __name__ == '__main__':
    pytest.main([__file__]) 