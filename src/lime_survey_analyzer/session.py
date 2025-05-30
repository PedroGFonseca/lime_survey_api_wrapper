"""
Session management for LimeSurvey API.

This module provides clean separation of concerns for session handling,
making the authentication logic more maintainable and testable.
"""

from typing import Optional, Any, List
from contextlib import contextmanager
import requests


class SessionManager:
    """
    Manages LimeSurvey API sessions with clean lifecycle handling.
    
    Supports both temporary auto-sessions and persistent sessions.
    """
    
    def __init__(self, url: str, username: str, password: str, debug: bool = False):
        """
        Initialize session manager.
        
        Args:
            url: LimeSurvey RemoteControl API URL
            username: LimeSurvey username
            password: LimeSurvey password
            debug: Enable debug logging
        """
        self.url = url
        self.username = username
        self.password = password
        self.debug = debug
        self._session_key: Optional[str] = None
        self._request_id = 0
        self._persistent = False
    
    @property
    def session_key(self) -> Optional[str]:
        """Get current session key."""
        return self._session_key
    
    @property
    def is_connected(self) -> bool:
        """Check if session is active."""
        return self._session_key is not None
    
    @property
    def is_persistent(self) -> bool:
        """Check if session is persistent (not auto-managed)."""
        return self._persistent
    
    def create_session(self) -> str:
        """
        Create a new session with LimeSurvey server.
        
        Returns:
            Session key string
            
        Raises:
            Exception: If authentication fails
        """
        self._request_id += 1
        
        payload = {
            "method": "get_session_key",
            "params": [self.username, self.password],
            "id": self._request_id
        }
        
        if self.debug:
            print(f"DEBUG: Creating new session with LimeSurvey")
        
        response = requests.post(
            self.url,
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        
        result = response.json()
        
        if 'error' in result and result['error'] is not None:
            raise Exception(f"Session creation failed: {result['error']}")
        
        session_result = result['result']
        
        if isinstance(session_result, dict) and 'status' in session_result:
            raise Exception(f"Authentication failed: {session_result.get('status', 'Unknown error')}")
        
        self._session_key = session_result
        
        if self.debug:
            print(f"DEBUG: Session created: {session_result[:10]}...")
            
        return session_result
    
    def release_session(self) -> None:
        """
        Release current session with server.
        
        Safe to call multiple times or when no session exists.
        """
        if not self._session_key:
            return
            
        try:
            self._request_id += 1
            
            payload = {
                "method": "release_session_key",
                "params": [self._session_key],
                "id": self._request_id
            }
            
            if self.debug:
                print(f"DEBUG: Releasing session: {self._session_key[:10]}...")
            
            response = requests.post(
                self.url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
        except Exception:
            # Ignore errors when releasing - server might have cleaned up already
            if self.debug:
                print("DEBUG: Session release request failed (server may have cleaned up)")
        finally:
            self._session_key = None
            self._persistent = False
    
    def connect_persistent(self) -> 'SessionManager':
        """
        Create a persistent session for multiple API calls.
        
        Returns:
            Self for method chaining
        """
        if not self._session_key:
            self.create_session()
            self._persistent = True
        return self
    
    def disconnect_persistent(self) -> None:
        """
        Disconnect persistent session.
        """
        if self._persistent:
            self.release_session()
    
    @contextmanager
    def temporary_session(self):
        """
        Context manager for temporary sessions.
        
        Example:
            with session_manager.temporary_session() as session_key:
                # Use session_key for API calls
                pass
            # Session automatically cleaned up
        """
        session_key = self.create_session()
        try:
            yield session_key
        finally:
            self.release_session()
    
    def ensure_session_key(self, params: List[Any]) -> List[Any]:
        """
        Ensure session key is properly injected into API parameters.
        
        Args:
            params: Parameter list that may contain None placeholder for session key
            
        Returns:
            Parameter list with session key injected
        """
        final_params = params.copy()
        
        # Replace None session key placeholder with actual session key
        if len(final_params) > 0 and final_params[0] is None:
            if not self._session_key:
                raise Exception("No active session key available")
            final_params[0] = self._session_key
            
        return final_params 