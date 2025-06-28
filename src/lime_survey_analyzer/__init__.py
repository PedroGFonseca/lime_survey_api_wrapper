"""
LimeSurvey Analyzer - A comprehensive Python package for LimeSurvey API integration.

This package provides a clean, type-safe interface to LimeSurvey's RemoteControl API
with a focus on the 4 priority question types: L (Single Choice), M (Multiple Choice), 
S (Short Text), and R (Ranking).

Key Features:
- Manager-based API organization (surveys, questions, responses, participants)
- Comprehensive question type validation and modeling system
- Type-safe data models with full type hints
- Graceful handling of unsupported question types
- Session management with auto-session and persistent modes
- Proper logging and exception handling
- Secure file-based credential management

Security Best Practices:
- Credentials stored in configuration files in a secrets/ directory
- Configuration files are git-ignored to prevent accidental commits
- HTTPS enforced for production environments
- Comprehensive error handling and logging

Quick Start:
    from lime_survey_analyzer import LimeSurveyClient
    
    # Initialize client from configuration file
    api = LimeSurveyClient.from_config('secrets/credentials.ini')
    
    # List surveys
    surveys = api.surveys.list_surveys()
    
    # Get structured questions with validation
    questions = api.questions.list_questions_structured(survey_id)
    
    # Export responses
    responses = api.responses.export_responses(survey_id)

Configuration File Format:
    Create a file at secrets/credentials.ini:
    
    [limesurvey]
    url = https://your-limesurvey.com/admin/remotecontrol
    username = your_username
    password = your_password
"""

# Import core client
from .client import LimeSurveyClient

# Import all data models
from .models import (
    # Core survey models
    Survey, QuestionGroup, Question, SubQuestion, Answer, 
    
    # Response models
    Response, ResponseValue, ResponseData, QuestionResponses,
    
    # Question hierarchy models
    QuestionItem, QuestionHierarchy,
    
    # Properties and enums
    QuestionType, VisibilityState, MandatoryState, ResponseStatus,
    QuestionProperties, AnswerProperties, SubQuestionProperties,
)

# Import question type system
from .models.question_types import (
    # Core question type system
    QuestionCategory, QuestionTypeDefinition, AdvancedQuestionAttributes,
    PRIORITY_QUESTION_TYPES, get_priority_question_types,
    get_question_handler, is_priority_type, validate_question_attributes,
    
    # Priority handlers
    SingleChoiceRadioHandler, MultipleChoiceHandler, 
    ShortTextHandler, RankingHandler,
    
    # Base classes
    QuestionTypeHandler, NotImplementedHandler,
    
    # Complete registry
    QUESTION_TYPES,
)

# Import answer codes system for automatic mappings
from .models.question_answer_codes import (
    # Core classes
    AnswerCodeMapping, QuestionAnswerCodes,
    
    # Lookup utilities
    get_answer_codes_for_question_type, get_complete_question_mapping,
    is_question_type_predefined, list_all_predefined_mappings,
    
    # Convenience functions
    get_type_e_mapping, get_type_a_likert_mapping,
    
    # Registry mappings
    QUESTION_TYPE_TO_ANSWER_CODES, ALTERNATIVE_MAPPINGS,
)

# Import utilities
from .utils.logging import setup_logger, get_logger, configure_package_logging

# Import exceptions
from .exceptions import (
    # Base exception
    LimeSurveyError,
    
    # Specific exceptions
    AuthenticationError, APIError, SurveyNotFoundError,
    
    # Utility function
    handle_api_error,
)

# Import the original class for backward compatibility
from .analyser import SurveyAnalysis

# Re-export other important components
from .types import (
    SurveyProperties,
    SurveySummary,
    QuestionData,
    OptionData,
    ResponseMetadata,
    GroupData
)

# Import types for type checking
from . import types

# Backward compatibility
LimeSurveyDirectAPI = LimeSurveyClient

__version__ = "1.0.0"

__all__ = [
    # Main client
    "LimeSurveyClient",
    
    # Core data models
    "Survey",
    "QuestionGroup", 
    "Question",
    "SubQuestion",
    "Answer",
    "Response",
    "ResponseValue",
    "ResponseData", 
    "QuestionResponses",
    "QuestionItem",
    "QuestionHierarchy",
    
    # Properties and enums
    "QuestionType",
    "VisibilityState",
    "MandatoryState",
    "ResponseStatus", 
    "QuestionProperties",
    "AnswerProperties",
    "SubQuestionProperties",
    
    # Priority Question Type System
    "QuestionCategory",
    "QuestionTypeDefinition", 
    "AdvancedQuestionAttributes",
    "PRIORITY_QUESTION_TYPES",
    "get_priority_question_types",
    "get_question_handler",
    "is_priority_type",
    "validate_question_attributes",
    
    # Priority handlers
    "SingleChoiceRadioHandler",
    "MultipleChoiceHandler",
    "ShortTextHandler", 
    "RankingHandler",
    
    # Base classes
    "QuestionTypeHandler",
    "NotImplementedHandler",
    
    # Complete registry
    "QUESTION_TYPES",
    
    # Answer Codes System for automatic mappings
    "AnswerCodeMapping",
    "QuestionAnswerCodes", 
    "get_answer_codes_for_question_type",
    "get_complete_question_mapping",
    "is_question_type_predefined",
    "list_all_predefined_mappings",
    "get_type_e_mapping",
    "get_type_a_likert_mapping",
    "QUESTION_TYPE_TO_ANSWER_CODES",
    "ALTERNATIVE_MAPPINGS",
    
    # Utilities
    "setup_logger",
    "get_logger", 
    "configure_package_logging",
    
    # Exceptions
    "LimeSurveyError",
    "AuthenticationError",
    "APIError",
    "SurveyNotFoundError",
    
    # Analysis functionality
    "SurveyAnalysis",
    "SurveyProperties", 
    "SurveySummary",
    "QuestionData",
    "OptionData", 
    "ResponseMetadata",
    "GroupData"
] 