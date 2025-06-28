#!/usr/bin/env python3
"""
Integration Tests: Survey Analysis Processing

Tests that the SurveyAnalysis system properly processes mock survey data
through all question handlers and produces correct analytical results.

Focus: Question processing, data transformation, and result accuracy.
"""

import pytest
import pandas as pd
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import numpy as np

# Add source directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'examples'))

# Import components
from enhanced_data_generators import create_enhanced_test_data
from mock_data_dashboard_demo import MockSurveyAnalysis
from lime_survey_analyzer.analyser import get_columns_codes_for_responses_user_input


class TestSurveyAnalysisProcessing:
    """Test that SurveyAnalysis properly processes mock survey data."""
    
    @pytest.fixture(scope="class")
    def mock_analysis(self):
        """Create MockSurveyAnalysis instance with realistic data."""
        mock_data = create_enhanced_test_data(survey_id="ANALYSIS_TEST_333")
        analysis = MockSurveyAnalysis(mock_data, survey_id="ANALYSIS_TEST_333", verbose=False)
        analysis.process_all_questions()
        return analysis
    
    def test_analysis_initialization_with_mock_data(self):
        """Test that MockSurveyAnalysis initializes correctly with mock data."""
        mock_data = create_enhanced_test_data(survey_id="INIT_TEST")
        analysis = MockSurveyAnalysis(mock_data, survey_id="INIT_TEST", verbose=False)
        
        # Verify initialization
        assert analysis.survey_id == "INIT_TEST"
        assert hasattr(analysis, 'questions')
        assert hasattr(analysis, 'options')
        assert hasattr(analysis, 'responses_user_input')
        assert hasattr(analysis, 'response_column_codes')
        
        # Verify data assignment
        assert isinstance(analysis.questions, pd.DataFrame)
        assert isinstance(analysis.options, pd.DataFrame)
        assert isinstance(analysis.responses_user_input, pd.DataFrame)
        assert not analysis.questions.empty
        assert not analysis.responses_user_input.empty
        
        # Verify response column codes mapping exists
        assert hasattr(analysis, 'response_codes_to_question_codes')
        assert isinstance(analysis.response_codes_to_question_codes, dict)

    def test_question_processing_coverage(self, mock_analysis):
        """Test that analysis processes a high percentage of questions successfully."""
        # Get main questions (not sub-questions)
        main_questions = mock_analysis.questions[
            mock_analysis.questions['parent_qid'].fillna('None') == '0'
        ]
        
        total_main_questions = len(main_questions)
        processed_questions = len(mock_analysis.processed_responses)
        
        # Should process most questions successfully
        success_rate = processed_questions / total_main_questions
        assert success_rate >= 0.75, f"Should process ≥75% of questions, got {success_rate:.2%}"
        
        # Verify processed responses exist and are not empty
        assert len(mock_analysis.processed_responses) > 0, "Should have processed responses"
        
        for qid, result in mock_analysis.processed_responses.items():
            assert result is not None, f"Processed result for {qid} should not be None"
            
            # Result should be pandas object
            assert isinstance(result, (pd.Series, pd.DataFrame, dict)), \
                f"Result for {qid} should be pandas Series/DataFrame or dict, got {type(result)}"

    def test_radio_question_processing_accuracy(self, mock_analysis):
        """Test that radio questions are processed correctly."""
        # Find radio questions in processed results
        radio_results = {}
        
        for qid, result in mock_analysis.processed_responses.items():
            qid_str = str(qid)
            question_info = mock_analysis.questions[mock_analysis.questions['qid'] == qid_str]
            
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type in ['listradio', 'image_select-listradio']:
                    radio_results[qid] = result
        
        assert len(radio_results) > 0, "Should have processed radio questions"
        
        # Test radio question result structure
        for qid, result in list(radio_results.items())[:3]:  # Test first 3
            assert isinstance(result, pd.Series), f"Radio question {qid} should return Series"
            assert len(result) > 0, f"Radio question {qid} should have response counts"
            assert result.sum() > 0, f"Radio question {qid} should have total responses"
            
            # Option labels should be meaningful (not just codes)
            option_labels = result.index.tolist()
            meaningful_labels = [label for label in option_labels if len(str(label)) > 2]
            assert len(meaningful_labels) > 0, f"Radio question {qid} should have meaningful option labels"
            
            # Values should be non-negative integers
            assert all(result >= 0), f"Radio question {qid} should have non-negative counts"
            assert all(isinstance(val, (int, np.integer)) for val in result.values), \
                f"Radio question {qid} should have integer counts"

    def test_ranking_question_processing_accuracy(self, mock_analysis):
        """Test that ranking questions are processed correctly."""
        # Find ranking questions in processed results
        ranking_results = {}
        
        for qid, result in mock_analysis.processed_responses.items():
            qid_str = str(qid)
            question_info = mock_analysis.questions[mock_analysis.questions['qid'] == qid_str]
            
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type == 'ranking':
                    ranking_results[qid] = result
        
        assert len(ranking_results) > 0, "Should have processed ranking questions"
        
        # Test ranking question result structure
        for qid, result in list(ranking_results.items())[:3]:  # Test first 3
            assert isinstance(result, pd.DataFrame), f"Ranking question {qid} should return DataFrame"
            assert not result.empty, f"Ranking question {qid} should have data"
            
            # Should have multiple columns (options) and rows (ranks)
            assert result.shape[0] > 1, f"Ranking question {qid} should have multiple ranks"
            assert result.shape[1] > 1, f"Ranking question {qid} should have multiple options"
            
            # Column names should be meaningful option text
            option_names = result.columns.tolist()
            meaningful_options = [opt for opt in option_names if len(str(opt)) > 2]
            assert len(meaningful_options) > 0, f"Ranking question {qid} should have meaningful option names"
            
            # Values should be non-negative numbers
            numeric_values = result.select_dtypes(include=[np.number])
            assert not numeric_values.empty, f"Ranking question {qid} should have numeric values"
            assert (numeric_values >= 0).all().all(), f"Ranking question {qid} should have non-negative values"

    def test_text_question_processing_accuracy(self, mock_analysis):
        """Test that text questions are processed correctly."""
        # Find text questions in processed results
        text_results = {}
        
        for qid, result in mock_analysis.processed_responses.items():
            qid_str = str(qid)
            question_info = mock_analysis.questions[mock_analysis.questions['qid'] == qid_str]
            
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type in ['longfreetext', 'shortfreetext', 'numerical']:
                    text_results[qid] = result
        
        assert len(text_results) > 0, "Should have processed text questions"
        
        # Test text question result structure
        for qid, result in list(text_results.items())[:3]:  # Test first 3
            assert isinstance(result, pd.Series), f"Text question {qid} should return Series"
            
            # Should contain text responses (strings)
            text_responses = result.dropna()
            if len(text_responses) > 0:
                assert all(isinstance(resp, str) for resp in text_responses.values), \
                    f"Text question {qid} should contain string responses"
                
                # Responses should be non-empty
                non_empty_responses = [resp for resp in text_responses.values if len(resp.strip()) > 0]
                assert len(non_empty_responses) > 0, f"Text question {qid} should have non-empty responses"

    def test_multiple_choice_question_processing_accuracy(self, mock_analysis):
        """Test that multiple choice questions are processed correctly."""
        # Find multiple choice questions in processed results
        mc_results = {}
        
        for qid, result in mock_analysis.processed_responses.items():
            qid_str = str(qid)
            question_info = mock_analysis.questions[mock_analysis.questions['qid'] == qid_str]
            
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type in ['multiplechoice', 'image_select-multiplechoice']:
                    mc_results[qid] = result
        
        if len(mc_results) > 0:  # Only test if we have multiple choice questions
            # Test multiple choice result structure
            for qid, result in list(mc_results.items())[:2]:  # Test first 2
                assert isinstance(result, pd.DataFrame), f"Multiple choice question {qid} should return DataFrame"
                
                if not result.empty:
                    # Should have expected columns
                    expected_cols = ['option_text', 'absolute_counts', 'response_rates']
                    for col in expected_cols:
                        assert col in result.columns, f"Multiple choice {qid} should have {col} column"
                    
                    # Values should be realistic
                    counts = result['absolute_counts']
                    rates = result['response_rates']
                    
                    assert all(counts >= 0), f"Multiple choice {qid} should have non-negative counts"
                    assert all(rates >= 0) and all(rates <= 1), f"Multiple choice {qid} should have valid rates (0-1)"

    def test_error_handling_for_unsupported_questions(self, mock_analysis):
        """Test that unsupported question types are handled gracefully."""
        # Check that error log exists and contains reasonable information
        assert hasattr(mock_analysis, 'fail_message_log')
        
        if mock_analysis.fail_message_log:
            # Errors should be Exception objects
            for qid, error in mock_analysis.fail_message_log.items():
                assert isinstance(error, Exception), f"Error for {qid} should be Exception object"
                
                # Error should have meaningful message
                error_msg = str(error)
                assert len(error_msg) > 0, f"Error for {qid} should have message"
        
        # Total failures should be reasonable (< 25% of questions)
        total_questions = len(mock_analysis.questions[
            mock_analysis.questions['parent_qid'].fillna('None') == '0'
        ])
        failure_rate = len(mock_analysis.fail_message_log) / total_questions
        assert failure_rate < 0.25, f"Failure rate should be <25%, got {failure_rate:.2%}"

    def test_response_column_mapping_accuracy(self, mock_analysis):
        """Test that response columns are mapped correctly to questions."""
        # Verify response column codes were created
        assert hasattr(mock_analysis, 'response_column_codes')
        assert isinstance(mock_analysis.response_column_codes, pd.DataFrame)
        assert not mock_analysis.response_column_codes.empty
        
        # Verify mapping structure
        assert 'question_code' in mock_analysis.response_column_codes.columns
        assert 'appendage' in mock_analysis.response_column_codes.columns
        
        # Test that mapped question codes exist in questions
        mapped_codes = mock_analysis.response_column_codes['question_code'].unique()
        question_codes = mock_analysis.questions['title'].unique()
        
        # Most mapped codes should exist in questions
        valid_mappings = set(mapped_codes) & set(question_codes)
        mapping_rate = len(valid_mappings) / len(mapped_codes)
        assert mapping_rate >= 0.8, f"Mapping rate should be ≥80%, got {mapping_rate:.2%}"
        
        # Test specific column patterns
        response_cols = mock_analysis.responses_user_input.columns.tolist()
        
        # Should map simple question codes (exclude metadata columns like 'id')
        metadata_cols = ['id', 'submitdate', 'lastpage', 'startlanguage', 'seed', 'startdate', 'datestamp', 'refurl']
        simple_cols = [col for col in response_cols if len(col) <= 15 and '[' not in col and col not in metadata_cols]
        for col in simple_cols[:5]:  # Test first 5
            if col in mock_analysis.response_column_codes.index:
                mapped_code = mock_analysis.response_column_codes.loc[col, 'question_code']
                assert mapped_code in question_codes, f"Simple column {col} should map to valid question code"

    def test_data_consistency_after_processing(self, mock_analysis):
        """Test that data remains consistent after processing."""
        # Verify original data structures are preserved
        assert isinstance(mock_analysis.questions, pd.DataFrame)
        assert isinstance(mock_analysis.responses_user_input, pd.DataFrame)
        assert not mock_analysis.questions.empty
        assert not mock_analysis.responses_user_input.empty
        
        # Verify processed responses link to valid questions
        for qid in mock_analysis.processed_responses.keys():
            qid_str = str(qid)
            question_exists = qid_str in mock_analysis.questions['qid'].values
            assert question_exists, f"Processed question {qid} should exist in questions data"
        
        # Verify data types are preserved
        assert mock_analysis.questions['qid'].dtype == 'object'
        assert mock_analysis.questions['question_theme_name'].dtype == 'object'


