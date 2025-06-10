"""
Tests for authentication functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from lime_survey_analyzer import LimeSurveyClient
from lime_survey_analyzer.exceptions import ConfigurationError


class TestAuthentication:
    """Test file-based authentication methods."""
    
    def test_from_config_success(self):
        """Test successful authentication from config file."""
        config_content = """[limesurvey]
url = https://test.com/admin/remotecontrol
username = testuser
password = testpass
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_content)):
                api = LimeSurveyClient.from_config('test.ini')
                assert api.url == 'https://test.com/admin/remotecontrol'
                assert api.username == 'testuser'
                assert api.password == 'testpass'
    
    def test_from_config_default_path(self):
        """Test authentication with default config path."""
        config_content = """[limesurvey]
url = https://test.com/admin/remotecontrol
username = testuser
password = testpass
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_content)):
                api = LimeSurveyClient.from_config()  # Should use default path
                assert api.url == 'https://test.com/admin/remotecontrol'
                assert api.username == 'testuser'
                assert api.password == 'testpass'
    
    def test_from_config_missing_file(self):
        """Test authentication failure when config file is missing."""
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(ConfigurationError, match="Configuration file not found"):
                LimeSurveyClient.from_config('nonexistent.ini')
    
    def test_from_config_missing_section(self):
        """Test authentication failure when config section is missing."""
        config_content = """[other]
url = https://test.com
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_content)):
                with pytest.raises(ConfigurationError, match="must contain \\[limesurvey\\] section"):
                    LimeSurveyClient.from_config('test.ini')
    
    def test_from_config_missing_keys(self):
        """Test authentication failure when required keys are missing."""
        config_content = """[limesurvey]
url = https://test.com/admin/remotecontrol
username = testuser
# password missing
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_content)):
                with pytest.raises(ConfigurationError, match="Missing required configuration keys"):
                    LimeSurveyClient.from_config('test.ini')
    
    def test_from_config_invalid_file(self):
        """Test authentication failure when config file is invalid."""
        config_content = """invalid config file content
not a valid ini format
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_content)):
                with pytest.raises(ConfigurationError, match="Failed to read configuration file"):
                    LimeSurveyClient.from_config('test.ini')
    
    def test_from_config_with_debug(self):
        """Test authentication with debug mode enabled."""
        config_content = """[limesurvey]
url = https://test.com/admin/remotecontrol
username = testuser
password = testpass
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_content)):
                api = LimeSurveyClient.from_config('test.ini', debug=True)
                assert api.debug is True
    
    def test_from_config_with_auto_session_false(self):
        """Test authentication with auto_session disabled."""
        config_content = """[limesurvey]
url = https://test.com/admin/remotecontrol
username = testuser
password = testpass
"""
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=config_content)):
                api = LimeSurveyClient.from_config('test.ini', auto_session=False)
                assert api.auto_session is False
    
    def test_manual_initialization(self):
        """Test manual initialization with credentials (discouraged but supported)."""
        api = LimeSurveyClient(
            url='https://test.com/admin/remotecontrol',
            username='testuser',
            password='testpass'
        )
        assert api.url == 'https://test.com/admin/remotecontrol'
        assert api.username == 'testuser'
        assert api.password == 'testpass'
    
    def test_url_validation(self):
        """Test URL validation during initialization."""
        with pytest.raises(ConfigurationError, match="URL must start with http"):
            LimeSurveyClient(
                url='invalid-url',
                username='testuser',
                password='testpass'
            )
    
    def test_http_warning(self):
        """Test warning for non-HTTPS URLs."""
        with pytest.warns(UserWarning, match="Using HTTP instead of HTTPS"):
            LimeSurveyClient(
                url='http://remote-server.com/admin/remotecontrol',
                username='testuser',
                password='testpass'
            )
    
    def test_localhost_http_no_warning(self):
        """Test no warning for localhost HTTP URLs."""
        with patch('warnings.warn') as mock_warn:
            LimeSurveyClient(
                url='http://localhost/admin/remotecontrol',
                username='testuser',
                password='testpass'
            )
            mock_warn.assert_not_called()
    
    def test_real_config_file_integration(self):
        """Test with a real temporary config file."""
        config_content = """[limesurvey]
url = https://test.com/admin/remotecontrol
username = testuser
password = testpass
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_content)
            temp_path = f.name
        
        try:
            api = LimeSurveyClient.from_config(temp_path)
            assert api.url == 'https://test.com/admin/remotecontrol'
            assert api.username == 'testuser'
            assert api.password == 'testpass'
        finally:
            os.unlink(temp_path) 