#!/usr/bin/env python3
"""
LimeSurvey Analyzer - Basic Usage Example

This script demonstrates basic usage of the LimeSurvey Analyzer library.
"""

from lime_survey_analyzer import LimeSurveyDirectAPI
import json
from pprint import pprint


def main():
    """Main example function."""
    
    print("🚀 LimeSurvey Analyzer - Basic Usage Example\n")
    
    # Authentication (choose one method)
    print("🔐 Setting up authentication...")
    
    # Method 1: Environment variables (recommended)
    try:
        api = LimeSurveyDirectAPI.from_env()
        print("✅ Using environment variables")
    except Exception:
        print("❌ Environment variables not set")
        
        # Method 2: Interactive prompt (fallback)
        print("🔑 Please enter your credentials:")
        api = LimeSurveyDirectAPI.from_prompt()
    
    # Use context manager for automatic session management
    with api:
        print("\n📊 Getting survey information...")
        
        # 1. List all surveys
        surveys = api.surveys.list_surveys()
        print(f"Found {len(surveys)} surveys:")
        
        for i, survey in enumerate(surveys[:3], 1):  # Show first 3
            print(f"  {i}. Survey {survey['sid']}: {survey['surveyls_title']}")
            print(f"     Status: {'Active' if survey['active'] == 'Y' else 'Inactive'}")
        
        if not surveys:
            print("❌ No surveys found. Check your permissions.")
            return
        
        # 2. Work with the first survey
        survey_id = surveys[0]['sid']
        print(f"\n🔍 Analyzing survey {survey_id}...")
        
        # Get survey properties
        survey_props = api.surveys.get_survey_properties(survey_id)
        print(f"Survey title: {survey_props.get('surveyls_title', 'Unknown')}")
        print(f"Active: {'Yes' if survey_props.get('active') == 'Y' else 'No'}")
        print(f"Anonymous: {'Yes' if survey_props.get('anonymized') == 'Y' else 'No'}")
        
        # 3. Explore survey structure
        print(f"\n❓ Exploring survey structure...")
        
        # Get question groups
        groups = api.questions.list_groups(survey_id)
        print(f"Question groups: {len(groups)}")
        
        for group in groups:
            print(f"  - Group {group['gid']}: {group['group_name']}")
        
        # Get questions
        questions = api.questions.list_questions(survey_id)
        print(f"Questions: {len(questions)}")
        
        for question in questions[:3]:  # Show first 3
            print(f"  - Q{question['qid']}: {question['title']} ({question['type']})")
        
        # 4. Get response data
        print(f"\n📈 Getting response data...")
        
        # Get response IDs
        response_ids = api.responses.get_response_ids(survey_id)
        print(f"Total responses: {len(response_ids)}")
        
        if response_ids:
            # Export responses as JSON
            responses = api.responses.export_responses(survey_id, document_type='json')
            
            if isinstance(responses, list) and responses:
                print(f"Exported {len(responses)} responses")
                print(f"Fields per response: {len(responses[0])}")
                
                # Show first response (sample)
                print("\nSample response (first 3 fields):")
                first_response = responses[0]
                for i, (key, value) in enumerate(first_response.items()):
                    if i >= 3:
                        break
                    print(f"  {key}: {value}")
                print(f"  ... and {len(first_response) - 3} more fields")
                
                # Save responses to file
                with open(f'survey_{survey_id}_responses.json', 'w') as f:
                    json.dump(responses, f, indent=2)
                print(f"\n💾 Responses saved to: survey_{survey_id}_responses.json")
                
            else:
                print("No response data available")
        else:
            print("No responses found in this survey")
        
        # 5. Try to get statistics
        print(f"\n📊 Getting survey statistics...")
        try:
            stats = api.responses.export_statistics(survey_id)
            print("✅ Statistics exported successfully")
            print(f"Statistics type: {type(stats)}")
        except Exception as e:
            print(f"❌ Statistics export failed: {e}")
            print("(This is normal for surveys with no responses)")
        
        # 6. Check participants (if available)
        print(f"\n👥 Checking participant data...")
        try:
            participants = api.participants.list_participants(survey_id)
            print(f"Found {len(participants)} participants")
        except Exception as e:
            print(f"❌ Participant data not available: {e}")
            print("(Many surveys use anonymous responses)")
    
    print("\n✅ Example completed successfully!")
    print("\n💡 Next steps:")
    print("   - Analyze your data with pandas: pd.DataFrame(responses)")
    print("   - Create visualizations with matplotlib or plotly")
    print("   - Perform statistical analysis with scipy")
    print("   - Build ML models with scikit-learn")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your credentials and network connection.") 