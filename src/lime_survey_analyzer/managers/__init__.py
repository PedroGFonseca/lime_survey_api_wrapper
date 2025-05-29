"""
Manager classes for LimeSurvey API operations.

This package contains focused manager classes that implement the Interface Segregation
Principle by grouping related API operations together.
"""

from .base import BaseManager
from .survey import SurveyManager
from .question import QuestionManager
from .response import ResponseManager
from .participant import ParticipantManager

__all__ = [
    "BaseManager",
    "SurveyManager",
    "QuestionManager", 
    "ResponseManager",
    "ParticipantManager"
] 