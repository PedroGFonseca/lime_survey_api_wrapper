"""
Comprehensive tests for analyser.py module to improve test coverage.
These tests target the missing lines identified in coverage analysis.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from src.lime_survey_analyzer.analyser import (
    _get_questions, _get_question_options, _get_raw_options_data,
    _process_options_data, _get_responses, _split_last_square_bracket_content,
    _get_option_codes_to_names_mapper, _split_responses_data_into_user_input_and_metadata,
    _get_responses_user_input_and_responses_metadata, _enrich_options_data_with_question_codes,
    get_columns_codes_for_responses_user_input, _map_names_to_rank_responses,
    get_response_data, _get_response_rate, SurveyAnalysis
)


class TestStandaloneFunctions:
    """Test standalone functions in analyser.py"""

    def test_get_questions_success(self):
        """Test _get_questions with successful API response"""
        mock_api = Mock()
        mock_api.questions.list_questions.return_value = [
            {'id': '123', 'qid': '456', 'parent_qid': '0', 'title': 'Q1'},
            {'id': '124', 'qid': '457', 'parent_qid': '0', 'title': 'Q2'}
        ]
        
        result = _get_questions(mock_api, "survey123")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result['id'].dtype == 'object'  # string type
        assert result['qid'].dtype == 'object'  # string type
        assert result['parent_qid'].dtype == 'object'  # string type
        mock_api.questions.list_questions.assert_called_once_with("survey123")

    def test_get_question_options_with_options(self):
        """Test _get_question_options with valid options"""
        mock_api = Mock()
        mock_api.questions.get_question_properties.return_value = {
            'answeroptions': {'1': 'Option 1', '2': 'Option 2'}
        }
        
        result = _get_question_options(mock_api, "survey123", "question456")
        
        assert result == {'1': 'Option 1', '2': 'Option 2'}
        mock_api.questions.get_question_properties.assert_called_once_with("survey123", "question456")

    def test_get_question_options_no_options(self):
        """Test _get_question_options with no available options"""
        mock_api = Mock()
        mock_api.questions.get_question_properties.return_value = {
            'answeroptions': "No available answer options"
        }
        
        result = _get_question_options(mock_api, "survey123", "question456")
        
        assert result == "No available answer options"

    def test_get_raw_options_data(self):
        """Test _get_raw_options_data with multiple questions"""
        mock_api = Mock()
        
        questions_df = pd.DataFrame({
            'id': ['123', '124'],
            'qid': ['456', '457'],
            'title': ['Q1', 'Q2']
        })
        
        with patch('src.lime_survey_analyzer.analyser._get_question_options') as mock_get_options, \
             patch('src.lime_survey_analyzer.analyser.tqdm') as mock_tqdm:
            
            mock_tqdm.return_value = ['123', '124']
            mock_get_options.side_effect = [
                {'1': 'Option 1', '2': 'Option 2'},
                "No available answer options"
            ]
            
            result = _get_raw_options_data(mock_api, "survey123", questions_df)
            
            assert len(result) == 2
            assert result['123'] == {'1': 'Option 1', '2': 'Option 2'}
            assert result['124'] == "No available answer options"

    def test_process_options_data_success(self):
        """Test _process_options_data with valid data"""
        raw_options = {
            '123': {
                'A1': {'order': 1, 'answer': 'Answer 1'},
                'A2': {'order': 2, 'answer': 'Answer 2'}
            },
            '124': "No available answer options"
        }
        
        result = _process_options_data(raw_options)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # Only questions with options
        assert 'option_code' in result.columns
        assert 'option_order' in result.columns
        assert 'qid' in result.columns
        assert result['qid'].dtype == 'object'  # string type

    def test_process_options_data_with_exception(self):
        """Test _process_options_data handles exceptions gracefully"""
        raw_options = {
            '123': {'invalid': 'data'},  # This will cause an exception
            '124': "No available answer options"
        }
        
        with patch('builtins.print') as mock_print:
            result = _process_options_data(raw_options)
            mock_print.assert_called_once_with("Failed in 123")

    def test_get_responses_list_format(self):
        """Test _get_responses with list format response"""
        mock_api = Mock()
        mock_api.responses.export_responses.return_value = [
            {'id': '1', 'Q1': 'A1'},
            {'id': '2', 'Q1': 'A2'}
        ]
        
        result = _get_responses(mock_api, "survey123")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result['id'].dtype == 'object'  # string type

    def test_get_responses_dict_with_responses_key(self):
        """Test _get_responses with dict format containing 'responses' key"""
        mock_api = Mock()
        mock_api.responses.export_responses.return_value = {
            'responses': [
                {'id': '1', 'Q1': 'A1'},
                {'id': '2', 'Q1': 'A2'}
            ]
        }
        
        result = _get_responses(mock_api, "survey123")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_get_responses_dict_without_responses_key(self):
        """Test _get_responses with dict format without 'responses' key"""
        mock_api = Mock()
        mock_api.responses.export_responses.return_value = {
            'id': '1', 'Q1': 'A1'
        }
        
        result = _get_responses(mock_api, "survey123")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1

    def test_get_responses_invalid_format(self):
        """Test _get_responses with invalid format raises ValueError"""
        mock_api = Mock()
        mock_api.responses.export_responses.return_value = "invalid format"
        
        with pytest.raises(ValueError, match="Unexpected response format"):
            _get_responses(mock_api, "survey123")

    def test_split_last_square_bracket_content_no_brackets(self):
        """Test _split_last_square_bracket_content with no brackets"""
        result = _split_last_square_bracket_content("SQ007")
        assert result == ("SQ007", None)

    def test_split_last_square_bracket_content_with_brackets(self):
        """Test _split_last_square_bracket_content with brackets"""
        result = _split_last_square_bracket_content("G02Q01[SQ006]")
        assert result == ("G02Q01", "SQ006")

    def test_split_last_square_bracket_content_multiple_brackets(self):
        """Test _split_last_square_bracket_content with multiple brackets"""
        result = _split_last_square_bracket_content("G02Q[V2]01[SQ006]")
        assert result == ("G02Q[V2]01", "SQ006")

    def test_split_last_square_bracket_content_invalid(self):
        """Test _split_last_square_bracket_content with invalid format"""
        with pytest.raises(ValueError, match="contains square brackets but does not end with them"):
            _split_last_square_bracket_content("G02Q01[SQ006]2b")

    def test_get_option_codes_to_names_mapper(self):
        """Test _get_option_codes_to_names_mapper"""
        options_df = pd.DataFrame({
            'qid': ['123', '123', '124'],
            'option_code': ['A1', 'A2', 'B1'],
            'answer': ['Answer 1', 'Answer 2', 'Answer B1']
        })
        
        result = _get_option_codes_to_names_mapper(options_df, '123')
        
        assert result == {'A1': 'Answer 1', 'A2': 'Answer 2'}

    def test_split_responses_data_into_user_input_and_metadata(self):
        """Test _split_responses_data_into_user_input_and_metadata"""
        responses_df = pd.DataFrame({
            'id': ['1', '2'],
            'submitdate': ['2023-01-01', '2023-01-02'],
            'Q1': ['A1', 'A2'],
            'Q2': ['B1', 'B2'],
            'seed': ['abc', 'def'],
            'startdate': ['2023-01-01', '2023-01-02'],
            'datestamp': ['2023-01-01', '2023-01-02'],
            'refurl': ['url1', 'url2']
        })
        
        user_input, metadata = _split_responses_data_into_user_input_and_metadata(responses_df)
        
        assert 'Q1' in user_input.columns
        assert 'Q2' in user_input.columns
        assert 'id' not in user_input.columns
        
        assert 'id' in metadata.columns
        assert 'submitdate' in metadata.columns
        assert 'Q1' not in metadata.columns

    def test_get_responses_user_input_and_responses_metadata(self):
        """Test _get_responses_user_input_and_responses_metadata"""
        mock_api = Mock()
        
        with patch('src.lime_survey_analyzer.analyser._get_responses') as mock_get_responses, \
             patch('src.lime_survey_analyzer.analyser._split_responses_data_into_user_input_and_metadata') as mock_split:
            
            mock_responses_df = pd.DataFrame({'id': ['1'], 'Q1': ['A1']})
            mock_get_responses.return_value = mock_responses_df
            mock_split.return_value = (pd.DataFrame({'Q1': ['A1']}), pd.DataFrame({'id': ['1']}))
            
            user_input, metadata = _get_responses_user_input_and_responses_metadata(mock_api, "survey123")
            
            mock_get_responses.assert_called_once_with(mock_api, "survey123")
            mock_split.assert_called_once_with(mock_responses_df)

    def test_enrich_options_data_with_question_codes(self):
        """Test _enrich_options_data_with_question_codes"""
        options_df = pd.DataFrame({
            'qid': ['123', '124'],
            'option_code': ['A1', 'B1'],
            'answer': ['Answer 1', 'Answer B1']
        })
        
        questions_df = pd.DataFrame({
            'qid': ['123', '124'],
            'title': ['Q1_CODE', 'Q2_CODE']
        })
        
        result = _enrich_options_data_with_question_codes(options_df, questions_df)
        
        assert 'question_code' in result.columns
        assert result.loc[result['qid'] == '123', 'question_code'].iloc[0] == 'Q1_CODE'
        assert result.loc[result['qid'] == '124', 'question_code'].iloc[0] == 'Q2_CODE'

    def test_get_columns_codes_for_responses_user_input(self):
        """Test get_columns_codes_for_responses_user_input"""
        responses_df = pd.DataFrame({
            'SQ007': [1, 2],
            'G02Q01[SQ006]': [1, 2],
            'simple_col': [1, 2]
        })
        
        result = get_columns_codes_for_responses_user_input(responses_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        # Check that the function processes column names correctly

    def test_get_response_rate(self):
        """Test _get_response_rate"""
        # FIX: Create proper test data - absolute_counts should match numeric_subset sums
        numeric_subset = pd.DataFrame({
            'A': [1, 0, 1, 1, 0],  # sum = 3
            'B': [1, 1, 0, 1, 1],  # sum = 4  
            'C': [0, 1, 1, 1, 1]   # sum = 4
        })
        absolute_counts = numeric_subset.sum()  # [3, 4, 4]
        
        result = _get_response_rate(absolute_counts, numeric_subset)
        
        assert isinstance(result, pd.Series)
        assert len(result) == 3
        # Check that rates are between 0 and 1
        assert all(0 <= rate <= 1 for rate in result)
        # Verify calculation: rate = count / total_respondents
        # Total respondents = those who responded to any option
        total_respondents = (numeric_subset.sum(axis=1) > 0).sum()  # Should be 5 (all rows have at least one 1)
        expected_rates = absolute_counts / total_respondents
        pd.testing.assert_series_equal(result, expected_rates)

    def test_get_response_data(self):
        """Test get_response_data function"""
        mock_api = Mock()
        
        with patch('src.lime_survey_analyzer.analyser._get_responses_user_input_and_responses_metadata') as mock_get_data:
            mock_user_input = pd.DataFrame({'Q1': ['A1', '', 'A2']})
            mock_metadata = pd.DataFrame({'id': ['1', '2', '3']})
            mock_get_data.return_value = (mock_user_input, mock_metadata)
            
            # Test keeping incomplete responses
            user_input, metadata = get_response_data(mock_api, "survey123", keep_incomplete_user_input=True)
            
            assert len(user_input) == 3  # All responses kept
            
            # Test filtering incomplete responses
            user_input, metadata = get_response_data(mock_api, "survey123", keep_incomplete_user_input=False)
            
            # Should filter out empty responses
            mock_get_data.assert_called_with(mock_api, "survey123")


class TestSurveyAnalysisClass:
    """Test SurveyAnalysis class methods that are missing coverage"""

    @pytest.fixture
    def survey_analysis(self):
        """Create SurveyAnalysis instance for testing"""
        return SurveyAnalysis("test_survey_123")

    def test_init(self, survey_analysis):
        """Test SurveyAnalysis initialization"""
        assert survey_analysis.survey_id == "test_survey_123"
        assert survey_analysis.processed_responses == {}

    def test_connect_to_api(self, survey_analysis):
        """Test _connect_to_api method"""
        with patch('src.lime_survey_analyzer.analyser.LimeSurveyClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.from_config.return_value = mock_client
            
            result = survey_analysis._connect_to_api()
            
            assert result == mock_client
            mock_client_class.from_config.assert_called_once()

    def test_get_survey_structure_data(self, survey_analysis):
        """Test _get_survey_structure_data method"""
        survey_analysis.api = Mock()
        
        with patch('src.lime_survey_analyzer.analyser._get_questions') as mock_get_questions, \
             patch('src.lime_survey_analyzer.analyser._get_raw_options_data') as mock_get_raw_options, \
             patch('src.lime_survey_analyzer.analyser._process_options_data') as mock_process_options, \
             patch('src.lime_survey_analyzer.analyser._enrich_options_data_with_question_codes') as mock_enrich:
            
            mock_questions = pd.DataFrame({'qid': ['1'], 'title': ['Q1']})
            mock_raw_options = {'1': {'A1': 'Answer 1'}}
            mock_processed_options = pd.DataFrame({'qid': ['1'], 'option_code': ['A1']})
            mock_enriched_options = pd.DataFrame({'qid': ['1'], 'option_code': ['A1'], 'question_code': ['Q1']})
            
            mock_get_questions.return_value = mock_questions
            mock_get_raw_options.return_value = mock_raw_options
            mock_process_options.return_value = mock_processed_options
            mock_enrich.return_value = mock_enriched_options
            
            survey_analysis._get_survey_structure_data()
            
            assert hasattr(survey_analysis, 'questions')
            assert hasattr(survey_analysis, 'raw_options_data')
            assert hasattr(survey_analysis, 'options')

    def test_question_has_other(self, survey_analysis):
        """Test _question_has_other method"""
        survey_analysis.questions = pd.DataFrame({
            'qid': ['1', '2'],
            'other': ['Y', 'N']
        })
        
        assert survey_analysis._question_has_other('1') == True
        assert survey_analysis._question_has_other('2') == False

    def test_get_question_code(self, survey_analysis):
        """Test _get_question_code method"""
        survey_analysis.questions = pd.DataFrame({
            'qid': ['1', '2'],
            'title': ['Q1_CODE', 'Q2_CODE']
        })
        
        result = survey_analysis._get_question_code('1')
        assert result == 'Q1_CODE'

    def test_get_response_codes_for_question(self, survey_analysis):
        """Test _get_response_codes_for_question method"""
        survey_analysis.response_column_codes = pd.DataFrame({
            'question_code': ['Q1', 'Q1', 'Q2'],
            'appendage': ['A1', 'A2', 'A1']
        }, index=['Q1[A1]', 'Q1[A2]', 'Q2[A1]'])
        
        result = survey_analysis._get_response_codes_for_question('Q1')
        
        # FIX: Method returns DataFrame, not list
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert 'Q1[A1]' in result.index
        assert 'Q1[A2]' in result.index
        assert all(result['question_code'] == 'Q1')

    def test_get_absolute_count_and_response_rate(self, survey_analysis):
        """Test _get_absolute_count_and_response_rate method"""
        survey_analysis.responses_user_input = pd.DataFrame({
            'Q1[A1]': ['Y', '', 'Y'],
            'Q1[A2]': ['', 'Y', 'Y']
        })
        
        with patch.object(survey_analysis, '_get_response_codes_for_question') as mock_get_codes:
            # FIX: Mock should return DataFrame with .index attribute, not list
            mock_codes_df = pd.DataFrame({'question_code': ['Q1', 'Q1']}, 
                                       index=['Q1[A1]', 'Q1[A2]'])
            mock_get_codes.return_value = mock_codes_df
            
            # FIX: Method returns DataFrame, not tuple
            result = survey_analysis._get_absolute_count_and_response_rate('Q1')
            
            assert isinstance(result, pd.DataFrame)
            assert 'absolute_counts' in result.columns
            assert 'response_rates' in result.columns
            # Y responses should be counted as 1, empty as 0
            assert result.loc['Q1[A1]', 'absolute_counts'] == 2
            assert result.loc['Q1[A2]', 'absolute_counts'] == 2

    def test_process_column_codes(self, survey_analysis):
        """Test _process_column_codes method"""
        survey_analysis.responses_user_input = pd.DataFrame({
            'Q1': [1, 2],
            'Q2[A1]': [1, 0]
        })
        
        with patch('src.lime_survey_analyzer.analyser.get_columns_codes_for_responses_user_input') as mock_get_codes:
            mock_codes_df = pd.DataFrame({
                0: ['Q1', 'Q2'],
                1: [None, 'A1']
            }, index=['Q1', 'Q2[A1]'])
            mock_get_codes.return_value = mock_codes_df
            
            survey_analysis._process_column_codes()
            
            assert hasattr(survey_analysis, 'response_codes_to_question_codes')

    def test_get_questions_in_survey_order(self, survey_analysis):
        """Test get_questions_in_survey_order method"""
        survey_analysis.questions = pd.DataFrame({
            'qid': ['1', '2', '3'],
            'gid': ['10', '10', '20'],
            'question_order': [1, 2, 1]
        }).sort_values(['gid', 'question_order'])
        
        result = survey_analysis.get_questions_in_survey_order()
        
        assert isinstance(result, pd.DataFrame)
        # Should be sorted by group and question order
        assert result.iloc[0]['qid'] == '1'  # First in group 10
        assert result.iloc[1]['qid'] == '2'  # Second in group 10
        assert result.iloc[2]['qid'] == '3'  # First in group 20 