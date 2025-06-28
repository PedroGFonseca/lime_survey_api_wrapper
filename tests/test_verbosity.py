"""
Tests for verbosity functionality in SurveyAnalysis class.

These tests verify that the verbose flag properly controls output messages,
progress bars, and logging throughout the analysis process.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import pandas as pd
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

# Import the SurveyAnalysis class
from lime_survey_analyzer import SurveyAnalysis


class TestVerbosityControl(unittest.TestCase):
    """Test class for verbosity control functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.survey_id = "test_survey_123"
        self.mock_api = Mock()
        
        # Mock survey structure data
        self.mock_questions = pd.DataFrame([
            {'id': '1', 'qid': '1', 'parent_qid': '0', 'question_theme_name': 'listradio'},
            {'id': '2', 'qid': '2', 'parent_qid': '0', 'question_theme_name': 'multiplechoice'},
        ])
        
        self.mock_options = pd.DataFrame([
            {'qid': '1', 'option_code': 'A1', 'answer': 'Option 1'},
            {'qid': '2', 'option_code': 'A1', 'answer': 'Option A'},
        ])
        
        self.mock_responses = pd.DataFrame([
            {'id': 1, 'Q1': 'A1', 'Q2': 'A1'},
            {'id': 2, 'Q1': 'A2', 'Q2': 'A2'},
        ])
        
        # Configure API mock
        self.mock_api.surveys.get_survey_properties.return_value = {'title': 'Test Survey'}
        self.mock_api.surveys.get_summary.return_value = {'response_count': 2}
        self.mock_api.questions.list_groups.return_value = []
        self.mock_api.questions.get_question_properties.return_value = {
            'attributes': {'max_answers': '1'}
        }

    def test_verbose_initialization_default_false(self):
        """Test that verbose defaults to False."""
        analysis = SurveyAnalysis(self.survey_id)
        self.assertFalse(analysis.verbose)

    def test_verbose_initialization_explicit_true(self):
        """Test explicit verbose=True initialization."""
        analysis = SurveyAnalysis(self.survey_id, verbose=True)
        self.assertTrue(analysis.verbose)

    def test_verbose_initialization_explicit_false(self):
        """Test explicit verbose=False initialization."""
        analysis = SurveyAnalysis(self.survey_id, verbose=False)
        self.assertFalse(analysis.verbose)

    @patch('lime_survey_analyzer.analyser._get_questions')
    @patch('lime_survey_analyzer.analyser._get_raw_options_data')
    @patch('lime_survey_analyzer.analyser._process_options_data')
    @patch('lime_survey_analyzer.analyser._enrich_options_data_with_question_codes')
    @patch('lime_survey_analyzer.analyser.cache_manager')
    def test_verbose_false_suppresses_cache_messages(self, mock_cache, mock_enrich, 
                                                   mock_process, mock_raw_options, mock_questions):
        """Test that verbose=False suppresses cache hit/miss messages."""
        # Setup mocks
        mock_cache.get_cached.return_value = None  # Force cache miss
        mock_questions.return_value = self.mock_questions
        mock_raw_options.return_value = {}
        mock_process.return_value = self.mock_options
        mock_enrich.return_value = self.mock_options
        
        analysis = SurveyAnalysis(self.survey_id, verbose=False)
        analysis.api = self.mock_api
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            analysis._get_survey_structure_data()
        
        output = stdout_capture.getvalue()
        
        # Should not contain cache messages
        self.assertNotIn("Cache HIT", output)
        self.assertNotIn("Cache STORE", output)
        self.assertNotIn("Loading survey structure", output)

    @patch('lime_survey_analyzer.analyser._get_questions')
    @patch('lime_survey_analyzer.analyser._get_raw_options_data')
    @patch('lime_survey_analyzer.analyser._process_options_data')
    @patch('lime_survey_analyzer.analyser._enrich_options_data_with_question_codes')
    @patch('lime_survey_analyzer.analyser.cache_manager')
    def test_verbose_true_shows_cache_messages(self, mock_cache, mock_enrich, 
                                             mock_process, mock_raw_options, mock_questions):
        """Test that verbose=True shows cache hit/miss messages."""
        # Setup mocks
        mock_cache.get_cached.return_value = None  # Force cache miss
        mock_questions.return_value = self.mock_questions
        mock_raw_options.return_value = {}
        mock_process.return_value = self.mock_options
        mock_enrich.return_value = self.mock_options
        
        analysis = SurveyAnalysis(self.survey_id, verbose=True)
        analysis.api = self.mock_api
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            analysis._get_survey_structure_data()
        
        output = stdout_capture.getvalue()
        
        # Should contain cache messages
        self.assertIn("Loading survey structure", output)
        self.assertIn("Cache STORE", output)

    @patch('lime_survey_analyzer.analyser.cache_manager')
    def test_verbose_false_suppresses_max_answers_cache_messages(self, mock_cache):
        """Test that verbose=False suppresses max answers cache messages."""
        mock_cache.get_cached.return_value = None  # Force cache miss
        
        analysis = SurveyAnalysis(self.survey_id, verbose=False)
        analysis.api = self.mock_api
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            result = analysis._get_max_answers("1")
        
        output = stdout_capture.getvalue()
        
        # Should not contain cache messages
        self.assertNotIn("Cache HIT", output)
        self.assertNotIn("Cache STORE", output)

    @patch('lime_survey_analyzer.analyser.cache_manager')
    def test_verbose_true_shows_max_answers_cache_messages(self, mock_cache):
        """Test that verbose=True shows max answers cache messages."""
        mock_cache.get_cached.return_value = None  # Force cache miss
        
        analysis = SurveyAnalysis(self.survey_id, verbose=True)
        analysis.api = self.mock_api
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            result = analysis._get_max_answers("1")
        
        output = stdout_capture.getvalue()
        
        # Should contain cache messages
        self.assertIn("Cache STORE", output)

    @patch('lime_survey_analyzer.analyser.tqdm')
    @patch('lime_survey_analyzer.analyser._get_question_options')
    def test_verbose_false_no_progress_bar_raw_options(self, mock_get_options, mock_tqdm):
        """Test that verbose=False doesn't show progress bar for raw options."""
        from lime_survey_analyzer.analyser import _get_raw_options_data
        
        mock_get_options.return_value = {}
        
        # Call with verbose=False
        result = _get_raw_options_data(self.mock_api, self.survey_id, self.mock_questions, verbose=False)
        
        # tqdm should not be called
        mock_tqdm.assert_not_called()

    @patch('lime_survey_analyzer.analyser.tqdm')
    @patch('lime_survey_analyzer.analyser._get_question_options')
    def test_verbose_true_shows_progress_bar_raw_options(self, mock_get_options, mock_tqdm):
        """Test that verbose=True shows progress bar for raw options."""
        from lime_survey_analyzer.analyser import _get_raw_options_data
        
        mock_get_options.return_value = {}
        mock_tqdm.return_value = self.mock_questions['id']
        
        # Call with verbose=True
        result = _get_raw_options_data(self.mock_api, self.survey_id, self.mock_questions, verbose=True)
        
        # tqdm should be called with proper parameters
        mock_tqdm.assert_called_once_with(self.mock_questions['id'], desc="Loading question options")

    def test_verbose_false_suppresses_option_processing_errors(self):
        """Test that verbose=False suppresses option processing error messages."""
        from lime_survey_analyzer.analyser import _process_options_data
        
        # Create problematic raw options data that will cause errors
        bad_raw_options = {
            '1': {'invalid': 'data'},  # This will cause an error in processing
        }
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            result = _process_options_data(bad_raw_options, verbose=False)
        
        output = stdout_capture.getvalue()
        
        # Should not contain error messages
        self.assertNotIn("Failed processing options", output)

    def test_verbose_true_shows_option_processing_errors(self):
        """Test that verbose=True shows option processing error messages."""
        from lime_survey_analyzer.analyser import _process_options_data
        
        # Create problematic raw options data that will cause errors
        bad_raw_options = {
            '1': {'invalid': 'data'},  # This will cause an error in processing
        }
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            result = _process_options_data(bad_raw_options, verbose=True)
        
        output = stdout_capture.getvalue()
        
        # Should contain error messages
        self.assertIn("Failed processing options", output)

    @patch('lime_survey_analyzer.analyser.tqdm')
    def test_verbose_false_no_progress_bar_process_all_questions(self, mock_tqdm):
        """Test that verbose=False doesn't show progress bar for processing questions."""
        analysis = SurveyAnalysis(self.survey_id, verbose=False)
        analysis.questions = self.mock_questions
        analysis.processed_responses = {}
        
        # Mock the process_question method to avoid actual processing
        with patch.object(analysis, 'process_question'):
            analysis.process_all_questions()
        
        # tqdm should not be called
        mock_tqdm.assert_not_called()

    @patch('lime_survey_analyzer.analyser.tqdm')
    def test_verbose_true_shows_progress_bar_process_all_questions(self, mock_tqdm):
        """Test that verbose=True shows progress bar for processing questions."""
        analysis = SurveyAnalysis(self.survey_id, verbose=True)
        analysis.questions = self.mock_questions
        analysis.processed_responses = {}
        
        # Mock tqdm to return the itertuples result
        mock_tqdm.return_value = self.mock_questions.itertuples()
        
        # Mock the process_question method to avoid actual processing
        with patch.object(analysis, 'process_question'):
            analysis.process_all_questions()
        
        # tqdm should be called with proper parameters
        mock_tqdm.assert_called_once()
        call_args = mock_tqdm.call_args
        self.assertIn('desc', call_args.kwargs)
        self.assertEqual(call_args.kwargs['desc'], "Processing questions")

    def test_verbose_false_suppresses_question_processing_errors(self):
        """Test that verbose=False suppresses question processing error messages."""
        analysis = SurveyAnalysis(self.survey_id, verbose=False)
        analysis.questions = self.mock_questions
        analysis.processed_responses = {}
        
        # Mock process_question to raise an exception
        def mock_process_question(qid):
            raise ValueError(f"Test error for question {qid}")
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            with patch.object(analysis, 'process_question', side_effect=mock_process_question):
                analysis.process_all_questions()
        
        output = stdout_capture.getvalue()
        
        # Should not contain error messages
        self.assertNotIn("Failed to process question", output)
        
        # But should still track errors in fail_message_log
        self.assertEqual(len(analysis.fail_message_log), 2)

    def test_verbose_true_shows_question_processing_errors(self):
        """Test that verbose=True shows question processing error messages."""
        analysis = SurveyAnalysis(self.survey_id, verbose=True)
        analysis.questions = self.mock_questions
        analysis.processed_responses = {}
        
        # Mock process_question to raise an exception
        def mock_process_question(qid):
            raise ValueError(f"Test error for question {qid}")
        
        # Capture stdout
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            with patch.object(analysis, 'process_question', side_effect=mock_process_question):
                analysis.process_all_questions()
        
        output = stdout_capture.getvalue()
        
        # Should contain error messages
        self.assertIn("Failed to process question", output)
        self.assertIn("Test error for question", output)

    @patch('lime_survey_analyzer.analyser._get_questions')
    @patch('lime_survey_analyzer.analyser._get_raw_options_data')
    @patch('lime_survey_analyzer.analyser._process_options_data')
    @patch('lime_survey_analyzer.analyser._enrich_options_data_with_question_codes')
    @patch('lime_survey_analyzer.analyser.get_response_data')
    def test_setup_method_respects_verbosity(self, mock_get_responses, mock_enrich, 
                                           mock_process, mock_raw_options, mock_questions):
        """Test that the setup method respects the verbosity setting."""
        # Setup mocks
        mock_questions.return_value = self.mock_questions
        mock_raw_options.return_value = {}
        mock_process.return_value = self.mock_options
        mock_enrich.return_value = self.mock_options
        mock_get_responses.return_value = (self.mock_responses, pd.DataFrame())
        
        # Test with verbose=False
        analysis_quiet = SurveyAnalysis(self.survey_id, verbose=False)
        
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            analysis_quiet.setup(api=self.mock_api)
        
        quiet_output = stdout_capture.getvalue()
        
        # Test with verbose=True
        analysis_verbose = SurveyAnalysis(self.survey_id, verbose=True)
        
        stdout_capture = io.StringIO()
        with redirect_stdout(stdout_capture):
            analysis_verbose.setup(api=self.mock_api)
        
        verbose_output = stdout_capture.getvalue()
        
        # Verbose output should contain more information
        self.assertGreater(len(verbose_output), len(quiet_output))

    def test_verbosity_consistency_across_methods(self):
        """Test that verbosity setting is consistent across all methods."""
        analysis = SurveyAnalysis(self.survey_id, verbose=True)
        
        # Verify that the verbose flag is accessible and consistent
        self.assertTrue(analysis.verbose)
        
        # Test that changing verbosity affects behavior
        analysis.verbose = False
        self.assertFalse(analysis.verbose)


