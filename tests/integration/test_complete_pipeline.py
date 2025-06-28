#!/usr/bin/env python3
"""
Integration Tests: Complete Mock Data Pipeline

Tests the complete survey analysis and visualization pipeline using enhanced mock data.
This validates the end-to-end workflow: Data Generation → Analysis → Charts → Dashboard

These tests use NO real survey data and NO API calls - completely safe for CI/CD.
"""

import pytest
import pandas as pd
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import tempfile
import shutil

# Add source directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import our enhanced data generator
from enhanced_data_generators import create_enhanced_test_data

# Import analysis and visualization components
from lime_survey_analyzer.analyser import SurveyAnalysis
from lime_survey_analyzer.viz.charts.horizontal_bar import create_horizontal_bar_chart
from lime_survey_analyzer.viz.charts.ranking_stacked import create_ranking_stacked_bar_chart
from lime_survey_analyzer.viz.config import get_config
from lime_survey_analyzer.viz.utils.text import clean_html_tags

# Import the mock analysis adapter from our demo
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'examples'))
from mock_data_dashboard_demo import MockSurveyAnalysis, create_chart_for_question, create_dashboard_app


class TestCompleteDataPipeline:
    """Test the complete pipeline from mock data generation to dashboard creation."""
    
    @pytest.fixture(scope="class")
    def mock_survey_data(self):
        """Generate enhanced mock survey data once per test class."""
        return create_enhanced_test_data(survey_id="TEST_SURVEY_123")
    
    @pytest.fixture(scope="class")
    def mock_analysis(self, mock_survey_data):
        """Create MockSurveyAnalysis instance with test data."""
        analysis = MockSurveyAnalysis(mock_survey_data, survey_id="TEST_SURVEY_123", verbose=False)
        analysis.process_all_questions()
        return analysis
    
    @pytest.fixture
    def viz_config(self):
        """Get visualization configuration."""
        return get_config()

    def test_mock_data_generation_completeness(self, mock_survey_data):
        """Test that enhanced mock data generator produces complete survey structure."""
        # Verify all required components exist
        required_keys = ['questions', 'options', 'responses_user_input', 'responses_metadata', 
                        'groups', 'properties', 'summary', 'survey_id']
        
        for key in required_keys:
            assert key in mock_survey_data, f"Missing required key: {key}"
        
        # Verify data structure integrity
        questions = mock_survey_data['questions']
        options = mock_survey_data['options']
        responses = mock_survey_data['responses_user_input']
        
        assert isinstance(questions, pd.DataFrame), "Questions should be DataFrame"
        assert isinstance(options, pd.DataFrame), "Options should be DataFrame"
        assert isinstance(responses, pd.DataFrame), "Responses should be DataFrame"
        
        # Verify realistic data volumes
        assert len(questions) >= 30, f"Should have realistic number of questions, got {len(questions)}"
        assert len(responses) >= 300, f"Should have realistic number of responses, got {len(responses)}"
        assert len(options) >= 100, f"Should have realistic number of options, got {len(options)}"
        
        # Verify question type distribution
        question_types = questions['question_theme_name'].value_counts()
        assert len(question_types) >= 8, f"Should have diverse question types, got {len(question_types)}"
        
        # Most common types should be well represented
        assert question_types.get('listradio', 0) >= 10, "Should have multiple radio questions"
        assert question_types.get('ranking', 0) >= 5, "Should have multiple ranking questions"

    def test_mock_analysis_setup_and_processing(self, mock_analysis):
        """Test that MockSurveyAnalysis properly processes mock data."""
        # Verify analysis setup
        assert mock_analysis.survey_id == "TEST_SURVEY_123"
        assert hasattr(mock_analysis, 'questions')
        assert hasattr(mock_analysis, 'options')
        assert hasattr(mock_analysis, 'responses_user_input')
        assert hasattr(mock_analysis, 'response_column_codes')
        
        # Verify questions were processed
        assert len(mock_analysis.processed_responses) > 0, "Should have processed some questions"
        
        # Verify processing success rate
        total_main_questions = len(mock_analysis.questions[
            mock_analysis.questions['parent_qid'].fillna('None') == '0'
        ])
        processed_count = len(mock_analysis.processed_responses)
        success_rate = processed_count / total_main_questions
        
        assert success_rate >= 0.80, f"Processing success rate should be ≥80%, got {success_rate:.2%}"
        
        # Verify error handling
        assert hasattr(mock_analysis, 'fail_message_log')
        if mock_analysis.fail_message_log:
            # Errors should be for known problematic question types
            for qid, error in mock_analysis.fail_message_log.items():
                assert isinstance(error, Exception), f"Error log should contain Exception objects"
    
    def test_question_type_processing_coverage(self, mock_analysis):
        """Test that all major question types are processed correctly."""
        processed_questions = mock_analysis.processed_responses
        
        # Get question info for processed questions
        question_types_processed = {}
        for qid in processed_questions.keys():
            qid_str = str(qid)
            question_info = mock_analysis.questions[mock_analysis.questions['qid'] == qid_str]
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type not in question_types_processed:
                    question_types_processed[q_type] = []
                question_types_processed[q_type].append(qid)
        
        # Verify major question types are represented
        expected_types = ['listradio', 'ranking', 'longfreetext', 'shortfreetext', 'multiplechoice']
        for q_type in expected_types:
            assert q_type in question_types_processed, f"Should process {q_type} questions"
            assert len(question_types_processed[q_type]) > 0, f"Should have processed {q_type} questions"
        
        # Test specific question type outputs
        for q_type, qids in question_types_processed.items():
            sample_qid = qids[0]
            result = processed_questions[sample_qid]
            
            if q_type == 'listradio':
                assert isinstance(result, pd.Series), f"Radio questions should return Series, got {type(result)}"
                assert len(result) > 0, "Radio question should have response counts"
                
            elif q_type == 'ranking':
                assert isinstance(result, pd.DataFrame), f"Ranking questions should return DataFrame, got {type(result)}"
                assert not result.empty, "Ranking question should have data"
                
            elif q_type in ['longfreetext', 'shortfreetext']:
                assert isinstance(result, pd.Series), f"Text questions should return Series, got {type(result)}"
                
            elif q_type == 'multiplechoice':
                assert isinstance(result, pd.DataFrame), f"Multiple choice should return DataFrame, got {type(result)}"
                if not result.empty:
                    expected_cols = ['option_text', 'absolute_counts', 'response_rates']
                    for col in expected_cols:
                        assert col in result.columns, f"Multiple choice result should have {col} column"

    def test_chart_creation_for_all_question_types(self, mock_analysis, viz_config):
        """Test that charts can be created for all processed question types."""
        charts_created = []
        charts_failed = []
        
        for question_id in mock_analysis.processed_responses.keys():
            try:
                chart = create_chart_for_question(mock_analysis, question_id, viz_config, verbose=False)
                if chart:
                    charts_created.append(chart)
                else:
                    charts_failed.append(question_id)
            except Exception as e:
                charts_failed.append((question_id, str(e)))
        
        # Verify high chart creation success rate
        total_processed = len(mock_analysis.processed_responses)
        charts_success_rate = len(charts_created) / total_processed
        assert charts_success_rate >= 0.85, f"Chart creation success rate should be ≥85%, got {charts_success_rate:.2%}"
        
        # Verify chart diversity
        chart_types = {}
        for chart in charts_created:
            chart_type = chart['chart_type']
            chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
        
        expected_chart_types = ['horizontal_bar', 'ranking_stacked', 'text_responses']
        for chart_type in expected_chart_types:
            assert chart_type in chart_types, f"Should create {chart_type} charts"
            assert chart_types[chart_type] > 0, f"Should have multiple {chart_type} charts"
        
        # Verify chart structure
        for chart in charts_created[:5]:  # Test first 5 charts
            assert 'question_id' in chart, "Chart should have question_id"
            assert 'title' in chart, "Chart should have title"
            assert 'chart_type' in chart, "Chart should have chart_type"
            assert 'data' in chart, "Chart should have data"
            
            # Clean title should not have HTML tags
            clean_title = clean_html_tags(chart['title'])
            assert '<' not in clean_title, "Chart title should not contain HTML tags"

    def test_dashboard_creation_with_realistic_data(self, mock_analysis, viz_config):
        """Test that dashboard can be created with realistic chart data."""
        # Create charts for dashboard
        charts = []
        for question_id in list(mock_analysis.processed_responses.keys())[:20]:  # Limit for testing
            chart = create_chart_for_question(mock_analysis, question_id, viz_config, verbose=False)
            if chart:
                charts.append(chart)
        
        assert len(charts) >= 10, f"Should create sufficient charts for testing, got {len(charts)}"
        
        # Create dashboard app
        app = create_dashboard_app(charts, "Test Survey Dashboard")
        
        # Verify dashboard structure
        assert app is not None, "Dashboard app should be created"
        assert hasattr(app, 'layout'), "Dashboard should have layout"
        assert hasattr(app, 'callback_map'), "Dashboard should have callbacks"
        
        # Verify app configuration
        assert app.config.external_stylesheets is not None, "Should have external stylesheets"

    def test_data_integrity_across_pipeline(self, mock_survey_data, mock_analysis):
        """Test that data maintains integrity throughout the pipeline."""
        # Test question ID consistency
        original_questions = mock_survey_data['questions']
        analysis_questions = mock_analysis.questions
        
        # Question IDs should match
        original_qids = set(original_questions['qid'].astype(str))
        analysis_qids = set(analysis_questions['qid'].astype(str))
        assert original_qids == analysis_qids, "Question IDs should be preserved"
        
        # Test response data integrity
        original_responses = mock_survey_data['responses_user_input']
        analysis_responses = mock_analysis.responses_user_input
        
        assert len(original_responses) == len(analysis_responses), "Response count should be preserved"
        assert set(original_responses.columns) == set(analysis_responses.columns), "Response columns should be preserved"
        
        # Test processed responses link back to original questions
        for qid in mock_analysis.processed_responses.keys():
            qid_str = str(qid)
            assert qid_str in analysis_qids, f"Processed question {qid} should exist in original questions"

    def test_error_handling_and_edge_cases(self, viz_config):
        """Test pipeline behavior with edge cases and malformed data."""
        # Test with minimal data
        minimal_data = create_enhanced_test_data("MINIMAL_TEST")
        
        # Modify to create edge cases
        minimal_data['questions'] = minimal_data['questions'].head(5)  # Only 5 questions
        minimal_data['responses_user_input'] = minimal_data['responses_user_input'].head(10)  # Only 10 responses
        
        # Should still work with minimal data
        minimal_analysis = MockSurveyAnalysis(minimal_data, verbose=False)
        minimal_analysis.process_all_questions()
        
        assert len(minimal_analysis.processed_responses) >= 1, "Should process at least some questions with minimal data"
        
        # Test chart creation with minimal data
        charts = []
        for qid in minimal_analysis.processed_responses.keys():
            chart = create_chart_for_question(minimal_analysis, qid, viz_config, verbose=False)
            if chart:
                charts.append(chart)
        
        # Should create dashboard even with minimal charts
        if charts:
            app = create_dashboard_app(charts, "Minimal Test Dashboard")
            assert app is not None, "Should create dashboard with minimal data"

    def test_configuration_consistency_across_components(self, mock_analysis, viz_config):
        """Test that visualization configuration is applied consistently."""
        # Test that config settings propagate to charts
        sample_qid = list(mock_analysis.processed_responses.keys())[0]
        chart = create_chart_for_question(mock_analysis, sample_qid, viz_config, verbose=False)
        
        if chart and chart.get('figure'):
            fig = chart['figure']
            
            # Verify figure has expected configuration
            assert hasattr(fig, 'layout'), "Figure should have layout"
            
            # Check that styling from config is applied
            layout = fig.layout
            assert layout.font is not None, "Figure should have font configuration"



