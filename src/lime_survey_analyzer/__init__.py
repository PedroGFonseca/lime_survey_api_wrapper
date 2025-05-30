"""
LimeSurvey API Analyzer

A comprehensive Python library for interacting with LimeSurvey's RemoteControl API.
Provides organized access to survey data, responses, and metadata through a clean,
manager-based architecture.

Features:
- Intuitive manager-based API organization
- Robust session management with auto-session and persistent modes  
- Comprehensive error handling and validation
- Read-only operations for maximum safety
- Support for all major LimeSurvey data types
- Optional graph visualization of conditional logic
- Extensive test coverage and documentation

Example:
    from lime_survey_analyzer import LimeSurveyDirectAPI
    
    # Auto-session mode (perfect for scripts)
    api = LimeSurveyDirectAPI.from_env()
    surveys = api.surveys.list_surveys()
    
    # Persistent session mode (efficient for applications)  
    api = LimeSurveyDirectAPI.from_env(auto_session=False)
    api.connect()
    surveys = api.surveys.list_surveys()
    responses = api.responses.export_responses(surveys[0]['sid'])
    api.disconnect()
"""

from .client import LimeSurveyDirectAPI
from .session import SessionManager
from .managers.survey import SurveyManager
from .managers.question import QuestionManager
from .managers.response import ResponseManager
from .managers.participant import ParticipantManager

__version__ = "1.0.0"
__author__ = "LimeSurvey API Team"
__email__ = "api@limesurvey.org"

__all__ = [
    "LimeSurveyDirectAPI",
    "SessionManager",
    "SurveyManager", 
    "QuestionManager",
    "ResponseManager",
    "ParticipantManager"
] 