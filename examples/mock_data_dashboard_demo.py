#!/usr/bin/env python3
"""
Mock Data Dashboard Demo

This script demonstrates the complete survey analysis and visualization pipeline
using generated mock data instead of real survey data. It creates:

1. Mock survey data using the enhanced generator
2. A SurveyAnalysis instance with the mock data
3. Processed question responses
4. Interactive charts and visualizations  
5. A Dash web application to display everything

This is completely safe to run and commit since it uses no real survey data.
"""

import pandas as pd
import sys
import os
from pathlib import Path
import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import our enhanced data generator
sys.path.insert(0, str(Path(__file__).parent.parent / 'tests'))
from enhanced_data_generators import create_enhanced_test_data

# Import our analysis and visualization modules
from lime_survey_analyzer.analyser import SurveyAnalysis
from lime_survey_analyzer.viz.charts.horizontal_bar import create_horizontal_bar_chart
from lime_survey_analyzer.viz.charts.ranking_stacked import create_ranking_stacked_bar_chart  
from lime_survey_analyzer.viz.charts.text_responses import create_text_responses_chart
from lime_survey_analyzer.viz.config import get_config
from lime_survey_analyzer.viz.utils.text import clean_html_tags


class MockSurveyAnalysis(SurveyAnalysis):
    """
    Mock version of SurveyAnalysis that works with generated data instead of API.
    """
    
    def __init__(self, mock_data: Dict[str, Any], survey_id: str = "MOCK_SURVEY", verbose: bool = False):
        """Initialize with mock data instead of API connection."""
        self.survey_id = survey_id
        self.verbose = verbose
        self.api = None  # No API connection needed
        
        # Set up data from mock generator
        self.questions = mock_data['questions']
        self.options = mock_data['options']
        self.responses_user_input = mock_data['responses_user_input']
        self.responses_metadata = mock_data['responses_metadata']
        self.groups = mock_data['groups']
        self.properties = mock_data['properties']
        self.summary = mock_data['summary']
        
        # Create response column codes mapping
        self._setup_response_column_codes()
        
        # Initialize containers
        self.processed_responses = {}
        self.fail_message_log = {}
        
        # Question handlers mapping (same as parent class)
        self.question_handlers = {
            'longfreetext': self._process_text_question,
            'listradio': self._process_radio_question,
            'numerical': self._process_text_question,
            'equation': self._process_radio_question,
            'multipleshorttext': self._process_multiple_short_text,
            'ranking': self._process_ranking_question,
            'shortfreetext': self._process_text_question,
            'image_select-listradio': self._process_radio_question,
            'multiplechoice': self._process_multiple_choice_question,
            'arrays/increasesamedecrease': self._process_array_question,
            'image_select-multiplechoice': self._process_multiple_choice_question
        }
    
    def _setup_response_column_codes(self):
        """Create response column codes mapping for mock data."""
        from lime_survey_analyzer.analyser import get_columns_codes_for_responses_user_input
        self.response_column_codes = get_columns_codes_for_responses_user_input(self.responses_user_input)
        self.response_codes_to_question_codes = self.response_column_codes['question_code'].to_dict()
    
    def setup(self, **kwargs):
        """Override setup method since we already have all data."""
        pass  # No setup needed for mock data
    
    def _get_max_answers(self, question_id):
        """Override to return reasonable defaults for mock data."""
        # For ranking questions, return a reasonable default
        question_id_str = str(question_id)
        if question_id_str in self.questions['qid'].values:
            question_info = self.questions[self.questions['qid'] == question_id_str].iloc[0]
            if question_info.get('question_theme_name') == 'ranking':
                return 5  # Reasonable default for rankings
        return 1000000  # Default fallback


