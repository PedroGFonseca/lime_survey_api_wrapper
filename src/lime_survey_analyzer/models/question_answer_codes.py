#!/usr/bin/env python3
"""
Question Answer Codes Enum

Comprehensive enum for handling predefined answer codes for LimeSurvey question types
that return "No available answer options" but have fixed/predefined answer options.

This addresses cases like:
- Type E (Array - Increase/Same/Decrease) returns "No available answer options"
- But has predefined codes: ['I', 'S', 'D'] 
- With human-readable text: I=Increase, S=Same, D=Decrease
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class AnswerCodeMapping:
    """Represents a complete answer code mapping for a question type."""
    codes: List[str]
    code_to_text: Dict[str, str]
    description: str
    
    def get_mapping_dict(self) -> Dict[str, Dict[str, any]]:
        """Get complete mapping in the format expected by our API."""
        mapping = {}
        for i, code in enumerate(self.codes):
            mapping[code] = {
                'text': self.code_to_text.get(code, f'Option {code}'),
                'order': i,
                'assessment_value': ''
            }
        return mapping
    
    def get_text_for_code(self, code: str) -> str:
        """Get human-readable text for a response code."""
        return self.code_to_text.get(code, f'Unknown option: {code}')


class QuestionAnswerCodes(Enum):
    """
    Enum containing predefined answer codes for LimeSurvey question types.
    
    Each enum value contains:
    - List of answer codes
    - Code-to-text mapping
    - Description of the question type
    
    Usage:
        # Get answer codes for Type E questions
        type_e_mapping = QuestionAnswerCodes.ARRAY_INCREASE_SAME_DECREASE.value
        codes = type_e_mapping.codes  # ['I', 'S', 'D']
        text_for_i = type_e_mapping.get_text_for_code('I')  # 'Increase'
        full_mapping = type_e_mapping.get_mapping_dict()
    """
    
    # Array question types
    ARRAY_INCREASE_SAME_DECREASE = AnswerCodeMapping(
        codes=['I', 'S', 'D'],
        code_to_text={'I': 'Increase', 'S': 'Same', 'D': 'Decrease'},
        description='Array (Increase/Same/Decrease) - Type E'
    )
    
    ARRAY_5_POINT = AnswerCodeMapping(
        codes=['1', '2', '3', '4', '5'],
        code_to_text={
            '1': 'Point 1', '2': 'Point 2', '3': 'Point 3', 
            '4': 'Point 4', '5': 'Point 5'
        },
        description='Array (5 point choice) - Type A'
    )
    
    ARRAY_10_POINT = AnswerCodeMapping(
        codes=[str(i) for i in range(1, 11)],
        code_to_text={str(i): f'Point {i}' for i in range(1, 11)},
        description='Array (10 point choice) - Type B'
    )
    
    ARRAY_YES_NO_UNCERTAIN = AnswerCodeMapping(
        codes=['Y', 'N', 'U'],
        code_to_text={'Y': 'Yes', 'N': 'No', 'U': 'Uncertain'},
        description='Array (Yes/No/Uncertain) - Type C'
    )
    
    # Single choice question types with predefined options
    FIVE_POINT_CHOICE = AnswerCodeMapping(
        codes=['1', '2', '3', '4', '5'],
        code_to_text={
            '1': 'Point 1', '2': 'Point 2', '3': 'Point 3',
            '4': 'Point 4', '5': 'Point 5'
        },
        description='5 Point Choice - Type 5'
    )
    
    YES_NO = AnswerCodeMapping(
        codes=['Y', 'N'],
        code_to_text={'Y': 'Yes', 'N': 'No'},
        description='Yes/No - Type Y'
    )
    
    GENDER = AnswerCodeMapping(
        codes=['M', 'F'],
        code_to_text={'M': 'Male', 'F': 'Female'},
        description='Gender - Type G'
    )
    
    # Enhanced mappings with more descriptive text
    ARRAY_5_POINT_LIKERT = AnswerCodeMapping(
        codes=['1', '2', '3', '4', '5'],
        code_to_text={
            '1': 'Strongly Disagree', '2': 'Disagree', '3': 'Neither Agree nor Disagree',
            '4': 'Agree', '5': 'Strongly Agree'
        },
        description='Array (5 point Likert scale) - Type A (Alternative mapping)'
    )
    
    ARRAY_SATISFACTION_5_POINT = AnswerCodeMapping(
        codes=['1', '2', '3', '4', '5'],
        code_to_text={
            '1': 'Very Dissatisfied', '2': 'Dissatisfied', '3': 'Neutral',
            '4': 'Satisfied', '5': 'Very Satisfied'
        },
        description='Array (5 point satisfaction scale) - Type A (Alternative mapping)'
    )
    
    ARRAY_FREQUENCY_5_POINT = AnswerCodeMapping(
        codes=['1', '2', '3', '4', '5'],
        code_to_text={
            '1': 'Never', '2': 'Rarely', '3': 'Sometimes',
            '4': 'Often', '5': 'Always'
        },
        description='Array (5 point frequency scale) - Type A (Alternative mapping)'
    )


# Type mapping for easy lookup
QUESTION_TYPE_TO_ANSWER_CODES = {
    'E': QuestionAnswerCodes.ARRAY_INCREASE_SAME_DECREASE,
    'A': QuestionAnswerCodes.ARRAY_5_POINT,
    'B': QuestionAnswerCodes.ARRAY_10_POINT,
    'C': QuestionAnswerCodes.ARRAY_YES_NO_UNCERTAIN,
    '5': QuestionAnswerCodes.FIVE_POINT_CHOICE,
    'Y': QuestionAnswerCodes.YES_NO,
    'G': QuestionAnswerCodes.GENDER,
}

# Alternative mappings for specific use cases
ALTERNATIVE_MAPPINGS = {
    'A_LIKERT': QuestionAnswerCodes.ARRAY_5_POINT_LIKERT,
    'A_SATISFACTION': QuestionAnswerCodes.ARRAY_SATISFACTION_5_POINT,
    'A_FREQUENCY': QuestionAnswerCodes.ARRAY_FREQUENCY_5_POINT,
}


def get_answer_codes_for_question_type(question_type: str, 
                                     alternative_mapping: Optional[str] = None) -> Optional[AnswerCodeMapping]:
    """
    Get answer code mapping for a question type.
    
    Args:
        question_type: LimeSurvey question type (e.g., 'E', 'A', 'B', etc.)
        alternative_mapping: Optional alternative mapping key (e.g., 'A_LIKERT')
        
    Returns:
        AnswerCodeMapping object or None if not found
        
    Examples:
        # Basic usage
        mapping = get_answer_codes_for_question_type('E')
        codes = mapping.codes  # ['I', 'S', 'D']
        
        # Alternative mapping
        mapping = get_answer_codes_for_question_type('A', 'A_LIKERT')
        text = mapping.get_text_for_code('1')  # 'Strongly Disagree'
    """
    if alternative_mapping and alternative_mapping in ALTERNATIVE_MAPPINGS:
        return ALTERNATIVE_MAPPINGS[alternative_mapping].value
    
    if question_type in QUESTION_TYPE_TO_ANSWER_CODES:
        return QUESTION_TYPE_TO_ANSWER_CODES[question_type].value
    
    return None


def get_complete_question_mapping(survey_id: str, question_id: str, 
                                question_type: str, answeroptions: any,
                                subquestions: List = None,
                                alternative_mapping: Optional[str] = None) -> Dict[str, any]:
    """
    Create complete question mapping handling both API and predefined answer options.
    
    This is the main function to use when you encounter "No available answer options".
    
    Args:
        survey_id: Survey ID
        question_id: Question ID  
        question_type: LimeSurvey question type
        answeroptions: Result from API (dict or "No available answer options")
        subquestions: List of sub-questions from API
        alternative_mapping: Optional alternative mapping for better text
        
    Returns:
        Complete mapping dictionary
        
    Examples:
        # When API returns "No available answer options"
        props = api.questions.get_question_properties(survey_id, question_id)
        mapping = get_complete_question_mapping(
            survey_id=survey_id,
            question_id=question_id,
            question_type=props['type'],
            answeroptions=props['answeroptions'],
            subquestions=props.get('subquestions', [])
        )
    """
    mapping = {
        'question_id': question_id,
        'question_type': question_type,
        'answer_options': {},
        'sub_questions': {},
        'response_format': 'single',
        'has_predefined_options': False,
        'source': 'unknown'
    }
    
    # Handle answer options
    if isinstance(answeroptions, dict) and answeroptions:
        # Normal case: API returns answer options
        mapping['source'] = 'api'
        for code, option_data in answeroptions.items():
            if isinstance(option_data, dict):
                mapping['answer_options'][code] = {
                    'text': option_data.get('answer', ''),
                    'order': option_data.get('sortorder', 0),
                    'assessment_value': option_data.get('assessment_value', '')
                }
                
    elif answeroptions == "No available answer options":
        # Array question case: Use predefined options
        answer_mapping = get_answer_codes_for_question_type(question_type, alternative_mapping)
        
        if answer_mapping:
            mapping['source'] = 'predefined'
            mapping['has_predefined_options'] = True
            mapping['answer_options'] = answer_mapping.get_mapping_dict()
    
    # Handle sub-questions
    if subquestions:
        mapping['response_format'] = 'array'
        for sq in subquestions:
            if isinstance(sq, dict):
                sq_code = sq.get('title', '')
                sq_text = sq.get('question', '')
                mapping['sub_questions'][sq_code] = sq_text
            elif isinstance(sq, str):
                mapping['sub_questions'][sq] = f'Sub-question {sq}'
    
    return mapping


def list_all_predefined_mappings() -> Dict[str, AnswerCodeMapping]:
    """
    Get all available predefined answer code mappings.
    
    Returns:
        Dictionary of all available mappings
    """
    all_mappings = {}
    
    # Add standard mappings
    for question_type, enum_value in QUESTION_TYPE_TO_ANSWER_CODES.items():
        all_mappings[f"TYPE_{question_type}"] = enum_value.value
    
    # Add alternative mappings
    for alt_key, enum_value in ALTERNATIVE_MAPPINGS.items():
        all_mappings[alt_key] = enum_value.value
    
    return all_mappings


# Convenience functions for common cases
def get_type_e_mapping() -> Dict[str, Dict[str, any]]:
    """Get Type E (Increase/Same/Decrease) mapping."""
    return QuestionAnswerCodes.ARRAY_INCREASE_SAME_DECREASE.value.get_mapping_dict()


def get_type_a_likert_mapping() -> Dict[str, Dict[str, any]]:
    """Get Type A Likert scale mapping."""
    return QuestionAnswerCodes.ARRAY_5_POINT_LIKERT.value.get_mapping_dict()


def is_question_type_predefined(question_type: str) -> bool:
    """Check if a question type has predefined answer codes."""
    return question_type in QUESTION_TYPE_TO_ANSWER_CODES 