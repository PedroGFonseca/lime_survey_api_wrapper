#!/usr/bin/env python3
"""
Data Structures for Visualization-Friendly Survey Analysis

Defines structured output formats optimized for visualization libraries,
providing clean separation between metadata, preprocessed data, and statistics.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Tuple
from enum import Enum


class QuestionType(Enum):
    """Supported question types"""
    RADIO = "radio"
    MULTIPLE_CHOICE = "multiple_choice"
    RANKING = "ranking"
    TEXT = "text"
    ARRAY = "array"
    MULTIPLE_SHORT_TEXT = "multiple_short_text"


class ChartType(Enum):
    """Recommended chart types for visualization"""
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    HORIZONTAL_BAR = "horizontal_bar"
    STACKED_BAR = "stacked_bar"
    HEATMAP = "heatmap"
    WORD_CLOUD = "word_cloud"
    TABLE = "table"
    SCATTER_PLOT = "scatter_plot"
    LINE_CHART = "line_chart"


@dataclass
class ConditionalLogic:
    """Represents conditional display logic for a question"""
    source_question_id: str
    source_question_code: str
    source_question_title: str
    condition_type: str  # equals, not_equals, greater_than, etc.
    condition_value: str
    condition_value_text: str  # Human-readable version


@dataclass
class QuestionMetadata:
    """Metadata about the question for visualization context"""
    question_id: str
    question_code: str
    question_title: str
    question_type: QuestionType
    is_mandatory: bool
    
    # Optional metadata
    question_order: Optional[int] = None
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    
    # Conditional logic
    conditional_logic: Optional[List[ConditionalLogic]] = None
    
    # Question-specific metadata
    allows_other: bool = False
    max_answers: Optional[int] = None  # For ranking questions
    allows_multiple_selection: bool = False  # For multiple choice
    
    # Response metadata
    total_possible_responses: int = 0
    actual_responses: int = 0
    response_rate: float = 0.0
    completion_rate: float = 0.0


@dataclass
class StatisticalSummary:
    """Statistical summary for the question"""
    # Basic counts
    total_responses: int
    valid_responses: int
    missing_responses: int
    
    # Percentages
    response_rate: float  # valid_responses / total_possible
    completion_rate: float  # (valid + missing) / total_possible
    
    # Question-type specific statistics
    unique_values: Optional[int] = None  # For text questions
    average_selections: Optional[float] = None  # For multiple choice
    average_text_length: Optional[float] = None  # For text questions
    most_common_rank: Optional[Dict[str, int]] = None  # For ranking


@dataclass
class VisualizationHints:
    """Hints for visualization libraries"""
    recommended_charts: List[ChartType]
    optimal_chart: ChartType
    
    # Chart-specific hints
    color_palette: Optional[List[str]] = None
    sort_order: Optional[str] = None  # ascending, descending, custom
    group_small_categories: bool = False
    max_categories_display: Optional[int] = None
    
    # Layout hints
    needs_rotation: bool = False  # For long labels
    suggested_width: Optional[int] = None
    suggested_height: Optional[int] = None


@dataclass
class QuestionAnalysisResult:
    """
    Comprehensive analysis result optimized for visualization libraries.
    
    Provides clean separation of concerns:
    - Metadata: Question context and properties
    - Raw data: Standardized preprocessed responses
    - Statistics: Ready-to-visualize aggregations
    - Hints: Guidance for chart selection and formatting
    """
    
    # Core identification
    metadata: QuestionMetadata
    
    # Preprocessed data (standardized format)
    raw_data: Optional[pd.DataFrame] = None
    
    # Statistics (ready for visualization)
    statistics: Dict[str, Union[pd.Series, pd.DataFrame]] = field(default_factory=dict)
    
    # Analysis summary
    summary: Optional[StatisticalSummary] = None
    
    # Visualization guidance
    viz_hints: Optional[VisualizationHints] = None
    
    # Legacy compatibility (for backward compatibility during transition)
    legacy_result: Optional[Union[pd.Series, pd.DataFrame, Dict]] = None
    
    def get_primary_statistic(self) -> Union[pd.Series, pd.DataFrame]:
        """Get the primary statistic for this question type"""
        if self.metadata.question_type == QuestionType.RADIO:
            return self.statistics.get('value_counts', pd.Series())
        elif self.metadata.question_type == QuestionType.MULTIPLE_CHOICE:
            return self.statistics.get('response_analysis', pd.DataFrame())
        elif self.metadata.question_type == QuestionType.RANKING:
            return self.statistics.get('ranking_matrix', pd.DataFrame())
        elif self.metadata.question_type == QuestionType.TEXT:
            return self.statistics.get('text_responses', pd.Series())
        elif self.metadata.question_type == QuestionType.ARRAY:
            return self.statistics.get('array_responses', pd.DataFrame())
        elif self.metadata.question_type == QuestionType.MULTIPLE_SHORT_TEXT:
            return self.statistics.get('text_by_subquestion', {})
        else:
            # Return first available statistic
            return next(iter(self.statistics.values())) if self.statistics else pd.Series()
    
    def get_chart_data(self, chart_type: ChartType) -> Union[pd.Series, pd.DataFrame, Dict]:
        """Get data formatted for specific chart type"""
        if chart_type == ChartType.BAR_CHART:
            return self._get_bar_chart_data()
        elif chart_type == ChartType.PIE_CHART:
            return self._get_pie_chart_data()
        elif chart_type == ChartType.HEATMAP:
            return self._get_heatmap_data()
        elif chart_type == ChartType.TABLE:
            return self._get_table_data()
        else:
            return self.get_primary_statistic()
    
    def _get_bar_chart_data(self) -> pd.Series:
        """Get data suitable for bar charts"""
        if self.metadata.question_type in [QuestionType.RADIO]:
            return self.statistics.get('value_counts', pd.Series())
        elif self.metadata.question_type == QuestionType.MULTIPLE_CHOICE:
            df = self.statistics.get('response_analysis', pd.DataFrame())
            if 'absolute_counts' in df.columns and 'option_text' in df.columns:
                return df.set_index('option_text')['absolute_counts']
        return pd.Series()
    
    def _get_pie_chart_data(self) -> pd.Series:
        """Get data suitable for pie charts"""
        # Similar to bar chart but might apply minimum threshold
        data = self._get_bar_chart_data()
        if self.viz_hints and self.viz_hints.group_small_categories:
            # Group categories below threshold
            threshold = 0.05  # 5% threshold
            total = data.sum()
            small_categories = data[data < (total * threshold)]
            if len(small_categories) > 1:
                large_categories = data[data >= (total * threshold)]
                other_total = small_categories.sum()
                result = large_categories.copy()
                result['Other'] = other_total
                return result
        return data
    
    def _get_heatmap_data(self) -> pd.DataFrame:
        """Get data suitable for heatmaps"""
        if self.metadata.question_type == QuestionType.RANKING:
            return self.statistics.get('ranking_matrix', pd.DataFrame())
        elif self.metadata.question_type == QuestionType.ARRAY:
            return self.statistics.get('array_responses', pd.DataFrame())
        return pd.DataFrame()
    
    def _get_table_data(self) -> pd.DataFrame:
        """Get data suitable for tables"""
        primary = self.get_primary_statistic()
        if isinstance(primary, pd.Series):
            return primary.to_frame('Count')
        elif isinstance(primary, pd.DataFrame):
            return primary
        else:
            return pd.DataFrame()


@dataclass
class CrossAnalysisResult:
    """Result for cross-question analysis (e.g., gender vs voting intention)"""
    
    # Source questions
    question1_metadata: QuestionMetadata
    question2_metadata: QuestionMetadata
    
    # Cross-tabulation data
    crosstab: pd.DataFrame
    
    # Statistical tests (if applicable)
    chi_square_stat: Optional[float] = None
    p_value: Optional[float] = None
    cramers_v: Optional[float] = None
    
    # Visualization hints
    viz_hints: Optional[VisualizationHints] = None


@dataclass
class SurveyAnalysisResults:
    """Complete survey analysis results"""
    
    # Survey metadata
    survey_id: str
    survey_title: Optional[str] = None
    total_questions: int = 0
    total_responses: int = 0
    
    # Individual question results
    question_results: Dict[str, QuestionAnalysisResult] = field(default_factory=dict)
    
    # Cross-analysis results
    cross_analyses: Dict[Tuple[str, str], CrossAnalysisResult] = field(default_factory=dict)
    
    # Summary statistics
    overall_completion_rate: float = 0.0
    questions_processed: int = 0
    questions_failed: int = 0
    
    def get_question_result(self, question_id: str) -> Optional[QuestionAnalysisResult]:
        """Get result for specific question"""
        return self.question_results.get(question_id)
    
    def get_cross_analysis(self, question1_id: str, question2_id: str) -> Optional[CrossAnalysisResult]:
        """Get cross-analysis result between two questions"""
        key = (question1_id, question2_id)
        return self.cross_analyses.get(key) or self.cross_analyses.get((question2_id, question1_id))
    
    def get_questions_by_type(self, question_type: QuestionType) -> List[QuestionAnalysisResult]:
        """Get all questions of a specific type"""
        return [result for result in self.question_results.values() 
                if result.metadata.question_type == question_type]


# Factory functions for common visualizations
def create_visualization_hints_for_question_type(question_type: QuestionType, 
                                                data_summary: Optional[Dict] = None) -> VisualizationHints:
    """Create appropriate visualization hints based on question type"""
    
    if question_type == QuestionType.RADIO:
        return VisualizationHints(
            recommended_charts=[ChartType.BAR_CHART, ChartType.PIE_CHART, ChartType.HORIZONTAL_BAR],
            optimal_chart=ChartType.BAR_CHART,
            sort_order="descending",
            max_categories_display=10
        )
    
    elif question_type == QuestionType.MULTIPLE_CHOICE:
        return VisualizationHints(
            recommended_charts=[ChartType.HORIZONTAL_BAR, ChartType.STACKED_BAR, ChartType.TABLE],
            optimal_chart=ChartType.HORIZONTAL_BAR,
            sort_order="descending",
            group_small_categories=True
        )
    
    elif question_type == QuestionType.RANKING:
        return VisualizationHints(
            recommended_charts=[ChartType.HEATMAP, ChartType.STACKED_BAR, ChartType.TABLE],
            optimal_chart=ChartType.HEATMAP,
            color_palette=["#f7fbff", "#08519c"]  # Blues
        )
    
    elif question_type == QuestionType.TEXT:
        return VisualizationHints(
            recommended_charts=[ChartType.WORD_CLOUD, ChartType.TABLE],
            optimal_chart=ChartType.WORD_CLOUD
        )
    
    elif question_type == QuestionType.ARRAY:
        return VisualizationHints(
            recommended_charts=[ChartType.STACKED_BAR, ChartType.HEATMAP, ChartType.TABLE],
            optimal_chart=ChartType.STACKED_BAR,
            color_palette=["#d73027", "#f7f7f7", "#1a9850"]  # Red-Gray-Green
        )
    
    elif question_type == QuestionType.MULTIPLE_SHORT_TEXT:
        return VisualizationHints(
            recommended_charts=[ChartType.TABLE],
            optimal_chart=ChartType.TABLE
        )
    
    else:
        return VisualizationHints(
            recommended_charts=[ChartType.TABLE],
            optimal_chart=ChartType.TABLE
        )


# Backward compatibility helpers
class BackwardCompatibilityWrapper:
    """Wrapper to maintain current API during transition"""
    
    @staticmethod
    def to_legacy_format(result: QuestionAnalysisResult) -> Union[pd.Series, pd.DataFrame, Dict]:
        """Convert new format back to current handler output format"""
        
        if result.legacy_result is not None:
            return result.legacy_result
        
        question_type = result.metadata.question_type
        
        if question_type == QuestionType.RADIO:
            return result.statistics.get('value_counts', pd.Series())
        
        elif question_type == QuestionType.MULTIPLE_CHOICE:
            return result.statistics.get('response_analysis', pd.DataFrame())
        
        elif question_type == QuestionType.RANKING:
            return result.statistics.get('ranking_matrix', pd.DataFrame())
        
        elif question_type == QuestionType.TEXT:
            return result.statistics.get('text_responses', pd.Series())
        
        elif question_type == QuestionType.ARRAY:
            return result.statistics.get('array_responses', pd.DataFrame())
        
        elif question_type == QuestionType.MULTIPLE_SHORT_TEXT:
            return result.statistics.get('text_by_subquestion', {})
        
        else:
            return result.get_primary_statistic()
    
    @staticmethod
    def from_legacy_format(question_id: str, question_code: str, question_title: str,
                          question_type: QuestionType, legacy_result: Union[pd.Series, pd.DataFrame, Dict],
                          **metadata_kwargs) -> QuestionAnalysisResult:
        """Create new format from legacy handler output"""
        
        metadata = QuestionMetadata(
            question_id=question_id,
            question_code=question_code,
            question_title=question_title,
            question_type=question_type,
            **metadata_kwargs
        )
        
        statistics = {}
        if question_type == QuestionType.RADIO and isinstance(legacy_result, pd.Series):
            statistics['value_counts'] = legacy_result
        elif question_type == QuestionType.MULTIPLE_CHOICE and isinstance(legacy_result, pd.DataFrame):
            statistics['response_analysis'] = legacy_result
        elif question_type == QuestionType.RANKING and isinstance(legacy_result, pd.DataFrame):
            statistics['ranking_matrix'] = legacy_result
        elif question_type == QuestionType.TEXT and isinstance(legacy_result, pd.Series):
            statistics['text_responses'] = legacy_result
        elif question_type == QuestionType.ARRAY and isinstance(legacy_result, pd.DataFrame):
            statistics['array_responses'] = legacy_result
        elif question_type == QuestionType.MULTIPLE_SHORT_TEXT and isinstance(legacy_result, dict):
            statistics['text_by_subquestion'] = legacy_result
        
        viz_hints = create_visualization_hints_for_question_type(question_type)
        
        return QuestionAnalysisResult(
            metadata=metadata,
            statistics=statistics,
            viz_hints=viz_hints,
            legacy_result=legacy_result
        ) 