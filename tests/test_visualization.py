"""Tests for the visualization system."""

import json
import pytest
import warnings
from unittest.mock import patch, MagicMock
from pathlib import Path

from lime_survey_analyzer.visualizations.conditional_graph import (
    ConditionalGraphVisualizer, 
    QuestionNode, 
    ConditionEdge,
    create_survey_graph
)


class TestQuestionNode:
    """Test QuestionNode dataclass."""
    
    def test_create_question_node(self):
        """Test creating a question node."""
        node = QuestionNode(
            qid="123",
            title="Q1",
            question_text="What is your age?",
            qtype="N",
            mandatory=True,
            always_hidden=False,
            group_name="Demographics"
        )
        
        assert node.qid == "123"
        assert node.title == "Q1"
        assert node.question_text == "What is your age?"
        assert node.qtype == "N"
        assert node.mandatory is True
        assert node.always_hidden is False
        assert node.group_name == "Demographics"


class TestConditionEdge:
    """Test ConditionEdge dataclass."""
    
    def test_create_condition_edge(self):
        """Test creating a condition edge."""
        edge = ConditionEdge(
            from_qid="123",
            to_qid="456",
            condition_text="Q1 == 'Yes'",
            condition_type="relevance",
            operator="==",
            value="Yes"
        )
        
        assert edge.from_qid == "123"
        assert edge.to_qid == "456"
        assert edge.condition_text == "Q1 == 'Yes'"
        assert edge.condition_type == "relevance"
        assert edge.operator == "=="
        assert edge.value == "Yes"