class TestQuestionHandlerAccuracy:
    """Test specific question handler methods for accuracy."""
    
    @pytest.fixture
    def analysis_with_specific_questions(self):
        """Create analysis with specific question types for targeted testing."""
        mock_data = create_enhanced_test_data(survey_id="HANDLER_TEST_444")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        
        # Process questions individually for testing
        return analysis, mock_data
    
    def test_get_max_answers_functionality(self, analysis_with_specific_questions):
        """Test that _get_max_answers method works correctly."""
        analysis, mock_data = analysis_with_specific_questions
        
        # Find a ranking question to test
        ranking_questions = analysis.questions[analysis.questions['question_theme_name'] == 'ranking']
        
        if not ranking_questions.empty:
            test_qid = ranking_questions.iloc[0]['qid']
            
            # Test max answers retrieval
            max_answers = analysis._get_max_answers(test_qid)
            
            assert isinstance(max_answers, int), "Max answers should be integer"
            assert max_answers > 0, "Max answers should be positive"
            assert max_answers <= 1000000, "Max answers should be reasonable"
    
    def test_question_code_retrieval_accuracy(self, analysis_with_specific_questions):
        """Test that question codes are retrieved correctly."""
        analysis, mock_data = analysis_with_specific_questions
        
        # Test question code retrieval for various questions
        for _, question in analysis.questions.head(5).iterrows():
            qid = question['qid']
            expected_code = question['title']
            
            retrieved_code = analysis._get_question_code(qid)
            assert retrieved_code == expected_code, f"Question code for {qid} should match title"
    
    def test_response_codes_for_question_accuracy(self, analysis_with_specific_questions):
        """Test that response codes are retrieved correctly for questions."""
        analysis, mock_data = analysis_with_specific_questions
        
        # Set up response column codes
        analysis._setup_response_column_codes()
        
        # Test retrieval for questions that have response data
        question_codes = analysis.response_column_codes['question_code'].unique()
        
        for question_code in question_codes[:3]:  # Test first 3
            try:
                response_codes = analysis._get_response_codes_for_question(question_code)
                
                assert isinstance(response_codes, pd.DataFrame), "Should return DataFrame"
                assert not response_codes.empty, f"Should have response codes for {question_code}"
                assert 'question_code' in response_codes.columns, "Should have question_code column"
                assert 'appendage' in response_codes.columns, "Should have appendage column"
                
                # All entries should match the requested question code
                assert all(response_codes['question_code'] == question_code), \
                    f"All response codes should match question {question_code}"
                    
            except ValueError:
                # Some questions might not have response codes - this is acceptable
                pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 