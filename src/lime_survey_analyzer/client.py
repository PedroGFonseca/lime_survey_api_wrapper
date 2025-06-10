"""
LimeSurvey API Client

A comprehensive Python client for interacting with LimeSurvey's RemoteControl API.
Provides organized access to survey, question, response, and participant operations
through dedicated manager classes.

Features:
- Read-only operations for maximum safety
- Secure credential handling via configuration files
- Automatic session management for seamless usage
- Comprehensive type hints and documentation
- Debug logging support
- Modular manager-based architecture following SOLID principles

Security Best Practices:
- Credentials stored in secure configuration files only
- Configuration files should be in a secrets/ directory that is git-ignored
- Enable HTTPS for production use
- Regularly rotate API credentials
- Monitor API access logs

Example:
    Simple usage:
    
    from lime_survey_analyzer import LimeSurveyClient
    
    # Create client from configuration file
    api = LimeSurveyClient.from_config('secrets/credentials.ini')
    
    # Survey operations
    surveys = api.surveys.list_surveys()
    survey_data = api.surveys.get_survey_properties("123456")
    
    # Question operations
    groups = api.questions.list_groups("123456")
    questions = api.questions.list_questions("123456")
    
    # Response operations
    responses = api.responses.export_responses("123456")
    
    # Participant operations
    participants = api.participants.list_participants("123456")

Author: Generated for LimeSurvey API integration
"""

import configparser
from pathlib import Path
from typing import List, Any, Optional
import requests

from .session import SessionManager
from .managers.survey import SurveyManager
from .managers.question import QuestionManager  
from .managers.response import ResponseManager
from .managers.participant import ParticipantManager

# Import logging
from .utils.logging import get_logger, configure_package_logging

# Import exceptions
from .exceptions import ConfigurationError, AuthenticationError, APIError, handle_api_error


