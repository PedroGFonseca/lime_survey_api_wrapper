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
        return self._make_request("list_surveys", params)
    
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