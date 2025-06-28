"""
Horizontal bar chart implementation.

Pure visualization function for creating horizontal bar charts.
"""

from typing import Dict, Any
import pandas as pd
import plotly.graph_objects as go
from ..utils.text import wrap_text_labels
from .base import get_chart_layout_base


def create_horizontal_bar_chart(data: pd.Series, title: str, config: Dict[str, Any]) -> go.Figure:
    """
    Create a horizontal bar chart for survey question results.
    
    Args:
        data: pd.Series with category names as index, counts as values
        title: Chart title
        config: Visualization configuration dictionary
        
    Returns:
        Plotly Figure object
    """
    style = config['chart_style']
    
    # Sort data so largest bar is on top (ascending order for horizontal bars)
    data_sorted = data.sort_values(ascending=True)
    
    # Wrap long category labels
    wrapped_labels = wrap_text_labels(list(data_sorted.index))
    
    # Create clean hover text
    hover_text = [f"{label}: {value} respostas" for label, value in zip(data_sorted.index, data_sorted.values)]
    
    # Create horizontal bar plot
    fig = go.Figure(data=[
        go.Bar(
            y=wrapped_labels,
            x=data_sorted.values,
            orientation='h',
            marker=dict(
                color=style['primary_color'],
                line=dict(color=style['border_color'], width=1)
            ),
            text=data_sorted.values,
            textposition='inside',
            textfont=dict(
                color=style['text_color'], 
                size=style['font_size_text'], 
                family=style['font_family']
            ),
            hovertext=hover_text,
            hoverinfo='text'
        )
    ])

    # Get base layout and add chart-specific settings
    layout = get_chart_layout_base(title, config)
    layout.update({
        'xaxis': {
            'title': {
                'text': "Number of Responses",
                'font': {'family': style['font_family'], 'size': style['font_size_axis']}
            },
            'tickfont': {'family': style['font_family'], 'size': style['font_size_axis']}
        },
        'yaxis': {
            'title': "",
            'tickfont': {'family': style['font_family'], 'size': style['font_size_axis']}
        },
        'height': style['chart_height'],
        'margin': {'l': 200, 'r': 50, 't': 80, 'b': 50}
    })
    
    fig.update_layout(layout)
    return fig 