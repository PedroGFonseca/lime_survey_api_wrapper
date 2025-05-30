"""
Core LimeSurvey Data Models

Survey and QuestionGroup classes representing the main structural elements.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class Survey:
    """
    Represents a LimeSurvey survey with its basic properties and metadata.
    """
    
    # Core identification
    sid: int
    title: str
    language: str = "en"
    
    # Survey metadata
    admin: str = ""
    email: str = ""
    created: Optional[datetime] = None
    active: bool = False
    anonymized: bool = True
    
    # Survey text elements (language-specific)
    description: str = ""
    welcome_text: str = ""
    end_text: str = ""
    end_url: str = ""
    
    # Survey behavior
    format: str = "G"  # G=Group by group, S=Single questions, A=All in one
    navigation: str = "N"  # N=None, I=Incremental, F=Flexible
    allow_backwards: bool = True
    show_progress_bar: bool = True
    
    # Access control
    public_statistics: bool = False
    public_graphs: bool = False
    list_public: bool = False
    
    # Response handling
    save_timings: bool = False
    token_table_exists: bool = False
    
    # Template and styling
    template: str = "vanilla"
    
    # Additional languages
    additional_languages: List[str] = field(default_factory=list)
    
    # Survey settings (raw from API)
    raw_attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestionGroup:
    """
    Represents a question group within a survey.
    Groups organize questions and can have conditional display logic.
    """
    
    # Core identification
    gid: int
    sid: int  # Parent survey ID
    group_name: str
    group_order: int = 0
    
    # Display properties
    title: str = ""
    description: str = ""
    language: str = "en"
    
    # Logic and behavior
    randomization_group: Optional[str] = None
    relevance_equation: str = "1"  # Always relevant by default
    
    # Inherited from survey
    inherited_navigation: str = "N"
    inherited_template: str = "vanilla"
    
    def __post_init__(self):
        """Post-initialization validation and setup"""
        if not self.group_name:
            self.group_name = f"G{self.gid}"
            
    @property
    def is_conditional(self) -> bool:
        """Returns True if group has conditional logic"""
        return self.relevance_equation != "1"
        
    @property 
    def display_title(self) -> str:
        """Returns the title for display, fallback to group_name"""
        return self.title if self.title else self.group_name 