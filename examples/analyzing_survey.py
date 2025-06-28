"""
Survey Analysis Examples

This module provides examples and shortcuts for common survey analysis tasks.
Updated to use the current API after removal of old_analyzing_survey.py.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Import main analysis components from current API
from lime_survey_analyzer import SurveyAnalysis, LimeSurveyClient
from lime_survey_analyzer.analyser import (
    get_response_data,
    get_columns_codes_for_responses_user_input,
    _get_questions,
    _get_raw_options_data,
    _process_options_data,
    _enrich_options_data_with_question_codes
)
from lime_survey_analyzer.utils.display import format_dataframe

# Convenience aliases for backward compatibility
analyze_survey_comprehensive = SurveyAnalysis.analyze_comprehensive
setup_api_client = LimeSurveyClient.from_config
create_survey_analysis = SurveyAnalysis

# For compatibility with old function signatures, provide simple wrappers
def get_survey_structure_data(api, survey_id, verbose=False):
    """
    Get survey structure data (questions, options, groups, properties, summary).
    Wrapper function for backward compatibility.
    """
    analysis = SurveyAnalysis(survey_id, verbose=verbose)
    analysis.api = api
    analysis._get_survey_structure_data()
    return analysis.questions, analysis.options, analysis.groups, analysis.properties, analysis.summary

# Alias for the display function
_format_dataframe = format_dataframe 