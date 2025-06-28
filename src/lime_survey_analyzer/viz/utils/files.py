"""
File handling utilities for visualization.

Pure functions for saving charts and managing output directories.
"""

import os
from typing import Optional
import plotly.graph_objects as go
from .text import clean_filename


def save_chart(fig: go.Figure, filename: str, output_dir: str, format: str = 'html', verbose: bool = False) -> Optional[str]:
    """
    Save a Plotly figure to file.
    
    Args:
        fig: Plotly Figure object
        filename: Base filename (without extension)
        output_dir: Output directory
        format: Output format ('html' or 'png')
        verbose: Whether to print save messages
        
    Returns:
        Path to saved file or None if failed
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Clean filename
    clean_name = clean_filename(filename)
    filepath = os.path.join(output_dir, f"{clean_name}.{format}")
    
    try:
        if format == 'html':
            fig.write_html(filepath, include_plotlyjs=True)
            if verbose:
                print(f"📊 Interactive plot saved: {filepath}")
        elif format == 'png':
            fig.write_image(filepath, width=800, height=400, scale=2)
            if verbose:
                print(f"📊 Static plot saved: {filepath}")
        else:
            if verbose:
                print(f"❌ Unsupported format: {format}")
            return None
            
        return filepath
    except Exception as e:
        if verbose:
            print(f"❌ Error saving plot: {e}")
        return None


def save_plot_as_html(fig: go.Figure, filename: str, output_dir: str = 'charts', verbose: bool = False) -> Optional[str]:
    """
    Save a Plotly figure as HTML file.
    
    Args:
        fig: Plotly Figure object
        filename: Base filename (without extension)
        output_dir: Output directory (default: 'charts')
        verbose: Whether to print save messages
        
    Returns:
        Path to saved file or None if failed
    """
    return save_chart(fig, filename, output_dir, 'html', verbose)


def save_plot_as_png(fig: go.Figure, filename: str, output_dir: str = 'charts', verbose: bool = False) -> Optional[str]:
    """
    Save a Plotly figure as PNG file.
    
    Args:
        fig: Plotly Figure object
        filename: Base filename (without extension)
        output_dir: Output directory (default: 'charts')
        verbose: Whether to print save messages
        
    Returns:
        Path to saved file or None if failed
    """
    return save_chart(fig, filename, output_dir, 'png', verbose)


def ensure_output_directory(directory: str) -> None:
    """
    Ensure output directory exists.
    
    Args:
        directory: Directory path to create if it doesn't exist
    """
    os.makedirs(directory, exist_ok=True) 