class TestVerbosityIntegration(unittest.TestCase):
    """Integration tests for verbosity functionality."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.survey_id = "integration_test_survey"
        self.mock_api = Mock()
        
        # Configure comprehensive API mock
        self.mock_api.surveys.get_survey_properties.return_value = {'title': 'Integration Test Survey'}
        self.mock_api.surveys.get_summary.return_value = {'response_count': 5}
        self.mock_api.questions.list_groups.return_value = []
        self.mock_api.questions.get_question_properties.return_value = {
            'attributes': {'max_answers': '2'}
        }

    @patch('lime_survey_analyzer.analyser._get_questions')
    @patch('lime_survey_analyzer.analyser._get_raw_options_data')
    @patch('lime_survey_analyzer.analyser._process_options_data')
    @patch('lime_survey_analyzer.analyser._enrich_options_data_with_question_codes')
    @patch('lime_survey_analyzer.analyser.get_response_data')
    @patch('lime_survey_analyzer.analyser.cache_manager')
    def test_full_analysis_workflow_verbose_false(self, mock_cache, mock_get_responses, mock_enrich, 
                                                 mock_process, mock_raw_options, mock_questions):
        """Test complete analysis workflow with verbose=False produces minimal output."""
        # Setup cache mock to force cache miss
        mock_cache.get_cached.return_value = None
        
        # Setup comprehensive mocks
        mock_questions.return_value = pd.DataFrame([
            {'id': '1', 'qid': '1', 'parent_qid': '0', 'question_theme_name': 'listradio'},
            {'id': '2', 'qid': '2', 'parent_qid': '0', 'question_theme_name': 'multiplechoice'},
            {'id': '3', 'qid': '3', 'parent_qid': '0', 'question_theme_name': 'shortfreetext'},
        ])
        
        mock_raw_options.return_value = {}
        mock_process.return_value = pd.DataFrame()
        mock_enrich.return_value = pd.DataFrame()
        # Provide non-empty response data to avoid processing errors
        mock_get_responses.return_value = (
            pd.DataFrame({'Q1': ['A1', 'A2'], 'Q2': ['B1', 'B2'], 'Q3': ['Text1', 'Text2']}),
            pd.DataFrame({'id': [1, 2], 'submitdate': ['2023-01-01', '2023-01-02']})
        )
        
        analysis = SurveyAnalysis(self.survey_id, verbose=False)
        
        # Capture all output
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            analysis.setup(api=self.mock_api)
            with patch.object(analysis, 'process_question'):  # Mock to avoid complex processing
                analysis.process_all_questions()
        
        stdout_output = stdout_capture.getvalue()
        stderr_output = stderr_capture.getvalue()
        
        # Should produce minimal output - allow for some system messages but no verbose messages
        self.assertNotIn("Cache HIT", stdout_output, "Verbose=False should not show cache messages")
        self.assertNotIn("Cache STORE", stdout_output, "Verbose=False should not show cache messages")
        self.assertNotIn("Loading", stdout_output, "Verbose=False should not show loading messages")
        
        # Only pandas warnings might appear in stderr, not our custom messages
        if stderr_output:
            self.assertNotIn("Cache HIT", stderr_output)
            self.assertNotIn("Cache STORE", stderr_output)
            self.assertNotIn("Loading", stderr_output)

    @patch('lime_survey_analyzer.analyser._get_questions')
    @patch('lime_survey_analyzer.analyser._get_raw_options_data')
    @patch('lime_survey_analyzer.analyser._process_options_data')
    @patch('lime_survey_analyzer.analyser._enrich_options_data_with_question_codes')
    @patch('lime_survey_analyzer.analyser.get_response_data')
    def test_full_analysis_workflow_verbose_true(self, mock_get_responses, mock_enrich, 
                                                mock_process, mock_raw_options, mock_questions):
        """Test complete analysis workflow with verbose=True produces detailed output."""
        # Setup comprehensive mocks
        mock_questions.return_value = pd.DataFrame([
            {'id': '1', 'qid': '1', 'parent_qid': '0', 'question_theme_name': 'listradio'},
            {'id': '2', 'qid': '2', 'parent_qid': '0', 'question_theme_name': 'multiplechoice'},
        ])
        
        mock_raw_options.return_value = {}
        mock_process.return_value = pd.DataFrame()
        mock_enrich.return_value = pd.DataFrame()
        mock_get_responses.return_value = (
            pd.DataFrame({'Q1': ['A1', 'A2'], 'Q2': ['B1', 'B2']}),
            pd.DataFrame({'id': [1, 2]})
        )
        
        analysis = SurveyAnalysis(self.survey_id, verbose=True)
        
        # Capture all output
        stdout_capture = io.StringIO()
        
        with redirect_stdout(stdout_capture):
            analysis.setup(api=self.mock_api)
            with patch.object(analysis, 'process_question'):  # Mock to avoid complex processing
                analysis.process_all_questions()
        
        stdout_output = stdout_capture.getvalue()
        
        # Should produce detailed output
        self.assertGreater(len(stdout_output.strip()), 0, "Verbose=True should produce output")


if __name__ == '__main__':
    unittest.main() 