def generate_mock_survey_data(verbose: bool = False) -> Dict[str, Any]:
    """Generate comprehensive mock survey data using enhanced generator."""
    if verbose:
        print("🏭 Generating mock survey data...")
    
    mock_data = create_enhanced_test_data()
    
    if verbose:
        print(f"✅ Generated mock data:")
        print(f"   📊 Survey: Mock Survey Analysis")
        print(f"   ❓ Questions: {len(mock_data['questions'])}")
        print(f"   📝 Responses: {len(mock_data['responses_user_input'])} completed, {len(mock_data['responses_metadata']) - len(mock_data['responses_user_input'])} incomplete")
        print(f"   🎯 Options: {len(mock_data['options'])}")
        print(f"   📋 Groups: {len(mock_data['groups'])}")
    
    return mock_data


def create_chart_for_question(analysis: MockSurveyAnalysis, question_id: str, config: Dict[str, Any], verbose: bool = False) -> Optional[Dict[str, Any]]:
    """Create a chart for a specific question."""
    try:
        question_id_str = str(question_id)
        question_info = analysis.questions[analysis.questions['qid'] == question_id_str]
        
        if question_info.empty:
            if verbose:
                print(f"⚠️ Question {question_id} not found")
            return None
        
        question_row = question_info.iloc[0]
        question_theme = question_row.get('question_theme_name', '')
        question_title = clean_html_tags(question_row['question'])
        
        if question_id not in analysis.processed_responses:
            if verbose:
                print(f"⚠️ No processed data for question {question_id}")
            return None
        
        data = analysis.processed_responses[question_id]
        
        # Create chart based on question type
        if question_theme in ['listradio', 'image_select-listradio']:
            if isinstance(data, pd.Series) and len(data) > 0:
                fig = create_horizontal_bar_chart(data, question_title, config)
                return {
                    'question_id': question_id,
                    'title': question_title,
                    'chart_type': 'horizontal_bar',
                    'figure': fig,
                    'data': data
                }
        
        elif question_theme == 'ranking':
            if isinstance(data, pd.DataFrame) and not data.empty:
                fig = create_ranking_stacked_bar_chart(data, question_title, config)
                return {
                    'question_id': question_id,
                    'title': question_title,
                    'chart_type': 'ranking_stacked',
                    'figure': fig,
                    'data': data
                }
        
        elif question_theme in ['longfreetext', 'shortfreetext', 'numerical']:
            if isinstance(data, pd.Series) and len(data) > 0:
                # Convert to list of text responses
                text_responses = data.dropna().tolist()
                return {
                    'question_id': question_id,
                    'title': question_title,
                    'chart_type': 'text_responses',
                    'figure': None,  # Text responses don't need plotly figures
                    'data': text_responses[:50]  # Limit for display
                }
        
        elif question_theme == 'multipleshorttext':
            if isinstance(data, dict):
                return {
                    'question_id': question_id,
                    'title': question_title,
                    'chart_type': 'multiple_short_text',
                    'figure': None,
                    'data': data
                }
        
        elif question_theme == 'multiplechoice':
            if isinstance(data, pd.DataFrame) and not data.empty:
                # Create horizontal bar chart from option_text and absolute_counts
                if 'option_text' in data.columns and 'absolute_counts' in data.columns:
                    series_data = data.set_index('option_text')['absolute_counts']
                    fig = create_horizontal_bar_chart(series_data, question_title, config)
                    return {
                        'question_id': question_id,
                        'title': question_title,
                        'chart_type': 'horizontal_bar',
                        'figure': fig,
                        'data': series_data
                    }
        
        else:
            if verbose:
                print(f"🚫 Unsupported question type: {question_theme}")
            return None
    
    except Exception as e:
        if verbose:
            print(f"❌ Error creating chart for question {question_id}: {e}")
        return None


