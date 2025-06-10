"""
Comprehensive tests for all Managers based on their actual implementations.

Focus on realistic usage patterns and good coverage of the actual code.
"""

import pytest
from unittest.mock import Mock, patch
import base64
import json
from src.lime_survey_analyzer.managers.question import QuestionManager
from src.lime_survey_analyzer.managers.response import ResponseManager
from src.lime_survey_analyzer.managers.survey import SurveyManager
from src.lime_survey_analyzer.managers.participant import ParticipantManager


class TestQuestionManagerReal:
    """Test QuestionManager with actual method signatures"""

    @pytest.fixture
    def question_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    def test_list_groups_basic(self, question_manager):
        """Test basic group listing"""
        expected_groups = [{'gid': '10', 'group_name': 'Demographics'}]
        question_manager._make_request = Mock(return_value=expected_groups)
        
        result = question_manager.list_groups("123456")
        
        assert result == expected_groups
        question_manager._make_request.assert_called_once()

    def test_list_questions_basic(self, question_manager):
        """Test basic question listing"""
        expected_questions = [{'qid': '123', 'type': 'L', 'title': 'Q1'}]
        question_manager._make_request = Mock(return_value=expected_questions)
        
        result = question_manager.list_questions("123456")
        
        assert result == expected_questions

    def test_get_question_properties_basic(self, question_manager):
        """Test getting question properties"""
        props = {'qid': '123', 'type': 'L', 'title': 'Q1'}
        question_manager._make_request = Mock(return_value=props)
        
        result = question_manager.get_question_properties("123456", "123")
        
        assert result == props

    def test_list_conditions_basic(self, question_manager):
        """Test listing conditions"""
        conditions = [{'cid': '1', 'qid': '123'}]
        question_manager._make_request = Mock(return_value=conditions)
        
        result = question_manager.list_conditions("123456")
        
        assert result == conditions

    def test_get_conditions_basic(self, question_manager):
        """Test getting conditions for question"""
        conditions = [{'cid': '1', 'scenario': '1'}]
        question_manager._make_request = Mock(return_value=conditions)
        
        result = question_manager.get_conditions("123456", "123")
        
        assert result == conditions

    def test_validate_question_types_basic(self, question_manager):
        """Test question validation with actual response structure"""
        mock_questions = [{'qid': '123', 'type': 'L'}]
        question_manager.list_questions = Mock(return_value=mock_questions)
        
        with patch('src.lime_survey_analyzer.managers.question.is_priority_type', return_value=True):
            result = question_manager.validate_question_types("123456")
            
            # Check actual response structure
            assert 'question_types' in result
            assert 'supported_count' in result
            assert 'total_count' in result


