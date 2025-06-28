"""
Text processing utilities for visualization.

Pure functions for text cleaning, wrapping, and formatting.
"""

import re
from typing import List, Optional


def clean_html_tags(text: str) -> str:
    """
    Remove HTML tags from text strings.
    
    Args:
        text: Input text that may contain HTML tags
        
    Returns:
        Clean text with HTML tags removed
    """
    if not isinstance(text, str):
        return str(text)
    # Remove HTML tags using regex
    clean_text = re.sub(r'<[^>]+>', '', text)
    return clean_text.strip()


def wrap_text_labels(labels: List[str], max_length: Optional[int] = None) -> List[str]:
    """
    Wrap long text labels to multiple lines for better chart readability.
    
    Args:
        labels: List of text labels to wrap
        max_length: Maximum length before wrapping (default: 40)
        
    Returns:
        List of wrapped labels with <br> tags for line breaks
    """
    if max_length is None:
        max_length = 40
    
    wrapped_labels = []
    for label in labels:
        # Clean HTML tags first
        clean_label = clean_html_tags(label)
        if len(clean_label) > max_length:
            words = clean_label.split()
            mid_point = len(words) // 2
            line1 = ' '.join(words[:mid_point])
            line2 = ' '.join(words[mid_point:])
            wrapped_labels.append(f"{line1}<br>{line2}")
        else:
            wrapped_labels.append(clean_label)
    return wrapped_labels


def clean_filename(filename: str, max_length: Optional[int] = None) -> str:
    """
    Clean filename for filesystem compatibility.
    
    Args:
        filename: Input filename to clean
        max_length: Maximum filename length (default: 100)
        
    Returns:
        Clean filename safe for filesystem use
    """
    if max_length is None:
        max_length = 100
    
    # Remove HTML tags first
    clean_name = clean_html_tags(filename)
    
    # Keep only safe characters including Portuguese characters
    safe_chars = "".join(c for c in clean_name if c.isalnum() or c in (' ', '-', '_', 'ã', 'á', 'à', 'â', 'é', 'ê', 'í', 'ó', 'ô', 'õ', 'ú', 'ç'))
    safe_chars = safe_chars.replace(' ', '_').rstrip()
    
    # Limit length
    return safe_chars[:max_length] 