def create_mobile_chart_card(chart_info: Dict[str, Any]) -> dbc.Card:
    """Create a mobile-optimized chart card."""
    clean_title = clean_html_tags(chart_info.get('title', 'Untitled Chart'))
    chart_type = chart_info.get('chart_type', 'unknown')
    question_id = chart_info.get('question_id', 'unknown')
    
    # Create chart content based on type
    if chart_type == 'text_responses':
        # For text responses, create a collapsible card
        data = chart_info.get('data', [])
        chart_content = dbc.Card([
            dbc.CardHeader([
                dbc.Button(
                    [
                        html.I(className="fas fa-chevron-down me-2"),
                        f"Text Responses ({len(data)} total)"
                    ],
                    id=f"btn-collapse-{question_id}",
                    color="light", 
                    size="sm",
                    className="w-100 text-start",
                    n_clicks=0
                )
            ]),
            dbc.Collapse(
                dbc.CardBody([
                    html.Div([
                        html.P(f"{idx + 1}. {response}", className="mb-2")
                        for idx, response in enumerate(data[:20])
                    ], className="overflow-auto", style={"maxHeight": "300px"})
                ], className="p-2"),
                id=f"collapse-{question_id}",
                is_open=False
            )
        ], className="mb-3")
        
    elif chart_type == 'multiple_short_text':
        # For multiple short text, show each sub-question
        data = chart_info.get('data', {})
        chart_content = html.Div([
            html.Div([
                html.H6(sub_title, className="text-primary mb-2"),
                html.Div([
                    html.P(f"• {response}", className="mb-1 small")
                    for response in sub_data.dropna().head(5)
                ], className="mb-3")
            ]) for sub_title, sub_data in data.items()
        ])
        
    else:
        # Regular plotly chart with mobile config
        figure = chart_info.get('figure')
        if figure is not None:
            # Create mobile-optimized figure
            mobile_fig = figure
            mobile_fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=40),
                font=dict(size=12),
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            
            chart_content = dcc.Graph(
                figure=mobile_fig,
                responsive=True,
                config={'displayModeBar': False}
            )
        else:
            chart_content = html.Div([
                html.P("Chart data not available", className="text-muted text-center p-3")
            ])
    
    return dbc.Card([
        dbc.CardHeader([
            html.H6(clean_title, className="mb-0 text-wrap"),
            dbc.Badge(chart_type.replace('_', ' ').title(), 
                     color="primary", className="ms-2")
        ]),
        dbc.CardBody(chart_content, className="p-2")
    ], className="mb-3 shadow-sm")