class TestResponseManagerReal:
    """Test ResponseManager with actual method signatures"""

    @pytest.fixture
    def response_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ResponseManager(mock_client)

    def test_export_responses_json_basic(self, response_manager):
        """Test JSON response export"""
        json_data = [{"id": "1", "Q1": "A"}]
        json_string = json.dumps(json_data)
        encoded_data = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        
        response_manager._make_request = Mock(return_value=encoded_data)
        
        result = response_manager.export_responses("123456", "json")
        
        assert result == json_data

    def test_export_responses_csv_basic(self, response_manager):
        """Test CSV response export"""
        csv_data = "id,Q1\n1,A\n2,B"
        encoded_data = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
        
        response_manager._make_request = Mock(return_value=encoded_data)
        
        result = response_manager.export_responses("123456", "csv")
        
        assert result == csv_data

    def test_export_responses_by_token_basic(self, response_manager):
        """Test export by token"""
        mock_data = {"data": "token_specific"}
        response_manager._make_request = Mock(return_value=mock_data)
        
        result = response_manager.export_responses_by_token("123456", "json", "ABC123")
        
        assert result == mock_data

    def test_export_statistics_basic(self, response_manager):
        """Test statistics export"""
        stats_data = b"PDF data"
        response_manager._make_request = Mock(return_value=stats_data)
        
        result = response_manager.export_statistics("123456", "pdf")
        
        assert result == stats_data

    def test_get_response_ids_basic(self, response_manager):
        """Test getting response IDs for token"""
        ids = ["101", "102"]
        response_manager._make_request = Mock(return_value=ids)
        
        result = response_manager.get_response_ids("123456", "ABC123")
        
        assert result == ids

    def test_get_response_ids_empty(self, response_manager):
        """Test empty response IDs"""
        response_manager._make_request = Mock(return_value=None)
        
        result = response_manager.get_response_ids("123456", "ABC123")
        
        assert result == []

    def test_get_all_response_ids_list_format(self, response_manager):
        """Test getting all response IDs from list format"""
        mock_responses = [
            {"id": "101", "Q1": "A"},
            {"id": "102", "Q1": "B"}
        ]
        response_manager.export_responses = Mock(return_value=mock_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        assert sorted(result) == ["101", "102"]

    def test_get_all_response_ids_with_responses_key(self, response_manager):
        """Test getting response IDs with nested structure"""
        mock_responses = {
            "responses": [
                {"id": "101", "Q1": "A"},
                {"id": "102", "Q1": "B"}
            ]
        }
        response_manager.export_responses = Mock(return_value=mock_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        assert sorted(result) == ["101", "102"]

    def test_get_all_response_ids_export_failure(self, response_manager):
        """Test handling export failure"""
        response_manager.export_responses = Mock(side_effect=Exception("Failed"))
        
        result = response_manager.get_all_response_ids("123456")
        
        assert result == []

    def test_export_responses_decode_failure(self, response_manager):
        """Test handling decode failure"""
        invalid_data = "not_base64!!!"
        response_manager._make_request = Mock(return_value=invalid_data)
        
        result = response_manager.export_responses("123456", "json")
        
        assert result == invalid_data

    def test_export_responses_non_string_response(self, response_manager):
        """Test handling non-string response"""
        direct_response = {"direct": "data"}
        response_manager._make_request = Mock(return_value=direct_response)
        
        result = response_manager.export_responses("123456", "json")
        
        assert result == direct_response


class TestSurveyManagerReal:
    """Test SurveyManager with actual method signatures"""

    @pytest.fixture
    def survey_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return SurveyManager(mock_client)

    def test_list_surveys_basic(self, survey_manager):
        """Test basic survey listing"""
        surveys = [{'sid': '123456', 'surveyls_title': 'Test Survey'}]
        survey_manager._make_request = Mock(return_value=surveys)
        
        result = survey_manager.list_surveys()
        
        assert result == surveys

    def test_list_surveys_no_surveys_found(self, survey_manager):
        """Test handling no surveys found"""
        error_response = {'status': 'No surveys found'}
        survey_manager._make_request = Mock(return_value=error_response)
        
        result = survey_manager.list_surveys()
        
        assert result == []

    def test_list_surveys_no_permission(self, survey_manager):
        """Test handling no permission"""
        error_response = {'status': 'No permission to access'}
        survey_manager._make_request = Mock(return_value=error_response)
        
        result = survey_manager.list_surveys()
        
        assert result == []

    def test_list_surveys_actual_error(self, survey_manager):
        """Test handling actual API errors"""
        error_response = {'status': 'Database error'}
        survey_manager._make_request = Mock(return_value=error_response)
        
        with pytest.raises(Exception) as exc_info:
            survey_manager.list_surveys()
        
        assert "Database error" in str(exc_info.value)

    def test_list_surveys_unexpected_format(self, survey_manager):
        """Test handling unexpected response format"""
        unexpected_response = "string response"
        survey_manager._make_request = Mock(return_value=unexpected_response)
        
        with pytest.raises(Exception) as exc_info:
            survey_manager.list_surveys()
        
        assert "Unexpected response format" in str(exc_info.value)

    def test_get_survey_properties_basic(self, survey_manager):
        """Test getting survey properties"""
        props = {'sid': '123456', 'surveyls_title': 'Test Survey', 'active': 'Y'}
        survey_manager._make_request = Mock(return_value=props)
        
        result = survey_manager.get_survey_properties("123456")
        
        assert result == props

    def test_get_summary_basic(self, survey_manager):
        """Test getting survey summary"""
        summary = {'completed': '100', 'incomplete': '25', 'total': '125'}
        survey_manager._make_request = Mock(return_value=summary)
        
        result = survey_manager.get_summary("123456")
        
        assert result == summary

    def test_get_summary_specific_stat(self, survey_manager):
        """Test getting specific summary statistic"""
        survey_manager._make_request = Mock(return_value={'completed': '100'})
        
        result = survey_manager.get_summary("123456", "completed")
        
        assert result == {'completed': '100'}

    def test_get_fieldmap_basic(self, survey_manager):
        """Test getting fieldmap"""
        fieldmap = {
            'Q1': {'qid': '123', 'type': 'L', 'question': 'Test question'},
            'id': {'type': 'id', 'title': 'Response ID'}
        }
        survey_manager._make_request = Mock(return_value=fieldmap)
        
        result = survey_manager.get_fieldmap("123456")
        
        assert result == fieldmap
        assert 'Q1' in result
        assert 'id' in result

    def test_get_fieldmap_empty_survey(self, survey_manager):
        """Test fieldmap for survey with no questions"""
        minimal_fieldmap = {
            'id': {'type': 'id'},
            'submitdate': {'type': 'submitdate'}
        }
        survey_manager._make_request = Mock(return_value=minimal_fieldmap)
        
        result = survey_manager.get_fieldmap("123456")
        
        assert result == minimal_fieldmap


class TestParticipantManagerReal:
    """Test ParticipantManager with actual method signatures"""

    @pytest.fixture
    def participant_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ParticipantManager(mock_client)

    def test_list_participants_basic(self, participant_manager):
        """Test basic participant listing"""
        participants = [
            {'tid': '1', 'token': 'ABC123', 'email': 'test@example.com'},
            {'tid': '2', 'token': 'DEF456', 'email': 'test2@example.com'}
        ]
        participant_manager._make_request = Mock(return_value=participants)
        
        result = participant_manager.list_participants("123456")
        
        assert result == participants

    def test_list_participants_with_parameters(self, participant_manager):
        """Test participant listing with pagination and filters"""
        participant_manager._make_request = Mock(return_value=[])
        
        result = participant_manager.list_participants(
            "123456", 
            start=10, 
            limit=50, 
            unused=True,
            attributes=["email", "firstname"]
        )
        
        assert result == []
        # Verify parameters were passed correctly
        participant_manager._make_request.assert_called_once()

    def test_list_participants_no_table(self, participant_manager):
        """Test handling surveys without participant table"""
        error_response = {'status': 'No survey participants table'}
        participant_manager._make_request = Mock(return_value=error_response)
        
        result = participant_manager.list_participants("123456")
        
        assert result == []

    def test_list_participants_exception_handling(self, participant_manager):
        """Test exception handling for participant table errors"""
        participant_manager._make_request = Mock(
            side_effect=Exception("No survey participants table")
        )
        
        result = participant_manager.list_participants("123456")
        
        assert result == []

    def test_list_participants_other_exception(self, participant_manager):
        """Test handling other exceptions"""
        participant_manager._make_request = Mock(
            side_effect=Exception("Database connection failed")
        )
        
        with pytest.raises(Exception) as exc_info:
            participant_manager.list_participants("123456")
        
        assert "Database connection failed" in str(exc_info.value)

    def test_get_participant_properties_basic(self, participant_manager):
        """Test getting participant properties"""
        props = {
            'tid': '1',
            'token': 'ABC123',
            'firstname': 'John',
            'lastname': 'Doe',
            'email': 'john@example.com'
        }
        participant_manager._make_request = Mock(return_value=props)
        
        result = participant_manager.get_participant_properties(
            "123456", 
            {"token": "ABC123"}
        )
        
        assert result == props

    def test_get_participant_properties_by_email(self, participant_manager):
        """Test getting participant properties by email"""
        participant_manager._make_request = Mock(return_value={})
        
        result = participant_manager.get_participant_properties(
            "123456",
            {"email": "test@example.com"},
            ["firstname", "lastname", "completed"]
        )
        
        assert result == {}

    def test_get_participant_properties_empty_response(self, participant_manager):
        """Test handling empty response"""
        participant_manager._make_request = Mock(return_value=None)
        
        result = participant_manager.get_participant_properties(
            "123456",
            {"token": "ABC123"}
        )
        
        assert result == {}

    def test_get_participant_properties_error_handling(self, participant_manager):
        """Test error handling for participant properties"""
        participant_manager._make_request = Mock(
            side_effect=Exception("Participant not found")
        )
        
        with pytest.raises(Exception) as exc_info:
            participant_manager.get_participant_properties(
                "123456",
                {"token": "INVALID"}
            )
        
        assert "Participant not found" in str(exc_info.value)


class TestManagersIntegration:
    """Test realistic integration scenarios across managers"""

    @pytest.fixture
    def survey_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return SurveyManager(mock_client)

    @pytest.fixture
    def question_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    @pytest.fixture
    def response_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ResponseManager(mock_client)

    @pytest.fixture
    def participant_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ParticipantManager(mock_client)

    def test_full_survey_analysis_workflow(self, survey_manager, question_manager, 
                                         response_manager, participant_manager):
        """Test complete survey analysis workflow"""
        # Mock survey listing
        surveys = [{'sid': '123456', 'surveyls_title': 'Test Survey', 'active': 'Y'}]
        
        # Mock survey properties 
        props = {'sid': '123456', 'active': 'Y', 'language': 'en'}
        
        # Use side_effect to return different values for different calls
        survey_manager._make_request = Mock(side_effect=[surveys, props])
        
        # Mock questions
        questions = [{'qid': '123', 'type': 'L', 'title': 'Q1'}]
        question_manager._make_request = Mock(return_value=questions)
        
        # Mock responses
        responses = [{"id": "1", "Q1": "A"}, {"id": "2", "Q1": "B"}]
        response_manager.export_responses = Mock(return_value=responses)
        
        # Mock participants
        participants = [{'tid': '1', 'token': 'ABC123', 'completed': 'Y'}]
        participant_manager._make_request = Mock(return_value=participants)
        
        # Execute workflow
        survey_list = survey_manager.list_surveys()
        survey_id = survey_list[0]['sid']
        
        survey_props = survey_manager.get_survey_properties(survey_id)
        questions_list = question_manager.list_questions(survey_id)
        response_data = response_manager.export_responses(survey_id, "json")
        participant_data = participant_manager.list_participants(survey_id)
        
        # Verify workflow completed
        assert survey_id == '123456'
        assert len(questions_list) == 1
        assert len(response_data) == 2
        assert len(participant_data) == 1

    def test_error_handling_across_managers(self, survey_manager, question_manager):
        """Test error handling across different managers"""
        # Mock survey manager success
        surveys = [{'sid': '123456'}]
        survey_manager._make_request = Mock(return_value=surveys)
        
        # Mock question manager failure
        question_manager._make_request = Mock(side_effect=Exception("API Error"))
        
        # Should handle individual manager failures
        survey_list = survey_manager.list_surveys()
        assert len(survey_list) == 1
        
        with pytest.raises(Exception):
            question_manager.list_questions("123456")

    def test_parameter_consistency_across_managers(self, survey_manager, question_manager,
                                                  response_manager, participant_manager):
        """Test that similar parameters work consistently across managers"""
        # All managers should handle survey_id consistently
        managers_and_methods = [
            (survey_manager, 'get_survey_properties', ['123456']),
            (question_manager, 'list_questions', ['123456']),
            (response_manager, 'export_responses', ['123456']),
            (participant_manager, 'list_participants', ['123456'])
        ]
        
        for manager, method_name, args in managers_and_methods:
            manager._make_request = Mock(return_value={})
            method = getattr(manager, method_name)
            
            # Should not raise exception for basic survey_id parameter
            try:
                method(*args)
            except Exception as e:
                pytest.fail(f"Method {method_name} failed: {e}")


class TestManagerErrorConditions:
    """Test edge cases and error conditions across all managers"""

    def test_empty_survey_id_handling(self):
        """Test handling of empty survey IDs"""
        mock_client = Mock()
        mock_client.session_key = "test_session"
        
        managers = [
            SurveyManager(mock_client),
            QuestionManager(mock_client),
            ResponseManager(mock_client),
            ParticipantManager(mock_client)
        ]
        
        for manager in managers:
            manager._make_request = Mock(return_value=[])
            
            # Should handle empty survey ID gracefully
            # (actual validation might be in the API, not client)
            try:
                if hasattr(manager, 'list_questions'):
                    manager.list_questions("")
                elif hasattr(manager, 'export_responses'):
                    manager.export_responses("")
                elif hasattr(manager, 'list_participants'):
                    manager.list_participants("")
                elif hasattr(manager, 'get_survey_properties'):
                    manager.get_survey_properties("")
            except Exception:
                # Expected - API should validate survey IDs
                pass

    def test_large_dataset_handling(self):
        """Test handling of large datasets"""
        mock_client = Mock()
        mock_client.session_key = "test_session"
        response_manager = ResponseManager(mock_client)
        
        # Mock large response dataset
        large_responses = [{"id": str(i), "Q1": f"Response{i}"} for i in range(1000)]
        response_manager.export_responses = Mock(return_value=large_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        # Should handle large datasets
        assert len(result) == 1000
        assert all(isinstance(rid, str) for rid in result)

    def test_unicode_data_handling(self):
        """Test handling of unicode characters"""
        mock_client = Mock()
        mock_client.session_key = "test_session"
        participant_manager = ParticipantManager(mock_client)
        
        # Mock unicode participant data
        unicode_participants = [
            {'tid': '1', 'firstname': 'José', 'lastname': 'García'},
            {'tid': '2', 'firstname': '山田', 'lastname': '太郎'}
        ]
        participant_manager._make_request = Mock(return_value=unicode_participants)
        
        result = participant_manager.list_participants("123456")
        
        # Should handle unicode correctly
        assert result[0]['firstname'] == 'José'
        assert result[1]['firstname'] == '山田' 