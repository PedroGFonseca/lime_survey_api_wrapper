"""
Type definitions for LimeSurvey Analyzer package.

This module contains TypedDict definitions, Protocol interfaces, and other type annotations
to provide strict type safety throughout the package.
"""

from typing import Dict, List, Optional, Union, TypedDict, Protocol, Any, Literal
import pandas as pd
from datetime import datetime


# API Response Types
class SurveyProperties(TypedDict, total=False):
    """Survey properties from LimeSurvey API."""
    sid: str
    surveyls_title: str
    surveyls_description: str
    surveyls_welcome: str
    surveyls_endtext: str
    surveyls_language: str
    active: str
    anonymized: str
    format: str
    savetimings: str
    template: str
    language: str
    datestamp: str
    usecookie: str
    allowregister: str
    allowsave: str
    autonumber_start: str
    autoredirect: str
    allowprev: str
    printanswers: str
    ipaddr: str
    refurl: str
    showsurveypolicynotice: str


class SurveySummary(TypedDict, total=False):
    """Survey summary statistics from API."""
    completed: int
    incomplete: int
    total: int


class QuestionData(TypedDict):
    """Question data structure from API."""
    qid: str
    parent_qid: str
    gid: str
    type: str
    title: str
    question: str
    preg: str
    help: str
    other: str
    mandatory: str
    question_order: str
    language: str
    scale_id: str
    same_default: str
    relevance: str
    modulename: str
    question_theme_name: str


class OptionData(TypedDict):
    """Option data structure for questions."""
    qid: str
    option_code: str
    answer: str
    option_order: int
    question_code: str
    assessment_value: Optional[str]


class ResponseMetadata(TypedDict, total=False):
    """Response metadata structure."""
    id: str
    submitdate: Optional[str]
    lastpage: Optional[int]
    startlanguage: str
    seed: Optional[str]
    startdate: Optional[str]
    datestamp: Optional[str]
    refurl: Optional[str]


class GroupData(TypedDict):
    """Question group data structure."""
    gid: str
    group_name: str
    group_order: str
    description: str
    language: str
    randomization_group: str
    grelevance: str


# Analysis Result Types
class QuestionStatistics(TypedDict, total=False):
    """Statistics for a single question."""
    value_counts: pd.Series
    response_analysis: pd.DataFrame
    ranking_matrix: pd.DataFrame
    text_responses: pd.Series
    array_responses: pd.DataFrame
    text_by_subquestion: Dict[str, pd.Series]


class ProcessedResponse(TypedDict, total=False):
    """Processed response data for a question."""
    question_id: str
    question_type: str
    data: Union[pd.Series, pd.DataFrame, Dict[str, pd.Series]]
    statistics: QuestionStatistics
    metadata: Dict[str, Any]


# Configuration Types
class AnalysisConfig(TypedDict, total=False):
    """Configuration for survey analysis."""
    keep_incomplete_responses: bool
    cache_enabled: bool
    cache_ttl_hours: int
    max_retries: int
    timeout_seconds: int
    bypass_cache: bool
    test_mode: bool


class CacheConfig(TypedDict, total=False):
    """Configuration for caching system."""
    cache_dir: str
    cache_ttl_hours: int
    enabled: bool
    bypass_cache: bool
    test_mode: bool


# Question Types
QuestionType = Literal[
    'listradio',           # Radio buttons
    'multiplechoice',      # Multiple choice 
    'ranking',             # Ranking
    'shortfreetext',       # Short text
    'longfreetext',        # Long text
    'numerical',           # Numerical input
    'equation',            # Equation
    'multipleshorttext',   # Multiple short text
    'arrays/increasesamedecrease',  # Array questions
    'image_select-listradio',       # Image select radio
    'image_select-multiplechoice'   # Image select multiple choice
]

ResponseStatus = Literal['complete', 'incomplete', 'all']
ExportFormat = Literal['json', 'csv', 'xml', 'excel', 'pdf']
HeadingType = Literal['code', 'full', 'abbreviated']
ResponseDetailType = Literal['short', 'long']


# Protocol Interfaces
class APIClient(Protocol):
    """Protocol for LimeSurvey API clients."""
    
    def export_responses(
        self, 
        survey_id: str, 
        document_type: ExportFormat = 'json',
        language_code: Optional[str] = None,
        completion_status: ResponseStatus = 'all',
        heading_type: HeadingType = 'code',
        response_type: ResponseDetailType = 'short'
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], str]:
        """Export survey responses."""
        ...
    
    def get_survey_properties(self, survey_id: str) -> SurveyProperties:
        """Get survey properties."""
        ...
    
    def get_summary(self, survey_id: str) -> SurveySummary:
        """Get survey summary."""
        ...


class QuestionProcessor(Protocol):
    """Protocol for question processing classes."""
    
    def process_question(self, question_id: str) -> Optional[ProcessedResponse]:
        """Process a single question."""
        ...
    
    def get_statistics(self, question_id: str) -> Optional[QuestionStatistics]:
        """Get statistics for a question."""
        ...


class CacheManager(Protocol):
    """Protocol for cache management."""
    
    def get_cached(self, func_name: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        """Get cached data."""
        ...
    
    def set_cached(self, data: Any, func_name: str, *args: Any, **kwargs: Any) -> None:
        """Store data in cache."""
        ...
    
    def clear_cache(self, survey_id: Optional[str] = None) -> None:
        """Clear cached data."""
        ...


# Data Processing Types
class ColumnMapping(TypedDict):
    """Mapping for response column codes."""
    question_code: str
    appendage: Optional[str]


class ResponseStats(TypedDict):
    """Response statistics for multiple choice questions."""
    absolute_counts: pd.Series
    response_rates: pd.Series


class RankingData(TypedDict):
    """Ranking question data structure."""
    ranking_matrix: pd.DataFrame
    option_names: Dict[str, str]
    max_answers: int


# Validation Types
class ValidationResult(TypedDict):
    """Result of data validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data_quality_score: Optional[float]


class ProcessingResult(TypedDict, total=False):
    """Result of data processing operation."""
    success: bool
    data: Optional[Union[pd.DataFrame, pd.Series, Dict[str, Any]]]
    errors: List[str]
    warnings: List[str]
    processing_time: float


# Survey Analysis Types
class SurveyAnalysisResult(TypedDict, total=False):
    """Complete survey analysis result."""
    survey_id: str
    survey_info: SurveyProperties
    summary: SurveySummary
    processed_responses: Dict[str, ProcessedResponse]
    questions: pd.DataFrame
    options: pd.DataFrame
    groups: List[GroupData]
    failure_log: Dict[str, Exception]
    analysis_metadata: Dict[str, Any] 