"""
LimeSurvey Property Definitions

Enums and data classes for question properties, answer properties, and other
LimeSurvey concepts based on official API documentation.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any, Dict, List
from datetime import datetime


class QuestionType(Enum):
    """LimeSurvey question types based on official documentation"""
    
    # Single response types
    LIST_RADIO = "L"              # List (Radio)
    LIST_DROPDOWN = "!"           # List (Dropdown)
    FIVE_POINT_CHOICE = "5"       # 5 Point Choice
    YES_NO = "Y"                  # Yes/No
    GENDER = "G"                  # Gender
    LANGUAGE = "I"                # Language Switch
    
    # Text input types  
    SHORT_FREE_TEXT = "S"         # Short free text
    LONG_FREE_TEXT = "T"          # Long free text
    HUGE_FREE_TEXT = "U"          # Huge free text
    NUMERICAL = "N"               # Numerical input
    
    # Multiple response types
    MULTIPLE_CHOICE = "M"         # Multiple choice checkbox
    MULTIPLE_CHOICE_COMMENTS = "P"  # Multiple choice with comments
    MULTIPLE_SHORT_TEXT = "Q"     # Multiple short text
    MULTIPLE_NUMERICAL = "K"      # Multiple numerical input
    
    # Array/Matrix types
    ARRAY_5_POINT = "A"           # Array (5 point choice)
    ARRAY_10_POINT = "B"          # Array (10 point choice)  
    ARRAY_YES_NO_UNCERTAIN = "C"  # Array (Yes/No/Uncertain)
    ARRAY_INCREASE_SAME_DECREASE = "E"  # Array (Increase/Same/Decrease)
    ARRAY_FLEXIBLE_ROW = "F"      # Array (Flexible) - Row
    ARRAY_FLEXIBLE_COLUMN = "H"   # Array (Flexible) - Column
    ARRAY_MULTI_FLEXI_NUMBERS = ":"  # Array Multi Flexi (Numbers)
    ARRAY_MULTI_FLEXI_TEXT = ";"  # Array Multi Flexi (Text)
    ARRAY_DUAL_SCALE = "1"        # Array dual scale
    
    # Special types
    DATE_TIME = "D"               # Date/Time
    EQUATION = "*"                # Equation
    FILE_UPLOAD = "|"             # File upload
    LIST_WITH_COMMENT = "O"       # List with comment
    RANKING = "R"                 # Ranking
    TEXT_DISPLAY = "X"            # Text display/Boilerplate


class VisibilityState(Enum):
    """Question visibility states"""
    VISIBLE = "visible"
    HIDDEN = "hidden" 
    CONDITIONAL = "conditional"


class MandatoryState(Enum):
    """Question mandatory states"""
    MANDATORY = "Y"
    OPTIONAL = "N"
    CONDITIONAL = "conditional"


class ResponseStatus(Enum):
    """Response completion status"""
    COMPLETE = "complete"
    INCOMPLETE = "incomplete" 
    PARTIAL = "partial"


@dataclass
class QuestionProperties:
    """
    Properties that apply to main questions.
    Based on official LimeSurvey question attributes.
    """
    
    # Core identification
    qid: int
    question_code: str
    question_type: QuestionType
    gid: int  # Group ID
    sid: int  # Survey ID
    
    # Display and behavior
    mandatory: MandatoryState = MandatoryState.OPTIONAL
    visibility: VisibilityState = VisibilityState.VISIBLE
    question_order: int = 0
    same_default: bool = False
    
    # Text content (language-specific)
    question_text: str = ""
    help_text: str = ""
    
    # Logic and validation
    relevance_equation: str = "1"  # Always relevant by default
    validation_regex: Optional[str] = None
    
    # Special features
    other_option: bool = False
    randomization_group: Optional[str] = None
    
    # Advanced attributes (from question_attributes table)
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}


@dataclass 
class AnswerProperties:
    """
    Properties for answer options/sub-questions.
    These inherit visibility/conditionality from parent question.
    """
    
    # Core identification
    aid: Optional[int] = None  # Answer ID
    code: str = ""  # Answer code
    parent_qid: int = 0  # Parent question ID
    scale_id: int = 0  # For dual-scale questions
    
    # Order and display
    sort_order: int = 0
    assessment_value: Optional[float] = None
    
    # Text content (language-specific)
    answer_text: str = ""
    
    # Inherited properties (from parent question)
    inherited_visibility: VisibilityState = VisibilityState.VISIBLE
    inherited_conditionality: str = "1"
    
    # Response-specific properties (filled during survey taking)
    displayed_order: Optional[int] = None  # Actual order shown to user (for randomized)
    was_randomized: bool = False


@dataclass
class SubQuestionProperties:
    """
    Properties for sub-questions (like in array questions).
    Based on LimeSurvey subquestion structure where parent_qid != 0.
    """
    
    # Core identification  
    sqid: int  # Sub-question ID
    parent_qid: int  # Parent question ID
    question_code: str  # Sub-question code
    scale_id: int = 0  # For dual-scale arrays
    
    # Order and display
    question_order: int = 0
    
    # Text content (language-specific)  
    question_text: str = ""
    help_text: str = ""
    
    # Inherited from parent question
    inherited_mandatory: MandatoryState = MandatoryState.OPTIONAL
    inherited_visibility: VisibilityState = VisibilityState.VISIBLE
    inherited_relevance: str = "1"
    
    # Future: individual subquestion properties
    relevance_equation: str = "1"  # Future: sub-question level relevance
    validation_regex: Optional[str] = None  # Future: sub-question validation
    
    # Response-specific
    displayed_order: Optional[int] = None
    was_randomized: bool = False 