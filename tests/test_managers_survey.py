"""
Comprehensive tests for SurveyManager.

Tests all survey management operations including listing surveys, getting properties,
summaries, fieldmaps, and handling various response formats and error conditions.
"""

import pytest
from unittest.mock import Mock, patch
from src.lime_survey_analyzer.managers.survey import SurveyManager


class TestSurveyManagerCore:
    """Test core SurveyManager functionality"""

    @pytest.fixture
    def survey_manager(self):
        """Create SurveyManager with mocked client"""
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return SurveyManager(mock_client)

    def test_list_surveys_success(self, survey_manager):
        """Test successful survey listing"""
        expected_surveys = [
            {
                'sid': '123456',
                'surveyls_title': 'Customer Satisfaction',
                'active': 'Y',
                'language': 'en'
            },
            {
                'sid': '789012',
                'surveyls_title': 'Product Feedback',
                'active': 'N',
                'language': 'es'
            }
        ]
        survey_manager._make_request = Mock(return_value=expected_surveys)
        
        result = survey_manager.list_surveys()
        
        assert result == expected_surveys
        assert len(result) == 2
        survey_manager._make_request.assert_called_once()

    def test_list_surveys_with_username(self, survey_manager):
        """Test survey listing with specific username"""
        survey_manager._make_request = Mock(return_value=[])
        
        survey_manager.list_surveys(username="testuser")
        
        # Verify username parameter is passed
        call_args = survey_manager._make_request.call_args
        assert 'sUsername' in str(call_args)

    def test_list_surveys_no_surveys_found(self, survey_manager):
        """Test handling when no surveys are found"""
        # Mock API response when no surveys exist
        error_response = {'status': 'No surveys found'}
        survey_manager._make_request = Mock(return_value=error_response)
        
        result = survey_manager.list_surveys()
        
        # Should return empty list, not raise exception
        assert result == []

    def test_list_surveys_no_permission(self, survey_manager):
        """Test handling when user has no permission"""
        # Mock API response for permission denied
        error_response = {'status': 'No permission to access surveys'}
        survey_manager._make_request = Mock(return_value=error_response)
        
        result = survey_manager.list_surveys()
        
        # Should return empty list for permission issues
        assert result == []

    def test_list_surveys_api_error(self, survey_manager):
        """Test handling of genuine API errors"""
        # Mock unexpected API error
        error_response = {'status': 'Database connection failed'}
        survey_manager._make_request = Mock(return_value=error_response)
        
        with pytest.raises(Exception) as exc_info:
            survey_manager.list_surveys()
        
        assert "Database connection failed" in str(exc_info.value)

    def test_list_surveys_unexpected_format(self, survey_manager):
        """Test handling of unexpected response format"""
        # Mock unexpected response format (neither list nor dict with status)
        unexpected_response = "Unexpected string response"
        survey_manager._make_request = Mock(return_value=unexpected_response)
        
        with pytest.raises(Exception) as exc_info:
            survey_manager.list_surveys()
        
        assert "Unexpected response format" in str(exc_info.value)

    def test_get_survey_properties_success(self, survey_manager):
        """Test successful survey properties retrieval"""
        expected_props = {
            'sid': '123456',
            'surveyls_title': 'Customer Survey',
            'surveyls_description': 'Annual customer satisfaction survey',
            'language': 'en',
            'active': 'Y',
            'anonymized': 'N',
            'format': 'G',
            'template': 'default',
            'assessments': 'N',
            'savetimings': 'Y',
            'datestamp': 'Y'
        }
        survey_manager._make_request = Mock(return_value=expected_props)
        
        result = survey_manager.get_survey_properties("123456")
        
        assert result == expected_props
        assert result['surveyls_title'] == 'Customer Survey'
        survey_manager._make_request.assert_called_once()

    def test_get_survey_properties_with_language(self, survey_manager):
        """Test survey properties with language parameter"""
        survey_manager._make_request = Mock(return_value={})
        
        survey_manager.get_survey_properties("123456", language="fr")
        
        # Verify language parameter is passed
        call_args = survey_manager._make_request.call_args
        assert 'language' in str(call_args)

    def test_get_summary_all_stats(self, survey_manager):
        """Test getting complete survey summary"""
        expected_summary = {
            'completed': '150',
            'incomplete': '25',
            'total': '175',
            'token_count': '200',
            'token_completed': '150',
            'token_incomplete': '25',
            'token_invalid': '25'
        }
        survey_manager._make_request = Mock(return_value=expected_summary)
        
        result = survey_manager.get_summary("123456")
        
        assert result == expected_summary
        assert result['completed'] == '150'
        assert result['total'] == '175'

    def test_get_summary_specific_stat(self, survey_manager):
        """Test getting specific summary statistic"""
        survey_manager._make_request = Mock(return_value={'completed': '150'})
        
        survey_manager.get_summary("123456", stat_name="completed")
        
        # Verify specific stat parameter is passed
        call_args = survey_manager._make_request.call_args[0][1]
        assert "completed" in call_args

    def test_get_fieldmap_success(self, survey_manager):
        """Test successful fieldmap retrieval"""
        expected_fieldmap = {
            'id': {
                'fieldname': 'id',
                'qid': '',
                'type': 'id',
                'title': 'Response ID'
            },
            'Q1': {
                'fieldname': 'Q1',
                'qid': '123',
                'type': 'L',
                'title': 'Q1',
                'question': 'What is your favorite color?',
                'group_name': 'Demographics',
                'group_order': '1'
            },
            'Q2SQ1': {
                'fieldname': 'Q2SQ1',
                'qid': '124',
                'type': 'M',
                'title': 'Q2[SQ1]',
                'question': 'Checkbox option 1',
                'group_name': 'Preferences'
            }
        }
        survey_manager._make_request = Mock(return_value=expected_fieldmap)
        
        result = survey_manager.get_fieldmap("123456")
        
        assert result == expected_fieldmap
        assert 'Q1' in result
        assert result['Q1']['qid'] == '123'
        assert result['Q1']['type'] == 'L'

    def test_get_fieldmap_with_language(self, survey_manager):
        """Test fieldmap with language parameter"""
        survey_manager._make_request = Mock(return_value={})
        
        survey_manager.get_fieldmap("123456", language="de")
        
        # Verify language parameter is passed
        call_args = survey_manager._make_request.call_args[0][1]
        assert "de" in call_args


