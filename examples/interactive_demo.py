#!/usr/bin/env python3
"""
LimeSurvey Analyzer - Interactive Demo

This file demonstrates all functionality of the LimeSurvey Analyzer library.
Each section can be copy-pasted into separate Jupyter notebook cells for interactive use.

Setup Instructions:
1. Clone the repository: git clone <repo_url>  
2. Navigate to the project: cd lime_survey_analyzer
3. Install in development mode: pip install -e .
4. Run this demo: python examples/interactive_demo.py

For Jupyter notebooks:
1. Ensure the package is installed (pip install -e .)
2. Copy each section between "# === CELL: ..." comments into separate notebook cells
"""

try:
    from lime_survey_analyzer import LimeSurveyDirectAPI
    print("✅ lime_survey_analyzer imported successfully!")
except ImportError as e:
    print("❌ Error: lime_survey_analyzer module not found!")
    print("\n📋 Setup Instructions:")
    print("1. Navigate to the project root directory")
    print("2. Install the package: pip install -e .")
    print("3. Run this demo again")
    print(f"\nTechnical error: {e}")
    exit(1)

import json
import pandas as pd
from pprint import pprint
import traceback
from datetime import datetime

# === CELL: Setup and Imports ===
print("🚀 LimeSurvey Analyzer - Interactive Demo")
print("=" * 50)

def print_section(title, emoji="📋"):
    """Print a nicely formatted section header"""
    print(f"\n{emoji} {title}")
    print("-" * (len(title) + 4))

def print_success(message):
    """Print a success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print an error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print an info message"""
    print(f"ℹ️  {message}")

def print_data_summary(data, name="Data"):
    """Print a nice summary of data"""
    if isinstance(data, list):
        print(f"📊 {name}: {len(data)} items")
        if data and isinstance(data[0], dict):
            print(f"   Sample keys: {list(data[0].keys())[:5]}")
    elif isinstance(data, dict):
        print(f"📊 {name}: {len(data)} fields")
        print(f"   Keys: {list(data.keys())[:5]}")
    else:
        print(f"📊 {name}: {type(data)}")

print_success("All imports and setup completed successfully!")

# === CELL: Authentication Setup ===
print_section("Authentication Setup", "🔐")

def setup_authentication():
    """Setup API authentication with fallback options"""
    try:
        # Try environment variables first
        api = LimeSurveyDirectAPI.from_env()
        print_success("Using environment variables for authentication")
        return api
    except Exception as e:
        print_error(f"Environment variables not set: {e}")
        
        try:
            # Try configuration file
            api = LimeSurveyDirectAPI.from_config('credentials.ini')
            print_success("Using configuration file for authentication")
            return api
        except Exception as e:
            print_error(f"Configuration file not found: {e}")
            
            # Interactive prompt as fallback
            print_info("Please enter your credentials manually:")
            api = LimeSurveyDirectAPI.from_prompt()
            print_success("Using interactive authentication")
            return api

# Create API client
api = setup_authentication()
print_info("API client ready for use!")

# === CELL: Survey Manager Demo ===
print_section("Survey Manager - Survey Operations", "📊")

def demo_survey_manager(api):
    """Demonstrate Survey Manager functionality"""
    
    with api:
        # List all surveys
        print("🔍 Listing all available surveys...")
        surveys = api.surveys.list_surveys()
        
        print_data_summary(surveys, "Surveys")
        
        if not surveys:
            print_error("No surveys found. Check your permissions.")
            return None
            
        # Display survey list with nice formatting
        print("\n📋 Your Surveys:")
        for i, survey in enumerate(surveys[:10], 1):  # Show first 10
            title = survey.get('surveyls_title', 'Untitled Survey')
            status = '🟢 Active' if survey.get('active') == 'Y' else '🔴 Inactive'
            lang = survey.get('language', 'Unknown')
            print(f"  {i:2d}. [{survey['sid']}] {title}")
            print(f"      Status: {status} | Language: {lang}")
            
        if len(surveys) > 10:
            print(f"      ... and {len(surveys) - 10} more surveys")
            
        return surveys

surveys = demo_survey_manager(api)

# === CELL: Survey Properties Demo ===
print_section("Survey Properties Analysis", "🔍")

