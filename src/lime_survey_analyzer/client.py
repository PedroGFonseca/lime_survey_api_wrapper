"""
LimeSurvey API Client

A comprehensive Python client for interacting with LimeSurvey's RemoteControl API.
Provides organized access to survey, question, response, and participant operations
through dedicated manager classes.

Features:
- Read-only operations for maximum safety
- Secure credential handling (environment variables, config files)
- Automatic session management for seamless usage
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
    Simple usage:
    
    from lime_survey_analyzer import LimeSurveyDirectAPI
    
    # Create client and start using immediately
    api = LimeSurveyDirectAPI.from_env()
    
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
    
    Session Management Modes:
    1. Auto-session (default): Automatically manages sessions per request - perfect for scripts
    2. Persistent session: Call connect() once, use until disconnect() - efficient for applications
    """
    
    def __init__(self, url: str, username: str, password: str, debug: bool = False, 
                 auto_session: bool = True):
        """
        Initialize the LimeSurvey API client.
        
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
        self.session_key = None
        self._request_id = 0
        self._persistent_session = False
        
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
    def from_env(cls, debug: bool = False, auto_session: bool = True) -> 'LimeSurveyDirectAPI':
        """
        Create API client from environment variables.
        
        Required environment variables:
        - LIMESURVEY_URL: Full URL to RemoteControl endpoint
        - LIMESURVEY_USERNAME: LimeSurvey username  
        - LIMESURVEY_PASSWORD: LimeSurvey password
        
        Args:
            debug: Enable debug logging
            auto_session: Enable automatic session management (default: True)
            
        Returns:
            Configured LimeSurveyDirectAPI instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        url = os.getenv('LIMESURVEY_URL')
        username = os.getenv('LIMESURVEY_USERNAME')  
        password = os.getenv('LIMESURVEY_PASSWORD')
        
        if not all([url, username, password]):
            missing = [name for name, value in [
                ('LIMESURVEY_URL', url),
                ('LIMESURVEY_USERNAME', username), 
                ('LIMESURVEY_PASSWORD', password)
            ] if not value]
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(url, username, password, debug, auto_session)
    
    @classmethod
    def from_config(cls, config_path: str = 'credentials.ini', debug: bool = False, auto_session: bool = True) -> 'LimeSurveyDirectAPI':
        """
        Create API client from configuration file.
        
        Expected config file format:
        [limesurvey]
        url = https://your-limesurvey.com/admin/remotecontrol
        username = your_username
        password = your_password
        
        Args:
            config_path: Path to configuration file
            debug: Enable debug logging  
            auto_session: Enable automatic session management (default: True)
            
        Returns:
            Configured LimeSurveyDirectAPI instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If required config values are missing
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
            
        config = configparser.ConfigParser()
        config.read(config_file)
        
        if 'limesurvey' not in config:
            raise ValueError("Configuration file must contain [limesurvey] section")
            
        section = config['limesurvey']
        required_keys = ['url', 'username', 'password']
        missing_keys = [key for key in required_keys if key not in section]
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
            
        return cls(
            section['url'], 
            section['username'], 
            section['password'], 
            debug,
            auto_session
        )
    
    @classmethod  
    def from_prompt(cls, debug: bool = False, auto_session: bool = True) -> 'LimeSurveyDirectAPI':
        """
        Create API client with interactive credential prompts.
        
        Args:
            debug: Enable debug logging
            auto_session: Enable automatic session management (default: True)
            
        Returns:
            Configured LimeSurveyDirectAPI instance
        """
        print("Enter LimeSurvey credentials:")
        url = input("URL (e.g., https://survey.example.com/admin/remotecontrol): ").strip()
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()
        
        return cls(url, username, password, debug, auto_session)
    
    def connect(self):
        """
        Establish a persistent session for multiple API calls.
        
        Use this for long-running applications or when making many API calls.
        Call disconnect() when done to clean up the session.
        
        Example:
            api = LimeSurveyDirectAPI.from_env(auto_session=False)
            api.connect()
            
            # Make multiple calls efficiently
            surveys = api.surveys.list_surveys()
            questions = api.questions.list_questions(surveys[0]['sid'])
            responses = api.responses.export_responses(surveys[0]['sid'])
            
            api.disconnect()
        """
        if not self.session_key:
            self._get_session_key()
            self._persistent_session = True
        return self
    
    def disconnect(self):
        """
        Close the persistent session and clean up resources.
        
        Call this when done with a persistent session to properly
        release the session on the LimeSurvey server.
        """
        if self._persistent_session:
            self._release_session_key()
            self._persistent_session = False
    
    def is_connected(self) -> bool:
        """
        Check if there's an active session.
        
        Returns:
            True if connected with an active session key, False otherwise
        """
        return self.session_key is not None

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
        if self.auto_session and not self.session_key:
            # Auto-session mode: temporarily get session for this request
            temp_session = True
            self._get_session_key()
        else:
            temp_session = False
        
        try:
            self._request_id += 1
            
            payload = {
                "method": method,
                "params": params,
                "id": self._request_id
            }
            
            if self.debug:
                # Only log method and param count for security
                print(f"DEBUG: Making request to {method} with {len(params)} parameters")
            
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'error' in result and result['error'] is not None:
                raise Exception(f"API Error: {result['error']}")
            
            return result['result']
            
        finally:
            # Clean up temporary session if auto-session mode
            if temp_session and self.auto_session:
                self._release_session_key()
    
    def _get_session_key(self) -> str:
        """
        Authenticate and get session key from LimeSurvey.
        
        Returns:
            Session key string for authenticated requests
        """
        # Make direct request to avoid recursion with _make_request
        self._request_id += 1
        
        payload = {
            "method": "get_session_key",
            "params": [self.username, self.password],
            "id": self._request_id
        }
        
        if self.debug:
            print(f"DEBUG: Authenticating with LimeSurvey")
        
        response = requests.post(
            self.url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        result = response.json()
        
        if 'error' in result and result['error'] is not None:
            raise Exception(f"API Error: {result['error']}")
        
        session_result = result['result']
        
        if isinstance(session_result, dict) and 'status' in session_result:
            # Error response format
            raise Exception(f"Authentication failed: {session_result.get('status', 'Unknown error')}")
        
        self.session_key = session_result
        return session_result
    
    def _release_session_key(self) -> None:
        """Release the current session key."""
        if self.session_key:
            try:
                # Make direct request to avoid recursion with _make_request
                self._request_id += 1
                
                payload = {
                    "method": "release_session_key",
                    "params": [self.session_key],
                    "id": self._request_id
                }
                
                response = requests.post(
                    self.url,
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                response.raise_for_status()
                
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
    
    # Session management methods for explicit control when needed 