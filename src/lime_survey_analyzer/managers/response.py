"""
Response data management operations for LimeSurvey API.
"""

from typing import Dict, Any, List, Optional, Union
from .base import BaseManager, requires_session
import base64
import json


class ResponseManager(BaseManager):
    """
    Manager for response data operations in LimeSurvey.
    
    Handles operations for exporting survey responses, statistics,
    and managing response data and files.
    """
    
    @requires_session
    def export_responses(self, survey_id: str, document_type: str = "json", 
                        language_code: str = None, completion_status: str = "all",
                        heading_type: str = "code", response_type: str = "short") -> Union[Dict, List, str]:
        """
        Export survey responses in various formats.
        
        Args:
            survey_id: Survey ID to export responses from
            document_type: Export format ("json", "csv", "xml", "excel", "pdf")
            language_code: Language for export (optional)
            completion_status: Response status filter ("all", "complete", "incomplete")
            heading_type: Column heading type ("code", "full", "abbreviated")  
                         "code" uses question codes that can be mapped to Question objects
            response_type: Response detail level ("short", "long")
            
        Returns:
            Exported response data in requested format
            
        Example:
            # Export as JSON with field names that match fieldmap
            responses = api.responses.export_responses("123456", "json")
            
            # Export only completed responses as CSV
            csv_data = api.responses.export_responses(
                "123456", 
                document_type="csv",
                completion_status="complete"
            )
        """
        params = [
            self._client.session_key,
            survey_id,
            document_type,
            language_code,
            completion_status,
            heading_type,
            response_type
        ]
        
        response = self._make_request("export_responses", params)
        
        # LimeSurvey API returns base64-encoded data
        if isinstance(response, str):
            try:
                # Decode base64 response
                decoded_data = base64.b64decode(response).decode('utf-8')
                
                # For JSON format, parse the decoded data
                if document_type.lower() == 'json':
                    try:
                        json_data = json.loads(decoded_data)
                        return json_data
                    except json.JSONDecodeError:
                        # If not valid JSON, return as string
                        return decoded_data
                else:
                    # For other formats (CSV, etc.), return decoded string
                    return decoded_data
                    
            except Exception:
                # If decoding fails, return original response
                return response
        
        # If response is not a string, return as is
        return response
    
    @requires_session
    def export_responses_by_token(self, survey_id: str, document_type: str = "json", 
                                 token: str = None, language_code: str = None,
                                 completion_status: str = "all", heading_type: str = "code",
                                 response_type: str = "short") -> Union[Dict, List, str]:
        """
        Export responses filtered by participant token.
        
        Args:
            survey_id: Survey ID to export from
            document_type: Export format ("json", "csv", "xml", "excel", "pdf")
            token: Participant token to filter by (optional - exports all if None)
            language_code: Language for export (optional)
            completion_status: Response status filter
            heading_type: Header format
            response_type: Response format
            
        Returns:
            Exported response data for the specified token
            
        Example:
            # Export responses for specific participant
            participant_data = api.responses.export_responses_by_token(
                "123456", 
                "json", 
                token="ABC123"
            )
        """
        params = [
            self._client.session_key,
            survey_id,
            document_type,
            token,
            language_code,
            completion_status,
            heading_type,
            response_type
        ]
        
        response = self._make_request("export_responses_by_token", params)
        return response
    
    @requires_session
    def export_statistics(self, survey_id: str, doc_type: str = "pdf") -> Union[str, bytes]:
        """
        Export statistical summary of survey responses.
        
        Args:
            survey_id: Survey ID to generate statistics for
            doc_type: Export format for statistics ("pdf", "xls", "html")
            
        Returns:
            Statistical report in the specified format
            
        Example:
            # Export PDF statistics report
            stats_pdf = api.responses.export_statistics("123456", "pdf")
            
            # Export Excel statistics
            stats_excel = api.responses.export_statistics("123456", "xls")
        """
        params = [self._client.session_key, survey_id, doc_type]
        response = self._make_request("export_statistics", params)
        return response
    
    @requires_session
    def get_response_ids(self, survey_id: str, token: str) -> List[str]:
        """
        Get list of response IDs for a survey and specific participant token.
        
        Args:
            survey_id: Survey ID to get response IDs for
            token: Participant token to get response IDs for (required)
            
        Returns:
            List of response ID strings for the specified participant
            
        Example:
            # Get response IDs for specific participant
            participant_ids = api.responses.get_response_ids("123456", "ABC123")
        """
        params = [self._client.session_key, survey_id, token]
        response = self._make_request("get_response_ids", params)
        return response if response else []
    
    @requires_session
    def get_all_response_ids(self, survey_id: str) -> List[str]:
        """
        Get list of ALL response IDs for a survey.
        
        This method exports responses in JSON format and extracts the response IDs,
        since the get_response_ids API method requires a specific participant token.
        
        Args:
            survey_id: Survey ID to get all response IDs for
            
        Returns:
            List of all response ID strings
            
        Example:
            # Get all response IDs in the survey
            all_response_ids = api.responses.get_all_response_ids("123456")
        """
        try:
            # Export responses with minimal data to get IDs
            responses = self.export_responses(
                survey_id, 
                document_type="json",
                heading_type="code",  # Use question codes that can be mapped to Question objects
                response_type="short"
            )
            
            # Extract response IDs from the exported data
            # After our fix, JSON responses should be properly parsed dictionaries or lists
            if isinstance(responses, dict):
                if 'responses' in responses:
                    # Standard LimeSurvey JSON format with 'responses' key
                    return [str(response.get('id', '')) for response in responses['responses'] if response.get('id')]
                elif responses:
                    # Flat dictionary format - extract IDs if available
                    ids = []
                    for key, value in responses.items():
                        if key == 'id' or (isinstance(key, str) and key.lower() == 'id'):
                            ids.append(str(value))
                    return ids
                    
            elif isinstance(responses, list):
                # List of response dictionaries
                return [str(response.get('id', '')) for response in responses if response.get('id')]
            else:
                # If still a string or other format, no IDs available
                return []
                
        except Exception:
            # If export fails, return empty list
            return [] 