def demo_survey_properties(api, surveys):
    """Demonstrate detailed survey properties"""
    
    if not surveys:
        print_error("No surveys available for analysis")
        return None
        
    # Use first survey for detailed analysis
    survey = surveys[0]
    survey_id = survey['sid']
    
    print(f"🎯 Analyzing Survey: {survey_id}")
    print(f"   Title: {survey.get('surveyls_title', 'Untitled')}")
    
    with api:
        print("\n🔍 Getting detailed survey properties...")
        survey_props = api.surveys.get_survey_properties(survey_id)
        
        # Display important properties
        print("\n📋 Survey Configuration:")
        important_props = [
            ('surveyls_title', 'Title', '📝'),
            ('active', 'Status', '🔄'),
            ('anonymized', 'Anonymous', '🔒'),
            ('language', 'Language', '🌍'),
            ('datecreated', 'Created', '📅'),
            ('startdate', 'Start Date', '🚀'),
            ('expires', 'Expires', '⏰'),
            ('listpublic', 'Public', '👁️'),
            ('format', 'Format', '📄')
        ]
        
        for prop, label, emoji in important_props:
            value = survey_props.get(prop, 'N/A')
            
            # Format special values
            if prop in ['active', 'anonymized', 'listpublic']:
                value = 'Yes' if value == 'Y' else 'No'
            elif prop == 'format':
                formats = {'G': 'Group by Group', 'S': 'Question by Question', 'A': 'All in One'}
                value = formats.get(value, value)
                
            print(f"  {emoji} {label}: {value}")
            
        # Get survey summary
        print("\n📊 Getting survey statistics...")
        try:
            summary = api.surveys.get_summary(survey_id)
            print("\n📈 Survey Summary:")
            
            if isinstance(summary, dict):
                for key, value in summary.items():
                    print(f"  📊 {key}: {value}")
            else:
                print_info(f"Summary type: {type(summary)}")
                
        except Exception as e:
            print_error(f"Could not get survey summary: {e}")
            print_info("This is normal for surveys with no responses")
            
    return survey_id

survey_id = demo_survey_properties(api, surveys) if surveys else None

# === CELL: Question Manager Demo ===
print_section("Question Manager - Survey Structure", "❓")

def demo_question_manager(api, survey_id):
    """Demonstrate Question Manager functionality"""
    
    if not survey_id:
        print_error("No survey ID available for question analysis")
        return None, None
        
    with api:
        print(f"🏗️ Exploring structure of survey {survey_id}...")
        
        # Get question groups
        print("\n📂 Getting question groups...")
        groups = api.questions.list_groups(survey_id)
        print_data_summary(groups, "Question Groups")
        
        if groups:
            print("\n📁 Question Groups:")
            for group in groups:
                name = group.get('group_name', 'Unnamed Group')
                order = group.get('group_order', 'N/A')
                print(f"  📁 Group {group['gid']}: {name} (Order: {order})")
                
                # Show description if available
                desc = group.get('description', '')
                if desc and desc.strip():
                    desc_preview = desc[:80] + "..." if len(desc) > 80 else desc
                    print(f"      📝 {desc_preview}")
        else:
            print_info("No question groups found")
            
        # Get all questions
        print("\n❓ Getting all questions...")
        questions = api.questions.list_questions(survey_id)
        print_data_summary(questions, "Questions")
        
        if questions:
            # Analyze question types and visibility
            question_types = {}
            hidden_count = 0
            conditional_count = 0
            
            for q in questions:
                qtype = q.get('type', 'Unknown')
                question_types[qtype] = question_types.get(qtype, 0) + 1
                
                # Check for basic hiding indicators in the list
                if q.get('hidden') == '1':
                    hidden_count += 1
                elif q.get('relevance') and q.get('relevance').strip() not in ['', '1']:
                    conditional_count += 1
                
            print("\n📊 Question Type Distribution:")
            for qtype, count in sorted(question_types.items()):
                print(f"  📝 {qtype}: {count} questions")
                
            print("\n👁️ Visibility Summary:")
            visible_count = len(questions) - hidden_count - conditional_count
            print(f"  ✅ Always Visible: {visible_count} questions")
            if conditional_count > 0:
                print(f"  🔄 Conditionally Visible: {conditional_count} questions")
            if hidden_count > 0:
                print(f"  🚫 Always Hidden: {hidden_count} questions")
                
            print(f"\n❓ Question Details (showing first 10):")
            for i, question in enumerate(questions[:10], 1):
                title = question.get('title', 'No Code')
                qtype = question.get('type', 'Unknown')
                mandatory = '⚠️ Required' if question.get('mandatory') == 'Y' else '📝 Optional'
                
                # Add visibility indicator
                visibility = ""
                if question.get('hidden') == '1':
                    visibility = " 🚫"
                elif question.get('relevance') and question.get('relevance').strip() not in ['', '1']:
                    visibility = " 🔄"
                else:
                    visibility = " ✅"
                
                q_text = question.get('question', 'No text available')
                q_text = q_text[:60] + "..." if len(q_text) > 60 else q_text
                
                print(f"  {i:2d}. [{title}] {qtype} - {mandatory}{visibility}")
                print(f"      📋 {q_text}")
                
            if len(questions) > 10:
                print(f"      ... and {len(questions) - 10} more questions")
        else:
            print_info("No questions found in this survey")
            
        return groups, questions

