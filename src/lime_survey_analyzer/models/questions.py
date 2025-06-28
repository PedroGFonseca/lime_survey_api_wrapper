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
    
    Automatically provides human-readable answer mappings for question types that
    normally return "No available answer options" from the LimeSurvey API.
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
    
    @property
    def has_predefined_options(self) -> bool:
        """
        Returns True if this question type has predefined answer options
        (like Type E: Increase/Same/Decrease).
        """
        from .question_answer_codes import is_question_type_predefined
        return is_question_type_predefined(self.properties.question_type.value)
    
    @property
    def is_array_question(self) -> bool:
        """Returns True if this is an array/matrix question type."""
        array_types = ['A', 'B', 'C', 'E', 'F', 'H', '1', ':', ';']
        return self.properties.question_type.value in array_types
        
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
    
    def get_answer_text_for_code(self, code: str) -> str:
        """
        Get human-readable text for an answer code.
        
        Args:
            code: Answer code (e.g., 'I', 'S', 'D' for Type E questions)
            
        Returns:
            Human-readable text (e.g., 'Increase', 'Same', 'Decrease')
            
        Example:
            question = api.questions.get_question_structured('YOUR_SURVEY_ID', '28')
            text = question.get_answer_text_for_code('I')  # Returns 'Increase'
        """
        answer = self.get_answer_by_code(code)
        if answer:
            return answer.properties.answer_text
        
        # Fallback to predefined mapping if answer not found
        if self.has_predefined_options:
            from .question_answer_codes import get_answer_codes_for_question_type
            mapping = get_answer_codes_for_question_type(self.properties.question_type.value)
            if mapping:
                return mapping.get_text_for_code(code)
        
        return f"Unknown code: {code}"
    
    def get_answer_codes_mapping(self) -> Dict[str, str]:
        """
        Get complete mapping of answer codes to human-readable text.
        
        Returns:
            Dictionary mapping codes to text (e.g., {'I': 'Increase', 'S': 'Same', 'D': 'Decrease'})
            
        Example:
            question = api.questions.get_question_structured('YOUR_SURVEY_ID', '28')
            mapping = question.get_answer_codes_mapping()
            # Returns: {'I': 'Increase', 'S': 'Same', 'D': 'Decrease'}
        """
        mapping = {}
        
        # First, get mappings from actual Answer objects
        for answer in self.answers:
            mapping[answer.properties.code] = answer.properties.answer_text
        
        # If no answers but has predefined options, use those
        if not mapping and self.has_predefined_options:
            from .question_answer_codes import get_answer_codes_for_question_type
            predefined_mapping = get_answer_codes_for_question_type(self.properties.question_type.value)
            if predefined_mapping:
                mapping = predefined_mapping.code_to_text
        
        return mapping
    
    def get_sub_questions_mapping(self) -> Dict[str, str]:
        """
        Get mapping of sub-question codes to human-readable text.
        
        Returns:
            Dictionary mapping sub-question codes to text
            
        Example:
            question = api.questions.get_question_structured('YOUR_SURVEY_ID', '28')
            sub_mapping = question.get_sub_questions_mapping()
            # Returns: {'29': 'Age of candidate', '30': 'Gender of candidate', ...}
        """
        return {sq.properties.question_code: sq.properties.question_text 
                for sq in self.sub_questions}
    
    def get_complete_response_mapping(self) -> Dict[str, Any]:
        """
        Get complete mapping for interpreting response data.
        
        Returns:
            Dictionary with answer_options, sub_questions, and response format info
            
        Example:
            question = api.questions.get_question_structured('YOUR_SURVEY_ID', '28')
            mapping = question.get_complete_response_mapping()
            # Returns: {
            #   'answer_options': {'I': 'Increase', 'S': 'Same', 'D': 'Decrease'},
            #   'sub_questions': {'29': 'Age of candidate', ...},
            #   'response_format': 'array',
            #   'example_response': '29[I]' -> 'Age of candidate: Increase'
            # }
        """
        mapping = {
            'question_id': self.qid,
            'question_type': self.properties.question_type.value,
            'question_text': self.properties.question_text,
            'answer_options': self.get_answer_codes_mapping(),
            'sub_questions': self.get_sub_questions_mapping(),
            'response_format': 'array' if self.has_sub_questions else 'single',
            'is_mandatory': self.is_mandatory,
            'allows_other': self.has_other_option
        }
        
        # Add example response interpretation
        if self.has_sub_questions and mapping['answer_options']:
            first_sub = list(mapping['sub_questions'].keys())[0] if mapping['sub_questions'] else 'SQ1'
            first_answer = list(mapping['answer_options'].keys())[0] if mapping['answer_options'] else 'A1'
            sub_text = mapping['sub_questions'].get(first_sub, 'Sub-question')
            answer_text = mapping['answer_options'].get(first_answer, 'Answer')
            mapping['example_response'] = f"'{first_sub}[{first_answer}]' → '{sub_text}: {answer_text}'"
        elif mapping['answer_options']:
            first_answer = list(mapping['answer_options'].keys())[0]
            answer_text = mapping['answer_options'][first_answer]
            mapping['example_response'] = f"'{first_answer}' → '{answer_text}'"
        
        return mapping
        
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