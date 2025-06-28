"""
Survey Analysis Functions

This module contains standalone functions for survey data analysis that don't depend on
SurveyAnalysis class instance state. These are the public API functions for analysis.
"""

from typing import Dict, Any, Optional, List, Union, Tuple, TypedDict, TYPE_CHECKING
import pandas as pd
from pathlib import Path
import json

from .client import LimeSurveyClient
from .cache_manager import get_cache_manager

# Forward reference for type hints
if TYPE_CHECKING:
    from .analyser import SurveyAnalysis


# Type definitions
class ResponseData(TypedDict, total=False):
    id: str
    submitdate: Optional[str]
    lastpage: Optional[int]
    startlanguage: str
    seed: Optional[str]
    startdate: Optional[str]
    datestamp: Optional[str]
    refurl: Optional[str]


def get_survey_structure_data(api: LimeSurveyClient, survey_id: str, verbose: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame, List[Dict[str, Any]], Dict[str, Any], Dict[str, Any]]:
    """
    Retrieves the complete structure and metadata of a survey.

    Parameters:
        api: The survey API client instance
        survey_id: The ID of the survey to analyze
        verbose: Whether to show cache messages

    Returns:
        tuple: (questions, options, groups, properties, summary)
            - questions: DataFrame containing survey questions
            - options: DataFrame containing question options and their metadata
            - groups: List of question groups
            - properties: Dictionary of survey properties from the API
            - summary: Dictionary of survey summary information
    """
    # Import here to avoid circular imports
    from .analyser import _get_questions, _get_raw_options_data, _process_options_data, _enrich_options_data_with_question_codes
    
    # Get cache manager with verbose setting
    cache_manager = get_cache_manager(verbose)
    
    # Try to get cached structure data first
    cached_result = cache_manager.get_cached('get_survey_structure_data', survey_id)
    if cached_result is not None:
        return cached_result
    
    if verbose:
        print("🌐 API CALL: get_survey_structure_data (not cached)")
    
    # Get survey details and response count
    properties = api.surveys.get_survey_properties(survey_id)
    summary = api.surveys.get_summary(survey_id)

    # Get question structure
    groups = api.questions.list_groups(survey_id)

    # getting questions data 
    questions = _get_questions(api, survey_id, verbose)

    # getting question options data 
    raw_options_data = _get_raw_options_data(api, survey_id, questions, verbose)  # this is slow, lots of api calls 
    options = _process_options_data(raw_options_data, verbose)
    options = _enrich_options_data_with_question_codes(options, questions)
    
    # Store in cache
    structure_data = (questions, options, groups, properties, summary)
    cache_manager.set_cached(structure_data, 'get_survey_structure_data', survey_id)
    
    return structure_data


