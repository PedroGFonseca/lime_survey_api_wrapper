#!/usr/bin/env python3
"""
Quick test script using local credentials.
This file is safe to modify for testing - it's in .gitignore
"""

from lime_survey_analyzer import LimeSurveyDirectAPI

def test_api():
    print("🚀 Quick API Test")
    
    # Try local config first
    try:
        api = LimeSurveyDirectAPI.from_config('test_credentials.ini')
        print("✅ Using test_credentials.ini")
    except Exception as e:
        print(f"❌ Config file error: {e}")
        print("📝 Please edit test_credentials.ini with your real credentials")
        return
    
    # Test list_surveys
    try:
        print("\n📊 Testing list_surveys()...")
        surveys = api.surveys.list_surveys()
        
        print(f"✅ Success! Type: {type(surveys)}")
        print(f"📊 Count: {len(surveys) if hasattr(surveys, '__len__') else 'No length'}")
        
        if isinstance(surveys, list):
            print("✅ Response is a list")
            for i, survey in enumerate(surveys[:3]):
                if isinstance(survey, dict):
                    sid = survey.get('sid', 'No ID')
                    title = survey.get('surveyls_title', 'No title')
                    print(f"  {i+1}. [{sid}] {title}")
                else:
                    print(f"  {i+1}. Unexpected survey type: {type(survey)}")
        else:
            print(f"❌ Response is not a list: {repr(surveys)}")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api() 