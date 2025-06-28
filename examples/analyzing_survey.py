"""
Compatibility bridge for test imports.
This file imports from the actual implementation in src/lime_survey_analyzer/old_analyzing_survey.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

# Import all functions that tests expect
from lime_survey_analyzer.old_analyzing_survey import * 