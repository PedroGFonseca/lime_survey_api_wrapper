"""Tests for the LimeSurvey API client."""

import os
import pytest
import warnings
from unittest.mock import patch, MagicMock

from lime_survey_analyzer import LimeSurveyDirectAPI
from lime_survey_analyzer.managers.base import requires_session


class TestLimeSurveyDirectAPI:
    """Test cases for LimeSurveyDirectAPI class."""

    def test_init_valid_url(self):
        """Test initialization with valid URL."""
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        assert api.url == "https://example.com/admin/remotecontrol"
        assert api.username == "user"
        assert api._password == "pass"
        assert api.session_key is None
        assert api.debug is False

    def test_init_invalid_url(self):
        """Test initialization with invalid URL."""
        with pytest.raises(ValueError, match="URL must start with http:// or https://"):
            LimeSurveyDirectAPI("invalid-url", "user", "pass")

    def test_init_http_warning(self):
        """Test warning for HTTP URLs."""
        with pytest.warns(UserWarning, match="Using HTTP instead of HTTPS"):
            LimeSurveyDirectAPI("http://example.com/admin/remotecontrol", "user", "pass")

    def test_init_localhost_no_warning(self):
        """Test no warning for localhost HTTP URLs."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            LimeSurveyDirectAPI("http://localhost/admin/remotecontrol", "user", "pass")
            # Filter for only our specific warning
            http_warnings = [warning for warning in w if "HTTP instead of HTTPS" in str(warning.message)]
            assert len(http_warnings) == 0

    def test_from_env_success(self):
        """Test creating client from environment variables."""
        env_vars = {
            'LIMESURVEY_URL': 'https://example.com/admin/remotecontrol',
            'LIMESURVEY_USERNAME': 'testuser',
            'LIMESURVEY_PASSWORD': 'testpass'
        }
        with patch.dict(os.environ, env_vars):
            api = LimeSurveyDirectAPI.from_env()
            assert api.url == 'https://example.com/admin/remotecontrol'
            assert api.username == 'testuser'
            assert api._password == 'testpass'

    def test_from_env_missing_vars(self):
        """Test error when environment variables are missing."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing required environment variables"):
                LimeSurveyDirectAPI.from_env()

    def test_from_config_success(self, tmp_path):
        """Test creating client from config file."""
        config_file = tmp_path / "test_config.ini"
        config_file.write_text("""
[limesurvey]
url = https://example.com/admin/remotecontrol
username = testuser
password = testpass
""")
        
        api = LimeSurveyDirectAPI.from_config(config_file)
        assert api.url == 'https://example.com/admin/remotecontrol'
        assert api.username == 'testuser'
        assert api._password == 'testpass'

    def test_from_config_missing_file(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            LimeSurveyDirectAPI.from_config("nonexistent.ini")

    def test_from_config_missing_section(self, tmp_path):
        """Test error when config section is missing."""
        config_file = tmp_path / "test_config.ini"
        config_file.write_text("[other_section]\nkey = value\n")
        
        with pytest.raises(ValueError, match="Section 'limesurvey' not found"):
            LimeSurveyDirectAPI.from_config(config_file)

    def test_from_config_missing_keys(self, tmp_path):
        """Test error when config keys are missing."""
        config_file = tmp_path / "test_config.ini"
        config_file.write_text("""
[limesurvey]
url = https://example.com/admin/remotecontrol
username = testuser
# password missing
""")
        
        with pytest.raises(ValueError, match="Missing required config keys"):
            LimeSurveyDirectAPI.from_config(config_file)

    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_from_prompt(self, mock_getpass, mock_input):
        """Test creating client from prompts."""
        mock_input.side_effect = ['https://example.com/admin/remotecontrol', 'testuser']
        mock_getpass.return_value = 'testpass'
        
        api = LimeSurveyDirectAPI.from_prompt()
        assert api.url == 'https://example.com/admin/remotecontrol'
        assert api.username == 'testuser'
        assert api._password == 'testpass'

    @patch('requests.post')
    def test_make_request_success(self, mock_post):
        """Test successful API request."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': 'test_result', 'error': None}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        result = api._make_request("test_method", ["param1", "param2"])
        
        assert result == 'test_result'
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_make_request_api_error(self, mock_post):
        """Test API request with error response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {'result': None, 'error': 'API Error Message'}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        
        with pytest.raises(Exception, match="API Error: API Error Message"):
            api._make_request("test_method", ["param1"])

    def test_build_params(self):
        """Test parameter building with optional parameters."""
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        
        # Test with no optional params
        result = api._build_params(["base1", "base2"])
        assert result == ["base1", "base2"]
        
        # Test with some optional params
        result = api._build_params(["base1"], opt1="value1", opt2=None, opt3="value3")
        assert result == ["base1", "value1", "value3"]

    def test_context_manager(self):
        """Test context manager functionality."""
        api = LimeSurveyDirectAPI("https://example.com/admin/remotecontrol", "user", "pass")
        
        with patch.object(api, '_get_session_key') as mock_get:
            with patch.object(api, '_release_session_key') as mock_release:
                with api:
                    pass
                
                mock_get.assert_called_once()
                mock_release.assert_called_once()


class TestRequiresSessionDecorator:
    """Test cases for the requires_session decorator."""

    def test_requires_session_with_session(self):
        """Test decorator when session exists."""
        class MockClient:
            def __init__(self):
                self.session_key = "test_session"
        
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
        result = manager.test_method()
        assert result == "success"
        assert manager._client.get_session_called
        assert manager._client.session_key == "new_session"


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
        
        with patch.object(manager, '_make_request') as mock_request:
            mock_request.return_value = expected_conditions
            
            result = manager.list_conditions("987654")
            
            # Verify correct API call
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
        
        with patch.object(manager, '_make_request') as mock_request:
            mock_request.return_value = expected_conditions
            
            result = manager.list_conditions("987654", "123")
            
            # Verify correct API call with question_id parameter
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
        
        with patch.object(manager, '_make_request') as mock_request:
            mock_request.return_value = expected_conditions
            
            result = manager.get_conditions("987654", "123")
            
            # Verify correct API call
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