class TestConditionalGraphVisualizer:
    """Test ConditionalGraphVisualizer class."""
    
    def test_init(self):
        """Test visualizer initialization."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")  # Ignore Graphviz warnings for testing
            viz = ConditionalGraphVisualizer()
            
        assert viz.nodes == {}
        assert viz.edges == []
    
    def test_get_installation_instructions_macos(self):
        """Test macOS installation instructions."""
        viz = ConditionalGraphVisualizer()
        
        with patch('platform.system', return_value='Darwin'):
            instructions = viz._get_installation_instructions()
            
        assert "brew install graphviz" in instructions
        assert "pip3 install graphviz" in instructions
        assert "macOS" in instructions
    
    def test_get_installation_instructions_linux(self):
        """Test Linux installation instructions."""
        viz = ConditionalGraphVisualizer()
        
        with patch('platform.system', return_value='Linux'):
            instructions = viz._get_installation_instructions()
            
        assert "apt-get install graphviz" in instructions
        assert "pip3 install graphviz" in instructions
        assert "Linux" in instructions
    
    def test_clean_text_normal(self):
        """Test text cleaning with normal text."""
        viz = ConditionalGraphVisualizer()
        
        result = viz._clean_text("What is your age?")
        assert result == "What is your age?"
    
    def test_clean_text_with_html(self):
        """Test text cleaning with HTML tags."""
        viz = ConditionalGraphVisualizer()
        
        result = viz._clean_text("<p>What is your <strong>age</strong>?</p>")
        assert result == "What is your age?"
    
    def test_clean_text_with_entities(self):
        """Test text cleaning with HTML entities."""
        viz = ConditionalGraphVisualizer()
        
        result = viz._clean_text("Age &gt; 18 &amp; &lt; 65")
        assert result == "Age > 18 & < 65"
    
    def test_clean_text_long(self):
        """Test text cleaning with long text."""
        viz = ConditionalGraphVisualizer()
        
        long_text = "A" * 150
        result = viz._clean_text(long_text)
        assert len(result) == 103  # 100 + "..."
        assert result.endswith("...")
    
    def test_clean_text_none(self):
        """Test text cleaning with None input."""
        viz = ConditionalGraphVisualizer()
        
        result = viz._clean_text(None)
        assert result == "No text available"
    
    def test_clean_text_empty(self):
        """Test text cleaning with empty string."""
        viz = ConditionalGraphVisualizer()
        
        result = viz._clean_text("")
        assert result == "No text available"
    
    def test_parse_relevance_equation_none(self):
        """Test parsing None relevance equation."""
        viz = ConditionalGraphVisualizer()
        
        result = viz._parse_relevance_equation(None)
        assert result == set()
    
    def test_parse_relevance_equation_empty(self):
        """Test parsing empty relevance equation."""
        viz = ConditionalGraphVisualizer()
        
        result = viz._parse_relevance_equation("")
        assert result == set()
    
    def test_parse_relevance_equation_simple(self):
        """Test parsing simple relevance equation."""
        viz = ConditionalGraphVisualizer()
        
        # Add some test nodes
        viz.nodes = {
            "123": QuestionNode("123", "Q1", "Question 1", "L", False, False, "Group1"),
            "456": QuestionNode("456", "Q2", "Question 2", "L", False, False, "Group1")
        }
        
        result = viz._parse_relevance_equation("123 == 'Yes'")
        assert "123" in result
    
    def test_parse_relevance_equation_with_naok(self):
        """Test parsing relevance equation with .NAOK format."""
        viz = ConditionalGraphVisualizer()
        
        # Add test nodes with question codes
        viz.nodes = {
            "123": QuestionNode("123", "G01Q01", "Question 1", "L", False, False, "Group1"),
            "456": QuestionNode("456", "G01Q02", "Question 2", "L", False, False, "Group1")
        }
        
        result = viz._parse_relevance_equation("((G01Q01.NAOK == 'Y'))")
        assert "123" in result
    
    def test_parse_relevance_equation_with_is_empty(self):
        """Test parsing relevance equation with is_empty function."""
        viz = ConditionalGraphVisualizer()
        
        # Add test nodes
        viz.nodes = {
            "123": QuestionNode("123", "G01Q01", "Question 1", "L", False, False, "Group1")
        }
        
        result = viz._parse_relevance_equation("is_empty(G01Q01.NAOK)")
        assert "123" in result
    
    def test_simplify_relevance_short(self):
        """Test simplifying short relevance equation."""
        viz = ConditionalGraphVisualizer()
        
        short_relevance = "Q1 == 'Yes'"
        result = viz._simplify_relevance(short_relevance)
        assert result == "Q1 == 'Yes'"
    
    def test_simplify_relevance_long(self):
        """Test simplifying long relevance equation."""
        viz = ConditionalGraphVisualizer()
        
        long_relevance = "A" * 80
        result = viz._simplify_relevance(long_relevance)
        assert len(result) == 63  # 60 + "..."
        assert result.endswith("...")
    
    def test_generate_analysis_empty(self):
        """Test analysis generation with empty graph."""
        viz = ConditionalGraphVisualizer()
        
        analysis = viz._generate_analysis()
        
        assert analysis['total_questions'] == 0
        assert analysis['total_edges'] == 0
        assert analysis['dependent_questions'] == 0
        assert analysis['trigger_questions'] == 0
        assert analysis['isolated_questions'] == 0
        assert analysis['legacy_conditions'] == 0
        assert analysis['relevance_conditions'] == 0
    
    def test_generate_analysis_with_data(self):
        """Test analysis generation with sample data."""
        viz = ConditionalGraphVisualizer()
        
        # Add test nodes
        viz.nodes = {
            "123": QuestionNode("123", "Q1", "Question 1", "L", False, False, "Group1"),
            "456": QuestionNode("456", "Q2", "Question 2", "L", False, False, "Group1"),
            "789": QuestionNode("789", "Q3", "Question 3", "L", False, False, "Group1")
        }
        
        # Add test edges
        viz.edges = [
            ConditionEdge("123", "456", "Q1 == 'Yes'", "relevance", "==", "Yes"),
            ConditionEdge("123", "789", "Q1 == 'No'", "legacy", "==", "No")
        ]
        
        analysis = viz._generate_analysis()
        
        assert analysis['total_questions'] == 3
        assert analysis['total_edges'] == 2
        assert analysis['dependent_questions'] == 2  # Q2 and Q3 depend on Q1
        assert analysis['trigger_questions'] == 1   # Q1 triggers others
        assert analysis['isolated_questions'] == 0  # All questions are connected
        assert analysis['legacy_conditions'] == 1
        assert analysis['relevance_conditions'] == 1
    
    def test_export_graph_data(self, tmp_path):
        """Test JSON export functionality."""
        viz = ConditionalGraphVisualizer()
        
        # Add test data
        viz.nodes = {
            "123": QuestionNode("123", "Q1", "Question 1", "L", True, False, "Group1")
        }
        viz.edges = [
            ConditionEdge("123", "456", "Q1 == 'Yes'", "relevance", "==", "Yes")
        ]
        
        output_file = tmp_path / "test_export.json"
        result_path = viz.export_graph_data(str(output_file))
        
        # Verify file was created
        assert Path(result_path).exists()
        
        # Verify content
        with open(result_path, 'r') as f:
            data = json.load(f)
        
        assert data['metadata']['total_questions'] == 1
        assert data['metadata']['total_edges'] == 1
        assert len(data['nodes']) == 1
        assert len(data['edges']) == 1
        assert data['nodes'][0]['title'] == "Q1"
        assert data['edges'][0]['condition'] == "Q1 == 'Yes'"
    
    def test_print_graph_summary_empty(self, capsys):
        """Test printing summary for empty graph."""
        viz = ConditionalGraphVisualizer()
        
        viz.print_graph_summary()
        
        captured = capsys.readouterr()
        assert "Total Questions: 0" in captured.out
        assert "Conditional Dependencies: 0" in captured.out
        assert "No conditional dependencies found" in captured.out
    
    def test_print_graph_summary_with_data(self, capsys):
        """Test printing summary with data."""
        viz = ConditionalGraphVisualizer()
        
        # Add test data
        viz.nodes = {
            "123": QuestionNode("123", "Q1", "Question 1", "L", False, False, "Group1"),
            "456": QuestionNode("456", "Q2", "Question 2", "L", False, False, "Group1")
        }
        viz.edges = [
            ConditionEdge("123", "456", "Q1 == 'Yes'", "relevance", "==", "Yes")
        ]
        
        viz.print_graph_summary()
        
        captured = capsys.readouterr()
        assert "Total Questions: 2" in captured.out
        assert "Conditional Dependencies: 1" in captured.out
        assert "Q1 → Q2" in captured.out
    
    @patch('lime_survey_analyzer.visualizations.conditional_graph.GRAPHVIZ_AVAILABLE', False)
    def test_create_graph_visualization_no_graphviz(self, capsys):
        """Test graph visualization when Graphviz is not available."""
        viz = ConditionalGraphVisualizer()
        
        result = viz.create_graph_visualization()
        
        assert result is None
        captured = capsys.readouterr()
        assert "Graphviz not available" in captured.out
    
    @patch('lime_survey_analyzer.visualizations.conditional_graph.GRAPHVIZ_AVAILABLE', True)
    @patch('lime_survey_analyzer.visualizations.conditional_graph.graphviz')
    def test_create_graph_visualization_success(self, mock_graphviz):
        """Test successful graph visualization creation."""
        viz = ConditionalGraphVisualizer()
        
        # Setup mock
        mock_dot = MagicMock()
        mock_dot.render.return_value = "test_graph.png"
        mock_graphviz.Digraph.return_value = mock_dot
        
        # Add test data
        viz.nodes = {
            "123": QuestionNode("123", "Q1", "Question 1", "L", False, False, "Group1")
        }
        
        result = viz.create_graph_visualization("test_output")
        
        assert result == "test_graph.png"
        mock_dot.render.assert_called_once()
    
    @patch('lime_survey_analyzer.visualizations.conditional_graph.GRAPHVIZ_AVAILABLE', True)
    @patch('lime_survey_analyzer.visualizations.conditional_graph.graphviz')
    def test_create_graph_visualization_render_error(self, mock_graphviz, capsys):
        """Test graph visualization with render error."""
        viz = ConditionalGraphVisualizer()
        
        # Setup mock to raise error
        mock_dot = MagicMock()
        mock_dot.render.side_effect = Exception("Render failed")
        mock_graphviz.Digraph.return_value = mock_dot
        
        result = viz.create_graph_visualization("test_output")
        
        assert result is None
        captured = capsys.readouterr()
        assert "Failed to render graph" in captured.out


class TestCreateSurveyGraph:
    """Test the create_survey_graph convenience function."""
    
    @patch('lime_survey_analyzer.visualizations.conditional_graph.ConditionalGraphVisualizer')
    def test_create_survey_graph(self, mock_visualizer_class):
        """Test the create_survey_graph function."""
        # Setup mocks
        mock_api = MagicMock()
        mock_viz = MagicMock()
        mock_visualizer_class.return_value = mock_viz
        
        mock_viz.analyze_survey_graph.return_value = {'test': 'analysis'}
        mock_viz.export_graph_data.return_value = "test.json"
        mock_viz.create_graph_visualization.return_value = "test.png"
        
        # Call function
        result = create_survey_graph(mock_api, "123", "output")
        
        # Verify calls
        mock_viz.analyze_survey_graph.assert_called_once_with(mock_api, "123")
        mock_viz.print_graph_summary.assert_called_once()
        mock_viz.export_graph_data.assert_called_once_with("output_data.json")
        mock_viz.create_graph_visualization.assert_called_once_with("output", format='png')
        
        # Verify result
        assert result['analysis'] == {'test': 'analysis'}
        assert result['json_export'] == "test.json"
        assert result['graph_image'] == "test.png" 