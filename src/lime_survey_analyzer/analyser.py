#!/usr/bin/env python3
"""
Survey Analysis Module

Contains the main SurveyAnalysis class and supporting functions for processing
LimeSurvey data with comprehensive type safety.
"""

import pandas as pd
import re
from tqdm import tqdm
from lime_survey_analyzer import LimeSurveyClient
from .cache_manager import get_cache_manager, cached_api_call
from typing import Dict, List, Optional, Union, Any, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import LimeSurveyClient
    from .types import (
        QuestionType, SurveyProperties, SurveySummary, GroupData,
        ProcessedResponse, QuestionStatistics, AnalysisConfig
    )

# Cache manager will be initialized with verbose setting when needed

def _get_questions(api: 'LimeSurveyClient', survey_id: str, verbose: bool = False) -> pd.DataFrame:
    """
    Get questions for a survey.
    
    Args:
        api: LimeSurvey API client
        survey_id: Survey ID
        verbose: Whether to show cache messages
        
    Returns:
        DataFrame containing survey questions with proper string types
        
    Raises:
        ValueError: If API returns invalid data
    """
    if not survey_id:
        raise ValueError("survey_id cannot be empty")
    
    # Get cache manager with verbose setting
    cache_manager = get_cache_manager(verbose)
    
    # Try cache first
    cached_result = cache_manager.get_cached('_get_questions', survey_id)
    if cached_result is not None:
        return cached_result
    
    # get the questions 
    if verbose:
        print("🌐 API CALL: _get_questions (not cached)")
    questions_raw = api.questions.list_questions(survey_id)
    
    if not questions_raw:
        raise ValueError(f"No questions found for survey {survey_id}")
    
    # turn them into a dataframe 
    questions = pd.DataFrame(questions_raw)
    
    # Validate required columns exist
    required_cols = ['id', 'qid', 'parent_qid']
    missing_cols = [col for col in required_cols if col not in questions.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in questions data: {missing_cols}")
    
    # make sure the ids stay strings 
    questions['id'] = questions['id'].astype(str)
    questions['qid'] = questions['qid'].astype(str)
    questions['parent_qid'] = questions['parent_qid'].astype(str)
    
    # Store in cache
    cache_manager.set_cached(questions, '_get_questions', survey_id)
    
    return questions

def _get_question_options(api: 'LimeSurveyClient', survey_id: str, question_id: str, verbose: bool = False) -> Union[str, Dict[str, Any]]:
    """
    Get options for a particular question, using cache if available.
    
    Args:
        api: LimeSurvey API client
        survey_id: Survey ID
        question_id: Question ID
        verbose: Whether to show cache messages
        
    Returns:
        Question options data or "No available answer options" string
    """
    # Get cache manager with verbose setting
    cache_manager = get_cache_manager(verbose)
    
    # Try cache first
    cached_result = cache_manager.get_cached('_get_question_options', survey_id, question_id)
    if cached_result is not None:
        return cached_result
    
    # Cache miss - call API
    if verbose:
        print("🌐 API CALL: _get_question_options (not cached)")
    props = api.questions.get_question_properties(survey_id, question_id)
    option_order = props['answeroptions']
    
    # Store in cache
    cache_manager.set_cached(option_order, '_get_question_options', survey_id, question_id)
        
    return option_order 

def _get_raw_options_data(api: 'LimeSurveyClient', survey_id: str, questions: pd.DataFrame, verbose: bool = False) -> Dict[str, Union[str, Dict[str, Any]]]:
    """
    Loops through the questions dataframe to get options data for each question.
    
    Args:
        api: LimeSurvey API client
        survey_id: Survey ID
        questions: DataFrame of questions
        verbose: Whether to show progress bar and cache messages
        
    Returns:
        Dictionary mapping question IDs to their options data
    """
    # Get cache manager with verbose setting
    cache_manager = get_cache_manager(verbose)
    
    # Try cache first
    cached_result = cache_manager.get_cached('_get_raw_options_data', survey_id, len(questions))
    if cached_result is not None:
        return cached_result
    
    # Cache miss - process questions
    if verbose:
        print("🌐 API CALL: _get_raw_options_data (not cached)")
    
    raw_options_data = {}
    question_ids = questions['id']
    
    if verbose:
        question_ids = tqdm(question_ids, desc="Loading question options")
        
    for qid in question_ids:
        raw_options_data[qid] = _get_question_options(api, survey_id, qid, verbose)
    
    # Store in cache
    cache_manager.set_cached(raw_options_data, '_get_raw_options_data', survey_id, len(questions))
        
    return raw_options_data

def _process_options_data(raw_options_data: Dict[str, Union[str, Dict[str, Any]]], verbose: bool = False) -> pd.DataFrame:
    """
    Process raw options data into a clean DataFrame.
    
    Args:
        raw_options_data: Dictionary of raw options data from API
        verbose: Whether to show error messages
        
    Returns:
        DataFrame with processed options data
        
    Raises:
        ValueError: If no valid options data found
    """
    if not raw_options_data:
        raise ValueError("raw_options_data cannot be empty")
    
    option_order = []
    
    for qid in raw_options_data.keys():
        if raw_options_data[qid] == "No available answer options":
            pass 
        else:
            try: 
                _order_data = pd.DataFrame(raw_options_data[qid])
                if _order_data.empty:
                    continue
                    
                _order_data = _order_data.T.reset_index()
                _order_data = _order_data.rename(columns={'index': 'option_code'})
                _order_data = _order_data.rename(columns={'order': 'option_order'})
                _order_data['qid'] = qid
                option_order.append(_order_data)

            except Exception as e: 
                if verbose:
                    print(f"Failed processing options for question {qid}: {e}")
                
    if not option_order:
        return pd.DataFrame(columns=['option_code', 'option_order', 'qid', 'answer'])
        
    options = pd.concat(option_order, ignore_index=True) 
    options['qid'] = options['qid'].astype(str)
    
    return options

def _get_responses(api: 'LimeSurveyClient', survey_id: str) -> pd.DataFrame:
    """
    Get response data from API and process into DataFrame.
    
    Args:
        api: LimeSurvey API client
        survey_id: Survey ID
        
    Returns:
        DataFrame containing response data with string IDs
        
    Raises:
        ValueError: If response format is unexpected
    """
    # Get responses from API
    responses = api.responses.export_responses(survey_id)
    
    # If responses is a list, use it directly
    if isinstance(responses, list):
        responses = pd.DataFrame(responses)
    # If responses is a dict, check for 'responses' key
    elif isinstance(responses, dict):
        if 'responses' in responses:
            responses = pd.DataFrame(responses['responses'])
        else:
            # If no 'responses' key, use the dict directly
            responses = pd.DataFrame([responses])
    else:
        raise ValueError(f"Unexpected response format: {type(responses)}")
    
    # make the ids strings 
    if 'id' in responses.columns:
        responses['id'] = responses['id'].astype(str)
    
    return responses

    
def _split_last_square_bracket_content(s):
    """
    
    These responses came form getting api.responses.export_responses(survey_id)['responses'], then turning into a dataframe, and getting the column names.  which was turned into a dataframe 
    The response format can be clean (like SQ007) or have the rank (like G02Q01[SQ006])
    
    The pattern splits the input string into two parts: the part before the last pair of square brackets at the end, and the content inside the brackets.

    If the string has no square brackets, returns (s, None).
    If the string contains square brackets but does not end with them, raises a ValueError.

    Args:
        s (str): The input string to process.

    Returns:
        tuple:
            - str: The part of the string before the last pair of square brackets.
            - str or None: The content inside the last pair of square brackets at the end of the string, or None if no square brackets are present.

    Raises:
        ValueError: If the string contains square brackets but does not end with them.

    Examples:
        >>> split_last_square_bracket_content("SQ007")
        ('SQ007', None)
        >>> split_last_square_bracket_content("G02Q01[SQ006]")
        ('G02Q01', 'SQ006')
        >>> split_last_square_bracket_content("G02Q[V2]01[SQ006]")
        ('G02Q[V2]01', 'SQ006')
        >>> split_last_square_bracket_content("G02Q01[SQ006]2b")
        ValueError: The string contains square brackets but does not end with them.

    """
    if '[' not in s and ']' not in s:
        return s, None

    match = re.search(r'^(.*)\[([^\[\]]+)\]$', s)
    if match:
        before, inside = match.groups()
        return before, inside
    else:
        raise ValueError("The string contains square brackets but does not end with them.")

        


def _get_option_codes_to_names_mapper(options, question_id):
    
    # get the subset of option_info codes we need from options 
    # CRITICAL FIX: Ensure question_id is string to match options DataFrame qid column type
    question_id_str = str(question_id)
    
    # Check if the question has any options - if not, return empty dict (original behavior)
    options_by_qid = options.set_index('qid')
    if question_id_str not in options_by_qid.index:
        # Return empty dict - let calling code handle this gracefully as it did before
        return {}
    
    relevant_option_codes_info = options_by_qid.loc[question_id_str]
    
    # If it's a single row, convert to DataFrame
    if not hasattr(relevant_option_codes_info, 'set_index'):
        # Single row case - create a simple mapping
        return {relevant_option_codes_info['option_code']: relevant_option_codes_info['answer']}

    # turn the option_codes and answer columns into a dict for mapping 
    options_codes_to_names_mapper = relevant_option_codes_info.set_index(
        'option_code')['answer'].to_dict()
    
    return options_codes_to_names_mapper


def _split_responses_data_into_user_input_and_metadata(responses: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split responses into user input and metadata components.
    
    Args:
        responses: DataFrame containing all response data
        
    Returns:
        Tuple of (user_input_df, metadata_df)
        
    Raises:
        ValueError: If responses DataFrame is empty or missing required columns
    """
    if responses.empty:
        raise ValueError("responses DataFrame cannot be empty")
    
    # Standard metadata columns that might exist
    all_metadata_cols = ['id', 'submitdate', 'lastpage', 'startlanguage', 'seed', 'startdate',
                        'datestamp', 'refurl']
    
    # Only use metadata columns that actually exist in the data
    available_metadata_cols = [col for col in all_metadata_cols if col in responses.columns]
    
    if not available_metadata_cols:
        raise ValueError("No standard metadata columns found in responses")
    
    # User input columns are everything else
    response_user_input_cols = [c for c in responses.columns if c not in available_metadata_cols]
    
    responses_metadata = responses[available_metadata_cols].copy()
    responses_user_input = responses[response_user_input_cols].copy()
    
    return responses_user_input, responses_metadata

def _get_responses_user_input_and_responses_metadata(api, survey_id):
    responses = _get_responses(api, survey_id)
    
    responses_user_input, responses_metadata = _split_responses_data_into_user_input_and_metadata(
        responses)
    
    return responses_user_input, responses_metadata

def _enrich_options_data_with_question_codes(options, questions):
    """
    in the options data we do not know the corresponding question_code, 
    but we do know the qid (question_id), so we can get it by mapping qids to question_codes 
    (annoying called "title" in the question dataset), and using that to make a mapper
    """
    questions_id_to_titles_mapper = questions.set_index('qid')['title'].to_dict()

    options['question_code'] = options['qid'].map(questions_id_to_titles_mapper)
    
    return options 

def get_columns_codes_for_responses_user_input(responses_user_input):
    """
    Creates a mapping for response column codes in the user input data.

    This function processes column names that may contain:
    - Simple question codes (e.g., 'SQ007')
    - Codes with rank information (e.g., 'G02Q01[SQ006]')
    - Codes with multiple choice options

    Parameters:
        responses_user_input: DataFrame containing the user responses

    Returns:
        DataFrame with columns:
            - question_code: The base question code
            - appendage: Either rank information or option code from square brackets,
                        or None if no brackets present
    """

    col_parts = {}
    for col in responses_user_input:
        col_parts[col] = _split_last_square_bracket_content(col)

    response_column_codes = pd.DataFrame(col_parts).T
    response_column_codes = response_column_codes.rename(
        columns={0: 'question_code', 1: 'appendage'})
    
    return response_column_codes



def _map_names_to_rank_responses(rank_responses, options, question_id):
    """
    Transforms a dataset of ranked responses with the answer codes as columns into one 
    where the column names are the text of the answer. 
    """
    
    options_codes_to_names_mapper = _get_option_codes_to_names_mapper(options,  
                                                                 question_id)
    rank_responses_named = rank_responses.rename(columns=options_codes_to_names_mapper)
    
    return rank_responses_named





def get_response_data(api: 'LimeSurveyClient', survey_id: str, keep_incomplete_user_input: bool = False) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Retrieves and processes response data from a survey.
    
    Args:
        api: LimeSurvey API client instance
        survey_id: ID of the survey to retrieve responses for
        keep_incomplete_user_input: Whether to keep incomplete responses in user input data
        
    Returns:
        Tuple containing:
        - responses_user_input: DataFrame containing only user responses to questions
        - responses_metadata: DataFrame containing metadata about responses (submitdate, lastpage, etc.)
        
    Raises:
        ValueError: If survey_id is empty or no responses found
    """
    if not survey_id:
        raise ValueError("survey_id cannot be empty")
    
    # getting response data 
    responses_user_input, responses_metadata = _get_responses_user_input_and_responses_metadata(api, survey_id)

    if responses_user_input.empty and responses_metadata.empty:
        raise ValueError(f"No response data found for survey {survey_id}")

    # remove incomplete answers for the responses with user input 
    # note: we will keep the metadata with the incomplete answers 
    
    if not keep_incomplete_user_input:
        # Check if submitdate column exists before using it
        if 'submitdate' in responses_metadata.columns:
            incomplete_answers = responses_metadata['submitdate'].isnull()
            
            # Filter out incomplete responses from user input only
            responses_user_input = responses_user_input[~incomplete_answers].copy()
        else:
            # If no submitdate column, we can't determine incomplete responses
            # Log a warning but continue
            print("Warning: 'submitdate' column not found, cannot filter incomplete responses")
    
    return responses_user_input, responses_metadata


def _get_response_rate(absolute_counts, numeric_subset):
    # mask which users responded to any of the options 
    user_responded = numeric_subset.sum(axis=1) > 0

    nr_of_respondents = user_responded.sum()

    # what fraction of respondents marked each option
    response_rate = absolute_counts / nr_of_respondents
    return response_rate


class SurveyAnalysis:
    """
    Main class for analyzing LimeSurvey data with comprehensive type safety.
    
    This class provides methods to load survey structure, process responses,
    and analyze different question types with proper error handling and caching.
    
    Args:
        survey_id: The ID of the survey to analyze
        verbose: Whether to show progress bars and status messages
    """
    
    def __init__(self, survey_id: str, verbose: bool = False) -> None:
        """
        Initialize SurveyAnalysis instance.
        
        Args:
            survey_id: The ID of the survey to analyze
            verbose: Whether to show progress bars and status messages
        """
        self.survey_id: str = survey_id
        self.verbose: bool = verbose
        self.api: Optional['LimeSurveyClient'] = None
        self.responses_user_input: Optional[pd.DataFrame] = None 
        self.responses_metadata: Optional[pd.DataFrame] = None 
        self.response_column_codes: Optional[pd.DataFrame] = None 
        self.options: Optional[pd.DataFrame] = None
        self.questions: Optional[pd.DataFrame] = None
        self.groups: Optional[List['GroupData']] = None 
        self.summary: Optional['SurveySummary'] = None 
        self.properties: Optional['SurveyProperties'] = None 
        self.processed_responses: Dict[str, Union[pd.Series, pd.DataFrame, Dict[str, pd.Series]]] = {}
        
        # Question handlers mapping
        self.question_handlers: Dict[str, Any] = {
            'longfreetext': self._process_text_question,
            'listradio': self._process_radio_question,
            'numerical': self._process_text_question,
            'multipleshorttext': self._process_multiple_short_text,
            'ranking': self._process_ranking_question,
            'shortfreetext': self._process_text_question,
            'image_select-listradio': self._process_radio_question,
            'multiplechoice': self._process_multiple_choice_question,
            'arrays/increasesamedecrease': self._process_array_question,
            # Note: equation and image_select-multiplechoice not implemented yet
        }
        
        # Error tracking
        self.fail_message_log: Dict[str, Exception] = {}
        
    def setup(self, keep_incomplete_user_input: bool = False, api: Optional['LimeSurveyClient'] = None, config_path: Optional[str] = None) -> None:
        """
        Set up the analysis by loading data and processing structure.
        
        Args:
            keep_incomplete_user_input: Whether to keep incomplete responses
            api: Optional pre-configured LimeSurveyClient instance
            config_path: Optional path to credentials file (used only if api is None)
        """
        self.api = api if api is not None else self._connect_to_api(config_path)
        self._load_response_data(keep_incomplete_user_input=keep_incomplete_user_input)
        self._get_survey_structure_data()
        self._process_column_codes()
        
    def _connect_to_api(self, config_path: Optional[str] = None) -> 'LimeSurveyClient':
        """
        Connect to the LimeSurvey API.
        
        Args:
            config_path: Optional path to credentials file
        
        Returns:
            Configured LimeSurvey API client
        """
        from .client import LimeSurveyClient
        return LimeSurveyClient.from_config(config_path) if config_path else LimeSurveyClient.from_config()
        
    def _load_response_data(self, keep_incomplete_user_input: bool) -> None:
        """
        Load response data from the API.
        
        Args:
            keep_incomplete_user_input: Whether to keep incomplete responses
        """
        self.responses_user_input, self.responses_metadata = get_response_data(
            api=self.api,  
            survey_id=self.survey_id, 
            keep_incomplete_user_input=keep_incomplete_user_input)
        
        
    def _get_survey_structure_data(self):
        """
        Get survey structure data (questions, options, groups, properties, summary).
        
        This method populates the following instance attributes:
            - questions: DataFrame of questions from the survey
            - options: DataFrame of question options/choices
            - groups: [TODO: Please specify what this contains]
                - properties: Dictionary of survey properties from the API
                - summary: [TODO: Please specify what this contains]

        Note:
            This function makes multiple API calls and can be slow, particularly 
            when fetching options data for surveys with many questions.
        """
        # Get cache manager with verbose setting
        cache_manager = get_cache_manager(self.verbose)
        
        # Try to get cached structure data first
        cached_result = cache_manager.get_cached('_get_survey_structure_data', self.survey_id)
        if cached_result is not None:
            self.questions, self.options, self.groups, self.properties, self.summary = cached_result
            return
        
        if self.verbose:
            print("🌐 Loading survey structure (not cached)...")
        
        # Get survey details and response count
        properties = self.api.surveys.get_survey_properties(self.survey_id)
        summary = self.api.surveys.get_summary(self.survey_id)

        # Get question structure
        groups = self.api.questions.list_groups(self.survey_id)

        # getting questions data 
        questions = _get_questions(self.api, self.survey_id, self.verbose)

        # getting question options data 
        raw_options_data = _get_raw_options_data(self.api, self.survey_id, questions, verbose=self.verbose)
        options = _process_options_data(raw_options_data, verbose=self.verbose)
        options = _enrich_options_data_with_question_codes(options, questions)
        
        # Store in cache
        structure_data = (questions, options, groups, properties, summary)
        cache_manager.set_cached(structure_data, '_get_survey_structure_data', self.survey_id)
        
        self.questions = questions
        self.options = options
        self.groups = groups  
        self.properties = properties
        self.summary = summary

    def _process_column_codes(self) -> None:
        """
        Process response column codes to create mapping between response codes and question codes.
        
        Raises:
            ValueError: If responses_user_input is not initialized
        """
        if not hasattr(self, 'responses_user_input') or self.responses_user_input is None:
            raise ValueError("responses_user_input not initialized. Call _load_response_data() first.")
        
        if self.responses_user_input.empty:
            raise ValueError("responses_user_input cannot be empty")
        
        # Process column codes
        response_column_codes = get_columns_codes_for_responses_user_input(self.responses_user_input)
        
        if response_column_codes.empty:
            raise ValueError("Failed to generate response column codes")
        
        # Rename columns for clarity
        response_column_codes.columns = ['question_code', 'appendage']
        
        # Store the mapping
        self.response_column_codes = response_column_codes
        
        # Also create a convenience mapper
        self.response_codes_to_question_codes = response_column_codes['question_code'].to_dict()

    def _get_max_answers(self, question_id):
        """Get maximum number of answers allowed for a question."""
        # Get cache manager with verbose setting
        cache_manager = get_cache_manager(self.verbose)
        
        # Try cache first
        cached_result = cache_manager.get_cached('_get_max_answers', self.survey_id, question_id)
        if cached_result is not None:
            try:
                return int(cached_result)
            except (ValueError, TypeError):
                # If cached value is invalid, fall through to fetch fresh data
                pass
        
        if self.verbose:
            print("🌐 API CALL: _get_max_answers (not cached)")
        props = self.api.questions.get_question_properties(self.survey_id, question_id)
        attributes = props['attributes']
        max_answers = attributes['max_answers']
        
        # make sure it is an int, handle empty/invalid values 
        if not max_answers or max_answers == '' or max_answers is None:
            # Default to a very large number if not specified (essentially unlimited)
            max_answers = 1000000
        else:
            try:
                max_answers = int(max_answers)
            except (ValueError, TypeError):
                # If conversion fails, use default (essentially unlimited)
                max_answers = 1000000
        
        # Store in cache
        cache_manager.set_cached(max_answers, '_get_max_answers', self.survey_id, question_id)
        
        return max_answers


    def _process_rank_question_options(self, question_code):
        # TODO: generalize, this also serves multiple choice 
        """

        
        Processes ranking question optiosn into value_counts of each rank. 

        The step where we use the options dataset does two things: 
        - removes the None and np.nan answers
        - ensures that option codes that no one answer are still in the rank responses 
        - (the responses data is not aware of options no one chose, but question structures are)
        """

        # TODO: rename 
        # subsets the question response codes for this dataset response codes for this particular question
        question_response_codes_subset = self._get_response_codes_for_question(question_code)

        rank_responses = {}
        # for 
        for response_code, response_info in question_response_codes_subset.iterrows():
            # rank is the appendage column - use explicit column name instead of position
            rank = response_info['appendage']
            # Convert rank to int for proper ordering
            try:
                rank = int(rank)
            except (ValueError, TypeError):
                # If conversion fails, keep as string but warn
                pass
            
            # In responses_user_input, subset that column name 
            response_col = self.responses_user_input[response_code]
            # now calculate the value counts 
            response_col_value_counts = response_col.value_counts(dropna=False)
            # stora that in responses 
            rank_responses[rank] = response_col_value_counts

        # turn the results in a dictionary and transpose 
        rank_responses = pd.DataFrame(rank_responses).T

        # Ensure index is sorted properly (integers first)
        rank_responses = rank_responses.sort_index()

        # now we will fix the follwing issues in the columns:
        # - presence of np.nan or None 
        # - absence of options which have not received any answers  
        try:
            relevant_options_for_question = self.options.set_index('question_code').loc[question_code]
            # adds responses that may not have been chosen by anyone 
            valid_options = relevant_options_for_question['option_code'].unique()
            # removes rank responses that are not acceptable opiton codes (np.nan, None)
            rank_responses = rank_responses.loc[:, valid_options]
        except (KeyError, IndexError, ValueError) as e:
            # If question_code not found in options or any pandas indexing error, use existing columns
            # This happens when a ranking question has no predefined options
            if self.verbose:
                print(f"⚠️ No options found for ranking question {question_code}, using response columns")
            # Clean up columns by removing NaN/None values if they exist
            clean_columns = [col for col in rank_responses.columns if pd.notna(col) and col != '' and col != 'None']
            rank_responses = rank_responses.loc[:, clean_columns]

        return rank_responses
    

    def _process_ranking_question(self, question_id):

        # get the question code
        question_code = self._get_question_code(question_id)

        max_answers = self._get_max_answers(question_id)

       # get the rank responses for this particular question
       # the reason is that rank repsonses show up as their own questions 
        rank_responses = self._process_rank_question_options(question_code)

        # Map the names to the rank responses options 
        # Revert to original behavior - handle gracefully if no options mapping available
        rank_responses_named = _map_names_to_rank_responses(rank_responses, self.options, question_id)

        # if the question has a maximum number of answers, cut the response dataframe at that number of answers
        rank_responses_named = rank_responses_named.iloc[:max_answers, :]   
        
        # adding zeros to pad any empty answers (e.g. option A was ranked 1 zero times)
        rank_responses_named = rank_responses_named.fillna(0)

        self.processed_responses[question_id] = rank_responses_named
    

    
        # let's subset the response codes for this question 
    def _get_response_codes_for_question(self, question_code: str) -> pd.DataFrame:
        """
        Get response codes for a specific question.
        
        Args:
            question_code: The question code to look up
            
        Returns:
            DataFrame containing response codes for the question
            
        Raises:
            ValueError: If response_column_codes is not initialized or question_code not found
        """
        if not hasattr(self, 'response_column_codes') or self.response_column_codes is None:
            raise ValueError("response_column_codes not initialized. Call _process_column_codes() first.")
        
        if not question_code:
            raise ValueError("question_code cannot be empty")
        
        response_codes_for_question = self.response_column_codes.loc[
            self.response_column_codes['question_code'] == question_code]
            
        if response_codes_for_question.empty:
            raise ValueError(f"No response codes found for question: {question_code}")
            
        return response_codes_for_question

    def _process_radio_question(self, question_id):
        question_code = self._get_question_code(question_id)

        # Get responses and filter out empty/null values before counting
        raw_responses = self.responses_user_input[question_code]
        # Filter out empty strings, None, and NaN values
        filtered_responses = raw_responses[raw_responses.notna() & (raw_responses != '')]
        responses = filtered_responses.value_counts()

        # getting the mapping between option codes and text answers 
        # CRITICAL FIX: Ensure question_id is string to match options DataFrame qid column type
        question_id_str = str(question_id)
        mapper = self.options.loc[self.options['qid'] == question_id_str].set_index(
            'option_code')['answer'].to_dict()
        # fixing the code that lime survey uses 
        mapper['-oth-'] = 'Other'

        # mapping in a safe way 
        responses.index = responses.index.map(lambda x: mapper.get(x, x))
        
        self.processed_responses[question_id] = responses


    def _process_other(self, question_id):
        # TODO: consider if this isn't taken care of by the text responses. 
        # If so, just pick the answer up later after processing 
        question_code = self._get_question_code(question_id=question_id)
        
        other_question_pattern = f"{question_code}[other]"
        
        responses = self.responses_user_input[other_question_pattern]
        
        self.processed_responses[question_id] = responses 
    
    def _get_absolute_count_and_response_rate(self, question_code: str) -> pd.DataFrame:
        """
        Calculate absolute counts and response rates for a question.
        
        Args:
            question_code: The question code to analyze
            
        Returns:
            DataFrame with absolute_counts and response_rates columns
            
        Raises:
            ValueError: If required data is not available or data format is invalid
        """
        if not hasattr(self, 'responses_user_input') or self.responses_user_input is None:
            raise ValueError("responses_user_input not initialized. Call _load_response_data() first.")
        
        # get the question response codes for this question
        question_response_codes = self._get_response_codes_for_question(question_code)

        # Validate that the response codes exist in responses_user_input
        missing_codes = [code for code in question_response_codes.index 
                        if code not in self.responses_user_input.columns]
        if missing_codes:
            raise ValueError(f"Response codes not found in user input data: {missing_codes}")

        # Get the subset of responses for this question
        response_subset = self.responses_user_input[question_response_codes.index].copy()
        
        # Convert responses to numeric format with strict validation
        # Expected format: 'Y' = selected, '' or NaN = not selected
        # Anything else is invalid data
        for col in response_subset.columns:
            valid_values = response_subset[col].isin(['Y', '', 'N']) | response_subset[col].isna()
            if not valid_values.all():
                invalid_values = response_subset[col][~valid_values].unique()
                raise ValueError(
                    f"Invalid response values in column {col}: {invalid_values}. "
                    f"Expected only 'Y', '', 'N', or NaN values."
                )
        
        # Convert to numeric: Y=1, everything else=0
        numeric_subset = response_subset.replace({'Y': 1, 'N': 0, '': 0}).fillna(0)
        # Explicitly ensure integer type to avoid future warning
        numeric_subset = numeric_subset.infer_objects(copy=False).astype(int)

        # how many respondents marked each option
        absolute_counts = numeric_subset.sum()

        # get the response rate (to not give users who answer a lot extra weight)
        response_rates = _get_response_rate(absolute_counts, numeric_subset)
        
        # join them in a dataframe 
        response_stats = pd.DataFrame({"absolute_counts": absolute_counts, 
                        "response_rates": response_rates})
        
        return response_stats


    def _process_multiple_choice_question(self, question_id):
        """
        Calculates statistics for multiple choice question responses.

        Parameters:
            question_id: The ID of the question to analyze
            questions: DataFrame containing survey questions
            responses_user_input: DataFrame containing user responses
            response_column_codes: DataFrame mapping response codes (from get_columns_codes_for_responses_user_input)

        Returns:
            DataFrame containing:
                - absolute_counts: Raw count of responses for each option
                - response_rates: Fraction of respondents who selected each option
                - option_code: The code for each response option
                - option_text: The human-readable text for each option

        Note:
            This function assumes responses are marked with 'Y' for selected options
            and empty strings for unselected options.
        """
        
        # get the question code 
        question_code = self._get_question_code(question_id)
        

        # calculate response counts and response rates 
        response_stats = self._get_absolute_count_and_response_rate(question_code)
        
        # enrich the data with the option code
        response_stats['option_code'] = self.response_column_codes.loc[response_stats.index, 'appendage']

        # unfortunately for multiple choice questions the options data is in the questions response
        options_data_for_question = self.questions.loc[self.questions.parent_qid==question_id]
        
        # get the mapper between option code (title) and question text (question) 
        code_to_question_text_mapper = options_data_for_question.set_index('title')['question'].to_dict()

        # use that mapper to map the option text to the response rate and response count 
        response_stats['option_text'] = response_stats['option_code'].map(lambda x: code_to_question_text_mapper.get(x, x))
    
        # Format the output nicely
        response_stats = response_stats[['option_text', 'absolute_counts', 'response_rates']]
        response_stats = response_stats.round(3)  # Round to 3 decimal places
        
        self.processed_responses[question_id] = response_stats
    

    def _process_sub_question_multiple_short_text(self, sub_question_qid,
                                                parent_question_code):
        # get the question code 
        sub_question_code = self._get_question_code(sub_question_qid)

        # compose a question code for from parent and sub_question codes  
        question_code_for_responses = f"{parent_question_code}[{sub_question_code}]"

        responses = self.responses_user_input[question_code_for_responses]
        
        return responses 

    def _process_multiple_short_text(self, question_id):
        # get question code 
        parent_question_code = self._get_question_code(question_id)
        
        # get sub-question qid 
        sub_question_qids = self.questions.loc[self.questions.parent_qid == question_id, 'qid'].values
        
        responses = {}
        # loop over the sub-questions 
        for sub_question_qid in sub_question_qids: 
            # get the text title for the sub-question
            # CRITICAL FIX: Ensure sub_question_qid is string to match questions DataFrame qid column type
            sub_question_qid_str = str(sub_question_qid)
            title = self.questions.set_index('qid').loc[sub_question_qid_str, 'question']

            responses[title] = self._process_sub_question_multiple_short_text(
                sub_question_qid, parent_question_code)
            
        self.processed_responses[question_id] = responses 
            
    def _process_text_question(self, question_id):
        question_code = self._get_question_code(question_id)
        responses = self.responses_user_input[question_code].dropna()
        
        self.processed_responses[question_id] = responses 

    def _question_has_other(self, question_id):
        
        # CRITICAL FIX: Ensure question_id is string to match questions DataFrame qid column type
        question_id_str = str(question_id)
        has_other = self.questions.set_index('qid').loc[question_id_str, 'other']
        
        if has_other == 'Y':
            return True 
        elif has_other == 'N':
            return False 
        else:
            print(question_id)
            raise ValueError("unexpected value in other column")
            
    
    def _get_question_code(self, question_id):
        """
        The question code is called "title" in the questions dataset 
        """
        # CRITICAL FIX: Ensure question_id is string to match questions DataFrame qid column type
        question_id_str = str(question_id)
        try:
            return self.questions.set_index('qid').loc[question_id_str, 'title']
        except KeyError:
            raise ValueError(f"Question ID {question_id_str} not found in questions dataset")
        except Exception as e:
            raise ValueError(f"Error retrieving question code for question {question_id_str}: {e}")

 
    def _process_array_subquestion(self, sub_question_qid, parent_question_code):

        lime_survey_array_question_mapper = {
            "I": "Increase",
            "S": "Same",
            "D": "Decrease"
            }
        # get its question code 
        sub_question_code = self._get_question_code(sub_question_qid)

        # compose a question code for array responses 
        question_code_for_responses = f"{parent_question_code}[{sub_question_code}]"

        # get the responses, with the lime survey codes (I, S, D)
        array_responses = self.responses_user_input[question_code_for_responses]

        # map those to human readable (Increases, Same, Diminishes)
        array_responses_human_readable = array_responses.map(lime_survey_array_question_mapper)

        return array_responses_human_readable

    def _process_array_question(self, question_id):

        # we will use the nomenclature parent_qid to show it's a parent and distinguish it 
        # from the children question ids 
        parent_qid = question_id

        # get the question code 
        parent_question_code = self._get_question_code(question_id=parent_qid)

        # get the ids of the sub questions for the array question 
        # CRITICAL FIX: Ensure parent_qid is string to match questions DataFrame parent_qid column type
        parent_qid_str = str(parent_qid)
        array_sub_questions_qids = self.questions.set_index('parent_qid').loc[
            parent_qid_str, 'qid'].values

        # loop over the sub_questions and get the answers 
        sub_question_responses = {}
        for sub_question_qid in array_sub_questions_qids:
            sub_question_responses[sub_question_qid] = self._process_array_subquestion(sub_question_qid, 
                                                                                  parent_question_code
                                                                                 )
        # make a dataframe 
        array_question_responses = pd.DataFrame(sub_question_responses)

        self.processed_responses[parent_qid] = array_question_responses
    
    def get_questions_in_survey_order(self):
        '''
        returns dataframe with question order, type, question_id, and question title text 
        '''
        return self.questions.set_index(['gid', 'question_order']).sort_index()

    def process_question(self, question_id): 

        # CRITICAL FIX: Ensure question_id is string to match questions DataFrame qid column type
        question_id_str = str(question_id)
        question = self.questions.set_index('qid').loc[question_id_str]
        question_theme = question['question_theme_name']


        handler = self.question_handlers.get(question_theme)
        if handler:
            return handler(question_id)
        else:
            raise NotImplementedError(f"Question type '{question_theme}' not yet implemented (question ID: {question_id_str})")
        
    
    def process_all_questions(self):
        """Process all questions in the survey."""
        # Get questions that are not sub-questions
        main_questions = self.questions[self.questions['parent_qid'].fillna('None') == '0']
        
        if self.verbose:
            main_questions = tqdm(main_questions.itertuples(), desc="Processing questions", total=len(main_questions))
        else:
            main_questions = main_questions.itertuples()
            
        for question in main_questions:
            try:
                self.process_question(question.qid)
            except Exception as e:
                if self.verbose:
                    print(f"Failed to process question {question.qid}: {e}")
                self.fail_message_log[question.qid] = e

    @classmethod
    def analyze_comprehensive(cls, survey_id: str, config_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Perform a comprehensive analysis of a survey.
        
        This is a convenience class method that combines multiple analysis steps
        into a single call with complete results.
        
        Args:
            survey_id: The ID of the survey to analyze
            config_path: Optional path to credentials file
            
        Returns:
            Dictionary containing:
                - survey_info: Survey properties from API
                - summary: Survey summary statistics  
                - processed_responses: All processed question responses
                - questions: DataFrame of questions
                - options: DataFrame of question options
                - groups: List of question groups
                - failure_log: Any questions that failed to process
                
        Returns None if analysis fails.
        """
        try:
            from .client import LimeSurveyClient
            
            # Initialize API client
            api = LimeSurveyClient.from_config(config_path) if config_path else LimeSurveyClient.from_config()
            
            # Create analysis instance
            analysis = cls(survey_id)
            analysis.setup(api=api)
            
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

