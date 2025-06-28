"""
Ranking stacked bar chart implementation.

Pure visualization function for creating stacked horizontal bar charts for ranking data.
"""

from typing import Dict, Any
import pandas as pd
import plotly.graph_objects as go
from ..utils.text import wrap_text_labels, clean_html_tags
from .base import should_show_internal_text, get_chart_layout_base


def create_ranking_stacked_bar_chart(data: pd.DataFrame, title: str, config: Dict[str, Any]) -> go.Figure:
    """
    Create a stacked horizontal bar chart for ranking question results.
    
    Args:
        data: pd.DataFrame with ranks as columns, options as rows, counts as values
        title: Chart title
        config: Visualization configuration dictionary
        
    Returns:
        Plotly Figure object
    """
    style = config['chart_style']
    settings = config['ranking_settings']
    
    # Transpose so options become rows and ranks become columns
    data_transposed = data.T
    
    # Sort by rank 1 values (first column after transpose) in descending order
    if 1 in data_transposed.columns:
        data_sorted = data_transposed.sort_values(by=1, ascending=True)
    else:
        data_sorted = data_transposed
    
    # Clean HTML from option labels and wrap text
    cleaned_labels = [clean_html_tags(label) for label in data_sorted.index]
    wrapped_labels = wrap_text_labels(cleaned_labels, max_length=settings['wrap_length'])
    
    # Create stacked horizontal bar chart
    fig = go.Figure()
    
    # Add each rank as a separate trace (stacked bars)
    for i, rank in enumerate(sorted(data_sorted.columns)):
        color_idx = min(i, len(style['ranking_colors']) - 1)
        values = data_sorted[rank].values
        
        # Calculate row totals for percentage calculation
        row_totals = data_sorted.sum(axis=1).values
        text_values = []
        
        for j, val in enumerate(values):
            # Determine if text should be shown
            percentage = (val / row_totals[j] * 100) if row_totals[j] > 0 else 0
            if should_show_internal_text(val, percentage, config):
                text_values.append(str(val))
            else:
                text_values.append('')
        
        # Create simple hover text
        hover_text = [f"Classificação {rank}: {val} respostas" for val in values]
        
        fig.add_trace(go.Bar(
            name=f'Classificação {rank}',
            y=wrapped_labels,
            x=values,
            orientation='h',
            marker=dict(
                color=style['ranking_colors'][color_idx],
                line=dict(color=style['border_color'], width=0.5)
            ),
            text=text_values,
            textposition='inside',
            textangle=0,
            textfont=dict(
                color=style['text_color'], 
                size=style['font_size_text'] - 4,
                family=style['font_family']
            ),
            insidetextfont=dict(
                color=style['text_color'],
                size=style['font_size_text'] - 4,
                family=style['font_family']
            ),
            hovertext=hover_text,
            hoverinfo='text',
            showlegend=True
        ))
    
    # Calculate dynamic height
    chart_height = max(settings['chart_height_min'], len(wrapped_labels) * settings['chart_height_per_row'])
    
    # Get base layout and add chart-specific settings
    layout = get_chart_layout_base(title, config)
    layout.update({
        'xaxis': {
            'title': {
                'text': "Número de Respostas",
                'font': {'family': style['font_family'], 'size': style['font_size_axis']}
            },
            'tickfont': {'family': style['font_family'], 'size': style['font_size_axis']}
        },
        'yaxis': {
            'title': "",
            'tickfont': {'family': style['font_family'], 'size': style['font_size_axis'] - 1},
            'tickmode': 'linear',
            'automargin': True
        },
        'barmode': 'stack',
        'height': chart_height,
        'margin': {'l': settings['left_margin'], 'r': settings['right_margin'], 't': 80, 'b': 50},
        'legend': {
            'orientation': "v",
            'yanchor': "top",
            'y': 1,
            'xanchor': "left",
            'x': 1.02,
            'font': {'family': style['font_family'], 'size': style['font_size_axis']}
        }
    })
    
    fig.update_layout(layout)
    return fig 