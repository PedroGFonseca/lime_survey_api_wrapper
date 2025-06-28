"""
Mobile-responsive Dash dashboard for displaying survey charts.
"""

import dash
from dash import dcc, html, Input, Output, State
from typing import List, Dict, Any
import dash_bootstrap_components as dbc
from .config import get_config
from .core import create_survey_visualizations
from .utils.text import clean_html_tags


def create_mobile_chart_card(chart_info: Dict[str, Any]) -> dbc.Card:
    """Create a mobile-optimized chart card."""
    # Handle missing fields gracefully
    clean_title = clean_html_tags(chart_info.get('title', 'Untitled Chart'))
    chart_type = chart_info.get('chart_type', 'unknown')
    question_id = chart_info.get('question_id', 'unknown')
    
    # Create chart content based on type
    if chart_type in ['text_responses', 'multiple_short_text']:
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
    else:
        # Regular plotly chart with mobile config
        figure = chart_info.get('figure')
        if figure is not None:
            # Create a copy to avoid modifying the original
            mobile_fig = figure
            mobile_fig.update_layout(
                height=400,  # Fixed height for mobile
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
                config={'displayModeBar': False}  # Hide toolbar on mobile
            )
        else:
            # Handle missing figure
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


def create_survey_dashboard(credentials_path: str, survey_id: int = None, verbose: bool = False) -> dash.Dash:
    """Create mobile-responsive survey dashboard using the working core function."""
    if verbose:
        print("🚀 Creating survey dashboard...")
    
    # Use the working core function to create charts
    result = create_survey_visualizations(
        survey_id=survey_id,
        credentials_path=credentials_path,
        output_format='dict',
        verbose=verbose
    )
    
    charts = result.get('charts', [])
    
    # Create Dash app with Bootstrap theme
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
    
    # Group charts for better mobile organization
    chart_sections = []
    section_size = 6  # 6 charts per section for mobile
    
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
                    n_clicks=0 if i > 0 else 1  # First section open by default
                )
            ]),
            dbc.Collapse(
                dbc.CardBody(
                    html.Div(section_charts, className="chart-grid"),
                    className="p-3"
                ),
                id=f"section-collapse-{i}",
                is_open=True if i == 0 else False  # First section open by default
            )
        ], className="mb-4")
        
        chart_sections.append(section)
    
    # Main layout
    app.layout = dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1(
                    [
                        html.I(className="fas fa-chart-line me-3"),
                        "Survey Results Dashboard"
                    ],
                    className="text-center mb-4 text-primary"
                ),
                dbc.Alert([
                    html.I(className="fas fa-mobile-alt me-2"),
                    f"Interactive dashboard with {len(charts)} survey visualizations. ",
                    "Tap sections to expand/collapse for easier navigation."
                ], color="info", className="text-center mb-4"),
                html.Div(chart_sections, id="chart-sections")
            ], width=12)
        ])
    ], fluid=True, className="py-3")
    
    # Add callbacks for collapsible sections
    for i in range(0, len(chart_cards), section_size):
        @app.callback(
            Output(f"section-collapse-{i}", "is_open"),
            Input(f"section-btn-{i}", "n_clicks"),
            State(f"section-collapse-{i}", "is_open"),
            prevent_initial_call=True
        )
        def toggle_section(n_clicks, is_open):
            if n_clicks:
                return not is_open
            return is_open
    
    # Add callbacks for text response collapses
    for chart in charts:
        if chart['chart_type'] in ['text_responses', 'multiple_short_text']:
            qid = chart['question_id']
            @app.callback(
                Output(f"collapse-{qid}", "is_open"),
                Input(f"btn-collapse-{qid}", "n_clicks"),
                State(f"collapse-{qid}", "is_open"),
                prevent_initial_call=True
            )
            def toggle_text(n_clicks, is_open):
                if n_clicks:
                    return not is_open
                return is_open
    
    if verbose:
        chart_types = {}
        for chart in charts:
            chart_types[chart['chart_type']] = chart_types.get(chart['chart_type'], 0) + 1
        
        type_summary = ", ".join([f"{count} {type_name}" for type_name, count in chart_types.items()])
        print(f"✅ Dashboard created with {len(charts)} charts ({type_summary})")
    
    return app


def run_survey_dashboard(credentials_path: str, 
                        survey_id: int = None,
                        host: str = '127.0.0.1', 
                        port: int = 8050,
                        debug: bool = False,
                        verbose: bool = False):
    """Create and run the mobile-responsive survey dashboard."""
    app = create_survey_dashboard(credentials_path, survey_id=survey_id, verbose=verbose)
    
    if verbose:
        print(f"🌐 Starting dashboard at http://{host}:{port}")
    
    app.run(host=host, port=port, debug=debug) 