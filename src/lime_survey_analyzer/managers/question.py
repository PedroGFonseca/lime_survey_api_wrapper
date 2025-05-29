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