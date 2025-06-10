"""
Question and group management operations for LimeSurvey API.
"""

from typing import Dict, Any, List, Optional
from .base import BaseManager, requires_session

# Import question type system for validation and modeling
from ..models import (
    Question, Answer, SubQuestion, QuestionProperties, AnswerProperties, SubQuestionProperties,
    QuestionType, MandatoryState, VisibilityState,
    get_question_handler, is_priority_type, PRIORITY_QUESTION_TYPES, QUESTION_TYPES,
    NotImplementedHandler
)

# Import the new answer codes enum system
from ..models.question_answer_codes import (
    get_answer_codes_for_question_type, 
    get_complete_question_mapping,
    is_question_type_predefined,
    QUESTION_TYPE_TO_ANSWER_CODES
)

# Import logging and exceptions
from ..utils.logging import get_logger
from ..exceptions import QuestionValidationError, QuestionNotFoundError, UnsupportedQuestionTypeError


class QuestionManager(BaseManager):
    """
    Manager for question and group-related operations in LimeSurvey.
    
    Handles operations for managing question groups and individual questions,
    including retrieving lists and detailed properties. Now integrated with
    the question type validation and modeling system.
    
    Automatically provides human-readable answer option mappings for questions
    that return "No available answer options" by using predefined answer codes.
    
    Priority question types (L, M, S, R) are fully supported with validation,
    database field generation, and response handling. Other question types
    will raise NotImplementedError until they are implemented.
    """
    
    def __init__(self, client):
        """Initialize the question manager with logging."""
        super().__init__(client)
        self.logger = get_logger(__name__)
    
    @requires_session
    def list_groups(self, survey_id: str, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of question groups in a survey.
        
        Args:
            survey_id: Survey ID to get groups for
            language: Language code for localized group data (optional)
            
        Returns:
            List of group dictionaries containing group metadata
            
        Example:
            groups = api.questions.list_groups("123456")
            for group in groups:
                print(f"Group: {group['group_name']} (ID: {group['gid']})")
        """
        params = self._build_params(
            [self._client.session_key, survey_id],
            language=language
        )
        return self._make_request("list_groups", params)
    
    @requires_session
    def get_group_properties(self, survey_id: str, group_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed properties for a specific question group.
        
        Args:
            survey_id: Survey ID containing the group
            group_id: Group ID to get properties for
            language: Language code for localized properties (optional)
            
        Returns:
            Dictionary containing group properties and settings
            
        Example:
            props = api.questions.get_group_properties("123456", "42")
            print(f"Group name: {props['group_name']}")
            print(f"Description: {props['description']}")
        """
        params = self._build_params(
            [self._client.session_key, group_id],
            language=language
        )
        return self._make_request("get_group_properties", params)
    
    @requires_session
    def list_questions(self, survey_id: str, group_id: Optional[str] = None, 
                      language: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of questions in a survey or specific group.
        
        Note: This returns raw API data. Use list_questions_structured() 
        for structured Question objects with validation.
        
        Args:
            survey_id: Survey ID to get questions for
            group_id: Optional group ID to filter questions by group
            language: Language code for localized question data (optional)
            
        Returns:
            List of question dictionaries containing question metadata
            
        Example:
            # Get all questions in survey
            questions = api.questions.list_questions("123456")
            
            # Get questions in specific group
            group_questions = api.questions.list_questions("123456", group_id="42")
        """
        params = self._build_params(
            [self._client.session_key, survey_id],
            iGroupID=group_id,
            language=language
        )
        return self._make_request("list_questions", params)
    
    @requires_session
    def list_questions_structured(self, survey_id: str, group_id: Optional[str] = None, 
                                 language: Optional[str] = None, 
                                 include_unsupported: bool = False) -> List[Question]:
        """
        Get list of questions as structured Question objects with validation.
        
        This method converts raw API data into proper Question objects and validates
        question types against the priority question type system.
        
        Args:
            survey_id: Survey ID to get questions for
            group_id: Optional group ID to filter questions by group
            language: Language code for localized question data (optional)
            include_unsupported: If False, filter out non-priority question types
            
        Returns:
            List of Question objects with proper validation and structure
            
        Raises:
            NotImplementedError: If question contains unsupported types (when include_unsupported=False)
            
        Example:
            # Get structured questions with validation
            questions = api.questions.list_questions_structured("123456")
            
            for question in questions:
                handler = get_question_handler(question.properties.question_type.value)
                errors = handler.validate_question_structure(question)
                if errors:
                    print(f"Question {question.qid} has validation errors: {errors}")
        """
        raw_questions = self.list_questions(survey_id, group_id, language)
        structured_questions = []
        
        self.logger.info(f"Processing {len(raw_questions)} questions with detailed properties")
        
        for raw_q in raw_questions:
            try:
                qid = raw_q.get('qid')
                if not qid:
                    self.logger.warning("Question found without QID, skipping")
                    continue
                
                # CRITICAL FIX: Get detailed properties to include answer options
                # The list_questions API call doesn't include answeroptions, but 
                # get_question_properties does
                try:
                    detailed_props = self.get_question_properties(survey_id, qid, language)
                    # Merge basic question data with detailed properties
                    # Detailed properties take precedence for completeness
                    merged_data = {**raw_q, **detailed_props}
                except Exception as e:
                    self.logger.warning(f"Could not get detailed properties for question {qid}: {e}")
                    # Fallback to basic data without options
                    merged_data = raw_q
                
                # Convert merged question data to structured Question object
                question = self._convert_raw_to_question(merged_data, survey_id)
                
                # Check if question type is supported
                if not include_unsupported and not is_priority_type(question.properties.question_type.value):
                    self.logger.debug(f"Skipping unsupported question type: {question.properties.question_type.value}")
                    continue
                
                # Validate question structure if it's a priority type
                if is_priority_type(question.properties.question_type.value):
                    handler = get_question_handler(question.properties.question_type.value)
                    errors = handler.validate_question_structure(question)
                    if errors:
                        self.logger.warning(f"Question {question.qid} validation warnings: {errors}")
                
                structured_questions.append(question)
                
            except Exception as e:
                self.logger.error(f"Error processing question {raw_q.get('qid', 'unknown')}: {e}")
                if not include_unsupported:
                    # Skip problematic questions unless explicitly including unsupported
                    continue
                raise
        
        self.logger.info(f"Successfully processed {len(structured_questions)} questions with full structure")
        return structured_questions

    @requires_session
    def get_question_properties(self, survey_id: str, question_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed properties for a specific question.
        
        Automatically enhances questions that return "No available answer options" 
        with human-readable answer mappings from predefined question type definitions.
        
        Args:
            survey_id: Survey ID containing the question
            question_id: Question ID to get properties for
            language: Language code for localized properties (optional)
            
        Returns:
            Dictionary containing question properties, settings, and answer options.
            For questions that normally return "No available answer options", this
            method automatically adds a 'predefined_answer_options' field with
            human-readable mappings.
            
        Example:
            props = api.questions.get_question_properties("123456", "789")
            print(f"Question: {props['question']}")
            print(f"Type: {props['type']}")
            
            # For questions with normal answer options
            if isinstance(props.get('answeroptions'), dict):
                print("Custom answer options:", props['answeroptions'])
            
            # For questions with predefined options (like Type E)
            if 'predefined_answer_options' in props:
                print("Predefined options:", props['predefined_answer_options'])
                # Example output for Type E:
                # {'I': {'text': 'Increase', 'order': 0}, 'S': {'text': 'Same', 'order': 1}, ...}
        """
        params = self._build_params(
            [self._client.session_key, question_id],
            language=language
        )
        raw_props = self._make_request("get_question_properties", params)
        
        # Enhance with predefined answer options if needed
        return self._enhance_question_properties_with_predefined_options(raw_props, survey_id, question_id)
    
    def _enhance_question_properties_with_predefined_options(self, props: Dict[str, Any], 
                                                           survey_id: str, question_id: str) -> Dict[str, Any]:
        """
        Enhance question properties with predefined answer options when API returns 
        "No available answer options".
        
        Args:
            props: Raw question properties from API
            survey_id: Survey ID for context
            question_id: Question ID for context
            
        Returns:
            Enhanced properties with predefined_answer_options field added if applicable
        """
        answeroptions = props.get('answeroptions')
        question_type = props.get('type', '')
        
        # Only enhance if we have "No available answer options" and the type has predefined codes
        if answeroptions == "No available answer options" and is_question_type_predefined(question_type):
            self.logger.debug(f"Enhancing question {question_id} (type {question_type}) with predefined answer options")
            
            # Get the predefined mapping
            answer_mapping = get_answer_codes_for_question_type(question_type)
            if answer_mapping:
                # Add the human-readable mapping to the properties
                props['predefined_answer_options'] = answer_mapping.get_mapping_dict()
                props['answer_options_source'] = 'predefined'
                props['answer_options_description'] = answer_mapping.description
                
                # Also add convenience fields for common use cases
                props['answer_codes'] = answer_mapping.codes
                props['code_to_text_mapping'] = answer_mapping.code_to_text
        else:
            props['answer_options_source'] = 'api'
        
        return props
    
    @requires_session
    def get_question_structured(self, survey_id: str, question_id: str, language: Optional[str] = None) -> Question:
        """
        Get a question as a structured Question object with validation.
        
        Args:
            survey_id: Survey ID containing the question
            question_id: Question ID to get
            language: Language code for localized properties (optional)
            
        Returns:
            Question object with proper validation and structure
            
        Raises:
            NotImplementedError: If question type is not supported
            
        Example:
            question = api.questions.get_question_structured("123456", "789")
            handler = get_question_handler(question.properties.question_type.value)
            
            # Validate structure
            errors = handler.validate_question_structure(question)
            
            # Generate database fields  
            fields = handler.generate_database_fields(question)
        """
        raw_props = self.get_question_properties(survey_id, question_id, language)
        
        # Use the provided survey_id (we already know it from the parameter)
        question = self._convert_raw_to_question(raw_props, survey_id)
        
        # Validate if it's a priority type
        if is_priority_type(question.properties.question_type.value):
            handler = get_question_handler(question.properties.question_type.value)
            errors = handler.validate_question_structure(question)
            if errors:
                self.logger.warning(f"Question {question.qid} validation warnings: {errors}")
        else:
            # For non-priority types, we still allow access but warn
            self.logger.debug(f"Question {question.qid} uses unsupported type: {question.properties.question_type.value}")
        
        return question

    def _convert_raw_to_question(self, raw_data: Dict[str, Any], survey_id: str) -> Question:
        """
        Convert raw API question data to structured Question object.
        
        Args:
            raw_data: Raw question data from LimeSurvey API
            survey_id: Survey ID this question belongs to
            
        Returns:
            Question object with proper structure
        """
        # Create question properties
        properties = self._build_question_properties(raw_data, survey_id)
        
        # Create the question object
        question = Question(properties=properties)
        
        # Add answer options if present
        self._add_answer_options(question, raw_data)
        
        # Add sub-questions if present
        self._add_subquestions(question, raw_data)
        
        question.raw_data = raw_data
        return question

    def _build_question_properties(self, raw_data: Dict[str, Any], survey_id: str) -> QuestionProperties:
        """
        Extract and build question properties from raw API data.
        
        Args:
            raw_data: Raw question data from LimeSurvey API
            survey_id: Survey ID this question belongs to
            
        Returns:
            QuestionProperties object with validated data
        """
        # Map question type string to enum
        type_code = raw_data.get('type', 'S')  # Default to short text
        try:
            question_type = QuestionType(type_code)
        except ValueError:
            # Unknown question type - default to short text for safety
            question_type = QuestionType.SHORT_FREE_TEXT
            self.logger.warning(f"Unknown question type '{type_code}', defaulting to short text")
        
        # Map mandatory setting
        mandatory_val = raw_data.get('mandatory', 'N')
        mandatory = MandatoryState.MANDATORY if mandatory_val == 'Y' else MandatoryState.OPTIONAL
        
        return QuestionProperties(
            qid=int(raw_data.get('qid', 0)),
            question_code=raw_data.get('title', ''),
            question_type=question_type,
            gid=int(raw_data.get('gid', 0)),
            sid=int(survey_id),
            mandatory=mandatory,
            question_text=raw_data.get('question', ''),
            help_text=raw_data.get('help', ''),
            relevance_equation=raw_data.get('relevance', '1'),
            other_option=raw_data.get('other', 'N') == 'Y',
            question_order=int(raw_data.get('question_order', 0))
        )

    def _add_answer_options(self, question: Question, raw_data: Dict[str, Any]) -> None:
        """
        Add answer options to a question from raw API data.
        
        Automatically adds predefined answer options for question types that 
        return "No available answer options" but have known answer codes.
        
        Args:
            question: Question object to add answers to
            raw_data: Raw question data containing answer options
        """
        if 'answeroptions' not in raw_data or not raw_data['answeroptions']:
            return
        
        answeroptions = raw_data['answeroptions']
        
        # Handle LimeSurvey API's expected behaviors
        if isinstance(answeroptions, str):
            if answeroptions == "No available answer options":
                # Check if this question type has predefined answer options
                question_type = question.properties.question_type.value
                if is_question_type_predefined(question_type):
                    self.logger.debug(f"Adding predefined answer options for question {question.qid} (type {question_type})")
                    self._add_predefined_answer_options(question, question_type)
                else:
                    # This is expected behavior for text questions, etc.
                    self.logger.debug(f"Question {question.qid} has no answer options (as expected for question type {question_type})")
                return
            else:
                # Unexpected string content - log as warning
                self.logger.warning(f"Question {question.qid} has unexpected string answeroptions: '{answeroptions}'")
                return
        elif not isinstance(answeroptions, dict):
            # Handle other unexpected types
            self.logger.warning(f"Question {question.qid} has unexpected answeroptions type: {type(answeroptions)}")
            return
            
        # Process dictionary of answer options (normal case)
        for code, answer_data in answeroptions.items():
            if isinstance(answer_data, dict):
                # Normal case: answer_data is a dictionary with properties
                answer_props = AnswerProperties(
                    code=code,
                    answer_text=answer_data.get('answer', ''),
                    sort_order=int(answer_data.get('sortorder', answer_data.get('order', 0))),
                    parent_qid=question.properties.qid,
                    assessment_value=float(answer_data.get('assessment_value', 0)) if answer_data.get('assessment_value') else None
                )
                question.answers.append(Answer(properties=answer_props))
            elif isinstance(answer_data, str):
                # Sometimes answer_data is just the answer text string
                answer_props = AnswerProperties(
                    code=code,
                    answer_text=answer_data,
                    sort_order=0,
                    parent_qid=question.properties.qid,
                    assessment_value=None
                )
                question.answers.append(Answer(properties=answer_props))
            else:
                # Log unexpected answer data types but continue processing
                self.logger.debug(f"Question {question.qid} answer '{code}' has unexpected type: {type(answer_data)}")
                # Try to convert to string as fallback
                answer_props = AnswerProperties(
                    code=code,
                    answer_text=str(answer_data) if answer_data is not None else '',
                    sort_order=0,
                    parent_qid=question.properties.qid,
                    assessment_value=None
                )
                question.answers.append(Answer(properties=answer_props))
    
    def _add_predefined_answer_options(self, question: Question, question_type: str) -> None:
        """
        Add predefined answer options to a question based on its type.
        
        Args:
            question: Question object to add predefined answers to
            question_type: LimeSurvey question type code
        """
        answer_mapping = get_answer_codes_for_question_type(question_type)
        if not answer_mapping:
            return
        
        # Add each predefined answer option
        for i, code in enumerate(answer_mapping.codes):
            answer_props = AnswerProperties(
                code=code,
                answer_text=answer_mapping.get_text_for_code(code),
                sort_order=i,
                parent_qid=question.properties.qid,
                assessment_value=None
            )
            question.answers.append(Answer(properties=answer_props))
        
        self.logger.debug(f"Added {len(answer_mapping.codes)} predefined answer options to question {question.qid}")

    def _add_subquestions(self, question: Question, raw_data: Dict[str, Any]) -> None:
        """
        Add sub-questions to a question from raw API data.
        
        Args:
            question: Question object to add sub-questions to
            raw_data: Raw question data containing sub-questions
        """
        if 'subquestions' not in raw_data or not raw_data['subquestions']:
            return
            
        for sq_data in raw_data['subquestions']:
            if isinstance(sq_data, dict):
                sq_props = SubQuestionProperties(
                    sqid=int(sq_data.get('qid', 0)),
                    parent_qid=question.properties.qid,
                    question_code=sq_data.get('title', ''),
                    question_text=sq_data.get('question', ''),
                    question_order=int(sq_data.get('question_order', 0))
                )
                question.sub_questions.append(SubQuestion(properties=sq_props))

    @requires_session
    def validate_question_types(self, survey_id: str, group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate all questions in a survey against the question type system.
        
        Args:
            survey_id: Survey ID to validate
            group_id: Optional group ID to filter validation
            
        Returns:
            Dictionary with validation results, supported/unsupported counts, and error details
            
        Example:
            results = api.questions.validate_question_types("123456")
            print(f"Supported questions: {results['supported_count']}")
            print(f"Unsupported questions: {results['unsupported_count']}")
            
            for error in results['validation_errors']:
                print(f"Question {error['qid']}: {error['errors']}")
        """
        try:
            questions = self.list_questions_structured(survey_id, group_id, include_unsupported=True)
        except Exception as e:
            return {
                'error': f"Failed to retrieve questions: {str(e)}",
                'supported_count': 0,
                'unsupported_count': 0,
                'validation_errors': [],
                'question_types': {}
            }
        
        supported_count = 0
        unsupported_count = 0
        validation_errors = []
        question_types = {}
        
        for question in questions:
            type_code = question.properties.question_type.value
            
            # Count question types
            if type_code not in question_types:
                type_definition = QUESTION_TYPES.get(type_code)
                question_types[type_code] = {
                    'count': 0,
                    'supported': is_priority_type(type_code),
                    'name': type_definition.type_name if type_definition else 'Unknown'
                }
            question_types[type_code]['count'] += 1
            
            if is_priority_type(type_code):
                supported_count += 1
                
                # Validate structure for priority types
                try:
                    handler = get_question_handler(type_code)
                    errors = handler.validate_question_structure(question)
                    if errors:
                        validation_errors.append({
                            'qid': question.qid,
                            'type': type_code,
                            'errors': errors
                        })
                except Exception as e:
                    validation_errors.append({
                        'qid': question.qid,
                        'type': type_code,
                        'errors': [f"Handler error: {str(e)}"]
                    })
            else:
                unsupported_count += 1
        
        return {
            'supported_count': supported_count,
            'unsupported_count': unsupported_count,
            'total_count': len(questions),
            'validation_errors': validation_errors,
            'question_types': question_types,
            'priority_types_available': list(PRIORITY_QUESTION_TYPES.keys())
        }

    @requires_session
    def list_conditions(self, survey_id: str, question_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of conditions for a survey or specific question.
        
        Args:
            survey_id: Survey ID to get conditions for
            question_id: Optional question ID to filter conditions for specific question
            
        Returns:
            List of condition dictionaries containing condition logic and settings
            
        Note:
            This retrieves the older "Conditions" system. Modern surveys typically use
            relevance equations instead. Both systems control question visibility.
            
        Example:
            # Get all conditions in survey
            conditions = api.questions.list_conditions("123456")
            
            # Get conditions for specific question
            q_conditions = api.questions.list_conditions("123456", "789")
            
            for condition in conditions:
                print(f"Condition: {condition['cfieldname']} {condition['method']} {condition['value']}")
        """
        params = self._build_params(
            [self._client.session_key, survey_id],
            question_id=question_id
        )
        return self._make_request("list_conditions", params)
    
    @requires_session  
    def get_conditions(self, survey_id: str, question_id: str) -> List[Dict[str, Any]]:
        """
        Get detailed condition information for a specific question.
        
        Args:
            survey_id: Survey ID containing the question
            question_id: Question ID to get conditions for
            
        Returns:
            List of detailed condition dictionaries with full condition logic
            
        Note:
            Returns conditions from the older "Conditions" system. For modern surveys,
            check the 'relevance' property in get_question_properties() instead.
            
        Example:
            conditions = api.questions.get_conditions("123456", "789")
            
            for condition in conditions:
                source_field = condition['cfieldname']
                operator = condition['method'] 
                target_value = condition['value']
                print(f"Show question if {source_field} {operator} '{target_value}'")
        """
        params = self._build_params([self._client.session_key, survey_id, question_id])
        return self._make_request("get_conditions", params) 