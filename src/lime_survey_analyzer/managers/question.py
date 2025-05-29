"""
Question and group management operations for LimeSurvey API.
"""

from typing import Dict, Any, List, Optional
from .base import BaseManager, requires_session


class QuestionManager(BaseManager):
    """
    Manager for question and group-related operations in LimeSurvey.
    
    Handles operations for managing question groups and individual questions,
    including retrieving lists and detailed properties.
    """
    
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
    def get_group_properties(self, group_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed properties for a specific question group.
        
        Args:
            group_id: Group ID to get properties for
            language: Language code for localized properties (optional)
            
        Returns:
            Dictionary containing group properties and settings
            
        Example:
            props = api.questions.get_group_properties("42")
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
    def get_question_properties(self, question_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed properties for a specific question.
        
        Args:
            question_id: Question ID to get properties for
            language: Language code for localized properties (optional)
            
        Returns:
            Dictionary containing question properties, settings, and answer options
            
        Example:
            props = api.questions.get_question_properties("789")
            print(f"Question: {props['question']}")
            print(f"Type: {props['type']}")
            if 'answeroptions' in props:
                print("Answer options:", props['answeroptions'])
        """
        params = self._build_params(
            [self._client.session_key, question_id],
            language=language
        )
        return self._make_request("get_question_properties", params)
    
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