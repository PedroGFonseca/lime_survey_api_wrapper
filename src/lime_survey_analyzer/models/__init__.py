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

# Answer Codes System for predefined question types
from .question_answer_codes import (
    # Core classes
    AnswerCodeMapping,
    QuestionAnswerCodes,
    
    # Lookup utilities
    get_answer_codes_for_question_type,
    get_complete_question_mapping,
    is_question_type_predefined,
    list_all_predefined_mappings,
    
    # Convenience functions
    get_type_e_mapping,
    get_type_a_likert_mapping,
    
    # Registry mappings
    QUESTION_TYPE_TO_ANSWER_CODES,
    ALTERNATIVE_MAPPINGS,
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
    
    # Answer Codes System
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
] 