groups, questions = demo_question_manager(api, survey_id) if survey_id else (None, None)

# === CELL: Question Details Demo ===
print_section("Question Properties Analysis", "🔬")

def demo_question_properties(api, questions):
    """Demonstrate detailed question properties"""
    
    if not questions:
        print_error("No questions available for detailed analysis")
        return
        
    # Analyze first question in detail
    question = questions[0]
    question_id = question['qid']
    
    print(f"🔬 Detailed analysis of Question {question_id}")
    
    with api:
        try:
            question_props = api.questions.get_question_properties(question_id)
            
            print("\n📋 Question Properties:")
            important_q_props = [
                ('title', 'Question Code', '🏷️'),
                ('type', 'Question Type', '📝'),
                ('mandatory', 'Mandatory', '⚠️'),
                ('other', 'Other Option', '📌'),
                ('help', 'Help Text', '❓'),
                ('relevance', 'Relevance Logic', '🔧'),
                ('preg', 'Validation', '✅')
            ]
            
            for prop, label, emoji in important_q_props:
                value = question_props.get(prop, 'N/A')
                
                # Format special values
                if prop == 'mandatory':
                    value = 'Required' if value == 'Y' else 'Optional'
                elif prop == 'other':
                    value = 'Yes' if value == 'Y' else 'No'
                elif prop == 'relevance':
                    if value and value.strip() and value != '1':
                        # Complex relevance equation
                        if len(value) > 100:
                            value = value[:100] + "... [COMPLEX LOGIC]"
                        print(f"  {emoji} {label}: {value}")
                        print(f"      ⚠️ Question visibility controlled by conditions")
                        continue
                    else:
                        value = 'Always shown' if not value or value == '1' else 'Conditional'
                elif isinstance(value, str) and len(value) > 100:
                    value = value[:100] + "..."
                    
                print(f"  {emoji} {label}: {value}")
            
            # Check for hidden question indicators
            print(f"\n🔍 Visibility Analysis:")
            hidden_indicators = []
            
            # Check for always hidden attribute
            if question_props.get('hidden') == '1':
                hidden_indicators.append("🚫 Always Hidden (hidden=1)")
            
            # Check attributes for always_hidden
            attributes = question_props.get('attributes', {})
            if isinstance(attributes, dict):
                for attr_name, attr_value in attributes.items():
                    if 'hidden' in attr_name.lower() and attr_value == '1':
                        hidden_indicators.append(f"🚫 Always Hidden ({attr_name}=1)")
            
            # Check relevance equation for potential hiding
            relevance = question_props.get('relevance', '1')
            if relevance and relevance.strip():
                if relevance.strip() in ['0', 'false', '1==2']:
                    hidden_indicators.append("🚫 Always Hidden (relevance equation)")
                elif relevance.strip() != '1':
                    hidden_indicators.append("🔄 Conditionally Hidden (depends on other answers)")
            
            # Check for older condition system
            try:
                survey_id = question_props.get('sid')
                if survey_id:
                    conditions = api.questions.get_conditions(survey_id, question_id)
                    if conditions:
                        hidden_indicators.append(f"🔄 Has {len(conditions)} legacy condition(s)")
                        print(f"\n🔧 Legacy Conditions Found:")
                        for i, condition in enumerate(conditions[:3], 1):  # Show first 3
                            source_field = condition.get('cfieldname', 'Unknown')
                            method = condition.get('method', 'Unknown')
                            value = condition.get('value', 'Unknown')
                            print(f"    {i}. Show if '{source_field}' {method} '{value}'")
                        if len(conditions) > 3:
                            print(f"       ... and {len(conditions) - 3} more conditions")
            except Exception as e:
                # Condition checking failed - not critical
                print(f"      ℹ️ Could not check legacy conditions: {e}")
            
            if hidden_indicators:
                print("    " + "\n    ".join(hidden_indicators))
            else:
                print("    ✅ Question is always visible")
                
            # Show question text
            q_text = question_props.get('question', 'No question text')
            print(f"\n📝 Question Text:")
            print(f"  {q_text}")
            
        except Exception as e:
            print_error(f"Could not get question properties: {e}")

