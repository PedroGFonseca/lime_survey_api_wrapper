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

from .session import SessionManager
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
        
        # Initialize session manager
        self._session_manager = SessionManager(url, username, password, debug)
        
        # Initialize managers
        self.surveys = SurveyManager(self)
        self.questions = QuestionManager(self)
        self.responses = ResponseManager(self)
        self.participants = ParticipantManager(self)
    
    @property
    def session_key(self) -> Optional[str]:
        """Get current session key from session manager."""
        return self._session_manager.session_key
    
    @property
    def _persistent_session(self) -> bool:
        """Check if session is persistent (for backward compatibility)."""
        return self._session_manager.is_persistent
        
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
        """
        self._request_id += 1
        
        payload = {
            "method": method,
            "params": params,
            "id": self._request_id
        }
        
        if self.debug:
            print(f"DEBUG: Making request to {method} with {len(params)} parameters")
            session_key = params[0] if params else None
            print(f"DEBUG: Session key: {session_key[:10] if session_key else 'None'}...")
        
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