#!/usr/bin/env python3
"""
Conditional Graph Visualizer for LimeSurvey Question Dependencies

This module creates graph visualizations of conditional question logic using Graphviz.
Handles missing dependencies gracefully with helpful installation instructions.
"""

import re
import warnings
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass

# Try to import Graphviz with graceful fallback
try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    graphviz = None


@dataclass
class QuestionNode:
    """Represents a question node in the conditional graph."""
    qid: str
    title: str
    question_text: str
    qtype: str
    mandatory: bool
    always_hidden: bool = False
    group_name: str = ""


@dataclass
class ConditionEdge:
    """Represents a conditional dependency edge."""
    from_qid: str
    to_qid: str
    condition_text: str
    condition_type: str  # 'legacy' or 'relevance'
    operator: str = ""
    value: str = ""


class ConditionalGraphVisualizer:
    """
    Creates graph visualizations of LimeSurvey conditional question logic.
    
    Supports both legacy conditions and modern relevance equations.
    Gracefully handles missing Graphviz dependencies.
    """
    
    def __init__(self):
        """Initialize the visualizer with dependency checking."""
        self.nodes: Dict[str, QuestionNode] = {}
        self.edges: List[ConditionEdge] = []
        self._check_dependencies()
    
    def _check_dependencies(self) -> None:
        """Check if required dependencies are available."""
        if not GRAPHVIZ_AVAILABLE:
            instructions = self._get_installation_instructions()
            warnings.warn(
                f"Graphviz not available. Visualization features disabled.\n\n"
                f"To enable graph visualization:\n{instructions}",
                UserWarning
            )
    
    def _get_installation_instructions(self) -> str:
        """Get platform-specific installation instructions."""
        import platform
        system = platform.system().lower()
        
        if system == "darwin":  # macOS
            return (
                "📦 macOS Installation:\n"
                "  1. Install system package: brew install graphviz\n"
                "  2. Install Python package: pip3 install graphviz\n"
                "  3. If issues persist: pip3 install --global-option=build_ext --global-option=\"-I$(brew --prefix graphviz)/include/\" --global-option=\"-L$(brew --prefix graphviz)/lib/\" graphviz"
            )
        else:  # Linux
            return (
                "📦 Linux Installation:\n"
                "  Ubuntu/Debian: sudo apt-get install graphviz && pip3 install graphviz\n"
                "  RHEL/CentOS: sudo yum install graphviz && pip3 install graphviz\n"
                "  Arch: sudo pacman -S graphviz && pip3 install graphviz"
            )
    
    def analyze_survey_graph(self, api, survey_id: str) -> Dict[str, Any]:
        """
        Analyze the complete conditional structure of a survey.
        
        Args:
            api: LimeSurveyDirectAPI instance
            survey_id: Survey ID to analyze
            
        Returns:
            Dictionary containing graph analysis results
        """
        print("🔍 Analyzing survey conditional structure...")
        
        with api:
            # Get all questions and groups
            groups = api.questions.list_groups(survey_id)
            questions = api.questions.list_questions(survey_id)
            
            # Build question nodes
            group_map = {g['gid']: g.get('group_name', f"Group {g['gid']}") for g in groups}
            
            for q in questions:
                node = QuestionNode(
                    qid=q['qid'],
                    title=q.get('title', f"Q{q['qid']}"),
                    question_text=self._clean_text(q.get('question', 'No text')),
                    qtype=q.get('type', 'Unknown'),
                    mandatory=q.get('mandatory') == 'Y',
                    always_hidden=q.get('hidden') == '1',
                    group_name=group_map.get(q.get('gid'), 'Unknown Group')
                )
                self.nodes[q['qid']] = node
            
            # Analyze legacy conditions
            try:
                legacy_conditions = api.questions.list_conditions(survey_id)
                self._process_legacy_conditions(legacy_conditions)
                print(f"   ✅ Legacy conditions analyzed: {len(legacy_conditions)} found")
            except Exception as e:
                print(f"   ⚠️ Legacy conditions API unavailable: {e}")
                print(f"      (This is common - will analyze relevance equations instead)")
            
            # Analyze relevance equations
            try:
                self._process_relevance_equations(api, survey_id, questions)
                relevance_count = sum(1 for e in self.edges if e.condition_type == 'relevance')
                print(f"   ✅ Relevance equations analyzed: {relevance_count} dependencies found")
            except Exception as e:
                print(f"   ⚠️ Relevance equation analysis failed: {e}")
                print(f"      (Will show basic question structure only)")
            
            # Generate analysis
            analysis = self._generate_analysis()
            
            print(f"✅ Graph analysis complete:")
            print(f"   📊 Nodes: {len(self.nodes)}")
            print(f"   🔗 Conditional edges: {len(self.edges)}")
            print(f"   🎯 Questions with dependencies: {analysis['dependent_questions']}")
            
            return analysis
    
    def _process_legacy_conditions(self, conditions: List[Dict]) -> None:
        """Process legacy condition system into graph edges."""
        for condition in conditions:
            # Parse condition
            source_field = condition.get('cfieldname', '')
            target_qid = condition.get('qid')
            method = condition.get('method', '==')
            value = condition.get('value', '')
            
            # Extract source question ID from field name
            source_qid = self._extract_qid_from_fieldname(source_field)
            
            if source_qid and target_qid:
                edge = ConditionEdge(
                    from_qid=source_qid,
                    to_qid=target_qid,
                    condition_text=f"{source_field} {method} '{value}'",
                    condition_type='legacy',
                    operator=method,
                    value=value
                )
                self.edges.append(edge)
    
    def _process_relevance_equations(self, api, survey_id: str, questions: List[Dict]) -> None:
        """Process modern relevance equations into graph edges."""
        for q in questions:
            relevance = q.get('relevance', '1')
            if relevance and relevance.strip() and relevance.strip() != '1':
                # Try to get detailed properties for better relevance info
                try:
                    props = api.questions.get_question_properties(q['qid'])
                    relevance = props.get('relevance', relevance)
                except:
                    pass  # Use the basic relevance from question list
                
                # Parse relevance equation to find dependencies
                referenced_questions = self._parse_relevance_equation(relevance)
                
                for source_qid in referenced_questions:
                    if source_qid in self.nodes:
                        edge = ConditionEdge(
                            from_qid=source_qid,
                            to_qid=q['qid'],
                            condition_text=self._simplify_relevance(relevance),
                            condition_type='relevance',
                            operator='relevance',
                            value=relevance
                        )
                        self.edges.append(edge)
    
    def _extract_qid_from_fieldname(self, fieldname: str) -> Optional[str]:
        """Extract question ID from LimeSurvey field name."""
        # Common patterns: "123456X789X999", "survey_123_question_456"
        patterns = [
            r'(\d+)X\d+X(\d+)',  # Standard LimeSurvey format
            r'question_(\d+)',    # Alternative format
            r'(\d+)$'            # Just question ID
        ]
        
        for pattern in patterns:
            match = re.search(pattern, fieldname)
            if match:
                return match.group(1) if len(match.groups()) == 1 else match.group(2)
        
        return None
    
    def _parse_relevance_equation(self, relevance: str) -> Set[str]:
        """Parse relevance equation to find referenced question IDs."""
        referenced = set()
        
        # Handle None or empty relevance
        if not relevance or not isinstance(relevance, str):
            return referenced
        
        # Create a mapping of question titles to question IDs
        title_to_qid = {node.title: qid for qid, node in self.nodes.items()}
        
        # Common patterns for question references in relevance equations
        patterns = [
            r'(\d+)X\d+X(\d+)',           # Standard LimeSurvey format: 123456X789X999
            r'([A-Za-z0-9_]+)\.NAOK',     # LimeSurvey question code format: G01Q01.NAOK
            r'([A-Za-z0-9_]+)\.value',    # Question value format: QUESTION.value
            r'([A-Za-z0-9_]+)(?=\s*[<>=!])',  # Question followed by operator
            r'is_empty\(([A-Za-z0-9_]+)\.NAOK\)',  # is_empty(G03Q10.NAOK) format
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, relevance)
            for match in matches:
                if isinstance(match, tuple):
                    # Handle tuple matches (from groups in regex)
                    for submatch in match:
                        if submatch:  # Skip empty submatches
                            self._add_reference_if_valid(submatch, referenced, title_to_qid)
                else:
                    # Handle single matches
                    if match:
                        self._add_reference_if_valid(match, referenced, title_to_qid)
        
        return referenced
    
    def _add_reference_if_valid(self, reference: str, referenced: Set[str], title_to_qid: Dict[str, str]) -> None:
        """Add a reference to the set if it corresponds to a valid question."""
        # First try direct question ID lookup
        if reference in self.nodes:
            referenced.add(reference)
            return
            
        # Then try question title lookup
        if reference in title_to_qid:
            referenced.add(title_to_qid[reference])
            return
            
        # For numeric references, check if they exist as question IDs
        if reference.isdigit() and reference in self.nodes:
            referenced.add(reference)
    
    def _simplify_relevance(self, relevance: str) -> str:
        """Simplify relevance equation for display."""
        if len(relevance) > 60:
            return relevance[:60] + "..."
        return relevance
    
    def _clean_text(self, text: str) -> str:
        """Clean HTML and format text for display."""
        import re
        
        # Handle None or non-string input
        if not text or not isinstance(text, str):
            return "No text available"
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Decode common HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Limit length
        return text[:100] + "..." if len(text) > 100 else text
    
    def _generate_analysis(self) -> Dict[str, Any]:
        """Generate summary analysis of the conditional graph."""
        dependent_questions = set(edge.to_qid for edge in self.edges)
        trigger_questions = set(edge.from_qid for edge in self.edges)
        
        # Find isolated questions (no dependencies)
        all_question_ids = set(self.nodes.keys())
        isolated_questions = all_question_ids - dependent_questions - trigger_questions
        
        # Count condition types
        legacy_count = sum(1 for e in self.edges if e.condition_type == 'legacy')
        relevance_count = sum(1 for e in self.edges if e.condition_type == 'relevance')
        
        return {
            'total_questions': len(self.nodes),
            'total_edges': len(self.edges),
            'dependent_questions': len(dependent_questions),
            'trigger_questions': len(trigger_questions),
            'isolated_questions': len(isolated_questions),
            'legacy_conditions': legacy_count,
            'relevance_conditions': relevance_count,
            'nodes': list(self.nodes.keys()),
            'edges': [(e.from_qid, e.to_qid, e.condition_text) for e in self.edges]
        }
    
    def create_graph_visualization(self, output_path: str = "survey_graph", 
                                 format: str = "png", 
                                 show_groups: bool = True) -> Optional[str]:
        """
        Create a Graphviz visualization of the conditional graph.
        
        Args:
            output_path: Output file path (without extension)
            format: Output format ('png', 'svg', 'pdf')
            show_groups: Whether to group questions by survey groups
            
        Returns:
            Path to generated file, or None if Graphviz unavailable
        """
        if not GRAPHVIZ_AVAILABLE:
            print("❌ Graphviz not available. Cannot create visualization.")
            print(self._get_installation_instructions())
            return None
        
        # Create directed graph
        dot = graphviz.Digraph(comment='Survey Conditional Logic')
        dot.attr(rankdir='TB', size='12,8')
        dot.attr('node', shape='box', style='rounded,filled')
        
        if show_groups:
            # Group questions by survey groups
            groups = {}
            for qid, node in self.nodes.items():
                group = node.group_name
                if group not in groups:
                    groups[group] = []
                groups[group].append((qid, node))
            
            # Create subgraphs for each group
            for group_name, group_nodes in groups.items():
                with dot.subgraph(name=f'cluster_{group_name}') as cluster:
                    cluster.attr(label=group_name, style='dashed')
                    
                    for qid, node in group_nodes:
                        self._add_node_to_graph(cluster, qid, node)
        else:
            # Add all nodes without grouping
            for qid, node in self.nodes.items():
                self._add_node_to_graph(dot, qid, node)
        
        # Add edges
        for edge in self.edges:
            color = 'blue' if edge.condition_type == 'legacy' else 'green'
            style = 'solid' if edge.condition_type == 'legacy' else 'dashed'
            
            # Safely handle condition text for edge label
            condition_label = edge.condition_text if edge.condition_text else "condition"
            condition_label = condition_label.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
            if len(condition_label) > 50:
                condition_label = condition_label[:50] + "..."
            
            dot.edge(
                str(edge.from_qid),  # Ensure string
                str(edge.to_qid),    # Ensure string
                label=condition_label,
                color=color,
                style=style
            )
        
        # Render the graph
        try:
            output_file = dot.render(output_path, format=format, cleanup=True)
            print(f"✅ Graph visualization saved to: {output_file}")
            return output_file
        except Exception as e:
            print(f"❌ Failed to render graph: {e}")
            return None
    
    def _add_node_to_graph(self, graph, qid: str, node: QuestionNode) -> None:
        """Add a question node to the graph with appropriate styling."""
        # Choose node color based on properties
        if node.always_hidden:
            fillcolor = 'lightgray'
        elif node.mandatory:
            fillcolor = 'lightcoral'
        else:
            fillcolor = 'lightblue'
        
        # Create node label with safe string handling
        title = node.title if node.title else f"Q{qid}"
        qtype = node.qtype if node.qtype else 'Unknown'
        
        label = f"{title}\\n({qtype})"
        
        # Safely handle question text
        question_text = node.question_text if node.question_text else ""
        if len(question_text) > 0:
            # Clean and truncate question text for label
            clean_text = question_text.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
            if len(clean_text) > 40:
                clean_text = clean_text[:40] + "..."
            label += f"\\n{clean_text}"
        
        # Safely handle tooltip
        tooltip = question_text if question_text else f"Question {qid}"
        tooltip = tooltip.replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
        
        graph.node(
            str(qid),  # Ensure qid is string
            label=label,
            fillcolor=fillcolor,
            tooltip=tooltip
        )
    
    def export_graph_data(self, output_path: str = "survey_graph.json") -> str:
        """
        Export graph data as JSON for use with other visualization tools.
        
        Args:
            output_path: Path to save JSON file
            
        Returns:
            Path to exported JSON file
        """
        import json
        from datetime import datetime
        
        # Prepare data for JSON export
        graph_data = {
            'metadata': {
                'total_questions': len(self.nodes),
                'total_edges': len(self.edges),
                'generated_at': datetime.now().isoformat()
            },
            'nodes': [
                {
                    'id': qid,
                    'title': node.title,
                    'question_text': node.question_text,
                    'type': node.qtype,
                    'mandatory': node.mandatory,
                    'always_hidden': node.always_hidden,
                    'group': node.group_name
                }
                for qid, node in self.nodes.items()
            ],
            'edges': [
                {
                    'from': edge.from_qid,
                    'to': edge.to_qid,
                    'condition': edge.condition_text,
                    'type': edge.condition_type,
                    'operator': edge.operator,
                    'value': edge.value
                }
                for edge in self.edges
            ]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Graph data exported to: {output_path}")
        return output_path
    
    def print_graph_summary(self) -> None:
        """Print a text-based summary of the conditional graph."""
        print("\n📊 Conditional Graph Summary")
        print("=" * 50)
        
        analysis = self._generate_analysis()
        
        print(f"📊 Total Questions: {analysis['total_questions']}")
        print(f"🔗 Conditional Dependencies: {analysis['total_edges']}")
        print(f"🎯 Questions with Dependencies: {analysis['dependent_questions']}")
        print(f"🚀 Trigger Questions: {analysis['trigger_questions']}")
        print(f"🏝️ Isolated Questions: {analysis['isolated_questions']}")
        print(f"📜 Legacy Conditions: {analysis['legacy_conditions']}")
        print(f"🔧 Relevance Conditions: {analysis['relevance_conditions']}")
        
        if self.edges:
            print(f"\n🔗 Dependencies:")
            for edge in self.edges[:10]:  # Show first 10
                from_title = self.nodes.get(edge.from_qid, {}).title or edge.from_qid
                to_title = self.nodes.get(edge.to_qid, {}).title or edge.to_qid
                print(f"   {from_title} → {to_title}: {edge.condition_text}")
            
            if len(self.edges) > 10:
                print(f"   ... and {len(self.edges) - 10} more dependencies")
        else:
            print("\n✅ No conditional dependencies found (all questions always shown)")


def create_survey_graph(api, survey_id: str, output_path: str = "survey_graph") -> Dict[str, Any]:
    """
    Convenience function to create a complete survey conditional graph.
    
    Args:
        api: LimeSurveyDirectAPI instance
        survey_id: Survey ID to analyze
        output_path: Base path for output files
        
    Returns:
        Dictionary containing analysis results and file paths
    """
    visualizer = ConditionalGraphVisualizer()
    
    # Analyze the survey
    analysis = visualizer.analyze_survey_graph(api, survey_id)
    
    # Print summary
    visualizer.print_graph_summary()
    
    # Export data
    json_path = visualizer.export_graph_data(f"{output_path}_data.json")
    
    # Try to create visualization
    graph_path = visualizer.create_graph_visualization(output_path, format='png')
    
    return {
        'analysis': analysis,
        'json_export': json_path,
        'graph_image': graph_path,
        'graphviz_available': GRAPHVIZ_AVAILABLE
    } 