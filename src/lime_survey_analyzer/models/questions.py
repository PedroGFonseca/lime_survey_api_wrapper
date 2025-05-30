"""
Question Hierarchy Models

Question, SubQuestion, and Answer classes representing the LimeSurvey question structure
based on the parent_qid field and official API documentation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .properties import (
    QuestionType,
    QuestionProperties, 
    AnswerProperties,
    SubQuestionProperties,
    VisibilityState,
    MandatoryState
)


@dataclass
class Question:
    """
    Represents a main question in LimeSurvey.
    Main questions have parent_qid = 0 and can contain sub-questions and answers.
    """
    
    # From QuestionProperties
    properties: QuestionProperties
    
    # Relationships
    sub_questions: List['SubQuestion'] = field(default_factory=list)
    answers: List['Answer'] = field(default_factory=list)
    
    # Language variants (for multi-language surveys)
    language_variants: Dict[str, 'Question'] = field(default_factory=dict)
    
    # Raw API response data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Post-initialization validation"""
        # Ensure question code is set
        if not self.properties.question_code:
            self.properties.question_code = f"Q{self.properties.qid}"
    
    @property
    def qid(self) -> int:
        """Convenience property for question ID"""
        return self.properties.qid
        
    @property
    def question_code(self) -> str:
        """Convenience property for question code"""
        return self.properties.question_code
        
    @property
    def question_type(self) -> QuestionType:
        """Convenience property for question type"""
        return self.properties.question_type
        
    @property
    def is_mandatory(self) -> bool:
        """Returns True if question is mandatory"""
        return self.properties.mandatory == MandatoryState.MANDATORY
        
    @property
    def is_conditional(self) -> bool:
        """Returns True if question has conditional logic"""
        return self.properties.relevance_equation != "1"
        
    @property
    def has_sub_questions(self) -> bool:
        """Returns True if question has sub-questions (like array questions)"""
        return len(self.sub_questions) > 0
        
    @property
    def has_answers(self) -> bool:
        """Returns True if question has predefined answer options"""
        return len(self.answers) > 0
        
    @property
    def has_other_option(self) -> bool:
        """Returns True if question allows 'Other' option"""
        return self.properties.other_option
        
    def get_answer_by_code(self, code: str) -> Optional['Answer']:
        """Find answer by its code"""
        for answer in self.answers:
            if answer.properties.code == code:
                return answer
        return None
        
    def get_sub_question_by_code(self, code: str) -> Optional['SubQuestion']:
        """Find sub-question by its code"""
        for sq in self.sub_questions:
            if sq.properties.question_code == code:
                return sq
        return None
        
    def add_answer(self, answer: 'Answer') -> None:
        """Add an answer option to this question"""
        answer.properties.parent_qid = self.qid
        self.answers.append(answer)
        
    def add_sub_question(self, sub_question: 'SubQuestion') -> None:
        """Add a sub-question to this question"""
        sub_question.properties.parent_qid = self.qid
        self.sub_questions.append(sub_question)


@dataclass
class SubQuestion:
    """
    Represents a sub-question in LimeSurvey.
    Sub-questions have parent_qid != 0 and are used in array/matrix questions.
    
    Examples:
    - Rows in a matrix question
    - Individual items in a multiple choice array
    """
    
    # From SubQuestionProperties  
    properties: SubQuestionProperties
    
    # Language variants
    language_variants: Dict[str, 'SubQuestion'] = field(default_factory=dict)
    
    # Raw API response data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def sqid(self) -> int:
        """Convenience property for sub-question ID"""
        return self.properties.sqid
        
    @property
    def parent_qid(self) -> int:
        """Convenience property for parent question ID"""
        return self.properties.parent_qid
        
    @property
    def question_code(self) -> str:
        """Convenience property for sub-question code"""
        return self.properties.question_code
        
    @property
    def is_conditional(self) -> bool:
        """Returns True if sub-question has conditional logic"""
        return self.properties.relevance_equation != "1"


@dataclass  
class Answer:
    """
    Represents an answer option for a question.
    Answer options are predefined choices that users can select.
    
    Examples:
    - "Yes", "No" options in Yes/No question
    - "Very satisfied", "Satisfied", etc. in rating questions
    - "Other" option with text input
    """
    
    # From AnswerProperties
    properties: AnswerProperties
    
    # Language variants
    language_variants: Dict[str, 'Answer'] = field(default_factory=dict)
    
    # Raw API response data
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def aid(self) -> Optional[int]:
        """Convenience property for answer ID"""
        return self.properties.aid
        
    @property
    def code(self) -> str:
        """Convenience property for answer code"""
        return self.properties.code
        
    @property
    def parent_qid(self) -> int:
        """Convenience property for parent question ID"""
        return self.properties.parent_qid
        
    @property
    def answer_text(self) -> str:
        """Convenience property for answer text"""
        return self.properties.answer_text
        
    @property
    def has_assessment_value(self) -> bool:
        """Returns True if answer has assessment scoring value"""
        return self.properties.assessment_value is not None


# Type aliases for convenience
QuestionItem = Union[Question, SubQuestion, Answer]
QuestionHierarchy = Dict[int, Question]  # qid -> Question mapping 