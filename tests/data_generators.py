#!/usr/bin/env python3
"""
Data Generators for LimeSurvey Testing

Creates realistic synthetic data that matches patterns observed in real surveys.
Based on real survey analysis (38 questions, 359 responses, mix of question types).
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import random
from datetime import datetime, timedelta


@dataclass
class MockQuestionData:
    """Mock question data structure matching LimeSurvey API format"""
    qid: str
    title: str  # question_code 
    question: str  # question text
    question_theme_name: str
    other: str  # Y/N
    mandatory: str  # Y/N
    parent_qid: str
    gid: str
    question_order: int


@dataclass
class MockOptionData:
    """Mock option data structure"""
    qid: str
    option_code: str
    answer: str  # option text
    option_order: int
    question_code: str


class SurveyDataGenerator:
    """Generate realistic LimeSurvey data for testing current handlers"""
    
    def __init__(self, survey_id: str = "111111", num_responses: int = 359):
        self.survey_id = survey_id
        self.num_responses = num_responses
        self.response_ids = [f"R{i+1}" for i in range(num_responses)]
        
        # Realistic response patterns based on observed data
        self.realistic_distributions = {
            'satisfaction': [0.15, 0.25, 0.35, 0.20, 0.05],  # Skewed toward positive
            'agreement': [0.10, 0.15, 0.30, 0.30, 0.15],     # Normal distribution
            'frequency': [0.30, 0.25, 0.20, 0.15, 0.10],     # Decreasing frequency
        }
    
    def generate_radio_question_data(self, question_id: str = "Q001", 
                                   question_code: str = "satisfaction",
                                   question_text: str = "How satisfied are you?") -> Tuple[MockQuestionData, List[MockOptionData], pd.DataFrame]:
        """Generate radio question data matching _process_radio_question input"""
        
        # Mock question metadata
        question = MockQuestionData(
            qid=question_id,
            title=question_code,
            question=question_text,
            question_theme_name="listradio",
            other="N",
            mandatory="Y",
            parent_qid="0",
            gid="G01",
            question_order=1
        )
        
        # Mock options data
        options = [
            MockOptionData(qid=question_id, option_code="1", answer="Very Dissatisfied", option_order=1, question_code=question_code),
            MockOptionData(qid=question_id, option_code="2", answer="Dissatisfied", option_order=2, question_code=question_code),
            MockOptionData(qid=question_id, option_code="3", answer="Neutral", option_order=3, question_code=question_code),
            MockOptionData(qid=question_id, option_code="4", answer="Satisfied", option_order=4, question_code=question_code),
            MockOptionData(qid=question_id, option_code="5", answer="Very Satisfied", option_order=5, question_code=question_code),
        ]
        
        # Generate realistic response data
        choices = ["1", "2", "3", "4", "5"]
        probabilities = self.realistic_distributions['satisfaction']
        
        responses_data = {}
        responses_data['id'] = self.response_ids
        responses_data[question_code] = np.random.choice(choices, size=self.num_responses, p=probabilities)
        
        # Add some missing responses (realistic)
        missing_indices = np.random.choice(self.num_responses, size=int(self.num_responses * 0.05), replace=False)
        for idx in missing_indices:
            responses_data[question_code][idx] = np.nan
            
        responses_df = pd.DataFrame(responses_data)
        
        return question, options, responses_df
    
    def generate_multiple_choice_data(self, question_id: str = "Q002",
                                    question_code: str = "preferences",
                                    question_text: str = "Which features do you use?") -> Tuple[MockQuestionData, List[MockQuestionData], pd.DataFrame]:
        """Generate multiple choice data matching _process_multiple_choice_question input"""
        
        # Parent question
        parent_question = MockQuestionData(
            qid=question_id,
            title=question_code,
            question=question_text,
            question_theme_name="multiplechoice",
            other="N",
            mandatory="N",
            parent_qid="0",
            gid="G02",
            question_order=2
        )
        
        # Sub-questions (options as questions in LimeSurvey)
        sub_questions = [
            MockQuestionData(qid=f"{question_id}SQ001", title="SQ001", question="Feature A", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G02", question_order=1),
            MockQuestionData(qid=f"{question_id}SQ002", title="SQ002", question="Feature B", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G02", question_order=2),
            MockQuestionData(qid=f"{question_id}SQ003", title="SQ003", question="Feature C", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G02", question_order=3),
        ]
        
        # Generate Y/N responses for each option
        responses_data = {'id': self.response_ids}
        for sq in sub_questions:
            col_name = f"{question_code}[{sq.title}]"
            # Realistic multiple choice: some people select multiple options
            selection_probability = random.uniform(0.15, 0.45)  # 15-45% select each option
            responses = np.random.choice(['Y', ''], size=self.num_responses, p=[selection_probability, 1-selection_probability])
            responses_data[col_name] = responses
            
        responses_df = pd.DataFrame(responses_data)
        
        return parent_question, sub_questions, responses_df
    
    def generate_ranking_data(self, question_id: str = "Q003",
                            question_code: str = "priorities", 
                            question_text: str = "Rank these priorities") -> Tuple[MockQuestionData, List[MockOptionData], pd.DataFrame]:
        """Generate ranking data matching _process_ranking_question input"""
        
        question = MockQuestionData(
            qid=question_id,
            title=question_code,
            question=question_text,
            question_theme_name="ranking",
            other="N",
            mandatory="N",
            parent_qid="0",
            gid="G03",
            question_order=3
        )
        
        options = [
            MockOptionData(qid=question_id, option_code="A", answer="Quality", option_order=1, question_code=question_code),
            MockOptionData(qid=question_id, option_code="B", answer="Price", option_order=2, question_code=question_code),
            MockOptionData(qid=question_id, option_code="C", answer="Speed", option_order=3, question_code=question_code),
            MockOptionData(qid=question_id, option_code="D", answer="Support", option_order=4, question_code=question_code),
        ]
        
        # Generate ranking responses (each rank position gets an option code)
        responses_data = {'id': self.response_ids}
        option_codes = ["A", "B", "C", "D"]
        
        for rank in range(1, 5):  # Ranks 1-4
            col_name = f"{question_code}[{rank}]"
            rank_responses = []
            
            for _ in range(self.num_responses):
                if random.random() < 0.85:  # 85% complete the ranking
                    # Realistic ranking: some preferences are more common at certain ranks
                    if rank == 1:  # First choice preferences
                        choice = np.random.choice(option_codes, p=[0.4, 0.3, 0.2, 0.1])
                    elif rank == 2:
                        choice = np.random.choice(option_codes, p=[0.25, 0.35, 0.25, 0.15])
                    else:
                        choice = np.random.choice(option_codes)
                    rank_responses.append(choice)
                else:
                    rank_responses.append("")  # Incomplete ranking
                    
            responses_data[col_name] = rank_responses
            
        responses_df = pd.DataFrame(responses_data)
        
        return question, options, responses_df
    
    def generate_text_data(self, question_id: str = "Q004",
                          question_code: str = "feedback",
                          question_text: str = "Please provide feedback") -> Tuple[MockQuestionData, pd.DataFrame]:
        """Generate text question data matching _process_text_question input"""
        
        question = MockQuestionData(
            qid=question_id,
            title=question_code,
            question=question_text,
            question_theme_name="longfreetext",
            other="N",
            mandatory="N",
            parent_qid="0",
            gid="G04",
            question_order=4
        )
        
        # Generate realistic text responses
        sample_responses = [
            "Great service, very satisfied",
            "Could be better, needs improvement in customer support",
            "Excellent quality and fast delivery",
            "Average experience, nothing special",
            "Very poor service, would not recommend",
            "Outstanding product, exceeded expectations",
            "Decent but overpriced",
            "Good overall but shipping was slow",
            "Perfect, exactly what I needed",
            "Terrible experience, many issues"
        ]
        
        responses_data = {'id': self.response_ids}
        text_responses = []
        
        for _ in range(self.num_responses):
            if random.random() < 0.70:  # 70% provide text feedback
                response = random.choice(sample_responses)
                # Add some variation
                if random.random() < 0.3:
                    response += " " + random.choice(["Thanks!", "Hope this helps.", "Please improve."])
                text_responses.append(response)
            else:
                text_responses.append(np.nan)  # No response
                
        responses_data[question_code] = text_responses
        responses_df = pd.DataFrame(responses_data)
        
        return question, responses_df
    
    def generate_array_data(self, question_id: str = "Q005",
                           question_code: str = "trends",
                           question_text: str = "How have these changed?") -> Tuple[MockQuestionData, List[MockQuestionData], pd.DataFrame]:
        """Generate array question data matching _process_array_question input"""
        
        parent_question = MockQuestionData(
            qid=question_id,
            title=question_code,
            question=question_text,
            question_theme_name="arrays/increasesamedecrease",
            other="N",
            mandatory="N",
            parent_qid="0",
            gid="G05",
            question_order=5
        )
        
        # Array sub-questions
        sub_questions = [
            MockQuestionData(qid=f"{question_id}SQ001", title="SQ001", question="Product Quality", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G05", question_order=1),
            MockQuestionData(qid=f"{question_id}SQ002", title="SQ002", question="Customer Service", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G05", question_order=2),
            MockQuestionData(qid=f"{question_id}SQ003", title="SQ003", question="Pricing", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G05", question_order=3),
        ]
        
        # Generate I/S/D responses
        responses_data = {'id': self.response_ids}
        for sq in sub_questions:
            col_name = f"{question_code}[{sq.title}]"
            # Realistic distribution: more "Same" responses, some bias toward improvement
            responses = np.random.choice(['I', 'S', 'D'], size=self.num_responses, p=[0.35, 0.45, 0.20])
            # Add some missing responses
            missing_indices = np.random.choice(self.num_responses, size=int(self.num_responses * 0.08), replace=False)
            for idx in missing_indices:
                responses[idx] = ""
            responses_data[col_name] = responses
            
        responses_df = pd.DataFrame(responses_data)
        
        return parent_question, sub_questions, responses_df
    
    def generate_multiple_short_text_data(self, question_id: str = "Q006",
                                        question_code: str = "contact_info",
                                        question_text: str = "Contact Information") -> Tuple[MockQuestionData, List[MockQuestionData], pd.DataFrame]:
        """Generate multiple short text data matching _process_multiple_short_text input"""
        
        parent_question = MockQuestionData(
            qid=question_id,
            title=question_code,
            question=question_text,
            question_theme_name="multipleshorttext",
            other="N",
            mandatory="N",
            parent_qid="0",
            gid="G06",
            question_order=6
        )
        
        sub_questions = [
            MockQuestionData(qid=f"{question_id}SQ001", title="SQ001", question="First Name", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G06", question_order=1),
            MockQuestionData(qid=f"{question_id}SQ002", title="SQ002", question="Last Name", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G06", question_order=2),
            MockQuestionData(qid=f"{question_id}SQ003", title="SQ003", question="Email", question_theme_name=None, other="N", mandatory="N", parent_qid=question_id, gid="G06", question_order=3),
        ]
        
        # Generate realistic personal data
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Tom", "Anna", "Chris", "Emma"]
        last_names = ["Smith", "Johnson", "Brown", "Davis", "Wilson", "Miller", "Moore", "Taylor", "Anderson", "Thomas"]
        
        responses_data = {'id': self.response_ids}
        
        # First Name
        col_name = f"{question_code}[SQ001]"
        first_name_responses = []
        for _ in range(self.num_responses):
            if random.random() < 0.85:  # 85% provide first name
                first_name_responses.append(random.choice(first_names))
            else:
                first_name_responses.append("")
        responses_data[col_name] = first_name_responses
        
        # Last Name  
        col_name = f"{question_code}[SQ002]"
        last_name_responses = []
        for _ in range(self.num_responses):
            if random.random() < 0.80:  # 80% provide last name
                last_name_responses.append(random.choice(last_names))
            else:
                last_name_responses.append("")
        responses_data[col_name] = last_name_responses
        
        # Email
        col_name = f"{question_code}[SQ003]"
        email_responses = []
        for i in range(self.num_responses):
            if random.random() < 0.75:  # 75% provide email
                fname = responses_data[f"{question_code}[SQ001]"][i] or "user"
                lname = responses_data[f"{question_code}[SQ002]"][i] or "example"
                email = f"{fname.lower()}.{lname.lower()}@email.com"
                email_responses.append(email)
            else:
                email_responses.append("")
        responses_data[col_name] = email_responses
        
        responses_df = pd.DataFrame(responses_data)
        
        return parent_question, sub_questions, responses_df
    
    def generate_full_survey_data(self) -> Dict[str, Any]:
        """Generate a complete survey dataset with mixed question types"""
        
        questions_data = []
        options_data = []
        all_responses = {'id': self.response_ids}
        
        # Generate different question types
        question_generators = [
            ("radio", self.generate_radio_question_data, "Q001", "satisfaction", "How satisfied are you?"),
            ("multiple_choice", self.generate_multiple_choice_data, "Q002", "features", "Which features do you use?"),
            ("ranking", self.generate_ranking_data, "Q003", "priorities", "Rank these priorities"),
            ("text", self.generate_text_data, "Q004", "feedback", "Please provide feedback"),
            ("array", self.generate_array_data, "Q005", "trends", "How have these changed?"),
            ("multiple_short_text", self.generate_multiple_short_text_data, "Q006", "contact", "Contact Information"),
        ]
        
        for q_type, generator, qid, code, text in question_generators:
            if q_type == "text":
                # Text questions return (question, responses)
                question, responses = generator(qid, code, text)
                questions_data.append(question)
            elif q_type in ["radio", "ranking"]:
                # Radio and ranking return (question, options, responses)
                question, options, responses = generator(qid, code, text)
                questions_data.append(question)
                options_data.extend(options)
            else:
                # Multiple choice, array, multiple_short_text return (question, sub_questions, responses)
                question, sub_questions, responses = generator(qid, code, text)
                questions_data.append(question)
                questions_data.extend(sub_questions)
            
            # Merge response data
            for col in responses.columns:
                if col != 'id':
                    all_responses[col] = responses[col]
        
        return {
            'questions': questions_data,
            'options': options_data,
            'responses': pd.DataFrame(all_responses),
            'survey_metadata': {
                'survey_id': self.survey_id,
                'total_questions': len([q for q in questions_data if q.parent_qid == "0"]),
                'total_responses': self.num_responses,
                'completion_rate': 0.92  # Realistic completion rate
            }
        }


# Convenience functions for testing
def create_test_survey_data(survey_id: str = "111111", num_responses: int = 359):
    """Create test data matching real survey patterns"""
    generator = SurveyDataGenerator(survey_id, num_responses)
    return generator.generate_full_survey_data()


def create_single_question_test_data(question_type: str, **kwargs):
    """Create test data for a single question type"""
    generator = SurveyDataGenerator()
    
    if question_type == "radio":
        return generator.generate_radio_question_data(**kwargs)
    elif question_type == "multiple_choice":
        return generator.generate_multiple_choice_data(**kwargs)
    elif question_type == "ranking":
        return generator.generate_ranking_data(**kwargs)
    elif question_type == "text":
        return generator.generate_text_data(**kwargs)
    elif question_type == "array":
        return generator.generate_array_data(**kwargs)
    elif question_type == "multiple_short_text":
        return generator.generate_multiple_short_text_data(**kwargs)
    else:
        raise ValueError(f"Unknown question type: {question_type}") 