class TestCrossComponentIntegration:
    """Test integration between different components of the pipeline."""
    
    @pytest.fixture
    def mock_data_and_analysis(self):
        """Provide both mock data and analysis for cross-component testing."""
        mock_data = create_enhanced_test_data("CROSS_COMPONENT_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        return mock_data, analysis
    
    def test_question_option_relationship_integrity(self, mock_data_and_analysis):
        """Test that question-option relationships are maintained across components."""
        mock_data, analysis = mock_data_and_analysis
        
        # Get questions that have options
        questions_with_options = set(mock_data['options']['qid'])
        
        # Verify these questions exist in analysis
        analysis_qids = set(analysis.questions['qid'])
        missing_questions = questions_with_options - analysis_qids
        assert len(missing_questions) == 0, f"Questions with options should exist in analysis: {missing_questions}"
        
        # Test option mapping for processed radio questions
        radio_questions = analysis.questions[analysis.questions['question_theme_name'] == 'listradio']
        
        for _, question in radio_questions.iterrows():
            qid = question['qid']
            if qid in analysis.processed_responses:
                # Verify processed response uses option text, not codes
                processed_result = analysis.processed_responses[qid]
                if isinstance(processed_result, pd.Series):
                    # Response index should contain meaningful text, not just codes
                    response_labels = processed_result.index.tolist()
                    meaningful_labels = [label for label in response_labels if len(str(label)) > 2]
                    assert len(meaningful_labels) > 0, f"Radio question {qid} should have meaningful option labels"

    def test_response_data_flow_consistency(self, mock_data_and_analysis):
        """Test that response data flows consistently through the pipeline."""
        mock_data, analysis = mock_data_and_analysis
        
        # Verify response column mapping
        original_columns = set(mock_data['responses_user_input'].columns)
        mapped_columns = set(analysis.response_column_codes.index)
        
        # Most columns should be mappable (some might be metadata)
        overlap = original_columns & mapped_columns
        overlap_ratio = len(overlap) / len(original_columns)
        assert overlap_ratio >= 0.7, f"Most response columns should be mappable, got {overlap_ratio:.2%}"
        
        # Test that processed responses can be traced back to original data
        for qid, processed_result in analysis.processed_responses.items():
            question_info = analysis.questions[analysis.questions['qid'] == str(qid)]
            if not question_info.empty:
                question_code = question_info.iloc[0]['title']
                
                # Question code should exist in response mapping
                question_response_codes = analysis.response_column_codes[
                    analysis.response_column_codes['question_code'] == question_code
                ]
                
                if not question_response_codes.empty:
                    # At least one response column should map to this question
                    response_cols = question_response_codes.index.tolist()
                    original_data_cols = set(mock_data['responses_user_input'].columns)
                    mapped_cols = set(response_cols) & original_data_cols
                    assert len(mapped_cols) > 0, f"Question {qid} should have mappable response columns"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 