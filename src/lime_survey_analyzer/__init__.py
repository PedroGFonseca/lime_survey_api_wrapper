"""
LimeSurvey API Analyzer

A comprehensive Python client for interacting with LimeSurvey's RemoteControl API.
Provides organized access to survey, question, response, and participant operations.
"""

from .client import LimeSurveyDirectAPI
from .managers.survey import SurveyManager
from .managers.question import QuestionManager
from .managers.response import ResponseManager
from .managers.participant import ParticipantManager

__version__ = "1.0.0"
__author__ = "LimeSurvey API Team"
__email__ = "api@limesurvey.org"

__all__ = [
    "LimeSurveyDirectAPI",
    "SurveyManager", 
    "QuestionManager",
    "ResponseManager",
    "ParticipantManager"
] 