demo_question_properties(api, questions) if questions else None

# === CELL: Condition Analysis Demo ===
print_section("Conditional Logic Analysis", "🔧")

def demo_condition_analysis(api, survey_id):
    """Demonstrate comprehensive condition analysis for the survey"""
    
    if not survey_id:
        print_error("No survey ID available for condition analysis")
        return
        
    print(f"🔧 Analyzing all conditions in survey {survey_id}...")
    
    with api:
        try:
            # Get all conditions in the survey
            all_conditions = api.questions.list_conditions(survey_id)
            
            if all_conditions:
                print(f"\n📊 Found {len(all_conditions)} legacy conditions")
                
                # Group conditions by target question
                conditions_by_question = {}
                for condition in all_conditions:
                    qid = condition.get('qid', 'Unknown')
                    if qid not in conditions_by_question:
                        conditions_by_question[qid] = []
                    conditions_by_question[qid].append(condition)
                
                print(f"🎯 Affects {len(conditions_by_question)} questions")
                
                # Show summary of conditional questions
                print(f"\n🔄 Questions with Legacy Conditions:")
                for qid, question_conditions in conditions_by_question.items():
                    count = len(question_conditions)
                    print(f"   Question {qid}: {count} condition{'s' if count > 1 else ''}")
                    
                    # Show condition details for first few
                    for condition in question_conditions[:2]:
                        source = condition.get('cfieldname', 'Unknown')
                        method = condition.get('method', 'Unknown') 
                        value = condition.get('value', 'Unknown')
                        print(f"     • Show if '{source}' {method} '{value}'")
                    
                    if len(question_conditions) > 2:
                        print(f"     • ... and {len(question_conditions) - 2} more")
                
                print(f"\n💡 Note: Modern LimeSurvey surveys typically use 'relevance equations' instead of legacy conditions.")
                print(f"   Both systems control when questions are shown to respondents.")
                
            else:
                print("✅ No legacy conditions found")
                print("   This survey likely uses modern 'relevance equations' for conditional logic")
                
        except Exception as e:
            print_error(f"Could not analyze conditions: {e}")
            print_info("This survey may not use the legacy conditions system")

demo_condition_analysis(api, survey_id) if survey_id else None

# === CELL: Graph Visualization Demo ===
print_section("Conditional Graph Visualization", "📊")

