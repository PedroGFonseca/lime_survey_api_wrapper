"""
Comprehensive tests for QuestionManager.

Tests all question management operations including listing groups, questions,
getting properties, validation, and structured question conversion.
Focuses on realistic data flows and error conditions.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.lime_survey_analyzer.managers.question import QuestionManager
from src.lime_survey_analyzer.exceptions import QuestionValidationError, QuestionNotFoundError
from src.lime_survey_analyzer.models import Question, QuestionType


class TestQuestionManagerCore:
    """Test core QuestionManager functionality"""

    @pytest.fixture
    def question_manager(self):
        """Create QuestionManager with mocked client"""
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    @pytest.fixture
    def mock_raw_question_data(self):
        """Mock raw question data from API"""
        return {
            'qid': '123',
            'gid': '10',
            'type': 'L',
            'title': 'Q1',
            'question': 'What is your favorite color?',
            'help': '',
            'other': 'N',
            'mandatory': 'Y',
            'question_order': '1',
            'scale_id': '0',
            'same_default': '0',
            'relevance': '1',
            'modulename': '',
            'language': 'en',
            'answeroptions': {
                '1': {'code': '1', 'answer': 'Red', 'assessment_value': '1'},
                '2': {'code': '2', 'answer': 'Blue', 'assessment_value': '2'}
            }
        }

    def test_list_groups_success(self, question_manager):
        """Test successful group listing"""
        expected_groups = [
            {'gid': '10', 'group_name': 'Demographics', 'group_order': '1'},
            {'gid': '20', 'group_name': 'Preferences', 'group_order': '2'}
        ]
        question_manager._make_request = Mock(return_value=expected_groups)
        
        result = question_manager.list_groups("123456")
        
        assert result == expected_groups
        question_manager._make_request.assert_called_once()

    def test_list_groups_with_language(self, question_manager):
        """Test group listing with language parameter"""
        question_manager._make_request = Mock(return_value=[])
        
        question_manager.list_groups("123456", language="es")
        
        # Check that language parameter is passed correctly
        call_args = question_manager._make_request.call_args
        assert 'language' in str(call_args)

    def test_get_group_properties_success(self, question_manager):
        """Test successful group properties retrieval"""
        expected_props = {
            'gid': '10',
            'group_name': 'Demographics',
            'description': 'Basic demographic questions',
            'group_order': '1',
            'randomization_group': '',
            'grelevance': '1'
        }
        question_manager._make_request = Mock(return_value=expected_props)
        
        result = question_manager.get_group_properties("123456", "10")
        
        assert result == expected_props
        question_manager._make_request.assert_called_once()

    def test_list_questions_all_survey(self, question_manager):
        """Test listing all questions in survey"""
        expected_questions = [
            {'qid': '123', 'type': 'L', 'title': 'Q1'},
            {'qid': '124', 'type': 'M', 'title': 'Q2'}
        ]
        question_manager._make_request = Mock(return_value=expected_questions)
        
        result = question_manager.list_questions("123456")
        
        assert result == expected_questions
        question_manager._make_request.assert_called_once()

    def test_list_questions_by_group(self, question_manager):
        """Test listing questions filtered by group"""
        question_manager._make_request = Mock(return_value=[])
        
        question_manager.list_questions("123456", group_id="10")
        
        # Verify group_id parameter is passed
        call_args = question_manager._make_request.call_args
        assert 'iGroupID' in str(call_args)

    def test_get_question_properties_success(self, question_manager, mock_raw_question_data):
        """Test successful question properties retrieval"""
        question_manager._make_request = Mock(return_value=mock_raw_question_data)
        
        result = question_manager.get_question_properties("123456", "123")
        
        assert result == mock_raw_question_data
        question_manager._make_request.assert_called_once()

    def test_get_question_properties_with_enhancement(self, question_manager):
        """Test question properties with predefined option enhancement"""
        # Mock question without answer options (common case)
        mock_data = {
            'qid': '123',
            'type': 'L',
            'answeroptions': "No available answer options"
        }
        question_manager._make_request = Mock(return_value=mock_data)
        
        with patch.object(question_manager, '_enhance_question_properties_with_predefined_options') as mock_enhance:
            mock_enhance.return_value = mock_data
            
            result = question_manager.get_question_properties("123456", "123")
            
            mock_enhance.assert_called_once()


class TestQuestionManagerStructured:
    """Test structured question handling"""

    @pytest.fixture
    def question_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    def test_list_questions_structured_success(self, question_manager):
        """Test successful structured question listing"""
        # Mock raw question data
        raw_questions = [
            {'qid': '123', 'type': 'L', 'title': 'Q1'},
            {'qid': '124', 'type': 'M', 'title': 'Q2'}
        ]
        
        # Mock detailed properties for each question
        detailed_props = {
            'qid': '123',
            'type': 'L',
            'title': 'Q1',
            'question': 'Test question',
            'gid': '10',
            'answeroptions': {'1': {'answer': 'Yes'}, '2': {'answer': 'No'}}
        }
        
        question_manager.list_questions = Mock(return_value=raw_questions)
        question_manager.get_question_properties = Mock(return_value=detailed_props)
        
        with patch.object(question_manager, '_convert_raw_to_question') as mock_convert:
            # Mock Question object with priority type
            mock_question = Mock()
            mock_question.qid = '123'
            mock_question.properties.question_type.value = 'L'
            mock_convert.return_value = mock_question
            
            with patch('src.lime_survey_analyzer.managers.question.is_priority_type', return_value=True):
                with patch('src.lime_survey_analyzer.managers.question.get_question_handler') as mock_handler:
                    mock_handler.return_value.validate_question_structure.return_value = []
                    
                    result = question_manager.list_questions_structured("123456")
                    
                    assert len(result) == 2
                    assert all(q.qid in ['123', '124'] for q in result)

    def test_list_questions_structured_filter_unsupported(self, question_manager):
        """Test filtering of unsupported question types"""
        raw_questions = [
            {'qid': '123', 'type': 'L'},  # Supported
            {'qid': '124', 'type': 'X'}   # Unsupported
        ]
        
        question_manager.list_questions = Mock(return_value=raw_questions)
        question_manager.get_question_properties = Mock(return_value={'qid': '123', 'type': 'L'})
        
        with patch.object(question_manager, '_convert_raw_to_question') as mock_convert:
            mock_question = Mock()
            mock_question.qid = '123'
            mock_question.properties.question_type.value = 'L'
            mock_convert.return_value = mock_question
            
            with patch('src.lime_survey_analyzer.managers.question.is_priority_type', side_effect=lambda x: x == 'L'):
                result = question_manager.list_questions_structured("123456", include_unsupported=False)
                
                # Should only include supported types
                assert len(result) == 1
                assert result[0].qid == '123'

    def test_list_questions_structured_include_unsupported(self, question_manager):
        """Test including unsupported question types"""
        raw_questions = [
            {'qid': '123', 'type': 'L'},
            {'qid': '124', 'type': 'X'}
        ]
        
        question_manager.list_questions = Mock(return_value=raw_questions)
        question_manager.get_question_properties = Mock(return_value={'qid': '123', 'type': 'L'})
        
        with patch.object(question_manager, '_convert_raw_to_question') as mock_convert:
            mock_question = Mock()
            mock_question.qid = '123'
            mock_question.properties.question_type.value = 'L'
            mock_convert.return_value = mock_question
            
            result = question_manager.list_questions_structured("123456", include_unsupported=True)
            
            # Should include all questions regardless of type
            assert len(result) == 2

    def test_get_question_structured_success(self, question_manager):
        """Test getting single structured question"""
        mock_props = {
            'qid': '123',
            'type': 'L',
            'title': 'Q1',
            'question': 'Test question',
            'gid': '10'
        }
        
        question_manager.get_question_properties = Mock(return_value=mock_props)
        
        with patch.object(question_manager, '_convert_raw_to_question') as mock_convert:
            mock_question = Mock()
            mock_question.qid = '123'
            mock_convert.return_value = mock_question
            
            result = question_manager.get_question_structured("123456", "123")
            
            assert result.qid == '123'
            mock_convert.assert_called_once_with(mock_props, "123456")


class TestQuestionManagerConversion:
    """Test question data conversion methods"""

    @pytest.fixture
    def question_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    def test_convert_raw_to_question_basic(self, question_manager):
        """Test basic raw data to Question conversion"""
        raw_data = {
            'qid': '123',
            'gid': '10',
            'type': 'L',
            'title': 'Q1',
            'question': 'Test question',
            'help': 'Help text',
            'other': 'N',
            'mandatory': 'Y',
            'question_order': '1'
        }
        
        with patch.object(question_manager, '_build_question_properties') as mock_build_props:
            mock_props = Mock()
            mock_build_props.return_value = mock_props
            
            with patch.object(question_manager, '_add_answer_options') as mock_add_options:
                with patch.object(question_manager, '_add_subquestions') as mock_add_subq:
                    result = question_manager._convert_raw_to_question(raw_data, "123456")
                    
                    assert result.qid == '123'
                    assert result.gid == '10'
                    assert result.survey_id == "123456"
                    mock_build_props.assert_called_once()
                    mock_add_options.assert_called_once()
                    mock_add_subq.assert_called_once()

    def test_build_question_properties_complete(self, question_manager):
        """Test building question properties from raw data"""
        raw_data = {
            'type': 'L',
            'mandatory': 'Y',
            'question': 'Test question?',
            'help': 'Help text',
            'other': 'N',
            'question_order': '5',
            'scale_id': '0',
            'same_default': '0',
            'relevance': '1',
            'modulename': '',
            'language': 'en'
        }
        
        result = question_manager._build_question_properties(raw_data, "123456")
        
        # Verify all properties are set correctly
        assert result.question_type.value == 'L'
        assert result.mandatory.value == 'Y'
        assert result.question_text == 'Test question?'
        assert result.help_text == 'Help text'
        assert result.other_option.value == 'N'

    def test_add_answer_options_with_data(self, question_manager):
        """Test adding answer options when present in raw data"""
        mock_question = Mock()
        mock_question.answers = []
        
        raw_data = {
            'answeroptions': {
                '1': {'code': '1', 'answer': 'Option 1', 'assessment_value': '1'},
                '2': {'code': '2', 'answer': 'Option 2', 'assessment_value': '2'}
            }
        }
        
        question_manager._add_answer_options(mock_question, raw_data)
        
        # Verify options were added
        assert len(mock_question.answers) == 2

    def test_add_answer_options_no_data(self, question_manager):
        """Test handling when no answer options are available"""
        mock_question = Mock()
        mock_question.answers = []
        mock_question.properties.question_type.value = 'L'
        
        raw_data = {
            'answeroptions': "No available answer options"
        }
        
        with patch.object(question_manager, '_add_predefined_answer_options') as mock_predefined:
            question_manager._add_answer_options(mock_question, raw_data)
            
            mock_predefined.assert_called_once()

    def test_add_predefined_answer_options(self, question_manager):
        """Test adding predefined answer options for known question types"""
        mock_question = Mock()
        mock_question.answers = []
        
        with patch('src.lime_survey_analyzer.managers.question.get_answer_codes_for_question_type') as mock_get_codes:
            mock_get_codes.return_value = {
                'Y': 'Yes',
                'N': 'No'
            }
            
            question_manager._add_predefined_answer_options(mock_question, 'L')
            
            assert len(mock_question.answers) == 2
            mock_get_codes.assert_called_once_with('L')

    def test_add_subquestions_with_data(self, question_manager):
        """Test adding subquestions when present"""
        mock_question = Mock()
        mock_question.subquestions = []
        
        raw_data = {
            'subquestions': {
                '1': {'title': 'SQ1', 'question': 'Subquestion 1'},
                '2': {'title': 'SQ2', 'question': 'Subquestion 2'}
            }
        }
        
        question_manager._add_subquestions(mock_question, raw_data)
        
        assert len(mock_question.subquestions) == 2


class TestQuestionManagerValidation:
    """Test question validation functionality"""

    @pytest.fixture
    def question_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    def test_validate_question_types_success(self, question_manager):
        """Test successful question type validation"""
        mock_questions = [
            {'qid': '123', 'type': 'L'},
            {'qid': '124', 'type': 'M'}
        ]
        
        question_manager.list_questions = Mock(return_value=mock_questions)
        
        with patch('src.lime_survey_analyzer.managers.question.is_priority_type', return_value=True):
            with patch('src.lime_survey_analyzer.managers.question.get_question_handler') as mock_handler:
                mock_handler.return_value.validate_question_structure.return_value = []
                
                result = question_manager.validate_question_types("123456")
                
                assert 'validation_summary' in result
                assert 'detailed_results' in result
                assert 'supported_questions' in result

    def test_validate_question_types_with_errors(self, question_manager):
        """Test question validation with validation errors"""
        mock_questions = [
            {'qid': '123', 'type': 'L'}
        ]
        
        question_manager.list_questions = Mock(return_value=mock_questions)
        question_manager.get_question_structured = Mock()
        
        with patch('src.lime_survey_analyzer.managers.question.is_priority_type', return_value=True):
            with patch('src.lime_survey_analyzer.managers.question.get_question_handler') as mock_handler:
                mock_handler.return_value.validate_question_structure.return_value = ['Missing required field']
                
                result = question_manager.validate_question_types("123456")
                
                assert result['validation_summary']['total_errors'] > 0

    def test_validate_question_types_unsupported(self, question_manager):
        """Test validation with unsupported question types"""
        mock_questions = [
            {'qid': '123', 'type': 'X'}  # Unsupported type
        ]
        
        question_manager.list_questions = Mock(return_value=mock_questions)
        
        with patch('src.lime_survey_analyzer.managers.question.is_priority_type', return_value=False):
            result = question_manager.validate_question_types("123456")
            
            assert result['validation_summary']['unsupported_questions'] == 1


class TestQuestionManagerConditions:
    """Test condition handling methods"""

    @pytest.fixture
    def question_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    def test_list_conditions_all_survey(self, question_manager):
        """Test listing all conditions in survey"""
        expected_conditions = [
            {'cid': '1', 'qid': '123', 'scenario': '1'},
            {'cid': '2', 'qid': '124', 'scenario': '1'}
        ]
        question_manager._make_request = Mock(return_value=expected_conditions)
        
        result = question_manager.list_conditions("123456")
        
        assert result == expected_conditions

    def test_list_conditions_by_question(self, question_manager):
        """Test listing conditions for specific question"""
        question_manager._make_request = Mock(return_value=[])
        
        question_manager.list_conditions("123456", question_id="123")
        
        call_args = question_manager._make_request.call_args
        assert 'iQuestionID' in str(call_args)

    def test_get_conditions_for_question(self, question_manager):
        """Test getting conditions for specific question"""
        expected_conditions = [
            {'cid': '1', 'scenario': '1', 'cqid': '122', 'method': '==', 'value': 'Y'}
        ]
        question_manager._make_request = Mock(return_value=expected_conditions)
        
        result = question_manager.get_conditions("123456", "123")
        
        assert result == expected_conditions


class TestQuestionManagerErrorHandling:
    """Test error handling and edge cases"""

    @pytest.fixture
    def question_manager(self):
        mock_client = Mock()
        mock_client.session_key = "test_session"
        return QuestionManager(mock_client)

    def test_list_questions_structured_missing_qid(self, question_manager):
        """Test handling questions without QID"""
        raw_questions = [
            {'type': 'L', 'title': 'Q1'},  # Missing qid
            {'qid': '124', 'type': 'M', 'title': 'Q2'}
        ]
        
        question_manager.list_questions = Mock(return_value=raw_questions)
        question_manager.get_question_properties = Mock(return_value={'qid': '124', 'type': 'M'})
        
        with patch.object(question_manager, '_convert_raw_to_question') as mock_convert:
            mock_question = Mock()
            mock_question.qid = '124'
            mock_question.properties.question_type.value = 'M'
            mock_convert.return_value = mock_question
            
            with patch('src.lime_survey_analyzer.managers.question.is_priority_type', return_value=True):
                result = question_manager.list_questions_structured("123456")
                
                # Should skip question without QID
                assert len(result) == 1
                assert result[0].qid == '124'

    def test_get_question_properties_failure_fallback(self, question_manager):
        """Test fallback when detailed properties fail"""
        raw_questions = [
            {'qid': '123', 'type': 'L', 'title': 'Q1'}
        ]
        
        question_manager.list_questions = Mock(return_value=raw_questions)
        # Simulate failure getting detailed properties
        question_manager.get_question_properties = Mock(side_effect=Exception("API Error"))
        
        with patch.object(question_manager, '_convert_raw_to_question') as mock_convert:
            mock_question = Mock()
            mock_question.qid = '123'
            mock_question.properties.question_type.value = 'L'
            mock_convert.return_value = mock_question
            
            with patch('src.lime_survey_analyzer.managers.question.is_priority_type', return_value=True):
                result = question_manager.list_questions_structured("123456")
                
                # Should fallback to basic data
                assert len(result) == 1
                # Convert should be called with basic data (without detailed properties)
                call_args = mock_convert.call_args[0][0]
                assert call_args == {'qid': '123', 'type': 'L', 'title': 'Q1'}

    def test_enhance_question_properties_predefined_options(self, question_manager):
        """Test enhancement with predefined options"""
        props = {
            'qid': '123',
            'type': 'L',
            'answeroptions': "No available answer options"
        }
        
        with patch('src.lime_survey_analyzer.managers.question.is_question_type_predefined', return_value=True):
            with patch('src.lime_survey_analyzer.managers.question.get_answer_codes_for_question_type') as mock_get_codes:
                mock_get_codes.return_value = {'Y': 'Yes', 'N': 'No'}
                
                result = question_manager._enhance_question_properties_with_predefined_options(
                    props, "123456", "123"
                )
                
                # Should replace answeroptions with predefined ones
                assert isinstance(result['answeroptions'], dict)
                assert 'Y' in result['answeroptions']
                mock_get_codes.assert_called_once_with('L')

    def test_enhance_question_properties_no_predefined(self, question_manager):
        """Test enhancement when no predefined options available"""
        props = {
            'qid': '123',
            'type': 'X',  # Unknown type
            'answeroptions': "No available answer options"
        }
        
        with patch('src.lime_survey_analyzer.managers.question.is_question_type_predefined', return_value=False):
            result = question_manager._enhance_question_properties_with_predefined_options(
                props, "123456", "123"
            )
            
            # Should leave answeroptions unchanged
            assert result['answeroptions'] == "No available answer options" 