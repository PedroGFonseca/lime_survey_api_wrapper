"""
Participant management operations for LimeSurvey API.
"""

from typing import Dict, Any, List, Optional
from .base import BaseManager, requires_session


class ParticipantManager(BaseManager):
    """
    Manager for participant-related operations in LimeSurvey.
    
    Handles operations for managing survey participants, including
    listing participants and retrieving participant properties.
    """
    
    @requires_session
    def list_participants(self, survey_id: str, start: int = 0, limit: int = 10, 
                         unused: bool = False, 
                         attributes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get list of participants in a survey.
        
        Args:
            survey_id: Survey ID to get participants for
            start: Starting index for pagination (default: 0)
            limit: Maximum number of participants to return (default: 10)
            unused: Whether to include only unused tokens (default: False)
            attributes: List of participant attributes to include (optional)
            
        Returns:
            List of participant dictionaries containing participant data
            
        Raises:
            Exception: If survey has no participant table (uses anonymous responses)
            
        Note:
            Many surveys use anonymous responses and don't have participant tables.
            This is normal and not an error with the API client.
            
        Example:
            # Get first 20 participants
            participants = api.participants.list_participants("123456", limit=20)
            
            # Get unused tokens only
            unused_tokens = api.participants.list_participants(
                "123456", 
                unused=True
            )
            
            # Get specific attributes
            custom_data = api.participants.list_participants(
                "123456", 
                attributes=["email", "firstname", "lastname"]
            )
        """
        params = self._build_params(
            [self._client.session_key, survey_id, start, limit, unused],
            attributes=attributes
        )
        
        try:
            response = self._make_request("list_participants", params)
            
            # Handle the case where response is an error status
            if isinstance(response, dict) and 'status' in response:
                if 'No survey participants table' in str(response.get('status', '')):
                    # This is a normal condition for anonymous surveys
                    return []
                    
            return response if isinstance(response, list) else []
            
        except Exception as e:
            # Log the error but don't crash - many surveys don't use participants
            if 'No survey participants table' in str(e):
                return []
            raise
    
    @requires_session
    def get_participant_properties(self, survey_id: str, 
                                  token_query_properties: Dict[str, Any], 
                                  participant_query_properties: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get detailed properties for specific participants.
        
        Args:
            survey_id: Survey ID to query participants from
            token_query_properties: Dictionary specifying participant search criteria
            participant_query_properties: List of properties to retrieve (optional)
            
        Returns:
            Dictionary containing participant properties and data
            
        Raises:
            Exception: If survey has no participant table or participant not found
            
        Example:
            # Get participant by token
            participant = api.participants.get_participant_properties(
                "123456",
                {"token": "ABC123"}
            )
            
            # Get specific properties for participant by email
            custom_props = api.participants.get_participant_properties(
                "123456",
                {"email": "user@example.com"},
                ["firstname", "lastname", "completed"]
            )
        """
        params = self._build_params(
            [self._client.session_key, survey_id, token_query_properties],
            participant_query_properties=participant_query_properties
        )
        response = self._make_request("get_participant_properties", params)
        return response if response else {} 