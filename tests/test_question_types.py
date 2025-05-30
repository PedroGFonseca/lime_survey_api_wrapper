"""Tests for the question type system."""

import pytest
from unittest.mock import MagicMock

from lime_survey_analyzer.models import (
    # Core models
    Question, Answer, SubQuestion, QuestionProperties, AnswerProperties, SubQuestionProperties,
    
    # Enums
    QuestionType, MandatoryState, VisibilityState,
    
    # Question type system
    QuestionTypeDefinition, AdvancedQuestionAttributes,
    get_priority_question_types, get_question_handler, is_priority_type,
    validate_question_attributes, PRIORITY_QUESTION_TYPES, QUESTION_TYPES,
    
    # Handlers
    SingleChoiceRadioHandler, MultipleChoiceHandler, ShortTextHandler, RankingHandler,
    NotImplementedHandler
)


class TestQuestionTypeDefinition:
    """Test QuestionTypeDefinition functionality."""
    
    def test_priority_types_defined(self):
        """Test that all priority types are properly defined."""
        priority_types = get_priority_question_types()
        
        assert "L" in priority_types
        assert "M" in priority_types
        assert "S" in priority_types
        assert "R" in priority_types
        
        # Check they're marked as priority
        for type_code, definition in priority_types.items():
            assert definition.is_priority
            assert definition.type_code == type_code
    
    def test_priority_type_capabilities(self):
        """Test that priority types have correct capabilities."""
        # Single Choice Radio (L)
        l_def = PRIORITY_QUESTION_TYPES["L"]
        assert l_def.supports_answers
        assert l_def.supports_other_option
        assert not l_def.supports_multiple_responses
        assert l_def.supports_validation
        assert l_def.supports_randomization
        assert l_def.supports_assessment
        
        # Multiple Choice (M) 
        m_def = PRIORITY_QUESTION_TYPES["M"]
        assert m_def.supports_answers
        assert m_def.supports_other_option
        assert m_def.supports_multiple_responses
        assert m_def.supports_exclusive_options
        assert m_def.supports_array_filtering
        
        # Short Text (S)
        s_def = PRIORITY_QUESTION_TYPES["S"]
        assert not s_def.supports_answers
        assert not s_def.supports_other_option
        assert s_def.supports_validation
        
        # Ranking (R)
        r_def = PRIORITY_QUESTION_TYPES["R"]
        assert r_def.supports_answers
        assert not r_def.supports_other_option
        assert r_def.supports_randomization
        assert r_def.supports_array_filtering
    
    def test_is_priority_type(self):
        """Test priority type detection."""
        assert is_priority_type("L")
        assert is_priority_type("M")
        assert is_priority_type("S") 
        assert is_priority_type("R")
        
        assert not is_priority_type("F")  # Array
        assert not is_priority_type("T")  # Long text
        assert not is_priority_type("invalid")


class TestQuestionTypeHandlers:
    """Test question type handlers."""
    
    def test_handler_creation(self):
        """Test handler creation for priority types."""
        l_handler = get_question_handler("L")
        assert isinstance(l_handler, SingleChoiceRadioHandler)
        
        m_handler = get_question_handler("M")
        assert isinstance(m_handler, MultipleChoiceHandler)
        
        s_handler = get_question_handler("S")
        assert isinstance(s_handler, ShortTextHandler)
        
        r_handler = get_question_handler("R")
        assert isinstance(r_handler, RankingHandler)
    
    def test_unsupported_handler(self):
        """Test that unsupported types return NotImplementedHandler."""
        f_handler = get_question_handler("F")  # Array
        assert isinstance(f_handler, NotImplementedHandler)
        
        t_handler = get_question_handler("T")  # Long text
        assert isinstance(t_handler, NotImplementedHandler)
    
    def test_invalid_handler(self):
        """Test error for invalid question types."""
        with pytest.raises(ValueError, match="Unknown question type"):
            get_question_handler("INVALID")


