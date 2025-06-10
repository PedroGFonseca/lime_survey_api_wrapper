#!/usr/bin/env python3
"""
Test Suite for Current Handler Behavior

Captures exact current behavior of all question handlers to ensure
no regression during refactoring. Uses synthetic data generators
to avoid dependency on real API calls.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from lime_survey_analyzer.analyser import SurveyAnalysis
from tests.data_generators import SurveyDataGenerator, create_single_question_test_data


class TestCurrentHandlerBehavior:
    """Test suite that captures exact current behavior of handlers"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.generator = SurveyDataGenerator(survey_id="TEST_SURVEY", num_responses=100)
        
    def _create_mock_survey_analysis(self, questions_data, options_data, responses_data):
        """Create a mock SurveyAnalysis instance with test data"""
        survey = SurveyAnalysis("TEST_SURVEY")
        
        # Mock the setup to avoid API calls
        survey.api = Mock()
        
        # Convert mock data to DataFrames matching expected format
        questions_list = []
        for q in questions_data:
            questions_list.append({
                'qid': q.qid,
                'title': q.title,
                'question': q.question,
                'question_theme_name': q.question_theme_name,
                'other': q.other,
                'mandatory': q.mandatory,
                'parent_qid': q.parent_qid,
                'gid': q.gid,
                'question_order': q.question_order
            })
        survey.questions = pd.DataFrame(questions_list)
        
        if options_data:
            options_list = []
            for opt in options_data:
                options_list.append({
                    'qid': opt.qid,
                    'option_code': opt.option_code,
                    'answer': opt.answer,
                    'option_order': opt.option_order,
                    'question_code': opt.question_code
                })
            survey.options = pd.DataFrame(options_list)
        else:
            survey.options = pd.DataFrame()
        
        survey.responses_user_input = responses_data.drop('id', axis=1) if 'id' in responses_data.columns else responses_data
        survey.responses_metadata = pd.DataFrame({'id': responses_data.get('id', [])})
        
        # Set up response column codes (needed for some handlers)
        from lime_survey_analyzer.analyser import get_columns_codes_for_responses_user_input
        survey.response_column_codes = get_columns_codes_for_responses_user_input(survey.responses_user_input)
        
        # Initialize processed_responses dict
        survey.processed_responses = {}
        
        return survey


class TestRadioQuestionHandler(TestCurrentHandlerBehavior):
    """Test _process_radio_question behavior"""
    
    def test_radio_question_stores_value_counts_series(self):
        """Verify _process_radio_question stores pd.Series with value counts in processed_responses"""
        # Generate test data
        question, options, responses = self.generator.generate_radio_question_data(
            question_id="Q001", question_code="satisfaction", question_text="How satisfied?"
        )
        
        # Create mock survey
        survey = self._create_mock_survey_analysis([question], options, responses)
        
        # Process the question (stores result, doesn't return)
        survey._process_radio_question("Q001")
        
        # Verify result is stored in processed_responses
        assert "Q001" in survey.processed_responses, "Result should be stored in processed_responses"
        result = survey.processed_responses["Q001"]
        
        # Verify output format
        assert isinstance(result, pd.Series), "Radio question should store pd.Series"
        assert result.name is None or isinstance(result.name, str), "Series should have proper name"
        assert all(isinstance(idx, str) for idx in result.index), "Index should contain option text (strings)"
        assert all(isinstance(val, (int, np.integer)) for val in result.values), "Values should be counts (integers)"
        
        # Verify content makes sense
        assert len(result) >= 3, "Should have at least 3 response categories"
        assert len(result) <= 10, "Should have reasonable number of categories"
        assert result.sum() <= 100, "Total counts should not exceed total responses"
        
        # Verify option text mapping occurred (not just codes)
        expected_texts = ["Very Dissatisfied", "Dissatisfied", "Neutral", "Satisfied", "Very Satisfied"]
        
        # Allow for additional categories like NaN handling 
        valid_categories = 0
        for idx in result.index:
            if idx in expected_texts or idx in ["Other", "nan", str(np.nan), "n"]:
                valid_categories += 1
        
        assert valid_categories >= 3, f"Should have at least 3 valid categories, got indices: {list(result.index)}"
    
    def test_radio_question_handles_missing_data(self):
        """Verify radio questions handle missing responses correctly"""
        question, options, responses = self.generator.generate_radio_question_data()
        
        # Add more missing data
        responses_copy = responses.copy()
        responses_copy.loc[responses_copy.sample(20).index, 'satisfaction'] = np.nan
        
        survey = self._create_mock_survey_analysis([question], options, responses_copy)
        survey._process_radio_question("Q001")
        
        result = survey.processed_responses["Q001"]
        
        # Should still return valid Series, NaN values should be excluded from counts
        assert isinstance(result, pd.Series)
        assert result.sum() < 100  # Less than total responses due to missing data


