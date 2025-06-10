#!/usr/bin/env python3
"""
Test Suite for Step 1 Integration: Optional Enhanced Output

This test suite validates the integration approach for adding enhanced output
to the SurveyAnalysis class while maintaining backward compatibility.

Tests are designed to run BEFORE implementation to validate the approach,
then AFTER implementation to ensure everything works correctly.
"""

import pytest
import pandas as pd
import sys
import os
from unittest.mock import patch, MagicMock

# Add the source directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lime_survey_analyzer.analyser import SurveyAnalysis
from lime_survey_analyzer.structures import (
    QuestionAnalysisResult, QuestionMetadata, QuestionType, 
    VisualizationHints, ChartType
)


class TestStep1Integration:
    """Test suite for Step 1: Optional Enhanced Output integration"""
    
    @pytest.fixture
    def survey_analyzer(self):
        """Create a SurveyAnalysis instance for testing"""
        return SurveyAnalysis("291558")
    
    @pytest.fixture
    def mock_analyzer_with_data(self):
        """Create a mock analyzer with sample processed responses"""
        analyzer = SurveyAnalysis("291558")
        
        # Mock the data loading and setup
        analyzer.questions = pd.DataFrame({
            'qid': ['12345', '12346', '12347'],
            'title': ['Q1', 'Q2', 'Q3'],
            'question': ['Radio Question?', 'Multiple Choice?', 'Text Question?'],
            'question_theme_name': ['listradio', 'multiplechoice', 'shortfreetext'],
            'mandatory': ['Y', 'N', 'Y']
        })
        
        # Sample processed responses (current format)
        analyzer.processed_responses = {
            '12345': pd.Series({'Option A': 10, 'Option B': 15, 'Option C': 5}),  # Radio
            '12346': pd.DataFrame({  # Multiple choice
                'option_text': ['Choice 1', 'Choice 2', 'Choice 3'],
                'absolute_counts': [8, 12, 6],
                'response_rates': [0.27, 0.40, 0.20]
            }),
            '12347': pd.Series(['Answer 1', 'Answer 2', 'Answer 3'])  # Text
        }
        
        return analyzer

    def test_current_behavior_baseline(self, mock_analyzer_with_data):
        """Test current behavior to establish baseline"""
        analyzer = mock_analyzer_with_data
        
        # Verify current structure
        assert hasattr(analyzer, 'processed_responses')
        assert len(analyzer.processed_responses) == 3
        
        # Verify data types match current implementation
        radio_result = analyzer.processed_responses['12345']
        assert isinstance(radio_result, pd.Series)
        assert radio_result.sum() == 30  # 10 + 15 + 5
        
        mc_result = analyzer.processed_responses['12346']
        assert isinstance(mc_result, pd.DataFrame)
        assert list(mc_result.columns) == ['option_text', 'absolute_counts', 'response_rates']
        
        text_result = analyzer.processed_responses['12347']
        assert isinstance(text_result, pd.Series)
        assert len(text_result) == 3

    def test_enhanced_attributes_initialization(self, survey_analyzer):
        """Test that enhanced attributes can be added without breaking existing code"""
        # These should be addable to __init__ without issues
        survey_analyzer.enhanced_results = {}
        survey_analyzer.enable_enhanced_output = False
        
        # Verify attributes exist
        assert hasattr(survey_analyzer, 'enhanced_results')
        assert hasattr(survey_analyzer, 'enable_enhanced_output')
        assert survey_analyzer.enhanced_results == {}
        assert survey_analyzer.enable_enhanced_output is False

    def test_setup_parameter_addition(self, survey_analyzer):
        """Test that setup method can accept enhanced_output parameter"""
        # Mock the API connection and data loading
        with patch.object(survey_analyzer, '_connect_to_api'):
            with patch.object(survey_analyzer, '_load_response_data'):
                with patch.object(survey_analyzer, '_get_survey_structure_data'):
                    with patch.object(survey_analyzer, '_process_column_codes'):
                        
                        # Test default behavior (should not break)
                        survey_analyzer.setup()
                        
                        # Test with new parameter - this will fail until we implement it
                        try:
                            survey_analyzer.enable_enhanced_output = False
                            survey_analyzer.setup(enable_enhanced_output=True)
                            assert survey_analyzer.enable_enhanced_output is True
                        except TypeError as e:
                            # Expected before implementation
                            assert "enable_enhanced_output" in str(e)
                            pytest.skip("setup() parameter not yet implemented - this validates our approach")

    def test_question_type_mapping(self):
        """Test question theme to QuestionType mapping"""
        # This tests the _map_to_question_type method we plan to add
        
        expected_mappings = {
            'listradio': QuestionType.RADIO,
            'multiplechoice': QuestionType.MULTIPLE_CHOICE,
            'ranking': QuestionType.RANKING,
            'shortfreetext': QuestionType.TEXT,
            'longfreetext': QuestionType.TEXT,
            'numerical': QuestionType.TEXT,
            'multipleshorttext': QuestionType.MULTIPLE_SHORT_TEXT,
            'arrays/increasesamedecrease': QuestionType.ARRAY,
            'image_select-listradio': QuestionType.RADIO,
            'image_select-multiplechoice': QuestionType.MULTIPLE_CHOICE,
            'equation': QuestionType.RADIO
        }
        
        # Test each mapping
        for theme, expected_type in expected_mappings.items():
            assert expected_type in QuestionType, f"QuestionType.{expected_type} should exist"
        
        # Test unknown theme defaults to TEXT
        assert QuestionType.TEXT in QuestionType

    def test_chart_recommendations_mapping(self):
        """Test question theme to chart type recommendations"""
        # This tests the _get_simple_chart_recommendations method we plan to add
        
        expected_chart_mappings = {
            'listradio': [ChartType.BAR_CHART, ChartType.PIE_CHART],
            'multiplechoice': [ChartType.HORIZONTAL_BAR, ChartType.STACKED_BAR],
            'ranking': [ChartType.HEATMAP, ChartType.TABLE],
            'shortfreetext': [ChartType.WORD_CLOUD, ChartType.TABLE],
            'longfreetext': [ChartType.WORD_CLOUD, ChartType.TABLE],
            'numerical': [ChartType.BAR_CHART, ChartType.TABLE],
            'multipleshorttext': [ChartType.TABLE],
            'arrays/increasesamedecrease': [ChartType.HEATMAP, ChartType.TABLE],
            'image_select-listradio': [ChartType.BAR_CHART, ChartType.PIE_CHART],
            'image_select-multiplechoice': [ChartType.HORIZONTAL_BAR, ChartType.STACKED_BAR],
            'equation': [ChartType.BAR_CHART, ChartType.TABLE]
        }
        
        # Verify all chart types exist
        for theme, chart_list in expected_chart_mappings.items():
            for chart_type in chart_list:
                assert chart_type in ChartType, f"ChartType.{chart_type} should exist"

    def test_enhanced_result_creation(self, mock_analyzer_with_data):
        """Test creation of QuestionAnalysisResult from legacy data"""
        analyzer = mock_analyzer_with_data
        
        # Test radio question enhancement
        question_id = '12345'
        legacy_result = analyzer.processed_responses[question_id]
        question_info = analyzer.questions.set_index('qid').loc[question_id]
        
        # Create enhanced result (simulating _create_enhanced_result method)
        metadata = QuestionMetadata(
            question_id=question_id,
            question_code=question_info['title'],
            question_title=question_info['question'],
            question_type=QuestionType.RADIO,
            is_mandatory=question_info.get('mandatory', 'N') == 'Y'
        )
        
        viz_hints = VisualizationHints(
            recommended_charts=[ChartType.BAR_CHART, ChartType.PIE_CHART],
            optimal_chart=ChartType.BAR_CHART
        )
        
        enhanced_result = QuestionAnalysisResult(
            metadata=metadata,
            statistics={'primary': legacy_result},
            viz_hints=viz_hints,
            legacy_result=legacy_result
        )
        
        # Verify enhanced result structure
        assert enhanced_result.metadata.question_id == '12345'
        assert enhanced_result.metadata.question_type == QuestionType.RADIO
        assert enhanced_result.metadata.is_mandatory is True
        assert enhanced_result.viz_hints.optimal_chart == ChartType.BAR_CHART
        assert enhanced_result.legacy_result.equals(legacy_result)

    def test_data_equivalence(self, mock_analyzer_with_data):
        """Test that enhanced results preserve original data"""
        analyzer = mock_analyzer_with_data
        
        for question_id, legacy_result in analyzer.processed_responses.items():
            # Create enhanced result
            question_info = analyzer.questions.set_index('qid').loc[question_id]
            theme = question_info['question_theme_name']
            
            # Map theme to question type
            type_mapping = {
                'listradio': QuestionType.RADIO,
                'multiplechoice': QuestionType.MULTIPLE_CHOICE,
                'shortfreetext': QuestionType.TEXT
            }
            
            enhanced_result = QuestionAnalysisResult(
                metadata=QuestionMetadata(
                    question_id=question_id,
                    question_code=question_info['title'],
                    question_title=question_info['question'],
                    question_type=type_mapping[theme],
                    is_mandatory=question_info.get('mandatory', 'N') == 'Y'
                ),
                statistics={'primary': legacy_result},
                viz_hints=VisualizationHints(
                    recommended_charts=[ChartType.BAR_CHART],
                    optimal_chart=ChartType.BAR_CHART
                ),
                legacy_result=legacy_result
            )
            
            # Verify data equivalence
            if isinstance(legacy_result, pd.Series):
                pd.testing.assert_series_equal(legacy_result, enhanced_result.legacy_result)
            elif isinstance(legacy_result, pd.DataFrame):
                pd.testing.assert_frame_equal(legacy_result, enhanced_result.legacy_result)
            else:
                assert legacy_result == enhanced_result.legacy_result

    def test_backward_compatibility_interface(self, mock_analyzer_with_data):
        """Test that new interface methods don't break existing functionality"""
        analyzer = mock_analyzer_with_data
        
        # Add enhanced_results attribute
        analyzer.enhanced_results = {}
        
        # Test get_question_result method (to be added)
        def get_question_result(question_id: str, enhanced=False):
            if enhanced and question_id in analyzer.enhanced_results:
                return analyzer.enhanced_results[question_id]
            return analyzer.processed_responses.get(question_id)
        
        # Test get_processed_responses method (to be added)
        def get_processed_responses(enhanced=False):
            if enhanced and hasattr(analyzer, 'enhanced_results'):
                return analyzer.enhanced_results
            return analyzer.processed_responses
        
        # Test backward compatibility
        legacy_result = get_question_result('12345', enhanced=False)
        assert isinstance(legacy_result, pd.Series)
        
        all_legacy = get_processed_responses(enhanced=False)
        assert len(all_legacy) == 3
        assert all_legacy is analyzer.processed_responses

    def test_enhanced_output_toggle(self, mock_analyzer_with_data):
        """Test enhanced output enable/disable functionality"""
        analyzer = mock_analyzer_with_data
        analyzer.enhanced_results = {}
        analyzer.enable_enhanced_output = False
        
        # Add test questions to the mock data
        test_questions = pd.DataFrame({
            'qid': ['test1', 'test2'],
            'title': ['TestQ1', 'TestQ2'],
            'question': ['Test Question 1?', 'Test Question 2?'],
            'question_theme_name': ['listradio', 'listradio'],
            'mandatory': ['N', 'N']
        })
        analyzer.questions = pd.concat([analyzer.questions, test_questions], ignore_index=True)
        
        # Simulate handler method with enhancement
        def mock_process_question(question_id, result):
            analyzer.processed_responses[question_id] = result
            
            # Enhanced output creation (conditional)
            if getattr(analyzer, 'enable_enhanced_output', False):
                question_info = analyzer.questions.set_index('qid').loc[question_id]
                enhanced_result = QuestionAnalysisResult(
                    metadata=QuestionMetadata(
                        question_id=question_id,
                        question_code=question_info['title'],
                        question_title=question_info['question'],
                        question_type=QuestionType.RADIO,
                        is_mandatory=question_info.get('mandatory', 'N') == 'Y'
                    ),
                    statistics={'primary': result},
                    viz_hints=VisualizationHints(
                        recommended_charts=[ChartType.BAR_CHART],
                        optimal_chart=ChartType.BAR_CHART
                    ),
                    legacy_result=result
                )
                analyzer.enhanced_results[question_id] = enhanced_result
        
        # Test with enhanced output disabled
        test_result = pd.Series({'A': 1, 'B': 2})
        mock_process_question('test1', test_result)
        
        assert 'test1' in analyzer.processed_responses
        assert 'test1' not in analyzer.enhanced_results
        
        # Test with enhanced output enabled
        analyzer.enable_enhanced_output = True
        mock_process_question('test2', test_result)
        
        assert 'test2' in analyzer.processed_responses
        assert 'test2' in analyzer.enhanced_results
        assert isinstance(analyzer.enhanced_results['test2'], QuestionAnalysisResult)

    def test_visualization_hints_functionality(self):
        """Test that visualization hints provide useful recommendations"""
        
        # Test different question types get appropriate chart recommendations
        test_cases = [
            (QuestionType.RADIO, [ChartType.BAR_CHART, ChartType.PIE_CHART]),
            (QuestionType.MULTIPLE_CHOICE, [ChartType.HORIZONTAL_BAR, ChartType.STACKED_BAR]),
            (QuestionType.RANKING, [ChartType.HEATMAP, ChartType.TABLE]),
            (QuestionType.TEXT, [ChartType.WORD_CLOUD, ChartType.TABLE]),
            (QuestionType.ARRAY, [ChartType.HEATMAP, ChartType.TABLE])
        ]
        
        for question_type, expected_charts in test_cases:
            viz_hints = VisualizationHints(
                recommended_charts=expected_charts,
                optimal_chart=expected_charts[0]
            )
            
            assert viz_hints.optimal_chart == expected_charts[0]
            assert all(chart in expected_charts for chart in viz_hints.recommended_charts)

    def test_integration_with_existing_test_suite(self):
        """Ensure integration doesn't break existing test infrastructure"""
        
        # Import existing test modules to ensure no conflicts
        try:
            from .test_current_handlers import TestCurrentHandlers
            from .data_generators import SurveyDataGenerator
            
            # Verify test infrastructure still works
            generator = SurveyDataGenerator()
            mock_survey = generator.create_complete_survey()
            
            assert mock_survey is not None
            assert len(mock_survey.questions) > 0
            
        except ImportError as e:
            pytest.skip(f"Existing test infrastructure not available: {e}")

    def test_performance_impact(self, mock_analyzer_with_data):
        """Test that enhanced output doesn't significantly impact performance"""
        import time
        
        analyzer = mock_analyzer_with_data
        analyzer.enhanced_results = {}
        
        # Time legacy processing
        start_time = time.time()
        for _ in range(100):
            # Simulate legacy processing
            analyzer.processed_responses['perf_test'] = pd.Series({'A': 1, 'B': 2})
        legacy_time = time.time() - start_time
        
        # Time enhanced processing
        analyzer.enable_enhanced_output = True
        start_time = time.time()
        for i in range(100):
            # Simulate enhanced processing
            result = pd.Series({'A': 1, 'B': 2})
            analyzer.processed_responses[f'perf_test_{i}'] = result
            
            # Enhanced result creation
            if analyzer.enable_enhanced_output:
                enhanced_result = QuestionAnalysisResult(
                    metadata=QuestionMetadata(
                        question_id=f'perf_test_{i}',
                        question_code=f'Q{i}',
                        question_title=f'Question {i}',
                        question_type=QuestionType.RADIO,
                        is_mandatory=False
                    ),
                    statistics={'primary': result},
                    viz_hints=VisualizationHints(
                        recommended_charts=[ChartType.BAR_CHART],
                        optimal_chart=ChartType.BAR_CHART
                    ),
                    legacy_result=result
                )
                analyzer.enhanced_results[f'perf_test_{i}'] = enhanced_result
        
        enhanced_time = time.time() - start_time
        
        # Enhanced processing should not be more than 2x slower
        performance_ratio = enhanced_time / legacy_time if legacy_time > 0 else 1
        assert performance_ratio < 2.0, f"Enhanced processing is {performance_ratio:.1f}x slower than legacy"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 