class LimeSurveyClient:
    """
    Main LimeSurvey API client with organized manager-based access.
    
    This client provides access to LimeSurvey functionality through specialized managers:
    - surveys: Survey operations (list, properties, summary)
    - questions: Question and group operations  
    - responses: Response data and statistics
    - participants: Participant management
    
    Authentication is handled via configuration files stored in a secure location.
    
    Session Management Modes:
    1. Auto-session (default): Automatically manages sessions per request - perfect for scripts
    2. Persistent session: Call connect() once, use until disconnect() - efficient for applications
    """
    
    def __init__(self, url: str, username: str, password: str, debug: bool = False, 
                 auto_session: bool = True):
        """
        Initialize the LimeSurvey API client.
        
        Note: Direct initialization is discouraged. Use LimeSurveyClient.from_config() instead.
        
        Args:
            url: LimeSurvey RemoteControl API URL
            username: LimeSurvey username
            password: LimeSurvey password  
            debug: Enable debug logging for API requests
            auto_session: If True, automatically manage sessions per request (default)
                         If False, use connect()/disconnect() for explicit session control
        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self._password = password  # For backward compatibility with tests
        self.debug = debug
        self.auto_session = auto_session
        self._request_id = 0
        
        # Setup logging
        configure_package_logging(debug=debug)
        self.logger = get_logger(__name__)
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ConfigurationError("URL must start with http:// or https://")
        
        # Security warning for non-HTTPS URLs
        if url.startswith('http://') and not url.startswith('http://localhost'):
            import warnings
            warnings.warn(
                "Using HTTP instead of HTTPS may expose credentials. "
                "Use HTTPS in production environments.",
                UserWarning
            )
        
        # Initialize session manager
        self._session_manager = SessionManager(self.url, self.username, self.password, self.debug)
        
        # Initialize managers
        self.surveys = SurveyManager(self)
        self.questions = QuestionManager(self)
        self.responses = ResponseManager(self)
        self.participants = ParticipantManager(self)
        
        self.logger.debug(f"LimeSurveyClient initialized for {url}")
    
    @property
    def session_key(self) -> Optional[str]:
        """Get current session key from session manager."""
        return self._session_manager.session_key
    
    @property
    def _persistent_session(self) -> bool:
        """Check if session is persistent (for backward compatibility)."""
        return self._session_manager.is_persistent
        
    @classmethod
    def from_config(cls, config_path: str = 'secrets/credentials.ini', debug: bool = False, 
                   auto_session: bool = True) -> 'LimeSurveyClient':
        """
        Create API client from configuration file.
        
        This is the recommended way to create a LimeSurveyClient instance.
        
        Expected config file format:
        [limesurvey]
        url = https://your-limesurvey.com/admin/remotecontrol
        username = your_username
        password = your_password
        
        Args:
            config_path: Path to configuration file (default: secrets/credentials.ini)
            debug: Enable debug logging  
            auto_session: Enable automatic session management (default: True)
            
        Returns:
            Configured LimeSurveyClient instance
            
        Raises:
            ConfigurationError: If config file doesn't exist or is invalid
            
        Example:
            # Using default path
            api = LimeSurveyClient.from_config()
            
            # Using custom path
            api = LimeSurveyClient.from_config('path/to/my/config.ini')
            
            # With debug logging
            api = LimeSurveyClient.from_config(debug=True)
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}\n"
                f"Please create a configuration file with the following format:\n"
                f"[limesurvey]\n"
                f"url = https://your-limesurvey.com/admin/remotecontrol\n"
                f"username = your_username\n"
                f"password = your_password"
            )
            
        config = configparser.ConfigParser()
        try:
            config.read(config_file)
        except Exception as e:
            raise ConfigurationError(f"Failed to read configuration file: {e}")
        
        if 'limesurvey' not in config:
            raise ConfigurationError(
                f"Configuration file must contain [limesurvey] section. "
                f"Found sections: {list(config.sections())}"
            )
            
        section = config['limesurvey']
        required_keys = ['url', 'username', 'password']
        missing_keys = [key for key in required_keys if key not in section]
        
        if missing_keys:
            raise ConfigurationError(
                f"Missing required configuration keys: {', '.join(missing_keys)}\n"
                f"Required keys: {', '.join(required_keys)}"
            )
            
        return cls(
            section['url'], 
            section['username'], 
            section['password'], 
            debug,
            auto_session
        )
    
    def connect(self):
        """
        Establish a persistent session for multiple API calls.
        
        Use this for long-running applications or when making many API calls.
        Call disconnect() when done to clean up the session.
        
        Example:
            api = LimeSurveyClient.from_config(auto_session=False)
            api.connect()
            
            # Make multiple calls efficiently
            surveys = api.surveys.list_surveys()
            questions = api.questions.list_questions(surveys[0]['sid'])
            responses = api.responses.export_responses(surveys[0]['sid'])
            
            api.disconnect()
        """
        self._session_manager.connect_persistent()
        return self
    
    def disconnect(self):
        """
        Close the persistent session and clean up resources.
        
        Call this when done with a persistent session to properly
        release the session on the LimeSurvey server.
        """
        self._session_manager.disconnect_persistent()
    
    def is_connected(self) -> bool:
        """
        Check if there's an active session.
        
        Returns:
            True if connected with an active session key, False otherwise
        """
        return self._session_manager.is_connected

    def _make_request(self, method: str, params: List[Any]) -> Any:
        """
        Make a JSON-RPC request to the LimeSurvey API.
        
        Args:
            method: LimeSurvey API method name
            params: List of parameters for the API call
            
        Returns:
            API response data
            
        Raises:
            Exception: If the API request fails or returns an error
        """
        if self.auto_session:
            # Auto-session mode: use temporary session for this request
            with self._session_manager.temporary_session():
                final_params = self._session_manager.ensure_session_key(params)
                return self._execute_request(method, final_params)
        else:
            # Persistent session mode: use existing session
            final_params = self._session_manager.ensure_session_key(params)
            return self._execute_request(method, final_params)
    
    def _execute_request(self, method: str, params: List[Any]) -> Any:
        """
        Execute the actual HTTP request to LimeSurvey API.
        
        Args:
            method: API method name
            params: Complete parameter list with session key
            
        Returns:
            API response data
            
        Raises:
            APIError: If the API request fails or returns an error
            AuthenticationError: If authentication fails
        """
        self._request_id += 1
        
        payload = {
            "method": method,
            "params": params,
            "id": self._request_id
        }
        
        if self.debug:
            self.logger.debug(f"Making request to {method} with {len(params)} parameters")
            session_key = params[0] if params else None
            self.logger.debug(f"Session key: {session_key[:10] if session_key else 'None'}...")
        
        try:
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30  # Add timeout for better error handling
            )
            response.raise_for_status()
        except requests.exceptions.Timeout:
            raise APIError(f"Request to {method} timed out", api_method=method)
        except requests.exceptions.ConnectionError:
            raise APIError(f"Connection failed to {self.url}", api_method=method)
        except requests.exceptions.HTTPError as e:
            raise APIError(f"HTTP error {e.response.status_code}: {e}", api_method=method)
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}", api_method=method)
        
        try:
            result = response.json()
        except ValueError as e:
            raise APIError(f"Invalid JSON response: {e}", api_method=method)
        
        # Handle API-level errors
        if 'error' in result and result['error'] is not None:
            handle_api_error(result, method)
        
        return result['result']
    
    def _build_params(self, base_params: List[Any], **optional_params) -> List[Any]:
        """
        Build parameter list by adding non-None optional parameters.
        
        Args:
            base_params: Required parameters
            **optional_params: Optional parameters (None values are filtered out)
            
        Returns:
            Complete parameter list
        """
        params = base_params.copy()
        for value in optional_params.values():
            if value is not None:
                params.append(value)
        return params
    
    # Legacy methods for backward compatibility
    def _get_session_key(self) -> str:
        """Legacy method for backward compatibility."""
        return self._session_manager.create_session()
    
    def _release_session_key(self) -> None:
        """Legacy method for backward compatibility."""
        self._session_manager.release_session()


# Backward compatibility alias
LimeSurveyDirectAPI = LimeSurveyClient 