def create_dashboard_app(charts: List[Dict[str, Any]], survey_title: str = "Mock Survey Analysis") -> dash.Dash:
    """Create Dash app with survey charts."""
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    
    # Mobile-responsive meta tags and custom CSS
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <meta name="viewport" content="width=device-width, initial-scale=1.0, shrink-to-fit=no">
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
            <link href="https://fonts.googleapis.com/css2?family=Ubuntu:wght@300;400;500;700&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                body {
                    font-family: 'Ubuntu', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
                }
                .chart-grid {
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 1rem;
                }
                @media (min-width: 768px) {
                    .chart-grid {
                        grid-template-columns: 1fr 1fr;
                    }
                }
                @media (min-width: 1200px) {
                    .chart-grid {
                        grid-template-columns: 1fr 1fr 1fr;
                    }
                }
                .js-plotly-plot {
                    width: 100% !important;
                }
                .card-header h6 {
                    line-height: 1.3;
                    word-wrap: break-word;
                }
            </style>
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    # Create chart cards
    chart_cards = [create_mobile_chart_card(chart) for chart in charts]
    
    # Group charts for better organization
    chart_sections = []
    section_size = 6
    
    for i in range(0, len(chart_cards), section_size):
        section_charts = chart_cards[i:i + section_size]
        section_title = f"Questions {i+1}-{min(i+section_size, len(chart_cards))}"
        
        section = dbc.Card([
            dbc.CardHeader([
                dbc.Button(
                    [
                        html.I(className="fas fa-chart-bar me-2"),
                        section_title
                    ],
                    id=f"section-btn-{i}",
                    color="primary",
                    size="sm", 
                    className="w-100 text-start",
                    n_clicks=0 if i > 0 else 1
                )
            ]),
            dbc.Collapse(
                dbc.CardBody(
                    html.Div(section_charts, className="chart-grid"),
                    className="p-3"
                ),
                id=f"section-collapse-{i}",
                is_open=True if i == 0 else False
            )
        ], className="mb-4")
        
        chart_sections.append(section)
    
    # Main layout
    app.layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1([
                        html.I(className="fas fa-chart-line me-3"),
                        survey_title
                    ], className="display-6 mb-2 text-primary"),
                    html.P([
                        html.I(className="fas fa-info-circle me-2"),
                        f"Interactive dashboard with {len(charts)} visualizations from mock survey data"
                    ], className="lead text-muted mb-4"),
                    html.Hr()
                ], className="text-center py-4")
            ])
        ]),
        
        # Stats row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(len(charts)), className="text-primary mb-0"),
                        html.P("Total Charts", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(len([c for c in charts if c['chart_type'] == 'horizontal_bar'])), className="text-success mb-0"),
                        html.P("Radio Questions", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(len([c for c in charts if c['chart_type'] == 'ranking_stacked'])), className="text-warning mb-0"),
                        html.P("Ranking Questions", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(str(len([c for c in charts if c['chart_type'] == 'text_responses'])), className="text-info mb-0"),
                        html.P("Text Questions", className="text-muted mb-0")
                    ], className="text-center")
                ])
            ], width=3)
        ], className="mb-4"),
        
        # Charts sections
        html.Div(chart_sections, id="charts-container")
        
    ], fluid=True, className="px-3")
    
    # Add callbacks for collapsible sections
    for i in range(0, len(chart_cards), section_size):
        @app.callback(
            Output(f"section-collapse-{i}", "is_open"),
            Input(f"section-btn-{i}", "n_clicks"),
            State(f"section-collapse-{i}", "is_open"),
            prevent_initial_call=True
        )
        def toggle_section(n_clicks, is_open):
            return not is_open if n_clicks else is_open
    
    # Add callbacks for text response collapsibles
    for chart in charts:
        if chart['chart_type'] == 'text_responses':
            qid = chart['question_id']
            @app.callback(
                Output(f"collapse-{qid}", "is_open"),
                Input(f"btn-collapse-{qid}", "n_clicks"),
                State(f"collapse-{qid}", "is_open"),
                prevent_initial_call=True
            )
            def toggle_text(n_clicks, is_open):
                return not is_open if n_clicks else is_open
    
    return app


def main():
    """Main function to run the mock data dashboard demo."""
    print("🚀 Starting Mock Data Dashboard Demo")
    print("=" * 50)
    
    # Generate mock data
    mock_data = generate_mock_survey_data(verbose=True)
    
    print("\n📊 Setting up analysis...")
    
    # Create mock analysis instance
    analysis = MockSurveyAnalysis(mock_data, verbose=True)
    
    print("\n⚙️ Processing all questions...")
    
    # Process all questions
    analysis.process_all_questions()
    
    print(f"✅ Processed {len(analysis.processed_responses)} questions")
    if analysis.fail_message_log:
        print(f"⚠️ Failed to process {len(analysis.fail_message_log)} questions")
    
    print("\n🎨 Creating visualizations...")
    
    # Get visualization config
    config = get_config()
    
    # Create charts for all processed questions
    charts = []
    for question_id in analysis.processed_responses.keys():
        chart = create_chart_for_question(analysis, question_id, config, verbose=True)
        if chart:
            charts.append(chart)
    
    print(f"✅ Created {len(charts)} charts")
    
    # Create dashboard
    print("\n🌐 Creating dashboard...")
    survey_title = "Mock Survey Analysis Demo"
    app = create_dashboard_app(charts, survey_title)
    
    print("\n🎉 Dashboard ready!")
    print("📊 Chart breakdown:")
    chart_types = {}
    for chart in charts:
        chart_type = chart['chart_type']
        chart_types[chart_type] = chart_types.get(chart_type, 0) + 1
    
    for chart_type, count in chart_types.items():
        print(f"   • {chart_type.replace('_', ' ').title()}: {count}")
    
    print("\n" + "=" * 50)
    print("🌐 Starting web server...")
    print("📱 Dashboard will be available at: http://127.0.0.1:8050")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the app
    app.run(debug=False, host='127.0.0.1', port=8050)


if __name__ == "__main__":
    main() 