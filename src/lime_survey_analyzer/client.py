"""
LimeSurvey API Client

A comprehensive Python client for interacting with LimeSurvey's RemoteControl API.
Provides organized access to survey, question, response, and participant operations
through dedicated manager classes.

Features:
- Read-only operations for maximum safety
- Secure credential handling (environment variables, config files)
- Automatic session management
- Comprehensive type hints and documentation
- Debug logging support
- Modular manager-based architecture following SOLID principles

Security Best Practices:
- Never store credentials in code
- Use environment variables or secure config files
- Enable HTTPS for production use
- Regularly rotate API credentials
- Monitor API access logs

Example:
    Basic usage with environment variables:
    
    import os
    from lime_survey_analyzer import LimeSurveyDirectAPI
    
    api = LimeSurveyDirectAPI.from_env()
    
    with api:
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
        
        # Site operations
        languages = api.site.get_available_site_languages()

Author: Generated for LimeSurvey API integration
"""

import os
import json
import configparser
import getpass
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import requests

from .managers.survey import SurveyManager
from .managers.question import QuestionManager  
from .managers.response import ResponseManager
from .managers.participant import ParticipantManager


class LimeSurveyDirectAPI:
    """
    Main LimeSurvey API client with organized manager-based access.
    
    This client provides access to LimeSurvey functionality through specialized managers:
    - surveys: Survey operations (list, properties, summary)
    - questions: Question and group operations  
    - responses: Response data and statistics
    - participants: Participant management
    
    The client handles session management automatically and can be used as a context manager
    for automatic cleanup.
    """
    
    def __init__(self, url: str, username: str, password: str, debug: bool = False):
        """
        Initialize the LimeSurvey API client.
        
        Args:
            url: LimeSurvey RemoteControl API URL
            username: LimeSurvey username
            password: LimeSurvey password  
            debug: Enable debug logging for API requests
        """
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self._password = password  # For backward compatibility with tests
        self.debug = debug
        self.session_key = None
        self._request_id = 0
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Security warning for non-HTTPS URLs
        if url.startswith('http://') and not url.startswith('http://localhost'):
            import warnings
            warnings.warn(
                "Using HTTP instead of HTTPS may expose credentials. "
                "Use HTTPS in production environments.",
                UserWarning
            )
        
        # Initialize managers
        self.surveys = SurveyManager(self)
        self.questions = QuestionManager(self)
        self.responses = ResponseManager(self)
        self.participants = ParticipantManager(self)
        
    @classmethod
    def from_env(cls, debug: bool = False) -> 'LimeSurveyDirectAPI':
        """Create API client from environment variables.
        
        Required environment variables:
            LIMESURVEY_URL: LimeSurvey RemoteControl API URL
            LIMESURVEY_USERNAME: LimeSurvey username
            LIMESURVEY_PASSWORD: LimeSurvey password
            
        Args:
            debug: Enable debug logging
            
        Returns:
            LimeSurveyDirectAPI: Configured API client
            
        Raises:
            ValueError: If required environment variables are missing
            
        Example:
            export LIMESURVEY_URL="https://survey.example.com/admin/remotecontrol"
            export LIMESURVEY_USERNAME="api_user"
            export LIMESURVEY_PASSWORD="secure_password"
            
            api = LimeSurveyDirectAPI.from_env()
        """
        url = os.getenv('LIMESURVEY_URL')
        username = os.getenv('LIMESURVEY_USERNAME')
        password = os.getenv('LIMESURVEY_PASSWORD')
        
        if not all([url, username, password]):
            missing = [var for var, val in [
                ('LIMESURVEY_URL', url),
                ('LIMESURVEY_USERNAME', username),
                ('LIMESURVEY_PASSWORD', password)
            ] if not val]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(url, username, password, debug)
    
    @classmethod
    def from_config(cls, config_path: Union[str, Path], section: str = 'limesurvey', debug: bool = False) -> 'LimeSurveyDirectAPI':
        """Create API client from configuration file.
        
        Args:
            config_path: Path to configuration file (.ini format)
            section: Configuration section name
            debug: Enable debug logging
            
        Returns:
            LimeSurveyDirectAPI: Configured API client
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If required config values are missing
            
        Example config file (credentials.ini):
            [limesurvey]
            url = https://survey.example.com/admin/remotecontrol
            username = api_user
            password = secure_password
            
        Usage:
            api = LimeSurveyDirectAPI.from_config('credentials.ini')
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        config = configparser.ConfigParser()
        config.read(config_path)
        
        if section not in config:
            raise ValueError(f"Section '{section}' not found in config file")
        
        section_config = config[section]
        required_keys = ['url', 'username', 'password']
        missing_keys = [key for key in required_keys if key not in section_config]
        
        if missing_keys:
            raise ValueError(f"Missing required config keys in section '{section}': {', '.join(missing_keys)}")
        
        return cls(
            url=section_config['url'],
            username=section_config['username'],
            password=section_config['password'],
            debug=debug
        )
    
    @classmethod
    def from_prompt(cls, url: Optional[str] = None, username: Optional[str] = None, debug: bool = False) -> 'LimeSurveyDirectAPI':
        """Create API client with interactive credential prompting.
        
        Args:
            url: LimeSurvey URL (will prompt if not provided)
            username: Username (will prompt if not provided)
            debug: Enable debug logging
            
        Returns:
            LimeSurveyDirectAPI: Configured API client
            
        Example:
            api = LimeSurveyDirectAPI.from_prompt()
            # Will interactively prompt for URL, username, and password
        """
        if url is None:
            url = input("LimeSurvey URL (e.g., https://survey.example.com/admin/remotecontrol): ")
        
        if username is None:
            username = input("Username: ")
        
        password = getpass.getpass("Password: ")
        
        return cls(url, username, password, debug)
    
    def _make_request(self, method: str, params: List[Any]) -> Any:
        """
        Make a JSON-RPC request to the LimeSurvey API.
        
        Args:
            method: API method name
            params: List of parameters for the method
            
        Returns:
            API response data
            
        Raises:
            Exception: If request fails or API returns an error
        """
        self._request_id += 1
        
        payload = {
            "method": method,
            "params": params,
            "id": self._request_id,
            "jsonrpc": "2.0"
        }
        
        if self.debug:
            # Sanitize password from debug output
            sanitized_params = []
            for param in params:
                if isinstance(param, str) and param == self.password:
                    sanitized_params.append("***PASSWORD***")
                else:
                    sanitized_params.append(param)
            print(f"API Request: {method} with params: {sanitized_params}")
        
        try:
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            
            if self.debug:
                print(f"API Response: {data}")
            
            if 'error' in data and data['error'] is not None:
                error_msg = data['error']
                if isinstance(error_msg, dict):
                    error_msg = f"{error_msg.get('code', 'Unknown')}: {error_msg.get('message', 'Unknown error')}"
                raise Exception(f"API Error: {error_msg}")
            
            return data.get('result')
            
        except requests.RequestException as e:
            raise Exception(f"HTTP Error: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON decode error: {e}")
    
    def _get_session_key(self) -> str:
        """
        Authenticate and get session key from LimeSurvey.
        
        Returns:
            Session key string for authenticated requests
        """
        result = self._make_request("get_session_key", [self.username, self.password])
        
        if isinstance(result, dict) and 'status' in result:
            # Error response format
            raise Exception(f"Authentication failed: {result.get('status', 'Unknown error')}")
        
        self.session_key = result
        return result
    
    def _release_session_key(self) -> None:
        """Release the current session key."""
        if self.session_key:
            try:
                self._make_request("release_session_key", [self.session_key])
            except Exception:
                # Ignore errors when releasing session - server might have already cleaned up
                pass
            finally:
                self.session_key = None
    
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
    
    def __enter__(self):
        """Context manager entry - establish session."""
        self._get_session_key()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup session."""
        self._release_session_key()
        return False 