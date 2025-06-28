"""
Adapter for lime_survey_analyzer data extraction.

Functions to extract and format data from lime_survey_analyzer for visualization.
"""

import os
from typing import Tuple, List, Dict, Any
import pandas as pd
from lime_survey_analyzer import LimeSurveyClient, SurveyAnalysis
from ..utils.text import clean_html_tags


def setup_survey_analysis(credentials_path: str, verbose: bool = False) -> SurveyAnalysis:
    """
    Set up survey analysis with lime_survey_analyzer.
    
    Args:
        credentials_path: Path to credentials file
        verbose: Whether to print setup messages
        
    Returns:
        Configured SurveyAnalysis instance
    """
    api = LimeSurveyClient.from_config(credentials_path)
    # Get the actual survey ID from the API (use first available survey)
    surveys = api.surveys.list_surveys()
    actual_survey_id = surveys[0]['sid']
    
    if verbose:
        print(f"📡 Connecting to survey ID: {actual_survey_id}")
    
    analysis = SurveyAnalysis(actual_survey_id, verbose=False)  # Keep analysis quiet
    analysis.setup(api=api)
    analysis.process_all_questions()
    
    if verbose:
        print("✅ Survey analysis setup complete")
    
    return analysis


def get_survey_questions_metadata(analysis: SurveyAnalysis) -> pd.DataFrame:
    """
    Extract questions metadata as DataFrame.
    
    Args:
        analysis: Configured SurveyAnalysis instance
        
    Returns:
        DataFrame with question metadata indexed by question ID
    """
    return analysis.questions.set_index('qid')


def extract_listradio_data(analysis: SurveyAnalysis, question_id: int) -> Tuple[pd.Series, str]:
    """
    Extract data for listradio question.
    
    Args:
        analysis: Configured SurveyAnalysis instance
        question_id: Question ID to extract
        
    Returns:
        Tuple of (data_series, question_title)
        data_series: pd.Series with category names as index, counts as values
    """
    question_data = analysis.processed_responses[question_id]
    questions_df = get_survey_questions_metadata(analysis)
    question_id_str = str(question_id)
    question_title = questions_df.loc[question_id_str, 'question']
    
    return question_data, question_title


def extract_ranking_data(analysis: SurveyAnalysis, question_id: int) -> Tuple[pd.DataFrame, str]:
    """
    Extract data for ranking question.
    
    Args:
        analysis: Configured SurveyAnalysis instance
        question_id: Question ID to extract
        
    Returns:
        Tuple of (data_dataframe, question_title)
        data_dataframe: pd.DataFrame with ranks as columns, options as rows
    """
    # Check multiple possible locations for ranking data
    if hasattr(analysis, 'ranking_data') and question_id in analysis.ranking_data:
        ranking_data = analysis.ranking_data[question_id]
    elif hasattr(analysis, 'processed_responses') and question_id in analysis.processed_responses:
        ranking_data = analysis.processed_responses[question_id]
    else:
        raise ValueError(f"No ranking data found for question {question_id}")
    
    questions_df = get_survey_questions_metadata(analysis)
    question_id_str = str(question_id)
    question_title = questions_df.loc[question_id_str, 'question']
    
    return ranking_data, question_title


def extract_text_data(analysis: SurveyAnalysis, question_id: int) -> Tuple[pd.Series, str]:
    """
    Extract data for text question.
    
    Args:
        analysis: Configured SurveyAnalysis instance
        question_id: Question ID to extract
        
    Returns:
        Tuple of (data_series, question_title)
        data_series: pd.Series with text responses
    """
    question_data = analysis.processed_responses[question_id]
    questions_df = get_survey_questions_metadata(analysis)
    question_id_str = str(question_id)
    question_title = questions_df.loc[question_id_str, 'question']
    
    return question_data, question_title


def get_supported_questions(analysis: SurveyAnalysis, question_types: List[str]) -> List[Tuple[int, pd.Series]]:
    """
    Get all questions that are supported for visualization.
    
    Args:
        analysis: Configured SurveyAnalysis instance
        question_types: List of supported question types (e.g., ['listradio', 'ranking', 'text'])
        
    Returns:
        List of tuples (question_id, question_info)
    """
    questions_df = get_survey_questions_metadata(analysis)
    supported_questions = []
    
    for question_id in analysis.processed_responses.keys():
        question_id_str = str(question_id)
        if question_id_str in questions_df.index:
            question_info = questions_df.loc[question_id_str]
            question_theme = question_info.get('question_theme_name', '')
            
            # Also check for text questions by type
            question_type = question_info.get('type', '')
            if question_theme in question_types or (question_type in ['T', 'S', 'U'] and 'text' in question_types):
                supported_questions.append((question_id, question_info))
    
    return supported_questions