class TestMultipleChoiceHandler(TestCurrentHandlerBehavior):
    """Test _process_multiple_choice_question behavior"""
    
    def test_multiple_choice_stores_dataframe_with_specific_columns(self):
        """Verify _process_multiple_choice_question stores DataFrame with expected columns"""
        parent_question, sub_questions, responses = self.generator.generate_multiple_choice_data(
            question_id="Q002", question_code="features", question_text="Which features?"
        )
        
        all_questions = [parent_question] + sub_questions
        survey = self._create_mock_survey_analysis(all_questions, [], responses)
        
        survey._process_multiple_choice_question("Q002")
        
        result = survey.processed_responses["Q002"]
        
        # Verify output format
        assert isinstance(result, pd.DataFrame), "Multiple choice should store DataFrame"
        
        expected_columns = ['option_text', 'absolute_counts', 'response_rates']
        assert list(result.columns) == expected_columns, f"Expected columns {expected_columns}, got {list(result.columns)}"
        
        # Verify column types
        assert all(isinstance(text, str) for text in result['option_text']), "option_text should be strings"
        assert all(isinstance(count, (int, np.integer)) for count in result['absolute_counts']), "absolute_counts should be integers"
        assert all(isinstance(rate, (float, np.floating)) for rate in result['response_rates']), "response_rates should be floats"
        
        # Verify data ranges
        assert len(result) == 3, "Should have 3 options"
        assert all(result['absolute_counts'] >= 0), "Counts should be non-negative"
        assert all(0 <= rate <= 1 for rate in result['response_rates']), "Response rates should be between 0 and 1"


class TestRankingQuestionHandler(TestCurrentHandlerBehavior):
    """Test _process_ranking_question behavior"""
    
    def test_ranking_question_stores_dataframe_matrix(self):
        """Verify _process_ranking_question stores DataFrame with rank matrix"""
        question, options, responses = self.generator.generate_ranking_data(
            question_id="Q003", question_code="priorities", question_text="Rank priorities"
        )
        
        survey = self._create_mock_survey_analysis([question], options, responses)
        
        # Mock _get_max_answers to return expected value
        survey._get_max_answers = Mock(return_value=4)
        
        survey._process_ranking_question("Q003")
        
        result = survey.processed_responses["Q003"]
        
        # Verify output format
        assert isinstance(result, pd.DataFrame), "Ranking should store DataFrame"
        
        # Verify dimensions
        assert len(result) == 4, "Should have 4 rank positions (max_answers)"
        assert len(result.columns) == 4, "Should have 4 options to rank"
        
        # Verify index (rank positions)
        expected_ranks = list(range(1, 5))  # 1, 2, 3, 4
        assert list(result.index) == expected_ranks, f"Expected ranks {expected_ranks}, got {list(result.index)}"
        
        # Verify column names are human-readable (mapped from codes)
        expected_options = ["Quality", "Price", "Speed", "Support"]
        for col in result.columns:
            assert col in expected_options, f"Unexpected option name: {col}"


class TestTextQuestionHandler(TestCurrentHandlerBehavior):
    """Test _process_text_question behavior"""
    
    def test_text_question_stores_series_of_responses(self):
        """Verify _process_text_question stores pd.Series of actual responses"""
        question, responses = self.generator.generate_text_data(
            question_id="Q004", question_code="feedback", question_text="Feedback"
        )
        
        survey = self._create_mock_survey_analysis([question], [], responses)
        
        survey._process_text_question("Q004")
        
        result = survey.processed_responses["Q004"]
        
        # Verify output format
        assert isinstance(result, pd.Series), "Text question should store pd.Series"
        
        # Verify content
        assert all(isinstance(response, str) for response in result.values), "All responses should be strings"
        assert len(result) <= 100, "Should not exceed total responses"
        
        # Verify dropna() was applied (no NaN values)
        assert not result.isna().any(), "Should not contain NaN values (dropna applied)"


class TestArrayQuestionHandler(TestCurrentHandlerBehavior):
    """Test _process_array_question behavior"""
    
    def test_array_question_stores_dataframe_with_mapped_responses(self):
        """Verify _process_array_question stores DataFrame with human-readable responses"""
        parent_question, sub_questions, responses = self.generator.generate_array_data(
            question_id="Q005", question_code="trends", question_text="How have these changed?"
        )
        
        all_questions = [parent_question] + sub_questions
        survey = self._create_mock_survey_analysis(all_questions, [], responses)
        
        survey._process_array_question("Q005")
        
        result = survey.processed_responses["Q005"]
        
        # Verify output format
        assert isinstance(result, pd.DataFrame), "Array question should store DataFrame"
        
        # Verify dimensions
        assert len(result) <= 100, "Should not exceed number of responses"
        assert len(result.columns) == 3, "Should have 3 sub-questions"
        
        # Verify column names are sub-question IDs
        expected_columns = ["Q005SQ001", "Q005SQ002", "Q005SQ003"]
        for col in result.columns:
            assert col in expected_columns, f"Unexpected column: {col}"


