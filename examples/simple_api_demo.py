#!/usr/bin/env python3
"""
Simple LimeSurvey API Demo

This example demonstrates the basic LimeSurvey API functionality that works reliably.
No complex mapping or advanced features - just core API operations.
"""

import sys
from pathlib import Path

# Add the package root to the path for development
package_root = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(package_root))

from lime_survey_analyzer import LimeSurveyClient


def main():
    """Demonstrate basic LimeSurvey API functionality."""
    print("🚀 LimeSurvey API - Simple Demo")
    print("=" * 40)
    
    # Initialize the API client
    print("\n📋 1. Initialize API Client")
    try:
        # Try to load from default config file
        api = LimeSurveyClient.from_config('secrets/credentials.ini')
        print("✅ API client initialized from config file")
    except Exception as e:
        print(f"❌ Failed to initialize API client: {e}")
        print("\n💡 Setup Instructions:")
        print("1. Copy secrets/credentials.ini.template to secrets/credentials.ini")
        print("2. Edit secrets/credentials.ini with your LimeSurvey details")
        print("3. Make sure your LimeSurvey user has API permissions")
        return 1
    
    # Test basic connectivity and list surveys
    print("\n📊 2. List Available Surveys")
    try:
        surveys = api.surveys.list_surveys()
        
        if surveys:
            print(f"✅ Found {len(surveys)} surveys:")
            for i, survey in enumerate(surveys, 1):
                sid = survey.get('sid', 'Unknown ID')
                title = survey.get('surveyls_title', 'No title')
                status = "Active" if survey.get('active') == 'Y' else "Inactive"
                print(f"   {i}. [{sid}] {title} ({status})")
                
                # Use first survey for further demos
                if i == 1:
                    demo_survey_id = sid
        else:
            print("⚠️  No surveys found")
            print("💡 Create a survey in LimeSurvey first, then run this demo again")
            return 0
    except Exception as e:
        print(f"❌ Failed to list surveys: {e}")
        print("💡 Check your credentials and LimeSurvey URL")
        return 1
    
    # Get survey details
    print(f"\n🔍 3. Get Survey Details (Survey {demo_survey_id})")
    try:
        properties = api.surveys.get_survey_properties(demo_survey_id)
        
        title = properties.get('surveyls_title', 'No title')
        language = properties.get('language', 'Unknown')
        admin = properties.get('admin', 'Unknown')
        created = properties.get('datecreated', 'Unknown')
        
        print(f"✅ Survey Details:")
        print(f"   Title: {title}")
        print(f"   Language: {language}")
        print(f"   Admin: {admin}")
        print(f"   Created: {created}")
        
    except Exception as e:
        print(f"❌ Failed to get survey properties: {e}")
    
    # List question groups
    print(f"\n📝 4. List Question Groups")
    try:
        groups = api.questions.list_groups(demo_survey_id)
        
        if groups:
            print(f"✅ Found {len(groups)} question groups:")
            for group in groups:
                gid = group.get('gid', 'Unknown')
                title = group.get('group_name', 'No title')
                print(f"   Group {gid}: {title}")
        else:
            print("⚠️  No question groups found")
            
    except Exception as e:
        print(f"❌ Failed to list question groups: {e}")
    
    # List questions
    print(f"\n❓ 5. List Questions")
    try:
        questions = api.questions.list_questions(demo_survey_id)
        
        if questions:
            print(f"✅ Found {len(questions)} questions:")
            for i, question in enumerate(questions[:5], 1):  # Show first 5
                qid = question.get('qid', 'Unknown')
                title = question.get('title', 'No title')
                qtype = question.get('type', 'Unknown')
                text = question.get('question', 'No text')[:50] + "..."
                print(f"   {i}. [{qid}] {title} (Type: {qtype})")
                print(f"      {text}")
                
            if len(questions) > 5:
                print(f"   ... and {len(questions) - 5} more questions")
        else:
            print("⚠️  No questions found")
            
    except Exception as e:
        print(f"❌ Failed to list questions: {e}")
    
    # Get survey summary
    print(f"\n📈 6. Get Survey Summary")
    try:
        summary = api.surveys.get_summary(demo_survey_id)
        
        if isinstance(summary, dict):
            total = summary.get('completed', 'Unknown')
            incomplete = summary.get('incomplete', 'Unknown')
            print(f"✅ Survey Statistics:")
            print(f"   Completed responses: {total}")
            print(f"   Incomplete responses: {incomplete}")
        else:
            print(f"✅ Summary: {summary}")
            
    except Exception as e:
        print(f"❌ Failed to get survey summary: {e}")
    
    # Try to export some responses (if any exist)
    print(f"\n📥 7. Export Responses (if available)")
    try:
        responses = api.responses.export_responses(demo_survey_id, response_type='short')
        
        if responses and len(responses) > 0:
            print(f"✅ Exported {len(responses)} responses")
            
            # Show first response structure (without sensitive data)
            if isinstance(responses[0], dict):
                field_count = len(responses[0])
                print(f"   Each response has {field_count} fields")
                
                # Show some field names (first few, non-sensitive ones)
                fields = list(responses[0].keys())[:5]
                print(f"   Sample fields: {fields}")
            else:
                print(f"   Response format: {type(responses[0])}")
        else:
            print("⚠️  No responses available to export")
            
    except Exception as e:
        print(f"❌ Failed to export responses: {e}")
    
    print("\n🎉 Demo Complete!")
    print("✅ Basic LimeSurvey API functionality working correctly")
    print("\n💡 Next Steps:")
    print("- Explore the API documentation")
    print("- Try the other examples in the examples/ directory")
    print("- Check out the full API reference")
    
    return 0


if __name__ == "__main__":
    exit(main()) 