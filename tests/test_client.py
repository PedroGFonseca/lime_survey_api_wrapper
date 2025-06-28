"""Tests for the LimeSurvey API client."""

import os
import pytest
import warnings
from unittest.mock import patch, MagicMock

from lime_survey_analyzer import LimeSurveyClient
from lime_survey_analyzer.managers.base import requires_session
from lime_survey_analyzer.exceptions import LimeSurveyError


class TestLimeSurveyClient:
    """Test the main LimeSurveyClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.api = LimeSurveyClient(
            url='https://test.com/admin/remotecontrol',
            username='testuser',
            password='testpass'
        )
    
    def test_initialization(self):
        """Test client initialization."""
        assert self.api.url == 'https://test.com/admin/remotecontrol'
        assert self.api.username == 'testuser'
        assert self.api.password == 'testpass'
        assert self.api.auto_session is True  # Default
        assert self.api.debug is False  # Default
    
    def test_initialization_with_options(self):
        """Test client initialization with custom options."""
        api = LimeSurveyClient(
            url='https://test.com/admin/remotecontrol',
            username='testuser',
            password='testpass',
            auto_session=False,
            debug=True
        )
        assert api.auto_session is False
        assert api.debug is True
    
    def test_manager_access(self):
        """Test that managers are accessible."""
        assert hasattr(self.api, 'surveys')
        assert hasattr(self.api, 'questions')
        assert hasattr(self.api, 'responses')
        assert hasattr(self.api, 'participants')
    
    @patch('lime_survey_analyzer.client.SessionManager')
    def test_connect_disconnect(self, mock_session_manager_class):
        """Test connection and disconnection."""
        # Create a mock session manager instance
        mock_session_manager = MagicMock()
        mock_session_manager_class.return_value = mock_session_manager
        
        # Create a new API instance with the mocked session manager
        api = LimeSurveyClient("https://test.com/admin/remotecontrol", "user", "pass")
        
        # Test connection
        api.connect()
        mock_session_manager.connect_persistent.assert_called_once()
        
        # Test disconnection
        api.disconnect()
        mock_session_manager.disconnect_persistent.assert_called_once()
    
    def test_is_connected(self):
        """Test connection status checking."""
        # Initially not connected
        assert not self.api.is_connected()
        
        # Mock connection by setting session key via session manager
        self.api._session_manager._session_key = "test_session_key"
        assert self.api.is_connected()
        
        # Mock disconnection
        self.api._session_manager._session_key = None
        assert not self.api.is_connected()
    
    def test_session_property(self):
        """Test session property access."""
        # Test session_key property
        assert self.api.session_key is None
        
        # Mock session
        self.api._session_manager._session_key = "test_session"
        assert self.api.session_key == "test_session"


class TestLimeSurveyDirectAPI:
    """Test cases for LimeSurveyDirectAPI class."""

    def test_init_valid_url(self):
        """Test initialization with valid URL."""
        api = LimeSurveyClient("https://example.com/admin/remotecontrol", "user", "pass")
        assert api.url == "https://example.com/admin/remotecontrol"
        assert api.username == "user"
        assert api._password == "pass"
        assert api.session_key is None
        assert api.debug is False

    def test_init_invalid_url(self):
        """Test initialization with invalid URL."""
        with pytest.raises(LimeSurveyError, match="URL must start with http"):
            LimeSurveyClient("invalid-url", "user", "pass")

    def test_init_http_warning(self):
        """Test warning for HTTP URLs."""
        with pytest.warns(UserWarning, match="Using HTTP instead of HTTPS"):
            LimeSurveyClient("http://example.com/admin/remotecontrol", "user", "pass")

    def test_init_localhost_no_warning(self):
        """Test no warning for localhost HTTP URLs."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            LimeSurveyClient("http://localhost/admin/remotecontrol", "user", "pass")
            # Filter for only our specific warning
            http_warnings = [warning for warning in w if "HTTP instead of HTTPS" in str(warning.message)]
            assert len(http_warnings) == 0

    def test_from_config_success(self, tmp_path):
        """Test creating client from config file."""
        config_file = tmp_path / "test_config.ini"
        config_file.write_text("""
[limesurvey]
url = https://example.com/admin/remotecontrol
username = testuser
password = testpass
""")
        
        api = LimeSurveyClient.from_config(config_file)
        assert api.url == 'https://example.com/admin/remotecontrol'
        assert api.username == 'testuser'
        assert api._password == 'testpass'

    def test_from_config_missing_file(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(LimeSurveyError):
            LimeSurveyClient.from_config("nonexistent.ini")

    def test_from_config_missing_section(self, tmp_path):
        """Test error when config section is missing."""
        config_file = tmp_path / "test_config.ini"
        config_file.write_text("[other_section]\nkey = value\n")
        
        with pytest.raises(LimeSurveyError, match="must contain \\[limesurvey\\] section"):
            LimeSurveyClient.from_config(config_file)

    def test_from_config_missing_keys(self, tmp_path):
        """Test error when config keys are missing."""
        config_file = tmp_path / "test_config.ini"
        config_file.write_text("""
[limesurvey]
url = https://example.com/admin/remotecontrol
username = testuser
# password missing
""")
        
        with pytest.raises(LimeSurveyError, match="Missing required configuration keys"):
            LimeSurveyClient.from_config(config_file)

    @patch('requests.post')
    def test_make_request_success(self, mock_post):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'test_result', 'error': None}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test with auto_session=False to avoid extra session calls
        api = LimeSurveyClient("https://example.com/admin/remotecontrol", "user", "pass", auto_session=False)
        api._session_manager._session_key = "test_session"  # Set session via session manager for this test
        
        result = api._make_request("test_method", ["param1", "param2"])
        
        assert result == 'test_result'
        # Should only make one call when session exists and auto_session=False
        mock_post.assert_called_once_with(
            'https://example.com/admin/remotecontrol',
            json={'method': 'test_method', 'params': ['param1', 'param2'], 'id': 1},
            headers={'Content-Type': 'application/json'},
            timeout=30
        )

    @patch('requests.post')
    def test_make_request_api_error(self, mock_post):
        """Test API request with error response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': None, 'error': 'API Error Message'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Test with auto_session=False to avoid extra session calls
        api = LimeSurveyClient("https://example.com/admin/remotecontrol", "user", "pass", auto_session=False)
        api._session_manager._session_key = "test_session"  # Set session via session manager for this test
        
        with pytest.raises(Exception, match="API Error in test_method: API Error Message"):
            api._make_request("test_method", ["param1"])

    @patch('requests.post')
    def test_make_request_auto_session(self, mock_post):
        """Test API request with auto-session enabled."""
        # Mock successful session creation and API call
        session_response = MagicMock()
        session_response.json.return_value = {'result': 'session_key', 'error': None}
        session_response.raise_for_status.return_value = None
        
        api_response = MagicMock()
        api_response.json.return_value = {'result': 'test_result', 'error': None}
        api_response.raise_for_status.return_value = None
        
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        # Return different responses for different calls
        mock_post.side_effect = [session_response, api_response, release_response]

        api = LimeSurveyClient("https://example.com/admin/remotecontrol", "user", "pass", auto_session=True)
        result = api._make_request("test_method", ["param1"])
        
        assert result == 'test_result'
        # Should make 3 calls: get_session_key, test_method, release_session_key
        assert mock_post.call_count == 3

    def test_build_params(self):
        """Test parameter building with optional parameters."""
        api = LimeSurveyClient("https://example.com/admin/remotecontrol", "user", "pass")
        
        # Test with no optional params
        result = api._build_params(["base1", "base2"])
        assert result == ["base1", "base2"]
        
        # Test with some optional params
        result = api._build_params(["base1"], opt1="value1", opt2=None, opt3="value3")
        assert result == ["base1", "value1", "value3"]

    @patch('requests.post')
    def test_connect_disconnect(self, mock_post):
        """Test persistent session connect/disconnect functionality."""
        # Mock session creation response
        session_response = MagicMock()
        session_response.json.return_value = {'result': 'session_key', 'error': None}
        session_response.raise_for_status.return_value = None
        
        # Mock session release response
        release_response = MagicMock()
        release_response.raise_for_status.return_value = None
        
        mock_post.side_effect = [session_response, release_response]

        api = LimeSurveyClient("https://example.com/admin/remotecontrol", "user", "pass", auto_session=False)
        
        # Test connect
        assert not api.is_connected()
        api.connect()
        assert api.is_connected()
        assert api.session_key == "session_key"
        assert api._persistent_session is True
        
        # Test disconnect
        api.disconnect()
        assert not api.is_connected()
        assert api.session_key is None
        assert api._persistent_session is False

    def test_is_connected(self):
        """Test is_connected method."""
        api = LimeSurveyClient("https://example.com/admin/remotecontrol", "user", "pass", auto_session=False)
        
        assert not api.is_connected()
        
        api._session_manager._session_key = "test_session"
        assert api.is_connected()
        
        api._session_manager._session_key = None
        assert not api.is_connected()


class TestRequiresSessionDecorator:
    """Test cases for the requires_session decorator."""

    def test_requires_session_with_session(self):
        """Test decorator when session exists."""
        class MockClient:
            def __init__(self):
                self.session_key = "test_session"
                self.auto_session = True
        
        class MockManager:
            def __init__(self):
                self._client = MockClient()
            
            @requires_session
            def test_method(self):
                return "success"
        
        manager = MockManager()
        result = manager.test_method()
        assert result == "success"

    def test_requires_session_without_session(self):
        """Test decorator when session doesn't exist."""
        class MockClient:
            def __init__(self):
                self.session_key = None
                self.auto_session = False
                self.get_session_called = False
            
            def _get_session_key(self):
                self.session_key = "new_session"
                self.get_session_called = True
        
        class MockManager:
            def __init__(self):
                self._client = MockClient()
            
            @requires_session
            def test_method(self):
                return "success"
        
        manager = MockManager()
        with pytest.raises(Exception, match="No active session"):
            manager.test_method()

    def test_requires_session_auto_session_enabled(self):
        """Test decorator when auto_session is enabled."""
        class MockClient:
            def __init__(self):
                self.session_key = None
                self.auto_session = True
        
        class MockManager:
            def __init__(self):
                self._client = MockClient()
            
            @requires_session
            def test_method(self):
                return "success"
        
        manager = MockManager()
        result = manager.test_method()
        assert result == "success"