class TestMultipleShortTextHandler(TestCurrentHandlerBehavior):
    """Test _process_multiple_short_text behavior"""
    
    def test_multiple_short_text_stores_dict_of_series(self):
        """Verify _process_multiple_short_text stores dict with question titles as keys"""
        parent_question, sub_questions, responses = self.generator.generate_multiple_short_text_data(
            question_id="Q006", question_code="contact", question_text="Contact Info"
        )
        
        all_questions = [parent_question] + sub_questions
        survey = self._create_mock_survey_analysis(all_questions, [], responses)
        
        survey._process_multiple_short_text("Q006")
        
        result = survey.processed_responses["Q006"]
        
        # Verify output format
        assert isinstance(result, dict), "Multiple short text should store dict"
        
        # Verify keys are human-readable question titles
        expected_titles = ["First Name", "Last Name", "Email"]
        assert len(result) == 3, "Should have 3 sub-questions"
        for title in result.keys():
            assert title in expected_titles, f"Unexpected title: {title}"
        
        # Verify values are Series
        for title, series in result.items():
            assert isinstance(series, pd.Series), f"Value for '{title}' should be pd.Series"


class TestHandlerIntegration(TestCurrentHandlerBehavior):
    """Test integration behavior and edge cases"""
    
    def test_all_handlers_work_with_generated_data(self):
        """Integration test: verify all handlers work with generated data"""
        # Generate full survey data
        full_data = self.generator.generate_full_survey_data()
        
        # Create comprehensive mock survey
        survey = SurveyAnalysis("TEST_SURVEY")
        survey.api = Mock()
        
        # Convert questions to DataFrame
        questions_list = []
        for q in full_data['questions']:
            questions_list.append({
                'qid': q.qid,
                'title': q.title,
                'question': q.question,
                'question_theme_name': q.question_theme_name,
                'other': q.other,
                'mandatory': q.mandatory,
                'parent_qid': q.parent_qid,
                'gid': q.gid,
                'question_order': q.question_order
            })
        survey.questions = pd.DataFrame(questions_list)
        
        # Convert options to DataFrame
        if full_data['options']:
            options_list = []
            for opt in full_data['options']:
                options_list.append({
                    'qid': opt.qid,
                    'option_code': opt.option_code,
                    'answer': opt.answer,
                    'option_order': opt.option_order,
                    'question_code': opt.question_code
                })
            survey.options = pd.DataFrame(options_list)
        else:
            survey.options = pd.DataFrame()
        
        # Set up responses
        survey.responses_user_input = full_data['responses'].drop('id', axis=1)
        survey.responses_metadata = pd.DataFrame({'id': full_data['responses']['id']})
        
        from lime_survey_analyzer.analyser import get_columns_codes_for_responses_user_input
        survey.response_column_codes = get_columns_codes_for_responses_user_input(survey.responses_user_input)
        
        # Initialize processed_responses
        survey.processed_responses = {}
        
        # Mock methods that make API calls
        survey._get_max_answers = Mock(return_value=4)
        
        # Test each handler with appropriate question
        test_cases = [
            ("Q001", "radio", survey._process_radio_question),
            ("Q002", "multiple_choice", survey._process_multiple_choice_question),
            ("Q003", "ranking", survey._process_ranking_question),
            ("Q004", "text", survey._process_text_question),
            ("Q005", "array", survey._process_array_question),
            ("Q006", "multiple_short_text", survey._process_multiple_short_text),
        ]
        
        for question_id, q_type, handler in test_cases:
            try:
                handler(question_id)
                
                # Verify result was stored
                assert question_id in survey.processed_responses, f"{q_type} handler should store result"
                result = survey.processed_responses[question_id]
                assert result is not None, f"{q_type} handler returned None"
                
                if q_type == "radio":
                    assert isinstance(result, pd.Series)
                elif q_type in ["multiple_choice", "ranking", "array"]:
                    assert isinstance(result, pd.DataFrame)
                elif q_type == "text":
                    assert isinstance(result, pd.Series)
                elif q_type == "multiple_short_text":
                    assert isinstance(result, dict)
                    
            except Exception as e:
                pytest.fail(f"Handler for {q_type} failed: {str(e)}")
        
        # Verify we got results for all question types
        assert len(survey.processed_responses) == 6, "Should have results for all 6 question types"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"]) 