"""
Comprehensive tests for ResponseManager.

Tests all response data operations including exporting responses in various formats,
getting response IDs, statistics, and data processing with proper error handling.
"""

import pytest
from unittest.mock import Mock, patch
import base64
import json
from src.lime_survey_analyzer.managers.response import ResponseManager


class TestResponseManagerExport:
    """Test response export functionality"""

    @pytest.fixture
    def response_manager(self):
        """Create ResponseManager with mocked client"""
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ResponseManager(mock_client)

    def test_export_responses_json_success(self, response_manager):
        """Test successful JSON response export"""
        # Mock JSON response data
        json_data = [
            {"id": "1", "Q1": "A", "Q2": "Yes"},
            {"id": "2", "Q1": "B", "Q2": "No"}
        ]
        
        # Encode as base64 (how LimeSurvey API returns it)
        json_string = json.dumps(json_data)
        encoded_data = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        
        response_manager._make_request = Mock(return_value=encoded_data)
        
        result = response_manager.export_responses("123456", "json")
        
        assert result == json_data
        response_manager._make_request.assert_called_once()

    def test_export_responses_csv_success(self, response_manager):
        """Test successful CSV response export"""
        # Mock CSV response data
        csv_data = "id,Q1,Q2\n1,A,Yes\n2,B,No"
        encoded_data = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')
        
        response_manager._make_request = Mock(return_value=encoded_data)
        
        result = response_manager.export_responses("123456", "csv")
        
        assert result == csv_data
        response_manager._make_request.assert_called_once()

    def test_export_responses_with_filters(self, response_manager):
        """Test export with completion status and other filters"""
        response_manager._make_request = Mock(return_value="encoded_data")
        
        response_manager.export_responses(
            "123456", 
            document_type="json",
            language_code="es",
            completion_status="complete",
            heading_type="full",
            response_type="long"
        )
        
        # Verify all parameters are passed correctly
        call_args = response_manager._make_request.call_args[0][1]
        assert "complete" in call_args
        assert "es" in call_args
        assert "full" in call_args
        assert "long" in call_args

    def test_export_responses_invalid_json(self, response_manager):
        """Test handling of invalid JSON in response"""
        # Mock malformed JSON
        invalid_json = "not valid json"
        encoded_data = base64.b64encode(invalid_json.encode('utf-8')).decode('utf-8')
        
        response_manager._make_request = Mock(return_value=encoded_data)
        
        result = response_manager.export_responses("123456", "json")
        
        # Should return as string when JSON parsing fails
        assert result == invalid_json

    def test_export_responses_decode_failure(self, response_manager):
        """Test handling of base64 decode failure"""
        # Mock invalid base64 data
        invalid_base64 = "not_valid_base64!!!"
        
        response_manager._make_request = Mock(return_value=invalid_base64)
        
        result = response_manager.export_responses("123456", "json")
        
        # Should return original response when decoding fails
        assert result == invalid_base64

    def test_export_responses_non_string_response(self, response_manager):
        """Test handling when API returns non-string response"""
        # Mock direct dictionary response (not base64 encoded)
        direct_response = {"data": [{"id": "1", "Q1": "A"}]}
        
        response_manager._make_request = Mock(return_value=direct_response)
        
        result = response_manager.export_responses("123456", "json")
        
        # Should return response as-is
        assert result == direct_response

    def test_export_responses_by_token_success(self, response_manager):
        """Test successful export by token"""
        mock_response = {"data": "token_specific_data"}
        response_manager._make_request = Mock(return_value=mock_response)
        
        result = response_manager.export_responses_by_token(
            "123456", 
            "json", 
            token="ABC123"
        )
        
        assert result == mock_response
        # Verify token parameter is passed
        call_args = response_manager._make_request.call_args[0][1]
        assert "ABC123" in call_args

    def test_export_responses_by_token_all_parameters(self, response_manager):
        """Test export by token with all optional parameters"""
        response_manager._make_request = Mock(return_value={})
        
        response_manager.export_responses_by_token(
            "123456",
            document_type="csv",
            token="ABC123",
            language_code="fr",
            completion_status="incomplete",
            heading_type="abbreviated",
            response_type="short"
        )
        
        # Verify all parameters are passed
        call_args = response_manager._make_request.call_args[0][1]
        expected_params = ["123456", "csv", "ABC123", "fr", "incomplete", "abbreviated", "short"]
        for param in expected_params:
            assert param in call_args


