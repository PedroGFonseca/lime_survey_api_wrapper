"""
LimeSurvey Data Models

Comprehensive data models for LimeSurvey concepts including Questions, Options, 
Responses, and their relationships based on official LimeSurvey API documentation.

Priority Focus: Single Choice Radio (L), Multiple Choice (M), Short Text (S), Ranking (R)
"""

from .core import Survey, QuestionGroup
from .questions import Question, SubQuestion, Answer, QuestionItem, QuestionHierarchy
from .responses import Response, ResponseValue, ResponseData, QuestionResponses
from .properties import (
    QuestionType,
    VisibilityState,
    MandatoryState,
    ResponseStatus,
    QuestionProperties,
    AnswerProperties,
    SubQuestionProperties
)

# Priority Question Type System
from .question_types import (
    # Core definitions
    QuestionCategory,
    QuestionTypeDefinition,
    AdvancedQuestionAttributes,
    
    # Priority type registry and utilities
    PRIORITY_QUESTION_TYPES,
    get_priority_question_types,
    get_question_handler,
    is_priority_type,
    validate_question_attributes,
    
    # Priority handlers (fully implemented)
    SingleChoiceRadioHandler,
    MultipleChoiceHandler,
    ShortTextHandler,
    RankingHandler,
    
    # Base classes
    QuestionTypeHandler,
    NotImplementedHandler,
    
    # Complete registry (priority + not-yet-implemented)
    QUESTION_TYPES,
)

# Export all the main classes for easy importing
__all__ = [
    # Core models
    "Survey",
    "QuestionGroup", 
    "Question",
    "SubQuestion",
    "Answer",
    "QuestionItem",
    "QuestionHierarchy",
    "Response",
    "ResponseValue", 
    "ResponseData",
    "QuestionResponses",
    
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
] 