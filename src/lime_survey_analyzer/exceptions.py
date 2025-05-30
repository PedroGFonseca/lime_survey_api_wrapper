"""
Custom exceptions for LimeSurvey Analyzer.

This module provides a hierarchy of specific exceptions to replace generic
Exception usage throughout the codebase, improving error handling and debugging.
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


class ConfigurationError(LimeSurveyError):
    """
    Configuration or setup error.
    
    Raised when required configuration is missing, invalid, or
    when there are issues with environment setup.
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


class SessionError(LimeSurveyError):
    """
    Session management error.
    
    Raised when there are issues creating, maintaining, or
    releasing LimeSurvey API sessions.
    """
    pass


class QuestionValidationError(LimeSurveyError):
    """
    Question validation failed.
    
    Raised when question data doesn't meet expected structure
    or validation rules for the question type.
    """
    
    def __init__(self, message: str, question_id: Optional[str] = None,
                 question_type: Optional[str] = None, validation_errors: Optional[list] = None):
        """
        Initialize question validation error.
        
        Args:
            message: Error message
            question_id: ID of the question that failed validation
            question_type: Type of the question
            validation_errors: List of specific validation error messages
        """
        details = {}
        if question_id:
            details['question_id'] = question_id
        if question_type:
            details['question_type'] = question_type
        if validation_errors:
            details['validation_errors'] = validation_errors
            
        super().__init__(message, details)
        self.question_id = question_id
        self.question_type = question_type
        self.validation_errors = validation_errors or []


class UnsupportedQuestionTypeError(LimeSurveyError):
    """
    Question type not yet implemented.
    
    Raised when trying to use operations on question types that are
    not part of the priority question types (L, M, S, R).
    """
    
    def __init__(self, question_type: str, supported_types: Optional[list] = None):
        """
        Initialize unsupported question type error.
        
        Args:
            question_type: The unsupported question type code
            supported_types: List of currently supported question types
        """
        message = f"Question type '{question_type}' is not yet implemented"
        if supported_types:
            message += f". Supported types: {', '.join(supported_types)}"
            
        details = {
            'question_type': question_type,
            'supported_types': supported_types or []
        }
        
        super().__init__(message, details)
        self.question_type = question_type
        self.supported_types = supported_types or []


class DataValidationError(LimeSurveyError):
    """
    Data validation or parsing error.
    
    Raised when response data, survey data, or other API data
    doesn't match expected format or contains invalid values.
    """
    
    def __init__(self, message: str, data_type: Optional[str] = None,
                 field_name: Optional[str] = None, expected_format: Optional[str] = None):
        """
        Initialize data validation error.
        
        Args:
            message: Error message
            data_type: Type of data that failed validation (e.g., 'response', 'survey')
            field_name: Specific field that caused the error
            expected_format: Description of expected data format
        """
        details = {}
        if data_type:
            details['data_type'] = data_type
        if field_name:
            details['field_name'] = field_name
        if expected_format:
            details['expected_format'] = expected_format
            
        super().__init__(message, details)
        self.data_type = data_type
        self.field_name = field_name
        self.expected_format = expected_format


class SurveyNotFoundError(LimeSurveyError):
    """
    Survey not found or not accessible.
    
    Raised when trying to access a survey that doesn't exist
    or that the user doesn't have permission to access.
    """
    
    def __init__(self, survey_id: str, message: Optional[str] = None):
        """
        Initialize survey not found error.
        
        Args:
            survey_id: ID of the survey that wasn't found
            message: Optional custom error message
        """
        if message is None:
            message = f"Survey with ID '{survey_id}' not found or not accessible"
            
        details = {'survey_id': survey_id}
        super().__init__(message, details)
        self.survey_id = survey_id


class QuestionNotFoundError(LimeSurveyError):
    """
    Question not found or not accessible.
    
    Raised when trying to access a question that doesn't exist
    or that the user doesn't have permission to access.
    """
    
    def __init__(self, question_id: str, survey_id: Optional[str] = None, 
                 message: Optional[str] = None):
        """
        Initialize question not found error.
        
        Args:
            question_id: ID of the question that wasn't found
            survey_id: ID of the survey the question should belong to
            message: Optional custom error message
        """
        if message is None:
            if survey_id:
                message = f"Question with ID '{question_id}' not found in survey '{survey_id}'"
            else:
                message = f"Question with ID '{question_id}' not found"
                
        details = {'question_id': question_id}
        if survey_id:
            details['survey_id'] = survey_id
            
        super().__init__(message, details)
        self.question_id = question_id
        self.survey_id = survey_id


class ResponseExportError(LimeSurveyError):
    """
    Response data export failed.
    
    Raised when there are issues exporting response data from
    LimeSurvey surveys, such as format errors or data processing issues.
    """
    
    def __init__(self, message: str, survey_id: Optional[str] = None,
                 export_format: Optional[str] = None):
        """
        Initialize response export error.
        
        Args:
            message: Error message
            survey_id: ID of the survey being exported
            export_format: Format that was being exported (json, csv, etc.)
        """
        details = {}
        if survey_id:
            details['survey_id'] = survey_id
        if export_format:
            details['export_format'] = export_format
            
        super().__init__(message, details)
        self.survey_id = survey_id
        self.export_format = export_format


class VisualizationError(LimeSurveyError):
    """
    Visualization generation failed.
    
    Raised when there are issues generating graphs or other
    visualizations, often due to missing dependencies or data issues.
    """
    pass


# Convenience function for backward compatibility
def handle_api_error(response: Dict[str, Any], method: str) -> None:
    """
    Convert API error response to appropriate exception.
    
    Args:
        response: Raw API response dictionary
        method: API method that was called
        
    Raises:
        APIError: With details about the specific API error
    """
    if 'error' in response and response['error'] is not None:
        error_msg = str(response['error'])
        
        # Check for specific error types
        if 'session' in error_msg.lower() or 'authentication' in error_msg.lower():
            raise AuthenticationError(f"Authentication failed: {error_msg}")
        elif 'survey' in error_msg.lower() and 'not found' in error_msg.lower():
            raise SurveyNotFoundError('unknown', error_msg)
        else:
            raise APIError(f"API Error in {method}: {error_msg}", 
                          api_method=method, api_response=response) 