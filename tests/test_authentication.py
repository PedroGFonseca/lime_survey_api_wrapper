"""
Tests for authentication and session management functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from lime_survey_analyzer.session import SessionManager
from lime_survey_analyzer import LimeSurveyDirectAPI


class TestSessionManager:
    """Test cases for SessionManager class."""
    
    def test_init(self):
        """Test SessionManager initialization."""
        manager = SessionManager("https://example.com/api", "user", "pass", debug=True)
        assert manager.url == "https://example.com/api"
        assert manager.username == "user"
        assert manager.password == "pass"
        assert manager.debug is True
        assert manager.session_key is None
        assert not manager.is_connected
        assert not manager.is_persistent
    
    @patch('requests.post')
    def test_create_session_success(self, mock_post):
        """Test successful session creation."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'test_session_key', 'error': None}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        session_key = manager.create_session()
        
        assert session_key == "test_session_key"
        assert manager.session_key == "test_session_key"
        assert manager.is_connected
        
        # Verify request was made correctly
        mock_post.assert_called_once_with(
            "https://example.com/api",
            json={'method': 'get_session_key', 'params': ['user', 'pass'], 'id': 1},
            headers={'Content-Type': 'application/json'}
        )
    
    @patch('requests.post')
    def test_create_session_auth_failure(self, mock_post):
        """Test session creation with authentication failure."""
        # Mock auth failure response
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': {'status': 'Invalid username or password'}, 'error': None}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        
        with pytest.raises(Exception, match="Authentication failed: Invalid username or password"):
            manager.create_session()
        
        assert manager.session_key is None
        assert not manager.is_connected
    
    @patch('requests.post')
    def test_create_session_api_error(self, mock_post):
        """Test session creation with API error."""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': None, 'error': 'Internal server error'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        
        with pytest.raises(Exception, match="Session creation failed: Internal server error"):
            manager.create_session()
    
    @patch('requests.post')
    def test_release_session_success(self, mock_post):
        """Test successful session release."""
        # Setup session first
        create_response = MagicMock()
        create_response.json.return_value = {'result': 'test_session_key', 'error': None}
        create_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [create_response, release_response]
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        manager.create_session()
        
        assert manager.is_connected
        
        manager.release_session()
        
        assert manager.session_key is None
        assert not manager.is_connected
        assert not manager.is_persistent
        
        # Verify both calls were made
        assert mock_post.call_count == 2
    
    def test_release_session_no_session(self):
        """Test releasing session when none exists."""
        manager = SessionManager("https://example.com/api", "user", "pass")
        
        # Should not raise exception
        manager.release_session()
        
        assert manager.session_key is None
        assert not manager.is_connected
    
    @patch('requests.post')
    def test_release_session_error_handling(self, mock_post):
        """Test session release with network error."""
        # Setup session first
        create_response = MagicMock()
        create_response.json.return_value = {'result': 'test_session_key', 'error': None}
        create_response.raise_for_status.return_value = None
        
        # Release fails
        mock_post.side_effect = [create_response, Exception("Network error")]
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        manager.create_session()
        
        # Should not raise exception even if release fails
        manager.release_session()
        
        # Session should still be cleared locally
        assert manager.session_key is None
        assert not manager.is_connected
    
    @patch('requests.post')
    def test_connect_persistent(self, mock_post):
        """Test persistent session connection."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'test_session_key', 'error': None}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        result = manager.connect_persistent()
        
        assert result is manager  # Should return self for chaining
        assert manager.is_connected
        assert manager.is_persistent
    
    @patch('requests.post')
    def test_disconnect_persistent(self, mock_post):
        """Test persistent session disconnection."""
        create_response = MagicMock()
        create_response.json.return_value = {'result': 'test_session_key', 'error': None}
        create_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [create_response, release_response]
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        manager.connect_persistent()
        
        assert manager.is_persistent
        
        manager.disconnect_persistent()
        
        assert not manager.is_connected
        assert not manager.is_persistent
    
    @patch('requests.post')
    def test_temporary_session_context_manager(self, mock_post):
        """Test temporary session context manager."""
        create_response = MagicMock()
        create_response.json.return_value = {'result': 'test_session_key', 'error': None}
        create_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [create_response, release_response]
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        
        with manager.temporary_session() as session_key:
            assert session_key == "test_session_key"
            assert manager.is_connected
        
        # Session should be released after context
        assert not manager.is_connected
        assert mock_post.call_count == 2
    
    @patch('requests.post')
    def test_temporary_session_exception_handling(self, mock_post):
        """Test temporary session cleans up even on exception."""
        create_response = MagicMock()
        create_response.json.return_value = {'result': 'test_session_key', 'error': None}
        create_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [create_response, release_response]
        
        manager = SessionManager("https://example.com/api", "user", "pass")
        
        with pytest.raises(ValueError):
            with manager.temporary_session() as session_key:
                assert manager.is_connected
                raise ValueError("Test exception")
        
        # Session should still be released
        assert not manager.is_connected
    
    def test_ensure_session_key_with_none(self):
        """Test session key injection with None placeholder."""
        manager = SessionManager("https://example.com/api", "user", "pass")
        manager._session_key = "test_session_key"
        
        params = [None, "param1", "param2"]
        result = manager.ensure_session_key(params)
        
        assert result == ["test_session_key", "param1", "param2"]
        # Original params should not be modified
        assert params == [None, "param1", "param2"]
    
    def test_ensure_session_key_without_none(self):
        """Test session key injection without None placeholder."""
        manager = SessionManager("https://example.com/api", "user", "pass")
        manager._session_key = "test_session_key"
        
        params = ["existing_session", "param1", "param2"]
        result = manager.ensure_session_key(params)
        
        # Should not modify params if no None placeholder
        assert result == ["existing_session", "param1", "param2"]
    
    def test_ensure_session_key_no_session(self):
        """Test session key injection when no session exists."""
        manager = SessionManager("https://example.com/api", "user", "pass")
        
        params = [None, "param1"]
        
        with pytest.raises(Exception, match="No active session key available"):
            manager.ensure_session_key(params)


class TestLimeSurveyDirectAPIAuthentication:
    """Test authentication functionality in main API client."""
    
    @patch('requests.post')
    def test_auto_session_mode(self, mock_post):
        """Test auto-session mode creates and releases sessions automatically."""
        # Mock session creation, API call, and session release
        session_response = MagicMock()
        session_response.json.return_value = {'result': 'session_key', 'error': None}
        session_response.raise_for_status.return_value = None
        
        api_response = MagicMock()
        api_response.json.return_value = {'result': [{'sid': '123', 'title': 'Test'}], 'error': None}
        api_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [session_response, api_response, release_response]
        
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass", auto_session=True)
        
        # Make API call - should trigger auto-session
        result = api._make_request("list_surveys", [None])
        
        assert result == [{'sid': '123', 'title': 'Test'}]
        # Should have made 3 calls: create session, API call, release session
        assert mock_post.call_count == 3
        
        # Session should not be persistent after call
        assert not api.is_connected()
    
    @patch('requests.post')
    def test_persistent_session_mode(self, mock_post):
        """Test persistent session mode."""
        # Mock session creation and API call
        session_response = MagicMock()
        session_response.json.return_value = {'result': 'session_key', 'error': None}
        session_response.raise_for_status.return_value = None
        
        api_response = MagicMock()
        api_response.json.return_value = {'result': [{'sid': '123', 'title': 'Test'}], 'error': None}
        api_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [session_response, api_response, release_response]
        
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass", auto_session=False)
        
        # Connect persistent session
        api.connect()
        assert api.is_connected()
        
        # Make API call - should use existing session
        result = api._make_request("list_surveys", [None])
        assert result == [{'sid': '123', 'title': 'Test'}]
        
        # Disconnect
        api.disconnect()
        assert not api.is_connected()
        
        # Should have made 3 calls total
        assert mock_post.call_count == 3
    
    def test_auto_session_property(self):
        """Test auto_session property and behavior."""
        api_auto = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass", auto_session=True)
        api_manual = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass", auto_session=False)
        
        assert api_auto.auto_session is True
        assert api_manual.auto_session is False
    
    def test_session_key_property(self):
        """Test session_key property delegates to session manager."""
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        
        # Initially no session
        assert api.session_key is None
        
        # Mock session manager having a key
        api._session_manager._session_key = "test_key"
        assert api.session_key == "test_key"
    
    def test_is_connected_delegates_to_session_manager(self):
        """Test is_connected delegates to session manager."""
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        
        assert not api.is_connected()
        
        # Mock session manager being connected
        api._session_manager._session_key = "test_key"
        assert api.is_connected()
    
    def test_legacy_method_compatibility(self):
        """Test legacy methods still work for backward compatibility."""
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        
        # Mock the session manager methods
        api._session_manager.create_session = MagicMock(return_value="test_key")
        api._session_manager.release_session = MagicMock()
        
        # Test legacy methods
        key = api._get_session_key()
        assert key == "test_key"
        api._session_manager.create_session.assert_called_once()
        
        api._release_session_key()
        api._session_manager.release_session.assert_called_once()


class TestAuthenticationIntegration:
    """Integration tests for authentication with managers."""
    
    @patch('requests.post')
    def test_survey_manager_with_auto_session(self, mock_post):
        """Test survey manager works with auto-session."""
        # Mock session creation, API call, and release
        session_response = MagicMock()
        session_response.json.return_value = {'result': 'session_key', 'error': None}
        session_response.raise_for_status.return_value = None
        
        api_response = MagicMock()
        api_response.json.return_value = {'result': [{'sid': '123', 'surveyls_title': 'Test Survey'}], 'error': None}
        api_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [session_response, api_response, release_response]
        
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass", auto_session=True)
        
        # Call survey manager method
        surveys = api.surveys.list_surveys()
        
        assert len(surveys) == 1
        assert surveys[0]['sid'] == '123'
        assert surveys[0]['surveyls_title'] == 'Test Survey'
        
        # Verify session was created and released
        assert mock_post.call_count == 3
    
    @patch('requests.post')
    def test_multiple_calls_with_persistent_session(self, mock_post):
        """Test multiple API calls with persistent session."""
        # Mock session creation
        session_response = MagicMock()
        session_response.json.return_value = {'result': 'session_key', 'error': None}
        session_response.raise_for_status.return_value = None
        
        # Mock two API calls
        api_response1 = MagicMock()
        api_response1.json.return_value = {'result': [{'sid': '123'}], 'error': None}
        api_response1.raise_for_status.return_value = None
        
        api_response2 = MagicMock()
        api_response2.json.return_value = {'result': {'surveyls_title': 'Test'}, 'error': None}
        api_response2.raise_for_status.return_value = None
        
        # Mock session release
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [session_response, api_response1, api_response2, release_response]
        
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass", auto_session=False)
        
        # Connect persistent session
        api.connect()
        
        # Make two API calls
        surveys = api.surveys.list_surveys()
        props = api.surveys.get_survey_properties("123")
        
        # Disconnect
        api.disconnect()
        
        assert len(surveys) == 1
        assert props['surveyls_title'] == 'Test'
        
        # Should only create session once
        assert mock_post.call_count == 4  # create + 2 API calls + release 