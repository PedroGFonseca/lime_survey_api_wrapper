"""
Base manager class with shared functionality for all LimeSurvey API managers.
"""

from abc import ABC
from typing import Dict, Any, List, Optional
from functools import wraps


def requires_session(func):
    """Decorator to ensure session key exists before API call."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        # If auto_session is enabled, the _make_request method handles sessions automatically
        # If auto_session is disabled, we need a session key
        if not self._client.auto_session and not self._client.session_key:
            raise Exception(
                "No active session. Either:\n"
                "1. Call api.connect() for persistent session\n"
                "2. Enable auto_session=True (default)"
            )
        return func(self, *args, **kwargs)
    return wrapper


class BaseManager(ABC):
    """
    Base class for all LimeSurvey API managers.
    
    Provides shared functionality like making API requests and parameter building.
    Each manager focuses on a specific domain of LimeSurvey operations.
    """
    
    def __init__(self, client):
        """
        Initialize the manager with a reference to the main API client.
        
        Args:
            client: LimeSurveyDirectAPI instance for making requests
        """
        self._client = client
    
    def _make_request(self, method: str, params: List[Any]) -> Any:
        """
        Make an API request through the main client.
        
        Args:
            method: LimeSurvey API method name
            params: List of parameters for the API method
            
        Returns:
            API response data
            
        Raises:
            Exception: If API returns an error
        """
        return self._client._make_request(method, params)
    
    def _build_params(self, base_params: List[Any], **optional_params) -> List[Any]:
        """
        Build parameter list by adding non-None optional parameters.
        
        Args:
            base_params: Required parameters
            **optional_params: Optional parameters (None values are filtered out)
            
        Returns:
            Complete parameter list
        """
        return self._client._build_params(base_params, **optional_params) 