class TestSingleChoiceRadioHandler:
    """Test Single Choice Radio handler (L)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = get_question_handler("L")
        
        # Create a valid single choice question
        self.question = Question(
            properties=QuestionProperties(
                qid=101,
                question_code="satisfaction",
                question_type=QuestionType.LIST_RADIO,
                gid=1,
                sid=12345,
                mandatory=MandatoryState.MANDATORY,
                question_text="How satisfied are you?"
            )
        )
        
        # Add answer options
        self.question.answers = [
            Answer(properties=AnswerProperties(code="1", answer_text="Very Dissatisfied", parent_qid=101)),
            Answer(properties=AnswerProperties(code="2", answer_text="Dissatisfied", parent_qid=101)),
            Answer(properties=AnswerProperties(code="3", answer_text="Neutral", parent_qid=101)),
            Answer(properties=AnswerProperties(code="4", answer_text="Satisfied", parent_qid=101)),
            Answer(properties=AnswerProperties(code="5", answer_text="Very Satisfied", parent_qid=101)),
        ]
    
    def test_validate_structure_valid(self):
        """Test validation of valid single choice question."""
        errors = self.handler.validate_question_structure(self.question)
        assert errors == []
    
    def test_validate_structure_no_answers(self):
        """Test validation fails without answer options."""
        self.question.answers = []
        errors = self.handler.validate_question_structure(self.question)
        assert len(errors) == 1
        assert "must have answer options" in errors[0]
    
    def test_generate_database_fields(self):
        """Test database field generation."""
        fields = self.handler.generate_database_fields(self.question)
        assert fields == ["12345X1X101"]
    
    def test_validate_response(self):
        """Test response validation."""
        # Valid responses
        assert self.handler.validate_response("1", self.question)
        assert self.handler.validate_response("3", self.question)
        assert self.handler.validate_response("5", self.question)
        assert self.handler.validate_response("", self.question)  # Empty
        assert self.handler.validate_response(None, self.question)  # None
        
        # Invalid responses
        assert not self.handler.validate_response("6", self.question)
        assert not self.handler.validate_response("invalid", self.question)
    
    def test_response_with_other_option(self):
        """Test validation with 'other' option enabled."""
        self.question.properties.other_option = True
        assert self.handler.validate_response("other", self.question)
    
    def test_format_response_for_export(self):
        """Test response formatting for different export types."""
        # SPSS should convert numeric strings to integers
        assert self.handler.format_response_for_export("3", "spss") == 3
        assert self.handler.format_response_for_export("non-numeric", "spss") == "non-numeric"
        
        # Excel keeps original format
        assert self.handler.format_response_for_export("3", "excel") == "3"


class TestMultipleChoiceHandler:
    """Test Multiple Choice handler (M)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = get_question_handler("M")
        
        # Create a valid multiple choice question
        self.question = Question(
            properties=QuestionProperties(
                qid=201,
                question_code="features",
                question_type=QuestionType.MULTIPLE_CHOICE,
                gid=2,
                sid=12345,
                mandatory=MandatoryState.OPTIONAL,
                question_text="Which features do you use?"
            )
        )
        
        # Add answer options
        self.question.answers = [
            Answer(properties=AnswerProperties(code="surveys", answer_text="Survey Creation", parent_qid=201)),
            Answer(properties=AnswerProperties(code="reports", answer_text="Report Generation", parent_qid=201)),
            Answer(properties=AnswerProperties(code="export", answer_text="Data Export", parent_qid=201)),
        ]
    
    def test_validate_structure_valid(self):
        """Test validation of valid multiple choice question."""
        errors = self.handler.validate_question_structure(self.question)
        assert errors == []
    
    def test_generate_database_fields(self):
        """Test database field generation for multiple choice."""
        fields = self.handler.generate_database_fields(self.question)
        expected = [
            "12345X2X201surveys",
            "12345X2X201reports", 
            "12345X2X201export"
        ]
        assert fields == expected
    
    def test_generate_database_fields_with_other(self):
        """Test database field generation with 'other' option."""
        self.question.properties.other_option = True
        fields = self.handler.generate_database_fields(self.question)
        expected = [
            "12345X2X201surveys",
            "12345X2X201reports",
            "12345X2X201export",
            "12345X2X201other"
        ]
        assert fields == expected
    
    def test_validate_response(self):
        """Test response validation for multiple choice."""
        # Valid Y/N responses
        assert self.handler.validate_response("Y", self.question)
        assert self.handler.validate_response("N", self.question)
        assert self.handler.validate_response("", self.question)
        assert self.handler.validate_response(None, self.question)
        
        # Invalid responses
        assert not self.handler.validate_response("invalid", self.question)
        assert not self.handler.validate_response("1", self.question)
    
    def test_format_response_for_export(self):
        """Test response formatting for SPSS export."""
        # SPSS formatting: Y=1, everything else=0
        assert self.handler.format_response_for_export("Y", "spss") == 1
        assert self.handler.format_response_for_export("N", "spss") == 0
        assert self.handler.format_response_for_export("", "spss") == 0
        assert self.handler.format_response_for_export(None, "spss") == 0
        
        # Other formats keep original
        assert self.handler.format_response_for_export("Y", "excel") == "Y"