class TestSurveyManagerErrorHandling:
    """Test error handling and edge cases"""

    @pytest.fixture
    def survey_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return SurveyManager(mock_client)

    def test_list_surveys_empty_response(self, survey_manager):
        """Test handling empty survey list"""
        survey_manager._make_request = Mock(return_value=[])
        
        result = survey_manager.list_surveys()
        
        assert result == []

    def test_get_survey_properties_nonexistent_survey(self, survey_manager):
        """Test getting properties for non-existent survey"""
        # Mock API error for non-existent survey
        survey_manager._make_request = Mock(side_effect=Exception("Survey not found"))
        
        with pytest.raises(Exception) as exc_info:
            survey_manager.get_survey_properties("999999")
        
        assert "Survey not found" in str(exc_info.value)

    def test_get_summary_invalid_stat(self, survey_manager):
        """Test summary with invalid statistic name"""
        # Mock API handling invalid stat name
        error_response = {'status': 'Invalid statistic name'}
        survey_manager._make_request = Mock(return_value=error_response)
        
        result = survey_manager.get_summary("123456", stat_name="invalid_stat")
        
        # API may return error in response
        assert 'status' in result

    def test_get_fieldmap_inactive_survey(self, survey_manager):
        """Test fieldmap for inactive survey"""
        # Mock API error for inactive survey
        survey_manager._make_request = Mock(side_effect=Exception("Survey is not active"))
        
        with pytest.raises(Exception) as exc_info:
            survey_manager.get_fieldmap("123456")
        
        assert "Survey is not active" in str(exc_info.value)


