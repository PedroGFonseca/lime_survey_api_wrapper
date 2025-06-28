"""
Survey Analysis Module

This module provides a backward-compatible interface for survey analysis functions.
It imports from the main lime_survey_analyzer.analysis module.
"""

import sys
import os

# Add the src directory to the path so we can import lime_survey_analyzer
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Import all analysis functions from the main package
from lime_survey_analyzer.analyser import (
    get_response_data,
    get_columns_codes_for_responses_user_input,
    _get_questions,
    _get_raw_options_data,
    _process_options_data,
    _enrich_options_data_with_question_codes
)

import pandas as pd
import json
import os
from pathlib import Path

# Also import the main classes for comprehensive analysis
from lime_survey_analyzer import SurveyAnalysis, LimeSurveyClient

# Additional imports for compatibility


def get_response_stats_multiple_choice(question_id, questions, responses_user_input, response_column_codes):
    """
    Legacy function signature for backward compatibility with tests.
    
    This matches the old API where all parameters were passed separately.
    The original signature was (question_id, questions, responses_user_input, response_column_codes)
    """
    # Create a minimal SurveyAnalysis instance to work with the new API
    analysis = SurveyAnalysis("temp")
    analysis.questions = questions
    analysis.responses_user_input = responses_user_input
    analysis.response_column_codes = response_column_codes
    
    # Process the multiple choice question
    try:
        analysis._process_multiple_choice_question(question_id)
        return analysis.processed_responses.get(question_id)
    except Exception as e:
        print(f"Error processing multiple choice question {question_id}: {e}")
        return None


def process_ranking_questions(api, question_id, questions, responses_user_input, options):
    """
    Legacy function signature for backward compatibility with tests.
    
    This matches the old API where parameters were passed separately.
    """
    # Create a minimal SurveyAnalysis instance to work with the new API
    analysis = SurveyAnalysis("temp")
    analysis.api = api
    analysis.questions = questions
    analysis.responses_user_input = responses_user_input
    analysis.options = options
    analysis.response_column_codes = get_columns_codes_for_responses_user_input(responses_user_input)
    
    # Process the single question
    try:
        analysis._process_ranking_question(question_id)
        return analysis.processed_responses.get(question_id)
    except Exception as e:
        print(f"Error processing ranking question {question_id}: {e}")
        return None


def process_radio_question(question_id, questions, responses_user_input, options):
    """
    Legacy function signature for backward compatibility with tests.
    
    This matches the old API where parameters were passed separately.
    """
    # Create a minimal SurveyAnalysis instance to work with the new API
    analysis = SurveyAnalysis("temp")
    analysis.questions = questions
    analysis.responses_user_input = responses_user_input
    analysis.options = options
    
    # Process the single question
    try:
        analysis._process_radio_question(question_id)
        return analysis.processed_responses.get(question_id)
    except Exception as e:
        print(f"Error processing radio question {question_id}: {e}")
        return None


def process_all_radio_and_equasion_questions(questions, responses_user_input, options):
    """
    Legacy function signature for backward compatibility with tests.
    
    Note: Function name kept as 'equasion' (with typo) for backward compatibility.
    This matches the old API where parameters were passed separately.
    """
    # Create a minimal SurveyAnalysis instance to work with the new API
    analysis = SurveyAnalysis("temp")
    analysis.questions = questions
    analysis.responses_user_input = responses_user_input
    analysis.options = options
    
    results = {}
    
    # Filter for radio and equation questions
    radio_questions = questions[
        questions['question_theme_name'].isin(['listradio', 'equation'])
    ]
    
    for _, question in radio_questions.iterrows():
        question_id = question['qid']
        try:
            analysis._process_radio_question(question_id)
            results[question_id] = analysis.processed_responses.get(question_id)
        except Exception as e:
            print(f"Error processing question {question_id}: {e}")
            results[question_id] = None
    
    return results


def analyze_survey_comprehensive(survey_id: str, config_path: str = 'secrets/credentials.ini'):
    """
    Perform a comprehensive analysis of a survey.
    
    This is a convenience function that combines multiple analysis steps.
    """
    try:
        # Initialize API client
        api = LimeSurveyClient.from_config(config_path)
        
        # Create analysis instance
        analysis = SurveyAnalysis(survey_id)
        analysis.setup()
        
        # Process all questions
        analysis.process_all_questions()
        
        # Get survey metadata
        properties = api.surveys.get_survey_properties(survey_id)
        summary = api.surveys.get_summary(survey_id)
        
        return {
            'survey_info': properties,
            'summary': summary,
            'processed_responses': analysis.processed_responses,
            'questions': analysis.questions,
            'options': analysis.options,
            'groups': analysis.groups,
            'failure_log': analysis.fail_message_log
        }
        
    except Exception as e:
        print(f"Comprehensive analysis failed: {e}")
        return None


# Legacy compatibility functions
def setup_api_client(config_path: str = 'secrets/credentials.ini') -> LimeSurveyClient:
    """Set up and return an API client."""
    return LimeSurveyClient.from_config(config_path)


def create_survey_analysis(survey_id: str) -> SurveyAnalysis:
    """Create a SurveyAnalysis instance."""
    return SurveyAnalysis(survey_id) 


# Additional functions expected by tests
def get_survey_structure_data(api, survey_id, verbose=False):
    """
    Get survey structure data (questions, options, groups, properties, summary).
    Legacy wrapper function for backward compatibility.
    """
    analysis = SurveyAnalysis(survey_id, verbose=verbose)
    analysis.api = api
    analysis._get_survey_structure_data()
    return analysis.questions, analysis.options, analysis.groups, analysis.properties, analysis.summary


def _format_dataframe(df, title="DataFrame"):
    """
    Format a DataFrame for display.
    Legacy utility function for backward compatibility.
    """
    if df is None or df.empty:
        return f"{title}: Empty"
    return f"{title}:\n{df.to_string()}"


def _get_cache_dir():
    """Get the cache directory path."""
    return Path.home() / '.lime_survey_cache'


def _get_cache_path(cache_name):
    """Get the path for a specific cache file."""
    cache_dir = _get_cache_dir()
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"{cache_name}.json"


def _cache_options(options_data, cache_name):
    """Cache options data to a file."""
    try:
        cache_path = _get_cache_path(cache_name)
        with open(cache_path, 'w') as f:
            json.dump(options_data, f)
        return True
    except Exception:
        return False


def _get_cached_options(cache_name):
    """Retrieve cached options data from a file."""
    try:
        cache_path = _get_cache_path(cache_name)
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    except Exception:
        return None 