class TestShortTextHandler:
    """Test Short Text handler (S)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = get_question_handler("S")
        
        # Create a valid short text question
        self.question = Question(
            properties=QuestionProperties(
                qid=301,
                question_code="feedback",
                question_type=QuestionType.SHORT_FREE_TEXT,
                gid=3,
                sid=12345,
                mandatory=MandatoryState.OPTIONAL,
                question_text="Please provide feedback:"
            )
        )
    
    def test_validate_structure_valid(self):
        """Test validation of valid short text question."""
        errors = self.handler.validate_question_structure(self.question)
        assert errors == []
    
    def test_validate_structure_with_answers(self):
        """Test validation fails if answers are provided."""
        self.question.answers = [
            Answer(properties=AnswerProperties(code="1", answer_text="Option 1", parent_qid=301))
        ]
        errors = self.handler.validate_question_structure(self.question)
        assert len(errors) == 1
        assert "should not have predefined answer options" in errors[0]
    
    def test_generate_database_fields(self):
        """Test database field generation."""
        fields = self.handler.generate_database_fields(self.question)
        assert fields == ["12345X3X301"]
    
    def test_validate_response(self):
        """Test response validation."""
        # Valid text responses
        assert self.handler.validate_response("Great service!", self.question)
        assert self.handler.validate_response("", self.question)
        assert self.handler.validate_response(None, self.question)
        assert self.handler.validate_response("A" * 500, self.question)  # Under limit
        
        # Invalid - too long
        assert not self.handler.validate_response("A" * 1500, self.question)  # Over limit
    
    def test_format_response_for_export(self):
        """Test response formatting."""
        assert self.handler.format_response_for_export("text", "spss") == "text"
        assert self.handler.format_response_for_export("text", "excel") == "text"
        assert self.handler.format_response_for_export(None, "spss") == ""


class TestRankingHandler:
    """Test Ranking handler (R)."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = get_question_handler("R")
        
        # Create a valid ranking question
        self.question = Question(
            properties=QuestionProperties(
                qid=401,
                question_code="priorities",
                question_type=QuestionType.RANKING,
                gid=4,
                sid=12345,
                mandatory=MandatoryState.MANDATORY,
                question_text="Rank these features:"
            )
        )
        
        # Add items to rank
        self.question.answers = [
            Answer(properties=AnswerProperties(code="speed", answer_text="Fast Performance", parent_qid=401)),
            Answer(properties=AnswerProperties(code="ease", answer_text="Ease of Use", parent_qid=401)),
            Answer(properties=AnswerProperties(code="features", answer_text="Rich Features", parent_qid=401)),
        ]
    
    def test_validate_structure_valid(self):
        """Test validation of valid ranking question."""
        errors = self.handler.validate_question_structure(self.question)
        assert errors == []
    
    def test_validate_structure_no_answers(self):
        """Test validation fails without items to rank."""
        self.question.answers = []
        errors = self.handler.validate_question_structure(self.question)
        # Should get 2 errors: no answers AND less than 2 items
        assert len(errors) == 2
        assert any("must have answer options to rank" in error for error in errors)
        assert any("needs at least 2 items to rank" in error for error in errors)
    
    def test_validate_structure_too_few_answers(self):
        """Test validation fails with too few items to rank."""
        self.question.answers = [
            Answer(properties=AnswerProperties(code="speed", answer_text="Fast Performance", parent_qid=401))
        ]
        errors = self.handler.validate_question_structure(self.question)
        assert len(errors) == 1
        assert "needs at least 2 items to rank" in errors[0]
    
    def test_generate_database_fields(self):
        """Test database field generation for ranking."""
        fields = self.handler.generate_database_fields(self.question)
        expected = [
            "12345X4X4011",
            "12345X4X4012",
            "12345X4X4013"
        ]
        assert fields == expected
    
    def test_validate_response(self):
        """Test response validation for ranking."""
        # Valid responses (answer codes)
        assert self.handler.validate_response("speed", self.question)
        assert self.handler.validate_response("ease", self.question)
        assert self.handler.validate_response("features", self.question)
        assert self.handler.validate_response("", self.question)  # Empty rank position
        assert self.handler.validate_response(None, self.question)  # None
        
        # Invalid responses
        assert not self.handler.validate_response("invalid", self.question)
        assert not self.handler.validate_response("nonexistent", self.question)
    
    def test_format_response_for_export(self):
        """Test response formatting."""
        assert self.handler.format_response_for_export("speed", "spss") == "speed"
        assert self.handler.format_response_for_export("speed", "excel") == "speed"