class TestSurveyManagerDataProcessing:
    """Test data processing and formatting"""

    @pytest.fixture
    def survey_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return SurveyManager(mock_client)

    def test_list_surveys_large_dataset(self, survey_manager):
        """Test handling large number of surveys"""
        # Mock large survey list
        large_survey_list = []
        for i in range(100):
            large_survey_list.append({
                'sid': f'12345{i:02d}',
                'surveyls_title': f'Survey {i}',
                'active': 'Y' if i % 2 == 0 else 'N',
                'language': 'en'
            })
        
        survey_manager._make_request = Mock(return_value=large_survey_list)
        
        result = survey_manager.list_surveys()
        
        assert len(result) == 100
        assert all('sid' in survey for survey in result)

    def test_get_survey_properties_multilingual(self, survey_manager):
        """Test properties for multilingual survey"""
        multilingual_props = {
            'sid': '123456',
            'surveyls_title': 'Enquête Client',
            'language': 'fr',
            'additional_languages': 'en,es,de',
            'active': 'Y'
        }
        survey_manager._make_request = Mock(return_value=multilingual_props)
        
        result = survey_manager.get_survey_properties("123456", language="fr")
        
        assert result['language'] == 'fr'
        assert 'additional_languages' in result

    def test_get_summary_detailed_stats(self, survey_manager):
        """Test detailed summary statistics"""
        detailed_summary = {
            'completed': '1250',
            'incomplete': '187',
            'total': '1437',
            'token_count': '2000',
            'token_completed': '1250',
            'token_incomplete': '187',
            'token_invalid': '563',
            'token_sent': '2000',
            'token_opted_out': '15',
            'token_bounced': '12'
        }
        survey_manager._make_request = Mock(return_value=detailed_summary)
        
        result = survey_manager.get_summary("123456")
        
        # Verify all expected statistics are present
        expected_keys = ['completed', 'incomplete', 'total', 'token_count']
        for key in expected_keys:
            assert key in result
        
        # Test numeric values can be extracted
        assert int(result['completed']) > 0
        assert int(result['total']) > int(result['completed'])

    def test_get_fieldmap_complex_structure(self, survey_manager):
        """Test fieldmap with complex question structure"""
        complex_fieldmap = {
            # Simple question
            'Q1': {
                'fieldname': 'Q1',
                'qid': '123',
                'type': 'L',
                'title': 'Q1',
                'question': 'Simple list question'
            },
            # Multiple choice with subquestions
            'Q2SQ001': {
                'fieldname': 'Q2SQ001',
                'qid': '124',
                'type': 'M',
                'title': 'Q2[SQ001]',
                'question': 'Option 1',
                'parent_qid': '124'
            },
            # Array question
            'Q3SQ001_1': {
                'fieldname': 'Q3SQ001_1',
                'qid': '125',
                'type': 'F',
                'title': 'Q3[SQ001][1]',
                'question': 'Array subquestion',
                'scale_id': '1'
            },
            # Metadata fields
            'submitdate': {
                'fieldname': 'submitdate',
                'qid': '',
                'type': 'submitdate',
                'title': 'Date submitted'
            },
            'lastpage': {
                'fieldname': 'lastpage',
                'qid': '',
                'type': 'lastpage',
                'title': 'Last page'
            }
        }
        survey_manager._make_request = Mock(return_value=complex_fieldmap)
        
        result = survey_manager.get_fieldmap("123456")
        
        # Verify different question types are present
        assert 'Q1' in result  # Simple question
        assert 'Q2SQ001' in result  # Multiple choice subquestion
        assert 'Q3SQ001_1' in result  # Array question
        assert 'submitdate' in result  # Metadata
        
        # Verify structure is preserved
        assert result['Q2SQ001']['parent_qid'] == '124'
        assert result['Q3SQ001_1']['scale_id'] == '1'

    def test_get_fieldmap_empty_survey(self, survey_manager):
        """Test fieldmap for survey with no questions"""
        # Mock fieldmap with only metadata fields
        metadata_only_fieldmap = {
            'id': {'fieldname': 'id', 'type': 'id'},
            'submitdate': {'fieldname': 'submitdate', 'type': 'submitdate'},
            'lastpage': {'fieldname': 'lastpage', 'type': 'lastpage'}
        }
        survey_manager._make_request = Mock(return_value=metadata_only_fieldmap)
        
        result = survey_manager.get_fieldmap("123456")
        
        # Should still return metadata fields
        assert 'id' in result
        assert 'submitdate' in result
        assert len(result) == 3


class TestSurveyManagerIntegration:
    """Test integration scenarios and workflows"""

    @pytest.fixture
    def survey_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return SurveyManager(mock_client)

    def test_survey_workflow_complete(self, survey_manager):
        """Test complete survey information gathering workflow"""
        # Mock survey list
        surveys = [{'sid': '123456', 'surveyls_title': 'Test Survey'}]
        
        # Mock survey properties
        properties = {
            'sid': '123456',
            'surveyls_title': 'Test Survey',
            'active': 'Y',
            'language': 'en'
        }
        
        # Mock summary
        summary = {
            'completed': '100',
            'incomplete': '25',
            'total': '125'
        }
        
        # Mock fieldmap
        fieldmap = {
            'Q1': {'qid': '123', 'type': 'L', 'question': 'Test question'}
        }
        
        # Set up method returns
        survey_manager._make_request = Mock(side_effect=[surveys, properties, summary, fieldmap])
        
        # Execute workflow
        survey_list = survey_manager.list_surveys()
        survey_id = survey_list[0]['sid']
        props = survey_manager.get_survey_properties(survey_id)
        stats = survey_manager.get_summary(survey_id)
        fields = survey_manager.get_fieldmap(survey_id)
        
        # Verify workflow completed successfully
        assert survey_id == '123456'
        assert props['surveyls_title'] == 'Test Survey'
        assert stats['completed'] == '100'
        assert 'Q1' in fields
        
        # Verify all API calls were made
        assert survey_manager._make_request.call_count == 4

    def test_parameter_building_consistency(self, survey_manager):
        """Test that parameter building is consistent across methods"""
        survey_manager._make_request = Mock(return_value={})
        
        # Test methods with similar parameter patterns
        test_cases = [
            ('list_surveys', []),
            ('get_survey_properties', ['123456']),
            ('get_summary', ['123456']),
            ('get_fieldmap', ['123456'])
        ]
        
        for method_name, args in test_cases:
            method = getattr(survey_manager, method_name)
            method(*args)
            
            # Verify session key is always first parameter
            call_args = survey_manager._make_request.call_args[0][1]
            assert call_args[0] == "test_session"
            
            survey_manager._make_request.reset_mock() 