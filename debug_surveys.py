#!/usr/bin/env python3
"""
Debug script to diagnose the slice error with surveys.
"""

try:
    from lime_survey_analyzer import LimeSurveyDirectAPI
    
    print("🔧 Debug: Testing API response types...")
    
    # Try to create API client
    try:
        api = LimeSurveyDirectAPI.from_env()
        print("✅ API client created")
    except ValueError as e:
        print(f"❌ Environment variables not set: {e}")
        print("🔑 Using interactive prompt instead...")
        api = LimeSurveyDirectAPI.from_prompt()
    
    print("\n🔍 Testing list_surveys()...")
    
    try:
        surveys = api.surveys.list_surveys()
        
        print(f"✅ API call successful")
        print(f"📊 Response type: {type(surveys)}")
        print(f"📊 Response: {repr(surveys)}")
        
        if hasattr(surveys, '__len__'):
            print(f"📊 Length: {len(surveys)}")
        else:
            print("❌ No __len__ attribute")
            
        if hasattr(surveys, '__getitem__'):
            print("✅ Has __getitem__ (supports indexing)")
        else:
            print("❌ No __getitem__ (doesn't support indexing)")
            
        # Test if we can slice it
        try:
            slice_test = surveys[:3]
            print(f"✅ Slicing works: {type(slice_test)}")
        except Exception as e:
            print(f"❌ Slicing failed: {e}")
            
        # Test if we can iterate
        try:
            for i, survey in enumerate(surveys):
                print(f"✅ Survey {i}: {type(survey)} - {repr(survey)}")
                if i >= 2:  # Show first 3
                    break
        except Exception as e:
            print(f"❌ Iteration failed: {e}")
            
    except Exception as e:
        print(f"❌ API call failed: {e}")
        import traceback
        traceback.print_exc()
        
except ImportError as e:
    print(f"❌ Import failed: {e}") 