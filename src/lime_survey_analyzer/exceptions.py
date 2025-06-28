"""
Custom exceptions for LimeSurvey Analyzer.

Simplified exception hierarchy with only the essential exceptions that are actually used.
"""

from typing import Optional, Dict, Any


class LimeSurveyError(Exception):
    """
    Base exception for all LimeSurvey Analyzer operations.
    
    All custom exceptions in the package inherit from this base class,
    allowing for catch-all exception handling when needed.
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class AuthenticationError(LimeSurveyError):
    """
    Authentication or authorization failed.
    
    Raised when login credentials are invalid, session has expired,
    or user lacks permissions for the requested operation.
    """
    pass


class APIError(LimeSurveyError):
    """
    General API communication error.
    
    Raised when the LimeSurvey API returns an error response
    or when communication with the API fails.
    """
    
    def __init__(self, message: str, api_method: Optional[str] = None, 
                 api_response: Optional[Dict[str, Any]] = None):
        """
        Initialize API error with additional context.
        
        Args:
            message: Error message
            api_method: Name of the API method that failed
            api_response: Raw API response that caused the error
        """
        details = {}
        if api_method:
            details['api_method'] = api_method
        if api_response:
            details['api_response'] = api_response
            
        super().__init__(message, details)
        self.api_method = api_method
        self.api_response = api_response


class SurveyNotFoundError(LimeSurveyError):
    """
    Survey not found or not accessible.
    
    Raised when trying to access a survey that doesn't exist
    or that the user doesn't have permission to access.
    """
    
    def __init__(self, survey_id: str, message: Optional[str] = None):
        if message is None:
            message = f"Survey '{survey_id}' not found or not accessible"
        super().__init__(message, {'survey_id': survey_id})
        self.survey_id = survey_id


def handle_api_error(response: Dict[str, Any], method: str) -> None:
    """
    Handle LimeSurvey API error responses by raising appropriate exceptions.
    
    Args:
        response: API response dictionary containing error information
        method: Name of the API method that failed
        
    Raises:
        AuthenticationError: For authentication/session errors
        SurveyNotFoundError: When survey is not found
        APIError: For all other API errors
    """
    error_msg = response.get('error', 'Unknown API error')
    
    if 'Invalid session' in str(error_msg) or 'session' in str(error_msg).lower():
        raise AuthenticationError(f"Authentication failed: {error_msg}")
    elif 'Survey not found' in str(error_msg) or 'not found' in str(error_msg).lower():
        raise SurveyNotFoundError('unknown', error_msg)
    else:
        raise APIError(f"API Error in {method}: {error_msg}",
                      api_method=method, api_response=response) 