def demo_graph_visualization(api, survey_id):
    """Demonstrate graph visualization of conditional logic"""
    
    if not survey_id:
        print_error("No survey ID available for graph visualization")
        return
        
    print(f"📊 Creating conditional logic graph for survey {survey_id}...")
    
    try:
        # Import visualization module
        from lime_survey_analyzer.visualizations import create_survey_graph
        
        # Create the graph
        results = create_survey_graph(api, survey_id, output_path="survey_conditional_graph")
        
        print_success("Graph analysis completed!")
        print_info("Parser supports both numeric IDs and LimeSurvey question codes (e.g., G01Q01.NAOK)")
        
        if results['graphviz_available']:
            if results['graph_image']:
                print(f"🖼️ Graph image saved: {results['graph_image']}")
            else:
                print_info("Graph image could not be generated")
        else:
            print_info("Graphviz not available - only JSON export created")
        
        print(f"📄 Graph data exported: {results['json_export']}")
        
        # Show analysis summary
        analysis = results['analysis']
        print(f"\n📈 Graph Statistics:")
        print(f"   🔗 Total Dependencies: {analysis['total_edges']}")
        print(f"   🎯 Dependent Questions: {analysis['dependent_questions']}")
        print(f"   🚀 Trigger Questions: {analysis['trigger_questions']}")
        print(f"   🏝️ Independent Questions: {analysis['isolated_questions']}")
        
        if analysis['legacy_conditions'] > 0:
            print(f"   📜 Legacy Conditions: {analysis['legacy_conditions']}")
        if analysis['relevance_conditions'] > 0:
            print(f"   🔧 Relevance Conditions: {analysis['relevance_conditions']}")
        
        return results
        
    except ImportError:
        print_error("Graph visualization not available")
        print_info("To enable graph visualization:")
        print_info("  macOS: brew install graphviz && pip install graphviz")
        print_info("  Linux: sudo apt-get install graphviz && pip install graphviz")
        return None
    except Exception as e:
        print_error(f"Graph visualization failed: {e}")
        return None

demo_graph_visualization(api, survey_id) if survey_id else None

# === CELL: Response Manager Demo ===
print_section("Response Manager - Survey Data", "📈")

