"""
Question Type Implementations - Priority Types Focus

Focused implementation of the most important LimeSurvey question types:
1. Single Answer (Radio) - "L" 
2. Multiple Choice - "M"
3. Free Text (Short) - "S" 
4. Ranking - "R"

Other question types are defined but raise NotImplementedError until we're ready to implement them.

Based on: https://www.limesurvey.org/manual/Question_types
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Set
from enum import Enum

from .properties import QuestionType, MandatoryState, VisibilityState
from .questions import Question, SubQuestion, Answer
from .responses import ResponseValue


class QuestionCategory(Enum):
    """Categories of question types as defined by LimeSurvey"""
    PRIORITY = "priority"  # Our focus types
    ARRAYS = "arrays"
    MASK_QUESTIONS = "mask_questions"
    MULTIPLE_CHOICE = "multiple_choice"
    SINGLE_CHOICE = "single_choice"
    TEXT_QUESTIONS = "text_questions"


@dataclass
class QuestionTypeDefinition:
    """Defines the characteristics and capabilities of a LimeSurvey question type"""
    type_code: str
    type_name: str
    category: QuestionCategory
    is_priority: bool = False  # Whether this is a priority type we fully support
    supports_subquestions: bool = False
    supports_answers: bool = False
    supports_other_option: bool = False
    supports_multiple_responses: bool = False
    supports_array_filtering: bool = False
    supports_validation: bool = False
    supports_randomization: bool = False
    supports_exclusive_options: bool = False
    supports_assessment: bool = False
    supports_dropdown_mode: bool = False
    database_fields_per_response: int = 1
    max_database_columns: Optional[int] = None
    default_answer_codes: Optional[List[str]] = None
    reserved_properties: Set[str] = field(default_factory=set)


# Priority Question Types - Fully Implemented
PRIORITY_QUESTION_TYPES = {
    "L": QuestionTypeDefinition(
        type_code="L", type_name="List (Radio)", category=QuestionCategory.PRIORITY,
        is_priority=True, supports_answers=True, supports_other_option=True, 
        supports_randomization=True, supports_assessment=True, supports_validation=True
    ),
    "M": QuestionTypeDefinition(
        type_code="M", type_name="Multiple choice", category=QuestionCategory.PRIORITY,
        is_priority=True, supports_answers=True, supports_other_option=True, 
        supports_multiple_responses=True, supports_array_filtering=True, 
        supports_validation=True, supports_randomization=True,
        supports_exclusive_options=True, supports_assessment=True
    ),
    "S": QuestionTypeDefinition(
        type_code="S", type_name="Short free text", category=QuestionCategory.PRIORITY,
        is_priority=True, supports_validation=True
    ),
    "R": QuestionTypeDefinition(
        type_code="R", type_name="Ranking", category=QuestionCategory.PRIORITY,
        is_priority=True, supports_answers=True, supports_randomization=True, 
        supports_validation=True, supports_array_filtering=True
    ),
}

# Other Question Types - Defined but not yet implemented
OTHER_QUESTION_TYPES = {
    # Arrays
    "F": QuestionTypeDefinition(
        type_code="F", type_name="Array", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, supports_answers=True, supports_array_filtering=True,
        supports_validation=True, supports_randomization=True, supports_exclusive_options=True,
        supports_assessment=True, supports_dropdown_mode=True
    ),
    "A": QuestionTypeDefinition(
        type_code="A", type_name="Array (5 point choice)", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, default_answer_codes=["1", "2", "3", "4", "5"],
        supports_array_filtering=True, supports_validation=True
    ),
    "B": QuestionTypeDefinition(
        type_code="B", type_name="Array (10 point choice)", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, default_answer_codes=[str(i) for i in range(1, 11)],
        supports_array_filtering=True, supports_validation=True
    ),
    "C": QuestionTypeDefinition(
        type_code="C", type_name="Array (Yes/No/Uncertain)", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, default_answer_codes=["Y", "N", "U"],
        supports_array_filtering=True, supports_validation=True
    ),
    "E": QuestionTypeDefinition(
        type_code="E", type_name="Array (Increase/Same/Decrease)", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, default_answer_codes=["I", "S", "D"],
        supports_array_filtering=True, supports_validation=True
    ),
    "H": QuestionTypeDefinition(
        type_code="H", type_name="Array by column", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, supports_answers=True, supports_array_filtering=True,
        supports_validation=True
    ),
    "1": QuestionTypeDefinition(
        type_code="1", type_name="Array dual scale", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, supports_answers=True, supports_array_filtering=True,
        supports_validation=True, supports_dropdown_mode=True, database_fields_per_response=2
    ),
    ";": QuestionTypeDefinition(
        type_code=";", type_name="Array (Numbers)", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, supports_answers=True, supports_array_filtering=True,
        supports_validation=True
    ),
    ":": QuestionTypeDefinition(
        type_code=":", type_name="Array (Texts)", category=QuestionCategory.ARRAYS,
        supports_subquestions=True, supports_answers=True, supports_array_filtering=True,
        supports_validation=True
    ),
    
    # Other Single Choice
    "5": QuestionTypeDefinition(
        type_code="5", type_name="5 point choice", category=QuestionCategory.SINGLE_CHOICE,
        default_answer_codes=["1", "2", "3", "4", "5"], supports_assessment=True
    ),
    "!": QuestionTypeDefinition(
        type_code="!", type_name="List (Dropdown)", category=QuestionCategory.SINGLE_CHOICE,
        supports_answers=True, supports_other_option=True, supports_randomization=True,
        supports_assessment=True
    ),
    "O": QuestionTypeDefinition(
        type_code="O", type_name="List with comment", category=QuestionCategory.SINGLE_CHOICE,
        supports_answers=True, supports_other_option=True, supports_randomization=True,
        supports_assessment=True, database_fields_per_response=2
    ),
    
    # Other Multiple Choice
    "P": QuestionTypeDefinition(
        type_code="P", type_name="Multiple choice with comments", category=QuestionCategory.MULTIPLE_CHOICE,
        supports_answers=True, supports_other_option=True, supports_multiple_responses=True,
        supports_array_filtering=True, supports_validation=True, supports_randomization=True,
        supports_exclusive_options=True, supports_assessment=True, database_fields_per_response=2
    ),
    
    # Other Text Questions
    "T": QuestionTypeDefinition(
        type_code="T", type_name="Long free text", category=QuestionCategory.TEXT_QUESTIONS,
        supports_validation=True
    ),
    "U": QuestionTypeDefinition(
        type_code="U", type_name="Huge free text", category=QuestionCategory.TEXT_QUESTIONS,
        supports_validation=True
    ),
    "Q": QuestionTypeDefinition(
        type_code="Q", type_name="Multiple short text", category=QuestionCategory.TEXT_QUESTIONS,
        supports_subquestions=True, supports_validation=True, supports_array_filtering=True
    ),
    
    # Mask Questions
    "D": QuestionTypeDefinition(
        type_code="D", type_name="Date", category=QuestionCategory.MASK_QUESTIONS,
        supports_validation=True
    ),
    "|": QuestionTypeDefinition(
        type_code="|", type_name="File upload", category=QuestionCategory.MASK_QUESTIONS,
        supports_validation=True
    ),
    "G": QuestionTypeDefinition(
        type_code="G", type_name="Gender", category=QuestionCategory.MASK_QUESTIONS,
        default_answer_codes=["M", "F"]
    ),
    "I": QuestionTypeDefinition(
        type_code="I", type_name="Language switch", category=QuestionCategory.MASK_QUESTIONS
    ),
    "N": QuestionTypeDefinition(
        type_code="N", type_name="Numerical input", category=QuestionCategory.MASK_QUESTIONS,
        supports_validation=True
    ),
    "K": QuestionTypeDefinition(
        type_code="K", type_name="Multiple numerical input", category=QuestionCategory.MASK_QUESTIONS,
        supports_subquestions=True, supports_validation=True, supports_array_filtering=True
    ),
    "X": QuestionTypeDefinition(
        type_code="X", type_name="Text display", category=QuestionCategory.MASK_QUESTIONS
    ),
    "Y": QuestionTypeDefinition(
        type_code="Y", type_name="Yes/No", category=QuestionCategory.MASK_QUESTIONS,
        default_answer_codes=["Y", "N"]
    ),
    "*": QuestionTypeDefinition(
        type_code="*", type_name="Equation", category=QuestionCategory.MASK_QUESTIONS,
        supports_validation=True
    ),
}

# Combined registry
QUESTION_TYPES = {**PRIORITY_QUESTION_TYPES, **OTHER_QUESTION_TYPES}


@dataclass
class AdvancedQuestionAttributes:
    """Advanced attributes available for LimeSurvey questions"""
    # Validation
    em_validation_q: Optional[str] = None  # ExpressionScript validation equation
    em_validation_q_tip: Optional[str] = None  # Validation tip message
    preg_validation: Optional[str] = None  # Regular expression validation
    
    # Exclusive options (Multiple Choice)
    exclusive_option: Optional[str] = None  # Answer codes that are exclusive
    autocheck_exclusive_option: bool = False  # Auto-check exclusive if all others checked
    
    # Limits and constraints
    min_answers: Optional[int] = None
    max_answers: Optional[int] = None
    
    # Display options
    random_order: bool = False
    answer_order: str = "normal"  # "normal", "alphabetically", "random"
    
    # Other options (Single Choice, Multiple Choice)
    other_replace_text: Optional[str] = None
    other_comment_mandatory: bool = False
    other_numbers_only: bool = False
    
    # Assessment
    assessment_value: Optional[float] = None
    
    # Expression Script properties
    hidden: bool = False
    relevance: str = "1"  # ExpressionScript relevance equation
    
    # Statistics
    public_statistics: bool = False
    display_chart: bool = False
    chart_type: str = "bar"


class QuestionTypeHandler(ABC):
    """Base class for handling specific question type behaviors"""
    
    def __init__(self, definition: QuestionTypeDefinition):
        self.definition = definition
    
    @abstractmethod
    def validate_question_structure(self, question: Question) -> List[str]:
        """Validate that the question structure is valid for this type"""
        pass
    
    @abstractmethod
    def generate_database_fields(self, question: Question) -> List[str]:
        """Generate the database field names for this question"""
        pass
    
    @abstractmethod
    def validate_response(self, response_value: Any, question: Question) -> bool:
        """Validate that a response value is appropriate for this question type"""
        pass
    
    @abstractmethod
    def format_response_for_export(self, response_value: Any, format_type: str) -> Any:
        """Format response value for different export types (SPSS, Excel, etc.)"""
        pass


# PRIORITY IMPLEMENTATIONS - Fully Featured

class SingleChoiceRadioHandler(QuestionTypeHandler):
    """Handler for single choice radio questions (L)"""
    
    def validate_question_structure(self, question: Question) -> List[str]:
        errors = []
        if not question.answers:
            errors.append(f"Single choice radio question {question.properties.qid} must have answer options")
        if hasattr(question, 'sub_questions') and question.sub_questions:
            errors.append(f"Single choice radio question {question.properties.qid} should not have subquestions")
        return errors
    
    def generate_database_fields(self, question: Question) -> List[str]:
        """Single choice creates one column"""
        survey_id = question.properties.sid
        group_id = question.properties.gid
        question_id = question.properties.qid
        return [f"{survey_id}X{group_id}X{question_id}"]
    
    def validate_response(self, response_value: Any, question: Question) -> bool:
        """Validate single choice response"""
        if response_value is None or response_value == "":
            return True  # Empty is valid unless mandatory
        
        # Check if response matches one of the answer codes
        valid_codes = [answer.code for answer in question.answers]
        if question.properties.other_option:
            valid_codes.append("other")
        
        return str(response_value) in valid_codes
    
    def format_response_for_export(self, response_value: Any, format_type: str) -> Any:
        """Format for different export types"""
        if format_type == "spss":
            # SPSS prefers numeric codes
            if isinstance(response_value, str) and response_value.isdigit():
                return int(response_value)
        return response_value


class MultipleChoiceHandler(QuestionTypeHandler):
    """Handler for multiple choice questions (M)"""
    
    def validate_question_structure(self, question: Question) -> List[str]:
        errors = []
        if not question.answers:
            errors.append(f"Multiple choice question {question.properties.qid} must have answer options")
        if hasattr(question, 'sub_questions') and question.sub_questions:
            errors.append(f"Multiple choice question {question.properties.qid} should not have subquestions")
        return errors
    
    def generate_database_fields(self, question: Question) -> List[str]:
        """Multiple choice creates one column per answer option"""
        fields = []
        survey_id = question.properties.sid
        group_id = question.properties.gid
        question_id = question.properties.qid
        
        for answer in question.answers:
            fields.append(f"{survey_id}X{group_id}X{question_id}{answer.code}")
        
        # Add "other" field if other option is enabled
        if question.properties.other_option:
            fields.append(f"{survey_id}X{group_id}X{question_id}other")
        
        return fields
    
    def validate_response(self, response_value: Any, question: Question) -> bool:
        """Validate multiple choice response"""
        # Multiple choice responses are typically Y/N for each option
        return response_value in ["Y", "N", "", None]
    
    def format_response_for_export(self, response_value: Any, format_type: str) -> Any:
        """Format for different export types"""
        if format_type == "spss":
            # SPSS: Y=1, N=0, empty=0
            if response_value == "Y":
                return 1
            else:
                return 0
        return response_value


class ShortTextHandler(QuestionTypeHandler):
    """Handler for short free text questions (S)"""
    
    def validate_question_structure(self, question: Question) -> List[str]:
        errors = []
        if question.answers:
            errors.append(f"Short text question {question.properties.qid} should not have predefined answer options")
        if hasattr(question, 'sub_questions') and question.sub_questions:
            errors.append(f"Short text question {question.properties.qid} should not have subquestions")
        return errors
    
    def generate_database_fields(self, question: Question) -> List[str]:
        """Short text creates one column"""
        survey_id = question.properties.sid
        group_id = question.properties.gid
        question_id = question.properties.qid
        return [f"{survey_id}X{group_id}X{question_id}"]
    
    def validate_response(self, response_value: Any, question: Question) -> bool:
        """Validate text response"""
        # Text can be anything, but check length constraints if any
        if response_value is None:
            return True
        
        text = str(response_value)
        # Short text typically has reasonable length limits
        if len(text) > 1000:  # Reasonable limit for short text
            return False
        
        return True
    
    def format_response_for_export(self, response_value: Any, format_type: str) -> Any:
        """Format for different export types"""
        if response_value is None:
            return ""
        return str(response_value)


class RankingHandler(QuestionTypeHandler):
    """Handler for ranking questions (R)"""
    
    def validate_question_structure(self, question: Question) -> List[str]:
        errors = []
        if not question.answers:
            errors.append(f"Ranking question {question.properties.qid} must have answer options to rank")
        if len(question.answers) < 2:
            errors.append(f"Ranking question {question.properties.qid} needs at least 2 items to rank")
        if hasattr(question, 'sub_questions') and question.sub_questions:
            errors.append(f"Ranking question {question.properties.qid} should not have subquestions")
        return errors
    
    def generate_database_fields(self, question: Question) -> List[str]:
        """Ranking creates one column per rank position"""
        survey_id = question.properties.sid
        group_id = question.properties.gid
        question_id = question.properties.qid
        
        # Create fields for each possible rank position
        num_answers = len(question.answers)
        return [f"{survey_id}X{group_id}X{question_id}{i+1}" for i in range(num_answers)]
    
    def validate_response(self, response_value: Any, question: Question) -> bool:
        """Validate ranking response"""
        if response_value is None or response_value == "":
            return True  # Empty rank position is valid
        
        # Check if it's a valid answer code
        valid_codes = [answer.code for answer in question.answers]
        return str(response_value) in valid_codes
    
    def format_response_for_export(self, response_value: Any, format_type: str) -> Any:
        """Format for different export types"""
        return response_value


# NOT YET IMPLEMENTED HANDLERS - Raise NotImplementedError

class NotImplementedHandler(QuestionTypeHandler):
    """Placeholder handler for question types not yet implemented"""
    
    def validate_question_structure(self, question: Question) -> List[str]:
        raise NotImplementedError(f"Question type {self.definition.type_code} ({self.definition.type_name}) is not yet implemented")
    
    def generate_database_fields(self, question: Question) -> List[str]:
        raise NotImplementedError(f"Question type {self.definition.type_code} ({self.definition.type_name}) is not yet implemented")
    
    def validate_response(self, response_value: Any, question: Question) -> bool:
        raise NotImplementedError(f"Question type {self.definition.type_code} ({self.definition.type_name}) is not yet implemented")
    
    def format_response_for_export(self, response_value: Any, format_type: str) -> Any:
        raise NotImplementedError(f"Question type {self.definition.type_code} ({self.definition.type_name}) is not yet implemented")


# Question Type Handler Factory
def get_question_handler(question_type: str) -> QuestionTypeHandler:
    """Get the appropriate handler for a question type"""
    if question_type not in QUESTION_TYPES:
        raise ValueError(f"Unknown question type: {question_type}")
    
    definition = QUESTION_TYPES[question_type]
    
    # Priority types - fully implemented
    if question_type == "L":
        return SingleChoiceRadioHandler(definition)
    elif question_type == "M":
        return MultipleChoiceHandler(definition)
    elif question_type == "S":
        return ShortTextHandler(definition)
    elif question_type == "R":
        return RankingHandler(definition)
    
    # All other types - not yet implemented
    else:
        return NotImplementedHandler(definition)


def validate_question_attributes(question_type: str, attributes: Dict[str, Any]) -> List[str]:
    """Validate that question attributes are appropriate for the question type"""
    if question_type not in QUESTION_TYPES:
        return [f"Unknown question type: {question_type}"]
    
    definition = QUESTION_TYPES[question_type]
    errors = []
    
    # Only validate for priority types
    if not definition.is_priority:
        return []  # Skip validation for non-priority types
    
    # Check for unsupported features
    if attributes.get("exclusive_option") and not definition.supports_exclusive_options:
        errors.append(f"Question type {question_type} does not support exclusive options")
    
    if attributes.get("other") and not definition.supports_other_option:
        errors.append(f"Question type {question_type} does not support 'other' option")
    
    return errors


def get_priority_question_types() -> Dict[str, QuestionTypeDefinition]:
    """Get only the priority question types that are fully implemented"""
    return PRIORITY_QUESTION_TYPES


def is_priority_type(question_type: str) -> bool:
    """Check if a question type is one of our priority types"""
    return question_type in PRIORITY_QUESTION_TYPES 