def get_response_data(api: LimeSurveyClient, survey_id: str, keep_incomplete_user_input: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retrieves and processes response data from a survey.

    Parameters:
        api: The survey API client instance
        survey_id: The ID of the survey to get responses from
        keep_incomplete_user_input: Boolean flag to determine whether to include incomplete responses

    Returns:
        tuple: (responses_user_input, responses_metadata)
            - responses_user_input: DataFrame containing actual survey responses
            - responses_metadata: DataFrame containing metadata about responses
    """
    # Import here to avoid circular imports
    from .analyser import get_response_data as _get_response_data
    return _get_response_data(api, survey_id, keep_incomplete_user_input)


def get_columns_codes_for_responses_user_input(responses_user_input: pd.DataFrame) -> pd.DataFrame:
    """
    Creates a mapping for response column codes in the user input data.

    Parameters:
        responses_user_input: DataFrame containing the user responses

    Returns:
        DataFrame with columns:
            - question_code: The base question code
            - appendage: Either rank information or option code from square brackets
    """
    # Import here to avoid circular imports
    from .analyser import get_columns_codes_for_responses_user_input as _get_codes
    return _get_codes(responses_user_input)


def get_response_stats_multiple_choice(responses_user_input: pd.DataFrame, 
                                     response_column_codes: pd.DataFrame,
                                     question_code: str) -> pd.DataFrame:
    """
    Calculates statistics for multiple choice question responses.

    Parameters:
        responses_user_input: DataFrame containing user responses
        response_column_codes: DataFrame mapping response codes
        question_code: The question code to analyze

    Returns:
        DataFrame containing response statistics with absolute_counts and response_rates
    """
    # Import here to avoid circular imports
    from .analyser import _get_response_rate
    
    # Get the question response codes for this question
    question_response_codes = response_column_codes.loc[
        response_column_codes['question_code'] == question_code]

    # Fix pandas future warning by being explicit about downcasting
    numeric_subset = responses_user_input[
        question_response_codes.index].replace({'Y': 1, '': 0}).fillna(0)
    
    # Explicitly convert to int to avoid future warning
    numeric_subset = numeric_subset.infer_objects(copy=False).astype(int)

    # how many respondents marked each option
    absolute_counts = numeric_subset.sum()

    # get the response rate (to not give users who answer a lot extra weight)
    response_rates = _get_response_rate(absolute_counts, numeric_subset)
    
    # join them in a dataframe 
    response_stats = pd.DataFrame({
        "absolute_counts": absolute_counts, 
        "response_rates": response_rates
    })
    
    return response_stats


def process_ranking_questions(analysis: 'SurveyAnalysis', question_ids: List[str]) -> Dict[str, Optional[pd.DataFrame]]:
    """
    Process multiple ranking questions and return their results.

    Parameters:
        analysis: SurveyAnalysis instance with loaded data
        question_ids: List of question IDs to process

    Returns:
        Dictionary mapping question IDs to their processed ranking data
    """
    results = {}
    for question_id in question_ids:
        try:
            analysis._process_ranking_question(question_id)
            results[question_id] = analysis.processed_responses.get(question_id)
        except Exception as e:
            print(f"Error processing ranking question {question_id}: {e}")
            results[question_id] = None
    
    return results


def process_radio_question(analysis: 'SurveyAnalysis', question_id: str) -> Optional[pd.Series]:
    """
    Process a single radio question and return its results.

    Parameters:
        analysis: SurveyAnalysis instance with loaded data
        question_id: Question ID to process

    Returns:
        Series containing the processed radio question data, or None if processing failed
    """
    try:
        analysis._process_radio_question(question_id)
        return analysis.processed_responses.get(question_id)
    except Exception as e:
        print(f"Error processing radio question {question_id}: {e}")
        return None


def process_all_radio_and_equasion_questions(analysis: 'SurveyAnalysis') -> Dict[str, Optional[pd.Series]]:
    """
    Process all radio and equation questions in the survey.
    
    Note: Function name kept as 'equasion' (with typo) for backward compatibility with tests.

    Parameters:
        analysis: SurveyAnalysis instance with loaded data

    Returns:
        Dictionary mapping question IDs to their processed data
    """
    results = {}
    
    # Filter for radio and equation questions
    radio_questions = analysis.questions[
        analysis.questions['question_theme_name'].isin(['listradio', 'equation'])
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


# Cache management functions expected by tests
def _get_cache_dir() -> Path:
    """Get the cache directory path."""
    return Path('.question_cache')


def _get_cache_path(survey_id: str) -> Path:
    """Get the cache file path for a specific survey."""
    cache_dir = _get_cache_dir()
    return cache_dir / f"survey_{survey_id}_options.json"


def _cache_options(options_data: pd.DataFrame, survey_id: str) -> None:
    """Cache options data for a survey."""
    cache_dir = _get_cache_dir()
    cache_dir.mkdir(exist_ok=True)
    
    cache_path = _get_cache_path(survey_id)
    
    # Convert DataFrame to dict for JSON serialization
    options_dict = options_data.to_dict('records')
    
    with open(cache_path, 'w') as f:
        json.dump(options_dict, f, indent=2)


def _get_cached_options(survey_id: str) -> Optional[pd.DataFrame]:
    """Get cached options data for a survey."""
    cache_path = _get_cache_path(survey_id)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'r') as f:
            options_dict = json.load(f)
        
        return pd.DataFrame(options_dict)
    except Exception:
        return None


def _format_dataframe(df: pd.DataFrame, max_width: int = 80) -> str:
    """Format a DataFrame for display with specified maximum width."""
    try:
        from tabulate import tabulate
        return tabulate(df, headers='keys', tablefmt='grid', maxcolwidths=max_width)
    except ImportError:
        return str(df) 