def demo_response_manager(api, survey_id):
    """Demonstrate Response Manager functionality"""
    
    if not survey_id:
        print_error("No survey ID available for response analysis")
        return None
        
    with api:
        print(f"📊 Analyzing responses for survey {survey_id}...")
        
        # Get response IDs
        print("\n🔢 Getting response IDs...")
        response_ids = api.responses.get_all_response_ids(survey_id)
        
        print(f"📊 Found {len(response_ids)} total responses")
        
        if not response_ids:
            print_info("No responses found in this survey yet")
            print_info("This is normal for new or inactive surveys")
            return None
            
        # Show response ID sample
        if response_ids:
            sample_ids = response_ids[:10]
            print(f"🔍 Sample Response IDs: {sample_ids}")
            if len(response_ids) > 10:
                print(f"   ... and {len(response_ids) - 10} more")
                
        # Export responses
        print("\n📤 Exporting response data...")
        try:
            responses = api.responses.export_responses(survey_id, document_type='json')
            
            if isinstance(responses, list) and responses:
                print_success(f"Exported {len(responses)} responses as JSON")
                
                # Analyze response structure
                first_response = responses[0]
                field_count = len(first_response)
                
                print(f"\n📋 Response Structure:")
                print(f"  📊 Fields per response: {field_count}")
                print(f"  📊 Total data points: {len(responses) * field_count}")
                
                # Show field names (first 15)
                field_names = list(first_response.keys())
                print(f"\n🏷️ Field Names (first 15):")
                for i, field in enumerate(field_names[:15], 1):
                    print(f"  {i:2d}. {field}")
                if len(field_names) > 15:
                    print(f"      ... and {len(field_names) - 15} more fields")
                
                # Convert to DataFrame
                print(f"\n🐼 Converting to pandas DataFrame...")
                df = pd.DataFrame(responses)
                
                print(f"✅ DataFrame created successfully!")
                print(f"  📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
                print(f"  💾 Memory usage: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                
                # Show data types
                print(f"\n📊 Data Types Summary:")
                dtype_counts = df.dtypes.value_counts()
                for dtype, count in dtype_counts.items():
                    print(f"  📝 {dtype}: {count} columns")
                
                # Show sample data
                print(f"\n🔍 Sample Data (first 3 rows, first 5 columns):")
                sample_df = df.iloc[:3, :5]
                print(sample_df.to_string(max_colwidth=30))
                
                return df
                
            else:
                print_error("Response export failed or returned empty data")
                return None
                
        except Exception as e:
            print_error(f"Response export failed: {e}")
            return None

df = demo_response_manager(api, survey_id) if survey_id else None

# === CELL: Statistics Demo ===
print_section("Statistics Export", "📈")

def demo_statistics(api, survey_id):
    """Demonstrate statistics export functionality"""
    
    if not survey_id:
        print_error("No survey ID available for statistics")
        return
        
    with api:
        print(f"📈 Exporting statistics for survey {survey_id}...")
        
        try:
            # Try to export statistics
            stats = api.responses.export_statistics(survey_id)
            
            print_success("Statistics export completed!")
            print(f"📊 Statistics type: {type(stats)}")
            
            if isinstance(stats, dict):
                print(f"📊 Statistics contains {len(stats)} items")
                print("\n📋 Statistics Overview:")
                for i, (key, value) in enumerate(stats.items()):
                    if i >= 10:  # Show first 10 items
                        print(f"      ... and {len(stats) - 10} more items")
                        break
                    
                    # Format value for display
                    if isinstance(value, str) and len(value) > 80:
                        display_value = value[:80] + "..."
                    else:
                        display_value = value
                        
                    print(f"  📊 {key}: {display_value}")
                    
            elif isinstance(stats, str):
                print(f"📄 Statistics returned as text ({len(stats)} characters)")
                if len(stats) > 200:
                    print(f"📄 Preview: {stats[:200]}...")
                else:
                    print(f"📄 Content: {stats}")
            else:
                print(f"📊 Statistics: {stats}")
                
        except Exception as e:
            print_error(f"Statistics export failed: {e}")
            print_info("This is normal for surveys with no responses or insufficient data")

demo_statistics(api, survey_id) if survey_id else None

# === CELL: Participant Manager Demo ===
print_section("Participant Manager", "👥")

def demo_participant_manager(api, survey_id):
    """Demonstrate Participant Manager functionality"""
    
    if not survey_id:
        print_error("No survey ID available for participant analysis")
        return
        
    with api:
        print(f"👥 Checking participant data for survey {survey_id}...")
        
        try:
            participants = api.participants.list_participants(survey_id)
            
            print_success(f"Found {len(participants)} participants")
            
            if participants:
                print("\n👤 Participant Information:")
                
                for i, participant in enumerate(participants[:5], 1):  # Show first 5
                    print(f"\n  {i}. Participant {participant.get('tid', 'No ID')}:")
                    
                    # Show key participant fields
                    key_fields = ['firstname', 'lastname', 'email', 'token', 'completed']
                    for field in key_fields:
                        value = participant.get(field, 'N/A')
                        if field == 'completed':
                            value = 'Yes' if value == 'Y' else 'No'
                        print(f"     {field.capitalize()}: {value}")
                        
                if len(participants) > 5:
                    print(f"\n     ... and {len(participants) - 5} more participants")
                    
                # Participant statistics
                completed = sum(1 for p in participants if p.get('completed') == 'Y')
                print(f"\n📊 Participant Statistics:")
                print(f"  👥 Total: {len(participants)}")
                print(f"  ✅ Completed: {completed}")
                print(f"  ⏳ Pending: {len(participants) - completed}")
                
            else:
                print_info("No participant data found")
                print_info("This survey likely uses anonymous responses")
                
        except Exception as e:
            print_error(f"Participant data not available: {e}")
            print_info("Many surveys use anonymous responses and don't have participant tables")
            print_info("This is completely normal and expected behavior")

demo_participant_manager(api, survey_id) if survey_id else None

# === CELL: Complete Analysis Workflow ===
print_section("Complete Analysis Workflow", "🎯")

def complete_survey_analysis(api, survey_id):
    """Run a complete survey analysis combining all managers"""
    
    if not survey_id:
        print_error("No survey ID available for complete analysis")
        return None
        
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'survey_id': survey_id,
        'survey_info': {},
        'structure': {},
        'conditions': {},
        'responses': {},
        'participants': {},
        'success': True,
        'errors': []
    }
    
    print(f"🎯 Complete Analysis of Survey {survey_id}")
    print("=" * 60)
    
    with api:
        # 1. Survey Information
        print("\n📊 1. Survey Information Analysis")
        try:
            survey_props = api.surveys.get_survey_properties(survey_id)
            analysis_results['survey_info'] = {
                'title': survey_props.get('surveyls_title', 'Unknown'),
                'active': survey_props.get('active') == 'Y',
                'anonymous': survey_props.get('anonymized') == 'Y',
                'language': survey_props.get('language', 'Unknown'),
                'created': survey_props.get('datecreated', 'Unknown'),
                'format': survey_props.get('format', 'Unknown')
            }
            
            print("   ✅ Survey information collected")
            for key, value in analysis_results['survey_info'].items():
                print(f"     {key.replace('_', ' ').title()}: {value}")
                
        except Exception as e:
            error_msg = f"Survey info failed: {e}"
            analysis_results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # 2. Structure Analysis
        print("\n🏗️ 2. Survey Structure Analysis")
        try:
            groups = api.questions.list_groups(survey_id)
            questions = api.questions.list_questions(survey_id)
            
            # Question type analysis
            question_types = {}
            for q in questions:
                qtype = q.get('type', 'Unknown')
                question_types[qtype] = question_types.get(qtype, 0) + 1
            
            analysis_results['structure'] = {
                'groups': len(groups),
                'questions': len(questions),
                'question_types': question_types,
                'avg_questions_per_group': len(questions) / len(groups) if groups else 0
            }
            
            print("   ✅ Structure analysis completed")
            print(f"     Groups: {analysis_results['structure']['groups']}")
            print(f"     Questions: {analysis_results['structure']['questions']}")
            print(f"     Question Types: {len(question_types)}")
            
        except Exception as e:
            error_msg = f"Structure analysis failed: {e}"
            analysis_results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # 2.5. Condition Analysis (NEW!)
        print("\n🔧 2.5. Conditional Logic Analysis")
        try:
            all_conditions = api.questions.list_conditions(survey_id)
            
            # Count questions with relevance equations
            questions_with_relevance = 0
            for q in questions:
                if q.get('relevance') and q.get('relevance').strip() not in ['', '1']:
                    questions_with_relevance += 1
            
            analysis_results['conditions'] = {
                'legacy_conditions': len(all_conditions),
                'questions_with_relevance': questions_with_relevance,
                'total_conditional_questions': len(set([c.get('qid') for c in all_conditions])) + questions_with_relevance,
                'uses_modern_relevance': questions_with_relevance > 0,
                'uses_legacy_conditions': len(all_conditions) > 0
            }
            
            print("   ✅ Condition analysis completed")
            print(f"     Legacy Conditions: {analysis_results['conditions']['legacy_conditions']}")
            print(f"     Questions with Relevance: {questions_with_relevance}")
            
        except Exception as e:
            error_msg = f"Condition analysis failed: {e}"
            analysis_results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # 3. Response Analysis
        print("\n📈 3. Response Data Analysis")
        try:
            response_ids = api.responses.get_all_response_ids(survey_id)
            
            analysis_results['responses'] = {
                'count': len(response_ids),
                'exportable': False,
                'fields': 0
            }
            
            if response_ids:
                # Try to export data
                responses = api.responses.export_responses(survey_id, document_type='json')
                if isinstance(responses, list) and responses:
                    analysis_results['responses'].update({
                        'exportable': True,
                        'fields': len(responses[0]),
                        'data_points': len(responses) * len(responses[0])
                    })
            
            print("   ✅ Response analysis completed")
            print(f"     Total Responses: {analysis_results['responses']['count']}")
            print(f"     Data Exportable: {'Yes' if analysis_results['responses']['exportable'] else 'No'}")
            if analysis_results['responses']['exportable']:
                print(f"     Fields per Response: {analysis_results['responses']['fields']}")
            
        except Exception as e:
            error_msg = f"Response analysis failed: {e}"
            analysis_results['errors'].append(error_msg)
            print(f"   ❌ {error_msg}")
        
        # 4. Participant Analysis
        print("\n👥 4. Participant Data Analysis")
        try:
            participants = api.participants.list_participants(survey_id)
            
            completed = sum(1 for p in participants if p.get('completed') == 'Y')
            analysis_results['participants'] = {
                'available': True,
                'count': len(participants),
                'completed': completed,
                'completion_rate': (completed / len(participants) * 100) if participants else 0
            }
            
            print("   ✅ Participant analysis completed")
            print(f"     Total Participants: {len(participants)}")
            print(f"     Completed: {completed}")
            print(f"     Completion Rate: {analysis_results['participants']['completion_rate']:.1f}%")
            
        except Exception as e:
            analysis_results['participants'] = {
                'available': False,
                'reason': str(e)
            }
            print("   ℹ️ Participant data not available (anonymous survey)")
    
    # Summary
    print("\n" + "=" * 60)
    if analysis_results['errors']:
        print(f"⚠️ Analysis completed with {len(analysis_results['errors'])} issues")
        analysis_results['success'] = False
    else:
        print("✅ Complete analysis successful!")
    
    print(f"\n📊 Survey Analysis Summary:")
    print(f"  📋 Title: {analysis_results['survey_info'].get('title', 'Unknown')}")
    print(f"  🏗️ Structure: {analysis_results['structure'].get('groups', 0)} groups, {analysis_results['structure'].get('questions', 0)} questions")
    print(f"  📈 Responses: {analysis_results['responses'].get('count', 0)} total")
    print(f"  👥 Participants: {'Available' if analysis_results['participants'].get('available') else 'Anonymous survey'}")
    
    return analysis_results

# Run complete analysis
complete_results = complete_survey_analysis(api, survey_id) if survey_id else None

# === CELL: Data Analysis Ready ===
print_section("Ready for Data Analysis", "🚀")

def show_analysis_readiness(df, complete_results):
    """Show what's ready for data analysis"""
    
    print("🎉 LimeSurvey Data Export Complete!")
    print("=" * 50)
    
    if df is not None:
        print("✅ Survey data successfully exported and ready for analysis!")
        print(f"\n📊 Your Data:")
        print(f"  Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"  Size: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")
        
        print(f"\n🔬 Recommended Next Steps:")
        analysis_steps = [
            "📊 Data Exploration: df.info(), df.describe(), df.head()",
            "🧹 Data Cleaning: Handle missing values, data types",
            "📈 Visualizations: Use matplotlib, seaborn, or plotly",
            "📉 Statistical Analysis: Use scipy, statsmodels",
            "🤖 Machine Learning: Use scikit-learn, tensorflow",
            "📋 Reporting: Create reports with this notebook"
        ]
        
        for i, step in enumerate(analysis_steps, 1):
            print(f"  {i}. {step}")
            
        print(f"\n💡 Quick Start Examples:")
        print("  # Basic exploration")
        print("  df.head()  # View first few rows")
        print("  df.info()  # Data types and missing values")
        print("  df.describe()  # Statistical summary")
        print()
        print("  # Visualization examples")
        print("  import matplotlib.pyplot as plt")
        print("  df['column_name'].hist()  # Histogram")
        print("  df.plot(kind='scatter', x='col1', y='col2')  # Scatter plot")
        
    else:
        print("ℹ️ No response data available for analysis")
        print("   This could be because:")
        print("   - The survey has no responses yet")
        print("   - Export permissions are restricted")
        print("   - The survey is inactive")
        
    if complete_results:
        print(f"\n📋 Analysis Summary Available:")
        print(f"  Survey ID: {complete_results['survey_id']}")
        print(f"  Success: {'✅' if complete_results['success'] else '❌'}")
        if complete_results['errors']:
            print(f"  Issues: {len(complete_results['errors'])} warnings/errors")
    
    print(f"\n🛡️ Security Reminder:")
    print("  ✅ All operations were read-only")
    print("  ✅ No survey data was modified")
    print("  ✅ Credentials were handled securely")
    
    print(f"\n🎯 Mission Accomplished!")
    print("Your LimeSurvey data is now ready for analysis in Python! 🐍✨")

show_analysis_readiness(df, complete_results)

# === CELL: Final Summary ===
print_section("Demo Complete", "🎉")

print("🎊 LimeSurvey Analyzer Demo Complete!")
print("=" * 40)

print("\n📚 What you've seen:")
demo_features = [
    "🔐 Secure authentication methods",
    "📊 Survey listing and properties",
    "❓ Question structure exploration", 
    "📈 Response data export",
    "👥 Participant management",
    "📊 Statistics generation",
    "🎯 Complete analysis workflow"
]

for feature in demo_features:
    print(f"  {feature}")

print("\n🚀 Ready to use in your own projects!")
print("Copy the sections above into Jupyter notebook cells for interactive analysis.")

print(f"\n💡 Pro Tips:")
tips = [
    "Use environment variables for credentials in production",
    "Always use context managers (with api:) for session management",
    "Export data as JSON for fastest processing with pandas",
    "Handle exceptions gracefully for robust applications",
    "Remember: this library is read-only for safety"
]

for i, tip in enumerate(tips, 1):
    print(f"  {i}. {tip}")

print("\nHappy analyzing! 📊✨") 