class TestNotImplementedHandler:
    """Test NotImplementedHandler for unsupported types."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.handler = get_question_handler("F")  # Array type - not implemented
        
        self.question = Question(
            properties=QuestionProperties(
                qid=501,
                question_code="array_q",
                question_type=QuestionType.ARRAY_FLEXIBLE_ROW,  # Use actual enum value
                gid=5,
                sid=12345,
                mandatory=MandatoryState.OPTIONAL,
                question_text="Array question"
            )
        )
    
    def test_not_implemented_methods(self):
        """Test that all methods raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            self.handler.validate_question_structure(self.question)
        
        with pytest.raises(NotImplementedError):
            self.handler.generate_database_fields(self.question)
        
        with pytest.raises(NotImplementedError):
            self.handler.validate_response("test", self.question)
        
        with pytest.raises(NotImplementedError):
            self.handler.format_response_for_export("test", "spss")


class TestQuestionTypeValidation:
    """Test question type validation functions."""
    
    def test_validate_question_attributes_priority_types(self):
        """Test attribute validation for priority types."""
        # Valid attributes for multiple choice
        errors = validate_question_attributes("M", {
            "exclusive_option": "none",
            "other": True
        })
        assert errors == []
        
        # Invalid attribute for single choice (exclusive not supported)
        errors = validate_question_attributes("L", {
            "exclusive_option": "none"
        })
        assert len(errors) == 1
        assert "does not support exclusive options" in errors[0]
        
        # Invalid attribute for short text (other not supported)
        errors = validate_question_attributes("S", {
            "other": True
        })
        assert len(errors) == 1
        assert "does not support 'other' option" in errors[0]
    
    def test_validate_question_attributes_unknown_type(self):
        """Test validation for unknown question types."""
        errors = validate_question_attributes("INVALID", {})
        assert len(errors) == 1
        assert "Unknown question type" in errors[0]
    
    def test_validate_question_attributes_non_priority(self):
        """Test validation for non-priority types (should skip)."""
        # Should return empty list for non-priority types
        errors = validate_question_attributes("F", {
            "exclusive_option": "test"
        })
        assert errors == []


class TestAdvancedQuestionAttributes:
    """Test AdvancedQuestionAttributes functionality."""
    
    def test_default_attributes(self):
        """Test default attribute values."""
        attrs = AdvancedQuestionAttributes()
        
        assert attrs.em_validation_q is None
        assert attrs.exclusive_option is None
        assert attrs.min_answers is None
        assert attrs.max_answers is None
        assert attrs.random_order is False
        assert attrs.answer_order == "normal"
        assert attrs.other_replace_text is None
        assert attrs.assessment_value is None
        assert attrs.hidden is False
        assert attrs.relevance == "1"
        assert attrs.public_statistics is False
    
    def test_custom_attributes(self):
        """Test setting custom attribute values."""
        attrs = AdvancedQuestionAttributes(
            em_validation_q="strlen(feedback.NAOK) <= 500",
            min_answers=2,
            max_answers=5,
            random_order=True,
            assessment_value=1.5
        )
        
        assert attrs.em_validation_q == "strlen(feedback.NAOK) <= 500"
        assert attrs.min_answers == 2
        assert attrs.max_answers == 5
        assert attrs.random_order is True
        assert attrs.assessment_value == 1.5


class TestQuestionTypeIntegration:
    """Test integration between question types and other components."""
    
    def test_question_type_enum_consistency(self):
        """Test that QuestionType enum matches handler expectations."""
        # Priority types should have corresponding enum values
        assert QuestionType.LIST_RADIO.value == "L"
        assert QuestionType.MULTIPLE_CHOICE.value == "M"
        assert QuestionType.SHORT_FREE_TEXT.value == "S"
        assert QuestionType.RANKING.value == "R"
    
    def test_handler_definition_consistency(self):
        """Test that handlers match their definitions."""
        for type_code, definition in PRIORITY_QUESTION_TYPES.items():
            handler = get_question_handler(type_code)
            assert handler.definition == definition
            assert handler.definition.type_code == type_code
            assert handler.definition.is_priority is True
    
    def test_all_defined_types_have_handlers(self):
        """Test that all defined question types have handlers."""
        for type_code in QUESTION_TYPES.keys():
            # Should not raise exception
            handler = get_question_handler(type_code)
            assert handler is not None
            
            # Handler should have the correct definition
            assert handler.definition.type_code == type_code 