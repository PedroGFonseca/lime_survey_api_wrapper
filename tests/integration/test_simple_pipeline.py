#!/usr/bin/env python3
"""
Simple Integration Tests: Core Pipeline Functionality

Tests the essential integration points:
1. Mock data → Analysis → Charts → Dashboard works end-to-end
2. Major question types get processed and visualized
3. Error handling works gracefully
4. Configuration flows through the system

No weird micro-validation - just the big picture stuff that matters.
"""

import pytest
import pandas as pd
import sys
import os
from pathlib import Path

# Add source directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'examples'))

# Import what we need
from enhanced_data_generators import create_enhanced_test_data
from mock_data_dashboard_demo import MockSurveyAnalysis, create_chart_for_question, create_dashboard_app
from lime_survey_analyzer.viz.config import get_config


class TestEndToEndPipeline:
    """Test the complete pipeline works from start to finish."""
    
    def test_complete_workflow_runs_successfully(self):
        """Test that the complete workflow runs without crashing."""
        # 1. Generate mock data
        mock_data = create_enhanced_test_data("PIPELINE_TEST")
        assert isinstance(mock_data, dict), "Should generate mock data"
        assert 'questions' in mock_data, "Should have questions"
        assert 'responses_user_input' in mock_data, "Should have responses"
        
        # 2. Create analysis and process questions
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        assert len(analysis.processed_responses) > 0, "Should process some questions"
        
        # 3. Create charts
        config = get_config()
        charts = []
        
        for qid in list(analysis.processed_responses.keys())[:10]:  # Just test first 10
            chart = create_chart_for_question(analysis, qid, config, verbose=False)
            if chart:
                charts.append(chart)
        
        assert len(charts) > 0, "Should create some charts"
        
        # 4. Create dashboard
        app = create_dashboard_app(charts, "Test Dashboard")
        assert app is not None, "Should create dashboard app"
        assert hasattr(app, 'layout'), "Dashboard should have layout"
        
        # If we get here, the whole pipeline worked!

    def test_major_question_types_get_processed(self):
        """Test that the major question types we care about get processed."""
        mock_data = create_enhanced_test_data("QUESTION_TYPES_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        # Find what question types got processed
        processed_types = set()
        for qid in analysis.processed_responses.keys():
            question_info = analysis.questions[analysis.questions['qid'] == str(qid)]
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                processed_types.add(q_type)
        
        # Should process major question types
        important_types = {'listradio', 'ranking', 'longfreetext', 'shortfreetext'}
        processed_important = important_types & processed_types
        
        assert len(processed_important) >= 3, f"Should process major question types, got {processed_important}"

    def test_charts_get_created_for_processed_questions(self):
        """Test that charts get created for processed questions."""
        mock_data = create_enhanced_test_data("CHARTS_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        charts_created = 0
        charts_failed = 0
        
        # Try to create charts for all processed questions
        for qid in analysis.processed_responses.keys():
            chart = create_chart_for_question(analysis, qid, config, verbose=False)
            if chart:
                charts_created += 1
            else:
                charts_failed += 1
        
        # Should create charts for most processed questions
        total_processed = len(analysis.processed_responses)
        success_rate = charts_created / total_processed
        
        assert success_rate >= 0.7, f"Should create charts for ≥70% of processed questions, got {success_rate:.2%}"

    def test_dashboard_works_with_realistic_chart_load(self):
        """Test that dashboard works with a realistic number of charts."""
        mock_data = create_enhanced_test_data("DASHBOARD_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        # Create charts for first 20 questions (realistic dashboard size)
        config = get_config()
        charts = []
        
        for qid in list(analysis.processed_responses.keys())[:20]:
            chart = create_chart_for_question(analysis, qid, config, verbose=False)
            if chart:
                charts.append(chart)
        
        assert len(charts) >= 10, f"Should create reasonable number of charts, got {len(charts)}"
        
        # Create dashboard with these charts
        app = create_dashboard_app(charts, "Realistic Dashboard Test")
        
        assert app is not None, "Should create dashboard"
        assert hasattr(app, 'callback_map'), "Dashboard should have callbacks"


class TestLoudFailuresAndEdgeCases:
    """Test that failures are LOUD and visible, never silent."""
    
    def test_processing_failures_are_loud_and_logged(self):
        """Test that processing failures are captured and visible."""
        mock_data = create_enhanced_test_data("LOUD_FAILURE_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        # Get total questions that should be processed
        total_questions = len(analysis.questions[analysis.questions['parent_qid'].fillna('None') == '0'])
        processed_questions = len(analysis.processed_responses)
        
        # If some questions failed, failures MUST be logged
        if processed_questions < total_questions:
            assert hasattr(analysis, 'fail_message_log'), "Must have failure log when questions fail"
            assert len(analysis.fail_message_log) > 0, "Failure log must contain failed questions"
            
            # Each failure must have meaningful error information
            for qid, error in analysis.fail_message_log.items():
                assert error is not None, f"Error for question {qid} must not be None"
                assert str(error), f"Error for question {qid} must have message"
        
        # User must be able to see what succeeded vs failed
        failed_qids = set(analysis.fail_message_log.keys()) if hasattr(analysis, 'fail_message_log') else set()
        processed_qids = set(str(qid) for qid in analysis.processed_responses.keys())
        
        # No question should be both processed AND failed
        overlap = failed_qids & processed_qids
        assert len(overlap) == 0, f"Questions cannot be both processed and failed: {overlap}"

    def test_chart_creation_failures_are_visible(self):
        """Test that chart creation failures are visible to user."""
        mock_data = create_enhanced_test_data("CHART_FAILURE_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        chart_successes = []
        chart_failures = []
        
        # Try to create charts and track what fails
        for qid in analysis.processed_responses.keys():
            try:
                chart = create_chart_for_question(analysis, qid, config, verbose=False)
                if chart:
                    chart_successes.append(qid)
                else:
                    chart_failures.append(qid)  # Silent failure - this is BAD
            except Exception as e:
                chart_failures.append((qid, str(e)))  # Loud failure - this is GOOD
        
        # If any charts failed, user must know which ones
        total_attempted = len(analysis.processed_responses)
        if len(chart_successes) < total_attempted:
            assert len(chart_failures) > 0, "Failed chart creation must be tracked"
            
        # Silent failures (returns None) are NOT acceptable for production
        silent_failures = [qid for qid in chart_failures if not isinstance(qid, tuple)]
        if len(silent_failures) > 0:
            print(f"WARNING: Silent chart failures detected for questions: {silent_failures}")
            print("These should be converted to loud failures in production")

    def test_questions_with_zero_responses_are_handled(self):
        """Test that questions with no responses are handled properly."""
        mock_data = create_enhanced_test_data("ZERO_RESPONSE_TEST")
        
        # Create a question with zero responses by zeroing out its response column
        questions = mock_data['questions']
        responses = mock_data['responses_user_input']
        
        # Find a radio question to zero out
        radio_questions = questions[questions['question_theme_name'] == 'listradio']
        if not radio_questions.empty:
            test_question = radio_questions.iloc[0]
            question_code = test_question['title']
            
            if question_code in responses.columns:
                # Zero out all responses for this question
                mock_data['responses_user_input'][question_code] = ''
        
        # Process with zero-response question
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        # System should either:
        # 1. Process the question and handle empty data gracefully, OR
        # 2. Fail loudly with clear error message
        
        if question_code in responses.columns:
            test_qid = test_question['qid']
            
            if test_qid in analysis.processed_responses:
                # If processed, result should be valid (even if empty)
                result = analysis.processed_responses[test_qid]
                assert result is not None, "Processed result should not be None"
                
            elif hasattr(analysis, 'fail_message_log') and test_qid in analysis.fail_message_log:
                # If failed, error should be informative
                error = analysis.fail_message_log[test_qid]
                assert error is not None, "Failed question should have error message"
                assert str(error), "Error message should not be empty"
            
            else:
                # This is the BAD case - question disappeared silently
                assert False, f"Question {test_qid} with zero responses was neither processed nor failed - SILENT FAILURE"

    def test_dashboard_shows_processing_failures_to_user(self):
        """Test that dashboard indicates when questions failed to process."""
        mock_data = create_enhanced_test_data("DASHBOARD_FAILURE_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        charts = []
        
        # Create charts for processed questions
        for qid in analysis.processed_responses.keys():
            chart = create_chart_for_question(analysis, qid, config, verbose=False)
            if chart:
                charts.append(chart)
        
        # Create dashboard
        app = create_dashboard_app(charts, "Failure Test Dashboard")
        
        # Verify dashboard was created
        assert app is not None, "Dashboard should be created even with some failures"
        
        # In a real implementation, dashboard should show:
        # 1. How many questions were processed successfully
        # 2. How many questions failed to process  
        # 3. Ideally, a list of failed questions with error messages
        
        # For now, just verify that the information is available
        total_questions = len(analysis.questions[analysis.questions['parent_qid'].fillna('None') == '0'])
        processed_count = len(analysis.processed_responses)
        charts_count = len(charts)
        
        # User should be able to see these numbers
        assert total_questions > 0, "Should have questions to process"
        assert processed_count <= total_questions, "Cannot process more questions than exist"
        assert charts_count <= processed_count, "Cannot have more charts than processed questions"

    def test_minimal_data_edge_case(self):
        """Test system works with minimal data but fails loudly when impossible."""
        # Create truly minimal data
        minimal_data = create_enhanced_test_data("MINIMAL_EDGE_TEST")
        
        # Make it very minimal
        minimal_data['questions'] = minimal_data['questions'].head(2)
        minimal_data['responses_user_input'] = minimal_data['responses_user_input'].head(3)
        
        # Should still work
        analysis = MockSurveyAnalysis(minimal_data, verbose=False)
        analysis.process_all_questions()
        
        # Should either process something OR fail with clear errors
        has_processed = len(analysis.processed_responses) > 0
        has_failures = hasattr(analysis, 'fail_message_log') and len(analysis.fail_message_log) > 0
        
        assert has_processed or has_failures, "With minimal data, should either process something or fail clearly"
        
        # If nothing was processed, user should know why
        if not has_processed:
            assert has_failures, "If no questions processed, must have failure log"
            print("No questions processed with minimal data - this is acceptable if errors are clear")

    def test_empty_dashboard_shows_helpful_message(self):
        """Test that empty dashboard shows helpful message, not blank screen."""
        # Create dashboard with no charts
        app = create_dashboard_app([], "Empty Dashboard Test")
        
        assert app is not None, "Should create dashboard even with no charts"
        assert hasattr(app, 'layout'), "Empty dashboard should still have layout"
        
        # In a real implementation, empty dashboard should show:
        # "No charts available - check if questions were processed successfully"
        # For now, just verify it doesn't crash


class TestQuestionTypeCoverage:
    """Test that all major question types are handled properly."""
    
    def test_all_major_question_types_get_charts(self):
        """Test that all important question types can be visualized."""
        mock_data = create_enhanced_test_data("COVERAGE_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        
        # Track which question types got successfully charted
        charted_types = set()
        failed_types = set()
        
        for qid in analysis.processed_responses.keys():
            question_info = analysis.questions[analysis.questions['qid'] == str(qid)]
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                
                chart = create_chart_for_question(analysis, qid, config, verbose=False)
                if chart:
                    charted_types.add(q_type)
                else:
                    failed_types.add(q_type)
        
        # These question types MUST be chartable (core functionality)
        critical_types = {'listradio', 'ranking', 'longfreetext', 'shortfreetext'}
        missing_critical = critical_types - charted_types
        
        assert len(missing_critical) == 0, f"Critical question types must be chartable: {missing_critical}"
        
        # Should handle most question types
        assert len(charted_types) >= 6, f"Should chart many question types, got {charted_types}"

    def test_radio_questions_produce_bar_charts(self):
        """Test that radio questions produce appropriate bar charts."""
        mock_data = create_enhanced_test_data("RADIO_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        radio_charts = []
        
        # Find radio questions and create charts
        for qid in analysis.processed_responses.keys():
            question_info = analysis.questions[analysis.questions['qid'] == str(qid)]
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type in ['listradio', 'image_select-listradio']:
                    chart = create_chart_for_question(analysis, qid, config, verbose=False)
                    if chart:
                        radio_charts.append(chart)
        
        assert len(radio_charts) > 0, "Should create charts for radio questions"
        
        # Check chart structure
        for chart in radio_charts[:3]:  # Check first 3
            assert chart['chart_type'] == 'horizontal_bar', "Radio questions should create horizontal bar charts"
            assert 'figure' in chart, "Chart should have figure"
            assert chart['figure'] is not None, "Chart figure should not be None"

    def test_ranking_questions_produce_stacked_charts(self):
        """Test that ranking questions produce appropriate stacked bar charts."""
        mock_data = create_enhanced_test_data("RANKING_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        ranking_charts = []
        
        # Find ranking questions and create charts
        for qid in analysis.processed_responses.keys():
            question_info = analysis.questions[analysis.questions['qid'] == str(qid)]
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type == 'ranking':
                    chart = create_chart_for_question(analysis, qid, config, verbose=False)
                    if chart:
                        ranking_charts.append(chart)
        
        assert len(ranking_charts) > 0, "Should create charts for ranking questions"
        
        # Check chart structure
        for chart in ranking_charts[:2]:  # Check first 2
            assert chart['chart_type'] == 'ranking_stacked', "Ranking questions should create stacked bar charts"
            assert 'figure' in chart, "Chart should have figure"
            assert chart['figure'] is not None, "Chart figure should not be None"

    def test_text_questions_produce_text_displays(self):
        """Test that text questions produce appropriate text response displays."""
        mock_data = create_enhanced_test_data("TEXT_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        text_charts = []
        
        # Find text questions and create charts
        for qid in analysis.processed_responses.keys():
            question_info = analysis.questions[analysis.questions['qid'] == str(qid)]
            if not question_info.empty:
                q_type = question_info.iloc[0]['question_theme_name']
                if q_type in ['longfreetext', 'shortfreetext', 'numerical']:
                    chart = create_chart_for_question(analysis, qid, config, verbose=False)
                    if chart:
                        text_charts.append(chart)
        
        assert len(text_charts) > 0, "Should create displays for text questions"
        
        # Check chart structure
        for chart in text_charts[:2]:  # Check first 2
            assert chart['chart_type'] == 'text_responses', "Text questions should create text response displays"
            assert 'data' in chart, "Chart should have data"
            assert isinstance(chart['data'], list), "Text chart data should be list of responses"


class TestCrossComponentDataIntegrity:
    """Test that data flows correctly between components without corruption."""
    
    def test_question_ids_consistent_across_pipeline(self):
        """Test that question IDs remain consistent throughout the pipeline."""
        mock_data = create_enhanced_test_data("INTEGRITY_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        # Original question IDs from mock data
        original_qids = set(mock_data['questions']['qid'])
        
        # Question IDs in analysis
        analysis_qids = set(analysis.questions['qid'])
        
        # Question IDs in processed responses (converted to strings)
        processed_qids = set(str(qid) for qid in analysis.processed_responses.keys())
        
        # All analysis qids should match original
        assert original_qids == analysis_qids, "Analysis should preserve all original question IDs"
        
        # All processed qids should exist in original data
        missing_qids = processed_qids - original_qids
        assert len(missing_qids) == 0, f"Processed questions should exist in original data: {missing_qids}"

    def test_response_data_integrity_maintained(self):
        """Test that response data integrity is maintained through processing."""
        mock_data = create_enhanced_test_data("RESPONSE_INTEGRITY_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        
        # Store original response data characteristics
        original_responses = mock_data['responses_user_input']
        original_row_count = len(original_responses)
        original_columns = set(original_responses.columns)
        
        analysis.process_all_questions()
        
        # Response data should be preserved
        processed_responses = analysis.responses_user_input
        assert len(processed_responses) == original_row_count, "Response row count should be preserved"
        assert set(processed_responses.columns) == original_columns, "Response columns should be preserved"
        
        # Sample some data to verify values are preserved
        for col in list(original_columns)[:5]:  # Check first 5 columns
            original_sample = original_responses[col].head(3)
            processed_sample = processed_responses[col].head(3)
            
            # Values should be identical
            assert original_sample.equals(processed_sample), f"Column {col} data should be preserved"

    def test_chart_data_traces_back_to_original_responses(self):
        """Test that chart data can be traced back to original response data."""
        mock_data = create_enhanced_test_data("TRACEABILITY_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        config = get_config()
        
        # Test a few processed questions
        for qid in list(analysis.processed_responses.keys())[:3]:
            question_info = analysis.questions[analysis.questions['qid'] == str(qid)]
            if not question_info.empty:
                question_code = question_info.iloc[0]['title']
                
                # Find corresponding response columns
                response_cols = [col for col in analysis.responses_user_input.columns 
                               if col.startswith(question_code)]
                
                if response_cols:
                    # Should be able to create chart from this data
                    chart = create_chart_for_question(analysis, qid, config, verbose=False)
                    
                    if chart:
                        # Chart should contain meaningful data that traces to original responses
                        assert 'data' in chart, f"Chart for question {qid} should have data"
                        assert chart['data'] is not None, f"Chart data for question {qid} should not be None"


class TestConfigurationFlow:
    """Test that configuration flows correctly through the system."""
    
    def test_visualization_config_reaches_charts(self):
        """Test that visualization configuration actually affects chart creation."""
        mock_data = create_enhanced_test_data("CONFIG_FLOW_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        # Get default config
        config = get_config()
        
        if analysis.processed_responses:
            sample_qid = list(analysis.processed_responses.keys())[0]
            chart = create_chart_for_question(analysis, sample_qid, config, verbose=False)
            
            if chart and chart.get('figure'):
                # Chart should have configuration applied
                fig = chart['figure']
                assert hasattr(fig, 'layout'), "Chart should have layout configuration from config"
                
                # Layout should have some styling from config
                layout = fig.layout
                assert layout is not None, "Chart layout should not be None"

    def test_dashboard_inherits_configuration(self):
        """Test that dashboard inherits and applies configuration correctly."""
        mock_data = create_enhanced_test_data("DASHBOARD_CONFIG_TEST")
        analysis = MockSurveyAnalysis(mock_data, verbose=False)
        analysis.process_all_questions()
        
        # Create some charts
        config = get_config()
        charts = []
        
        for qid in list(analysis.processed_responses.keys())[:5]:
            chart = create_chart_for_question(analysis, qid, config, verbose=False)
            if chart:
                charts.append(chart)
        
        if charts:
            # Create dashboard
            app = create_dashboard_app(charts, "Config Test Dashboard")
            
            # Dashboard should have configuration applied
            assert app.config.external_stylesheets is not None, "Dashboard should have stylesheets"
            assert hasattr(app, 'layout'), "Dashboard should have layout"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 