class TestQuestionManagerConditions:
    """Test cases for Question Manager condition methods."""
    
    def test_list_conditions_all_survey(self):
        """Test listing all conditions in a survey."""
        from lime_survey_analyzer.managers.question import QuestionManager
        
        # Mock client
        mock_client = MagicMock()
        mock_client.session_key = "test_session"
        
        # Mock API response
        expected_conditions = [
            {
                'qid': '123',
                'cid': '1',
                'cfieldname': 'question_1',
                'method': '==',
                'value': 'Y'
            },
            {
                'qid': '124', 
                'cid': '2',
                'cfieldname': 'question_2',
                'method': '>',
                'value': '18'
            }
        ]
        
        manager = QuestionManager(mock_client)
        
        with patch.object(manager, '_make_request') as mock_request, \
             patch.object(manager, '_build_params') as mock_build_params:
            
            mock_request.return_value = expected_conditions
            mock_build_params.return_value = ["test_session", "987654"]
            
            result = manager.list_conditions("987654")
            
            # Verify correct _build_params call
            mock_build_params.assert_called_once_with(
                ["test_session", "987654"],
                question_id=None
            )
            # Verify _make_request call with built params
            mock_request.assert_called_once_with("list_conditions", ["test_session", "987654"])
            assert result == expected_conditions
            
    def test_list_conditions_specific_question(self):
        """Test listing conditions for a specific question."""
        from lime_survey_analyzer.managers.question import QuestionManager
        
        mock_client = MagicMock()
        mock_client.session_key = "test_session"
        
        expected_conditions = [
            {
                'qid': '123',
                'cid': '1', 
                'cfieldname': 'question_1',
                'method': '==',
                'value': 'Y'
            }
        ]
        
        manager = QuestionManager(mock_client)
        
        with patch.object(manager, '_make_request') as mock_request, \
             patch.object(manager, '_build_params') as mock_build_params:
            
            mock_request.return_value = expected_conditions
            mock_build_params.return_value = ["test_session", "987654", "123"]
            
            result = manager.list_conditions("987654", "123")
            
            # Verify correct _build_params call with question_id
            mock_build_params.assert_called_once_with(
                ["test_session", "987654"],
                question_id="123"
            )
            # Verify _make_request call with built params
            mock_request.assert_called_once_with("list_conditions", ["test_session", "987654", "123"])
            assert result == expected_conditions
            
    def test_get_conditions(self):
        """Test getting detailed conditions for a specific question."""
        from lime_survey_analyzer.managers.question import QuestionManager
        
        mock_client = MagicMock() 
        mock_client.session_key = "test_session"
        
        expected_conditions = [
            {
                'qid': '123',
                'cid': '1',
                'cfieldname': 'survey_123_question_1',
                'method': '==',
                'value': 'Y',
                'scenario': '1'
            },
            {
                'qid': '123',
                'cid': '2', 
                'cfieldname': 'survey_123_question_2',
                'method': '>',
                'value': '18',
                'scenario': '1'
            }
        ]
        
        manager = QuestionManager(mock_client)
        
        with patch.object(manager, '_make_request') as mock_request, \
             patch.object(manager, '_build_params') as mock_build_params:
            
            mock_request.return_value = expected_conditions
            mock_build_params.return_value = ["test_session", "987654", "123"]
            
            result = manager.get_conditions("987654", "123")
            
            # Verify correct _build_params call
            mock_build_params.assert_called_once_with(["test_session", "987654", "123"])
            # Verify _make_request call with built params
            mock_request.assert_called_once_with("get_conditions", ["test_session", "987654", "123"])
            assert result == expected_conditions
            
    def test_conditions_empty_response(self):
        """Test condition methods with empty responses."""
        from lime_survey_analyzer.managers.question import QuestionManager
        
        mock_client = MagicMock()
        mock_client.session_key = "test_session"
        
        manager = QuestionManager(mock_client)
        
        with patch.object(manager, '_make_request') as mock_request:
            mock_request.return_value = []
            
            # Test list_conditions
            result = manager.list_conditions("987654")
            assert result == []
            
            # Test get_conditions
            result = manager.get_conditions("987654", "123")
            assert result == [] 