def get_question_type_summary(analysis: SurveyAnalysis, verbose: bool = False) -> Dict[str, int]:
    """
    Get summary of question types in the survey.
    
    Args:
        analysis: Configured SurveyAnalysis instance
        verbose: Whether to print the summary
        
    Returns:
        Dictionary mapping question type to count
    """
    questions_df = get_survey_questions_metadata(analysis)
    unique_themes = questions_df['question_theme_name'].unique()
    
    summary = {}
    for theme in unique_themes:
        count = (questions_df['question_theme_name'] == theme).sum()
        summary[theme] = count
        if verbose:
            print(f"  - {theme}: {count} questions")
    
    # Also count text questions by type
    text_types = ['T', 'S', 'U']
    text_count = questions_df['type'].isin(text_types).sum()
    if text_count > 0:
        summary['text'] = text_count
        if verbose:
            print(f"  - text: {text_count} questions")
    
    return summary 


def extract_question_data(analysis, question_id: int, verbose: bool = False) -> Dict[str, Any]:
    """Extract data for a specific question from LimeSurvey analysis."""
    if verbose:
        print(f"🔍 Extracting data for question {question_id}")
    
    # Get question info
    question_id_str = str(question_id)
    question_info = analysis.questions[analysis.questions['qid'] == question_id_str]
    if question_info.empty:
        raise ValueError(f"Question {question_id} not found")
    
    question_row = question_info.iloc[0]
    question_type = question_row['type']
    question_theme_name = question_row.get('question_theme_name', '')
    question_text = question_row['question']
    
    if verbose:
        print(f"   Type: {question_type}, Theme: {question_theme_name}")
    
    # Handle different question types - check question type first, then theme
    if question_type == 'Q':
        # Multiple short text questions - multiple text boxes (takes precedence)
        try:
            analysis._process_multiple_short_text(question_id)
            responses = analysis.processed_responses[question_id]
            
            return {
                'chart_type': 'multiple_short_text',
                'data': responses,
                'title': clean_html_tags(question_text),
                'question_id': question_id,
                'question_type': question_type
            }
        except Exception as e:
            if verbose:
                print(f"   ❌ Failed to process multiple short text question: {e}")
            return None
            
    elif question_type in ['T', 'S', 'U']:
        # Text questions - text display
        try:
            analysis._process_text_question(question_id)
            responses = analysis.processed_responses[question_id]
            
            return {
                'chart_type': 'text_responses',
                'data': responses,
                'title': clean_html_tags(question_text),
                'question_id': question_id,
                'question_type': question_type
            }
        except Exception as e:
            if verbose:
                print(f"   ❌ Failed to process text question: {e}")
            return None
            
    elif question_theme_name == 'listradio':
        # Single choice questions - horizontal bar chart
        try:
            analysis._process_radio_question(question_id)
            responses = analysis.processed_responses[question_id]
            
            return {
                'chart_type': 'horizontal_bar',
                'data': responses,
                'title': clean_html_tags(question_text),
                'question_id': question_id,
                'question_type': question_type
            }
        except Exception as e:
            if verbose:
                print(f"   ❌ Failed to process listradio question: {e}")
            return None
            
    elif question_theme_name == 'ranking':
        # Ranking questions - stacked bar chart
        try:
            analysis._process_ranking_question(question_id)
            responses = analysis.processed_responses[question_id]
            
            return {
                'chart_type': 'ranking_stacked',
                'data': responses,
                'title': clean_html_tags(question_text),
                'question_id': question_id,
                'question_type': question_type
            }
        except Exception as e:
            if verbose:
                print(f"   ❌ Failed to process ranking question: {e}")
            return None
    
    else:
        if verbose:
            print(f"   ⚠️ Unsupported question type: {question_type} / {question_theme_name}")
        return None 


def extract_survey_data(survey_id, credentials_path=None, verbose=False):
    """
    Extract survey data and identify supported questions.
    
    Args:
        survey_id: Survey ID (not used, we get first available)
        credentials_path: Path to credentials file
        verbose: Enable verbose output
        
    Returns:
        Dictionary with analysis and supported questions
    """
    if verbose:
        print("📡 Connecting to first available survey...")
    
    # Setup analysis
    analysis = setup_survey_analysis(credentials_path, verbose)
    
    # Get all questions and identify supported ones
    questions = analysis.questions
    
    # CRITICAL FIX: Filter out sub-questions (parent_qid != '0')
    # Only process main questions to avoid SQ001/SQ002 type errors
    main_questions = questions[questions['parent_qid'] == '0']
    
    if verbose:
        print(f"📋 Total questions in survey: {len(questions)}")
        print(f"📋 Main questions (parent_qid='0'): {len(main_questions)}")
        print(f"📋 Sub-questions (parent_qid!='0'): {len(questions) - len(main_questions)}")
    
    supported_questions = []
    
    for _, question in main_questions.iterrows():
        qid = question['qid']
        question_type = question['type']
        question_theme_name = question.get('question_theme_name', '')
        
        # Check if this question type is supported
        if (question_theme_name in ['listradio', 'ranking'] or 
            question_type in ['T', 'S', 'U', 'Q']):
            supported_questions.append(qid)
    
    if verbose:
        print(f"📊 Found {len(supported_questions)} supported questions out of {len(main_questions)} main questions")
    
    return {
        'analysis': analysis,
        'supported_questions': supported_questions,
        'total_questions': len(main_questions)
    } 