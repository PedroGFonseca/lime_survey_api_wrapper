"""
Core visualization orchestration for survey data.
"""

import os
from typing import Dict, Any, Optional, List, Union
import plotly.graph_objects as go

from .config import get_config, validate_config
from .charts.horizontal_bar import create_horizontal_bar_chart
from .charts.ranking_stacked import create_ranking_stacked_bar_chart
from .charts.text_responses import create_text_responses_chart, create_multiple_short_text_chart
from .utils.files import save_chart, save_plot_as_html, save_plot_as_png
from .adapters.lime_survey import (
    setup_survey_analysis, 
    get_supported_questions, 
    get_question_type_summary,
    extract_listradio_data,
    extract_ranking_data,
    extract_text_data,
    extract_survey_data,
    extract_question_data
)


def create_chart_from_data(data: Dict[str, Any], config: Dict[str, Any] = None, verbose: bool = False) -> go.Figure:
    """Create a chart from processed survey data."""
    if config is None:
        config = get_config()
    
    chart_type = data.get('chart_type')
    chart_data = data.get('data')
    title = data.get('title', 'Survey Question')
    
    if verbose:
        print(f"📊 Creating {chart_type} chart: {title[:60]}...")
    
    if chart_type == 'horizontal_bar':
        return create_horizontal_bar_chart(chart_data, title, config)
    elif chart_type == 'ranking_stacked':
        return create_ranking_stacked_bar_chart(chart_data, title, config)
    elif chart_type == 'text_responses':
        return create_text_responses_chart(chart_data, title, config)
    elif chart_type == 'multiple_short_text':
        return create_multiple_short_text_chart(chart_data, title, config)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")


def create_chart_for_question(question_id: int, question_info, analysis, config: Dict[str, Any], verbose: bool = False) -> bool:
    """
    Create and save chart for a single question.
    
    Args:
        question_id: Question ID to process
        question_info: Question metadata
        analysis: Survey analysis instance
        config: Visualization configuration
        verbose: Whether to print progress messages
        
    Returns:
        True if chart was created successfully, False otherwise
    """
    question_theme = question_info.get('question_theme_name', '')
    question_type = question_info.get('type', '')
    question_title = question_info['question']
    output_settings = config['output_settings']
    
    try:
        if question_theme == 'listradio':
            if verbose:
                print(f"📊 Creating horizontal bar chart for listradio question {question_id}: {question_title[:50]}...")
            
            data, title = extract_listradio_data(analysis, question_id)
            fig = create_horizontal_bar_chart(data, title, config)
            saved_path = save_chart(fig, title, output_settings['plots_dir'], output_settings['default_format'], verbose)
            
            return saved_path is not None
            
        elif question_theme == 'ranking':
            if verbose:
                print(f"📊 Creating stacked bar chart for ranking question {question_id}: {question_title[:50]}...")
            
            data, title = extract_ranking_data(analysis, question_id)
            fig = create_ranking_stacked_bar_chart(data, title, config)
            saved_path = save_chart(fig, f"{title}_ranking", output_settings['plots_dir'], output_settings['default_format'], verbose)
            
            return saved_path is not None
            
        elif question_type in ['T', 'S', 'U']:  # Text questions
            if verbose:
                print(f"📝 Creating text responses display for text question {question_id}: {question_title[:50]}...")
            
            data, title = extract_text_data(analysis, question_id)
            fig = create_text_responses_chart(data, title, config)
            saved_path = save_chart(fig, f"{title}_text", output_settings['plots_dir'], output_settings['default_format'], verbose)
            
            return saved_path is not None
            
        else:
            # Question type not supported
            return False
            
    except Exception as e:
        if verbose:
            print(f"⚠️ Error creating chart for question {question_id}: {e}")
        return False


def generate_all_charts(analysis, config: Dict[str, Any], question_types: List[str] = None, verbose: bool = False) -> int:
    """
    Generate charts for all supported question types.
    
    Args:
        analysis: Survey analysis instance
        config: Visualization configuration
        question_types: List of question types to process (default: ['listradio', 'ranking', 'text'])
        verbose: Whether to print progress messages
        
    Returns:
        Number of charts created successfully
    """
    if question_types is None:
        question_types = ['listradio', 'ranking', 'text']
    
    charts_created = 0
    
    # Show available question types for debugging
    if verbose:
        print("📋 Available question theme names in survey:")
        get_question_type_summary(analysis, verbose=True)
        print()
    
    # Get all supported questions
    supported_questions = get_supported_questions(analysis, question_types)
    
    # Process each question
    for question_id, question_info in supported_questions:
        if create_chart_for_question(question_id, question_info, analysis, config, verbose):
            charts_created += 1
    
    return charts_created


def create_survey_visualizations(
    survey_id: Union[str, int], 
    credentials_path: Optional[str] = None,
    output_format: str = 'html',
    output_dir: str = 'charts',
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Create visualizations for all supported questions in a survey.
    
    Args:
        survey_id: LimeSurvey survey ID
        credentials_path: Path to credentials file (optional)
        output_format: 'html' or 'png' 
        output_dir: Directory to save charts
        verbose: Enable verbose output
    
    Returns:
        Dictionary with summary of created charts
    """
    if verbose:
        print(f"🚀 Creating survey visualizations...")
        print(f"📡 Survey ID: {survey_id}")
        print(f"📁 Output: {output_format} files in {output_dir}/")
    
    # Extract survey data
    survey_data = extract_survey_data(survey_id, credentials_path, verbose)
    
    # Get supported questions
    supported_questions = survey_data['supported_questions']
    analysis = survey_data['analysis']
    
    if verbose:
        print(f"📊 Processing {len(supported_questions)} supported questions...")
    
    # Create charts for each question
    charts_created = []
    charts_failed = []
    
    for question_id in supported_questions:
        try:
            # Extract question data
            question_data = extract_question_data(analysis, question_id, verbose)
            
            if question_data is None:
                charts_failed.append(question_id)
                continue
            
            # Create chart
            fig = create_chart_from_data(question_data, get_config(), verbose)
            
            # Save chart
            filename = f"question_{question_id}"
            if output_format == 'html':
                save_plot_as_html(fig, filename, output_dir)
            else:
                save_plot_as_png(fig, filename, output_dir)
            
            charts_created.append({
                'question_id': question_id,
                'chart_type': question_data['chart_type'],
                'title': question_data['title'],
                'filename': f"{filename}.{output_format}"
            })
            
            if verbose:
                print(f"✅ Created {question_data['chart_type']} chart for question {question_id}")
                
        except Exception as e:
            if verbose:
                print(f"❌ Failed to create chart for question {question_id}: {e}")
            charts_failed.append(question_id)
    
    # Summary
    summary = {
        'total_questions': len(supported_questions),
        'charts_created': len(charts_created),
        'charts_failed': len(charts_failed),
        'created_charts': charts_created,
        'failed_questions': charts_failed,
        'output_format': output_format,
        'output_dir': output_dir
    }
    
    if verbose:
        print(f"\n📈 Summary:")
        print(f"   ✅ {len(charts_created)} charts created")
        print(f"   ❌ {len(charts_failed)} failed")
        print(f"   📁 Saved to {output_dir}/ as {output_format} files")
    
    return summary 