class TestResponseManagerStatistics:
    """Test statistics export functionality"""

    @pytest.fixture
    def response_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ResponseManager(mock_client)

    def test_export_statistics_pdf(self, response_manager):
        """Test PDF statistics export"""
        mock_pdf_data = b"PDF binary data"
        response_manager._make_request = Mock(return_value=mock_pdf_data)
        
        result = response_manager.export_statistics("123456", "pdf")
        
        assert result == mock_pdf_data
        response_manager._make_request.assert_called_once()

    def test_export_statistics_excel(self, response_manager):
        """Test Excel statistics export"""
        mock_excel_data = "Excel data"
        response_manager._make_request = Mock(return_value=mock_excel_data)
        
        result = response_manager.export_statistics("123456", "xls")
        
        assert result == mock_excel_data
        # Verify correct doc_type parameter
        call_args = response_manager._make_request.call_args[0][1]
        assert "xls" in call_args

    def test_export_statistics_html(self, response_manager):
        """Test HTML statistics export"""
        mock_html_data = "<html>Statistics Report</html>"
        response_manager._make_request = Mock(return_value=mock_html_data)
        
        result = response_manager.export_statistics("123456", "html")
        
        assert result == mock_html_data


class TestResponseManagerResponseIDs:
    """Test response ID retrieval functionality"""

    @pytest.fixture
    def response_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ResponseManager(mock_client)

    def test_get_response_ids_success(self, response_manager):
        """Test successful response ID retrieval for token"""
        expected_ids = ["101", "102", "103"]
        response_manager._make_request = Mock(return_value=expected_ids)
        
        result = response_manager.get_response_ids("123456", "ABC123")
        
        assert result == expected_ids
        # Verify token parameter is passed
        call_args = response_manager._make_request.call_args[0][1]
        assert "ABC123" in call_args

    def test_get_response_ids_empty_result(self, response_manager):
        """Test handling of empty response IDs"""
        response_manager._make_request = Mock(return_value=None)
        
        result = response_manager.get_response_ids("123456", "ABC123")
        
        assert result == []

    def test_get_response_ids_false_result(self, response_manager):
        """Test handling of false/empty API response"""
        response_manager._make_request = Mock(return_value=False)
        
        result = response_manager.get_response_ids("123456", "ABC123")
        
        assert result == []

    def test_get_all_response_ids_from_dict(self, response_manager):
        """Test getting all response IDs from dictionary response"""
        # Mock response export returning dictionary format
        mock_responses = {
            "101": {"id": "101", "Q1": "A"},
            "102": {"id": "102", "Q1": "B"},
            "103": {"id": "103", "Q1": "C"}
        }
        
        response_manager.export_responses = Mock(return_value=mock_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        expected_ids = ["101", "102", "103"]
        assert sorted(result) == sorted(expected_ids)

    def test_get_all_response_ids_from_list(self, response_manager):
        """Test getting all response IDs from list response"""
        # Mock response export returning list format
        mock_responses = [
            {"id": "101", "Q1": "A"},
            {"id": "102", "Q1": "B"},
            {"id": "103", "Q1": "C"}
        ]
        
        response_manager.export_responses = Mock(return_value=mock_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        expected_ids = ["101", "102", "103"]
        assert sorted(result) == sorted(expected_ids)

    def test_get_all_response_ids_with_responses_key(self, response_manager):
        """Test getting response IDs when data has responses key"""
        # Mock response export with nested responses structure
        mock_responses = {
            "responses": [
                {"id": "101", "Q1": "A"},
                {"id": "102", "Q1": "B"}
            ]
        }
        
        response_manager.export_responses = Mock(return_value=mock_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        expected_ids = ["101", "102"]
        assert sorted(result) == sorted(expected_ids)

    def test_get_all_response_ids_mixed_id_fields(self, response_manager):
        """Test handling responses with different ID field names"""
        # Mock responses with various ID field names
        mock_responses = [
            {"id": "101", "Q1": "A"},
            {"response_id": "102", "Q1": "B"},
            {"rid": "103", "Q1": "C"},
            {"submitdate": "2023-01-01", "Q1": "D"}  # No valid ID field
        ]
        
        response_manager.export_responses = Mock(return_value=mock_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        # Should extract IDs from valid fields
        expected_ids = ["101", "102", "103"]
        assert sorted(result) == sorted(expected_ids)

    def test_get_all_response_ids_export_failure(self, response_manager):
        """Test handling when response export fails"""
        response_manager.export_responses = Mock(side_effect=Exception("Export failed"))
        
        result = response_manager.get_all_response_ids("123456")
        
        assert result == []

    def test_get_all_response_ids_invalid_format(self, response_manager):
        """Test handling invalid response format"""
        # Mock response that's neither dict nor list
        response_manager.export_responses = Mock(return_value="invalid format")
        
        result = response_manager.get_all_response_ids("123456")
        
        assert result == []

    def test_get_all_response_ids_empty_responses(self, response_manager):
        """Test handling empty responses"""
        response_manager.export_responses = Mock(return_value=[])
        
        result = response_manager.get_all_response_ids("123456")
        
        assert result == []


class TestResponseManagerEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def response_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return ResponseManager(mock_client)

    def test_export_responses_empty_survey(self, response_manager):
        """Test export from survey with no responses"""
        # Mock empty response
        empty_json = "[]"
        encoded_data = base64.b64encode(empty_json.encode('utf-8')).decode('utf-8')
        
        response_manager._make_request = Mock(return_value=encoded_data)
        
        result = response_manager.export_responses("123456", "json")
        
        assert result == []

    def test_export_statistics_large_survey(self, response_manager):
        """Test statistics export for large survey"""
        # Mock large statistics data
        large_stats = b"Large PDF statistics data" * 1000
        response_manager._make_request = Mock(return_value=large_stats)
        
        result = response_manager.export_statistics("123456", "pdf")
        
        assert len(result) > 1000
        assert result == large_stats

    def test_response_manager_parameter_validation(self, response_manager):
        """Test parameter validation and building"""
        # Test that all methods properly validate and pass parameters
        test_cases = [
            ("export_responses", ["123456", "json"]),
            ("export_responses_by_token", ["123456", "json", "TOKEN123"]),
            ("export_statistics", ["123456", "pdf"]),
            ("get_response_ids", ["123456", "TOKEN123"]),
        ]
        
        response_manager._make_request = Mock(return_value={})
        
        for method_name, args in test_cases:
            method = getattr(response_manager, method_name)
            try:
                method(*args)
                # Verify the method was called without errors
                assert response_manager._make_request.called
            except Exception as e:
                pytest.fail(f"Method {method_name} failed with args {args}: {e}")
            finally:
                response_manager._make_request.reset_mock()

    def test_export_responses_unicode_handling(self, response_manager):
        """Test handling of unicode characters in responses"""
        # Mock response with unicode characters
        unicode_data = [{"id": "1", "Q1": "Café", "Q2": "Résumé", "Q3": "中文"}]
        json_string = json.dumps(unicode_data, ensure_ascii=False)
        encoded_data = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
        
        response_manager._make_request = Mock(return_value=encoded_data)
        
        result = response_manager.export_responses("123456", "json")
        
        assert result == unicode_data
        assert result[0]["Q1"] == "Café"
        assert result[0]["Q2"] == "Résumé"
        assert result[0]["Q3"] == "中文"

    def test_get_all_response_ids_numeric_ids(self, response_manager):
        """Test handling of numeric response IDs"""
        # Mock responses with numeric IDs
        mock_responses = [
            {"id": 101, "Q1": "A"},  # Numeric ID
            {"id": "102", "Q1": "B"},  # String ID
            {"response_id": 103.0, "Q1": "C"}  # Float ID
        ]
        
        response_manager.export_responses = Mock(return_value=mock_responses)
        
        result = response_manager.get_all_response_ids("123456")
        
        # Should convert all to strings
        expected_ids = ["101", "102", "103"]
        assert sorted(result) == sorted(expected_ids)

    def test_export_responses_malformed_base64(self, response_manager):
        """Test handling of malformed base64 data"""
        # Mock malformed base64 (missing padding)
        malformed_base64 = "SGVsbG8gV29ybGQ"  # Missing padding
        
        response_manager._make_request = Mock(return_value=malformed_base64)
        
        result = response_manager.export_responses("123456", "json")
        
        # Should return original data when base64 decode fails
        assert result == malformed_base64 