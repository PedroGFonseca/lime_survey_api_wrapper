#!/usr/bin/env python3
"""
Integration Tests: Enhanced Mock Data Generation

Tests that the enhanced mock data generator produces data structures and patterns
that accurately represent real LimeSurvey data for reliable testing.

Focus: Data structure validation, format compliance, and realistic distributions.
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

# Import our enhanced data generator
from enhanced_data_generators import create_enhanced_test_data, EnhancedSurveyDataGenerator


class TestMockDataStructureCompliance:
    """Test that generated mock data matches real LimeSurvey API formats."""
    
    @pytest.fixture
    def mock_survey_data(self):
        """Generate test survey data."""
        return create_enhanced_test_data(survey_id="STRUCTURE_TEST_111")
    
    def test_questions_dataframe_structure(self, mock_survey_data):
        """Test that questions DataFrame matches expected LimeSurvey structure."""
        questions = mock_survey_data['questions']
        
        # Verify DataFrame type and non-empty
        assert isinstance(questions, pd.DataFrame), "Questions should be a DataFrame"
        assert not questions.empty, "Questions DataFrame should not be empty"
        
        # Verify required columns exist
        required_columns = [
            'qid', 'parent_qid', 'sid', 'gid', 'type', 'title', 'question',
            'question_theme_name', 'question_order', 'mandatory', 'other'
        ]
        
        for col in required_columns:
            assert col in questions.columns, f"Questions should have '{col}' column"
        
        # Verify data types
        assert questions['qid'].dtype == 'object', "qid should be string type"
        assert questions['parent_qid'].dtype == 'object', "parent_qid should be string type"
        assert questions['question_order'].dtype in ['int64', 'int32'], "question_order should be integer"
        
        # Verify question theme names are realistic
        valid_themes = {
            'listradio', 'ranking', 'longfreetext', 'shortfreetext', 'numerical',
            'multipleshorttext', 'multiplechoice', 'arrays/increasesamedecrease',
            'image_select-listradio', 'image_select-multiplechoice', 'equation'
        }
        
        actual_themes = set(questions['question_theme_name'].unique())
        invalid_themes = actual_themes - valid_themes
        assert len(invalid_themes) == 0, f"All question themes should be valid, found invalid: {invalid_themes}"
        
        # Verify parent_qid relationships
        main_questions = questions[questions['parent_qid'] == '0']
        sub_questions = questions[questions['parent_qid'] != '0']
        
        assert len(main_questions) > 0, "Should have main questions with parent_qid='0'"
        
        # All sub-questions should have valid parent IDs
        if not sub_questions.empty:
            parent_qids = set(main_questions['qid'])
            invalid_parents = set(sub_questions['parent_qid']) - parent_qids
            assert len(invalid_parents) == 0, f"All sub-questions should have valid parent qids: {invalid_parents}"

    def test_options_dataframe_structure(self, mock_survey_data):
        """Test that options DataFrame matches expected LimeSurvey structure."""
        options = mock_survey_data['options']
        questions = mock_survey_data['questions']
        
        assert isinstance(options, pd.DataFrame), "Options should be a DataFrame"
        assert not options.empty, "Options DataFrame should not be empty"
        
        # Verify required columns
        required_columns = ['qid', 'option_code', 'answer', 'question_code']
        for col in required_columns:
            assert col in options.columns, f"Options should have '{col}' column"
        
        # Verify data types
        assert options['qid'].dtype == 'object', "qid should be string type"
        assert options['option_code'].dtype == 'object', "option_code should be string type"
        
        # Verify all option qids exist in questions
        option_qids = set(options['qid'])
        question_qids = set(questions['qid'])
        orphaned_options = option_qids - question_qids
        assert len(orphaned_options) == 0, f"All options should link to valid questions: {orphaned_options}"
        
        # Verify option codes are meaningful
        for _, option in options.head(10).iterrows():  # Check first 10
            assert len(str(option['option_code'])) > 0, "Option codes should not be empty"
            assert len(str(option['answer'])) > 0, "Option answers should not be empty"

    def test_responses_dataframe_structure(self, mock_survey_data):
        """Test that responses DataFrame matches expected LimeSurvey structure."""
        responses = mock_survey_data['responses_user_input']
        metadata = mock_survey_data['responses_metadata']
        
        # Verify basic structure
        assert isinstance(responses, pd.DataFrame), "Responses should be a DataFrame"
        assert isinstance(metadata, pd.DataFrame), "Metadata should be a DataFrame"
        assert not responses.empty, "Responses should not be empty"
        assert not metadata.empty, "Metadata should not be empty"
        
        # Verify row counts relationship (metadata keeps all, responses filtered to complete)
        assert len(responses) <= len(metadata), "Responses should be subset of metadata (incomplete filtered out)"
        assert len(responses) > 0, "Should have some completed responses"
        assert len(metadata) > 0, "Should have metadata for all responses"
        
        # Typical completion rate should be reasonable (not 100% or 0%)
        completion_rate = len(responses) / len(metadata)
        assert 0.3 <= completion_rate <= 0.9, f"Completion rate should be reasonable, got {completion_rate:.2%}"
        
        # Verify metadata columns
        expected_metadata_cols = ['id', 'submitdate', 'lastpage', 'startdate', 'datestamp']
        for col in expected_metadata_cols:
            assert col in metadata.columns, f"Metadata should have '{col}' column"
        
        # Verify response column patterns (should match LimeSurvey naming)
        response_columns = responses.columns.tolist()
        
        # Should have simple question codes
        simple_codes = [col for col in response_columns if len(col) <= 10 and col.isalnum()]
        assert len(simple_codes) > 10, f"Should have simple question codes, found {len(simple_codes)}"
        
        # Should have ranking pattern columns (e.g., G02Q01[SQ006])
        ranking_pattern = [col for col in response_columns if '[' in col and ']' in col]
        assert len(ranking_pattern) > 5, f"Should have ranking pattern columns, found {len(ranking_pattern)}"

    def test_survey_metadata_structure(self, mock_survey_data):
        """Test that survey metadata matches expected formats."""
        properties = mock_survey_data['properties']
        summary = mock_survey_data['summary']
        groups = mock_survey_data['groups']
        
        # Verify properties structure
        assert isinstance(properties, dict), "Properties should be a dictionary"
        expected_props = ['sid', 'admin', 'active', 'language', 'datecreated']
        for prop in expected_props:
            assert prop in properties, f"Properties should have '{prop}' field"
        
        # Verify summary structure
        assert isinstance(summary, dict), "Summary should be a dictionary"
        expected_summary = ['completed_responses', 'incomplete_responses', 'full_responses']
        for field in expected_summary:
            assert field in summary, f"Summary should have '{field}' field"
            assert isinstance(summary[field], int), f"Summary {field} should be integer"
        
        # Verify groups structure
        assert isinstance(groups, list), "Groups should be a list"
        assert len(groups) > 0, "Should have at least one group"
        
        for group in groups:
            assert isinstance(group, dict), "Each group should be a dictionary"
            assert 'gid' in group, "Group should have gid"
            assert 'group_name' in group, "Group should have group_name"


class TestMockDataRealism:
    """Test that generated data has realistic patterns and distributions."""
    
    @pytest.fixture
    def mock_survey_data(self):
        """Generate test survey data."""
        return create_enhanced_test_data(survey_id="REALISM_TEST_222")
    
    def test_question_type_distribution_realistic(self, mock_survey_data):
        """Test that question type distribution matches real survey patterns."""
        questions = mock_survey_data['questions']
        
        # Get distribution of question types
        type_counts = questions['question_theme_name'].value_counts()
        
        # listradio should be most common (like in real surveys)
        assert type_counts.get('listradio', 0) >= 10, "Should have many radio questions like real surveys"
        
        # ranking should be well represented
        assert type_counts.get('ranking', 0) >= 5, "Should have multiple ranking questions"
        
        # text questions should exist
        text_questions = type_counts.get('longfreetext', 0) + type_counts.get('shortfreetext', 0)
        assert text_questions >= 3, "Should have text questions"
        
        # Should have diversity (at least 8 different types)
        assert len(type_counts) >= 8, f"Should have diverse question types, got {len(type_counts)}"

    def test_response_completion_patterns_realistic(self, mock_survey_data):
        """Test that response completion patterns match real survey behavior."""
        responses = mock_survey_data['responses_user_input']
        metadata = mock_survey_data['responses_metadata']
        summary = mock_survey_data['summary']
        
        # Verify completion rates are realistic
        completed = summary['completed_responses']
        incomplete = summary['incomplete_responses']
        total = summary['full_responses']
        
        assert total == completed + incomplete, "Total should equal completed + incomplete"
        
        completion_rate = completed / total
        assert 0.4 <= completion_rate <= 0.8, f"Completion rate should be realistic (40-80%), got {completion_rate:.2%}"
        
        # Verify completed responses have submit dates
        completed_responses = metadata[metadata['submitdate'].notna()]
        assert len(completed_responses) == completed, "Completed responses should have submit dates"
        
        # Verify incomplete responses don't have submit dates
        incomplete_responses = metadata[metadata['submitdate'].isna()]
        assert len(incomplete_responses) == incomplete, "Incomplete responses should not have submit dates"

    def test_response_data_realistic_patterns(self, mock_survey_data):
        """Test that response data has realistic answer patterns."""
        responses = mock_survey_data['responses_user_input']
        questions = mock_survey_data['questions']
        
        # Test radio question response patterns
        radio_questions = questions[questions['question_theme_name'] == 'listradio']['title'].tolist()
        
        for question_code in radio_questions[:3]:  # Test first 3
            if question_code in responses.columns:
                response_col = responses[question_code]
                
                # Should have realistic response distribution (not all same answer)
                value_counts = response_col.value_counts(dropna=False)
                
                if len(value_counts) > 1:
                    # No single answer should dominate completely
                    max_responses = value_counts.max()
                    total_responses = value_counts.sum()
                    max_percentage = max_responses / total_responses
                    
                    assert max_percentage < 0.9, f"No answer should dominate >90% for {question_code}"
                
                # Should have some missing responses (realistic)
                missing_responses = response_col.isna().sum() + (response_col == '').sum()
                missing_rate = missing_responses / len(response_col)
                assert missing_rate < 0.2, f"Missing rate should be <20% for {question_code}"

    def test_basic_response_data_structure(self, mock_survey_data):
        """Test that response data has basic expected structure."""
        responses = mock_survey_data['responses_user_input']
        
        # Should have realistic number of response columns
        assert len(responses.columns) > 50, f"Should have many response columns, got {len(responses.columns)}"
        
        # Should have mix of simple and complex column names (ranking patterns)
        simple_cols = [col for col in responses.columns if '[' not in col]
        complex_cols = [col for col in responses.columns if '[' in col and ']' in col]
        
        assert len(simple_cols) > 10, "Should have simple question columns"
        assert len(complex_cols) > 5, "Should have ranking/multiple choice patterns"


class TestMockDataGeneratorConfiguration:
    """Test that the data generator can be configured for different scenarios."""
    
    def test_custom_response_volumes(self):
        """Test that generator can create surveys with different response volumes."""
        # Small survey
        small_generator = EnhancedSurveyDataGenerator(
            survey_id="SMALL_TEST",
            completed_responses=50,
            incomplete_responses=30
        )
        small_data = small_generator.generate_complete_survey_dataset()
        
        assert len(small_data['responses_user_input']) == 50
        assert len(small_data['responses_metadata']) == 80  # 50 + 30
        assert small_data['summary']['completed_responses'] == 50
        assert small_data['summary']['incomplete_responses'] == 30
        
        # Large survey
        large_generator = EnhancedSurveyDataGenerator(
            survey_id="LARGE_TEST", 
            completed_responses=1000,
            incomplete_responses=500
        )
        large_data = large_generator.generate_complete_survey_dataset()
        
        assert len(large_data['responses_user_input']) == 1000
        assert len(large_data['responses_metadata']) == 1500  # 1000 + 500
        
    def test_consistent_data_generation(self):
        """Test that generator produces consistent data structures across runs."""
        # Generate data twice with same parameters
        data1 = create_enhanced_test_data("CONSISTENCY_TEST_A")
        data2 = create_enhanced_test_data("CONSISTENCY_TEST_B")
        
        # Structure should be consistent
        assert len(data1['questions']) == len(data2['questions']), "Question count should be consistent"
        assert len(data1['responses_user_input']) == len(data2['responses_user_input']), "Response count should be consistent"
        
        # Column structures should match
        assert set(data1['questions'].columns) == set(data2['questions'].columns), "Question columns should be consistent"
        assert set(data1['options'].columns) == set(data2['options'].columns), "Option columns should be consistent"
        
        # Question type distributions should be similar
        types1 = data1['questions']['question_theme_name'].value_counts()
        types2 = data2['questions']['question_theme_name'].value_counts()
        
        # Should have same question types available
        assert set(types1.index) == set(types2.index), "Question types should be consistent"

    def test_data_format_edge_cases(self):
        """Test that generator handles edge cases gracefully."""
        # Minimal data
        minimal_generator = EnhancedSurveyDataGenerator(
            survey_id="MINIMAL_TEST",
            completed_responses=5,
            incomplete_responses=2
        )
        minimal_data = minimal_generator.generate_complete_survey_dataset()
        
        # Should still create valid structure
        assert isinstance(minimal_data['questions'], pd.DataFrame)
        assert isinstance(minimal_data['responses_user_input'], pd.DataFrame)
        assert len(minimal_data['questions']) > 0
        assert len(minimal_data['responses_user_input']) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 