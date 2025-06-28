"""
Display utilities for survey analysis results.

This module provides functions for formatting and displaying survey data.
"""

import pandas as pd
from typing import Optional


def format_dataframe(df: Optional[pd.DataFrame], title: str = "DataFrame") -> str:
    """
    Format a DataFrame for display.
    
    Args:
        df: The DataFrame to format (can be None)
        title: Title to display above the DataFrame
        
    Returns:
        Formatted string representation of the DataFrame
    """
    if df is None or df.empty:
        return f"{title}: Empty"
    return f"{title}:\n{df.to_string()}" 