"""
Survey management operations for LimeSurvey API.
"""

from typing import Dict, Any, List, Optional
from .base import BaseManager, requires_session


class SurveyManager(BaseManager):
    """
    Manager for survey-related operations in LimeSurvey.
    
    Handles operations like listing surveys, getting survey properties,
    and retrieving survey summaries and statistics.
    """
    
    @requires_session
    def list_surveys(self, username: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of surveys accessible to the user.
        
        Args:
            username: Optional username to list surveys for (defaults to authenticated user)
            
        Returns:
            List of survey dictionaries containing survey metadata
            
        Example:
            surveys = api.surveys.list_surveys()
            for survey in surveys:
                print(f"Survey: {survey['surveyls_title']} (ID: {survey['sid']})")
        """
        params = self._build_params([self._client.session_key], sUsername=username)
        response = self._make_request("list_surveys", params)
        
        # Handle the case where response is an error status instead of a list
        if isinstance(response, dict) and 'status' in response:
            # Check for common error responses
            status = response.get('status', '')
            if 'No surveys found' in str(status) or 'No permission' in str(status):
                # This is a normal condition - return empty list
                return []
            else:
                # This is an actual error
                raise Exception(f"API Error: {status}")
        
        # Ensure we always return a list
        if isinstance(response, list):
            return response
        else:
            # Unexpected response format
            raise Exception(f"Unexpected response format from list_surveys: {type(response)} - {response}")
    
    @requires_session
    def get_survey_properties(self, survey_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed properties and settings for a specific survey.
        
        Args:
            survey_id: Survey ID to get properties for
            language: Language code for localized properties (optional)
            
        Returns:
            Dictionary containing survey properties and settings
            
        Example:
            props = api.surveys.get_survey_properties("123456")
            print(f"Survey title: {props['surveyls_title']}")
            print(f"Survey language: {props['language']}")
        """
        params = self._build_params(
            [self._client.session_key, survey_id], 
            language=language
        )
        return self._make_request("get_survey_properties", params)
    
    @requires_session
    def get_summary(self, survey_id: str, stat_name: str = "all") -> Dict[str, Any]:
        """
        Get summary statistics for a survey.
        
        Args:
            survey_id: Survey ID to get summary for
            stat_name: Type of statistics to retrieve ("all", "token_count", "completed", etc.)
            
        Returns:
            Dictionary containing survey statistics and summary data
            
        Example:
            summary = api.surveys.get_summary("123456")
            print(f"Total responses: {summary['completed']}")
            print(f"Incomplete responses: {summary['incomplete']}")
        """
        params = [self._client.session_key, survey_id, stat_name]
        return self._make_request("get_summary", params)
    
    @requires_session
    def get_fieldmap(self, survey_id: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Get survey fieldmap providing authoritative mapping between response fields and questions.
        
        This method returns the official mapping between database field names and survey questions,
        which is essential for properly interpreting response data without relying on field name patterns.
        
        Args:
            survey_id: Survey ID to get fieldmap for
            language: Language code for localized fieldmap (optional, defaults to survey base language)
            
        Returns:
            Dictionary containing fieldmap with field names as keys and question metadata as values
            
        Example:
            fieldmap = api.surveys.get_fieldmap("123456")
            
            for field_name, field_info in fieldmap.items():
                print(f"Field: {field_name}")
                print(f"  Question ID: {field_info.get('qid')}")
                print(f"  Question Type: {field_info.get('type')}")
                print(f"  Question Text: {field_info.get('question')}")
                print(f"  Group: {field_info.get('group_name')}")
        """
        params = [self._client.session_key, survey_id, language]
        return self._make_request("get_fieldmap", params) 