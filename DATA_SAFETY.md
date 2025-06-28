# 🔒 Data Safety Guide

## **CRITICAL: Never commit real survey data to git**

This repository contains tools for analyzing LimeSurvey data. Real survey responses often contain **personally identifiable information (PII)** and must never be committed to version control.

## **🚨 PROTECTED PATTERNS**

The following patterns are automatically ignored by git to protect sensitive data:

### **Survey ID Protection**
```bash
# Specific survey (example: YOUR_SURVEY_ID)
*survey_YOUR_SURVEY_ID*
*YOUR_SURVEY_ID*

# Any 6-digit survey ID patterns
survey_[0-9]*/
*_survey_[0-9]*
*_[0-9][0-9][0-9][0-9][0-9][0-9]*
```

### **Data Files (automatically ignored)**
```bash
# Survey exports and responses
*survey_data*
*survey_responses*
*responses*
*participant*
survey_*.csv
survey_*.json
survey_*.xlsx
response_*.csv
response_*.json

# LimeSurvey exports
*_responses_export*
*_structure_export*
*_participants_export*
lime_survey_export_*

# Analysis outputs
*_analysis_output*
*_analysis_results*
human_readable_*
advanced_analysis.*
```

### **Development Files (automatically ignored)**
```bash
# Real data testing
*_real_data*
*_live_data*
*_real_survey*
test_real_*
*_real_test*

# Cache directories
survey_cache/
response_cache/
api_cache/
```

## **✅ SAFE DEVELOPMENT PRACTICES**

### **1. Use Naming Conventions**
Always include safety keywords in filenames when working with real data:

```python
# ✅ SAFE - Will be ignored by git
test_real_data_YOUR_SURVEY_ID.py
survey_YOUR_SURVEY_ID_analysis_real.json
responses_real_data.csv
my_analysis_live_data.ipynb

# ❌ DANGEROUS - Could be committed
test_survey.py
analysis_results.json
survey_responses.csv
my_analysis.ipynb
```

### **2. Use Safe Directories**
Create local directories that are automatically ignored:

```bash
# ✅ SAFE - These directories are gitignored
mkdir real_data/
mkdir survey_cache/
mkdir temp/
mkdir survey_YOUR_SURVEY_ID/

# Store your real data analysis here
real_data/my_analysis.py
survey_cache/cached_responses.json
temp/test_results.csv
survey_YOUR_SURVEY_ID/analysis.ipynb
```

### **3. Testing with Real Data**
When testing with real surveys:

```python
# ✅ SAFE - Use real data patterns
def test_with_real_survey():
    """This file would be named: test_real_data_integration.py"""
    analyzer = SurveyAnalysis("YOUR_SURVEY_ID")  # Real survey ID
    analyzer.setup()
    # ... your analysis
    
    # Save results in safe location
    results.to_csv("real_data/test_results_YOUR_SURVEY_ID.csv")  # Gitignored
```

## **🔍 VERIFICATION COMMANDS**

### **Check what git would commit:**
```bash
# See what files git would add
git add . --dry-run

# Check git status before committing
git status

# Verify no sensitive files are staged
git diff --cached --name-only
```

### **Find potentially sensitive files:**
```bash
# Search for survey IDs in your files
grep -r "YOUR_SURVEY_ID" . --exclude-dir=.git

# Find files with survey data patterns
find . -name "*survey*" -type f
find . -name "*YOUR_SURVEY_ID*" -type f
find . -name "*response*" -type f
```

## **🚀 RECOMMENDED WORKFLOW**

### **For Integration Testing:**
```python
# File: tests/test_step1_real_survey_validation.py (GITIGNORED)
"""
Local validation using real survey YOUR_SURVEY_ID.
This file is automatically gitignored for safety.
"""

def test_step1_with_real_data():
    analyzer = SurveyAnalysis("YOUR_SURVEY_ID")
    analyzer.setup(enable_enhanced_output=True)
    analyzer.process_all_questions()
    
    # Verify enhanced output works
    enhanced = analyzer.get_processed_responses(enhanced=True)
    assert len(enhanced) > 0
    
    # Save validation report locally (gitignored location)
    import json
    with open("real_data/step1_validation_report.json", "w") as f:
        json.dump({
            "questions_processed": len(enhanced),
            "enhancement_successful": True
        }, f)
```

### **For Development Analysis:**
```python
# File: real_data/my_survey_analysis.py (GITIGNORED)
"""
Personal analysis of survey YOUR_SURVEY_ID.
This entire directory is gitignored.
"""

from lime_survey_analyzer.analyser import SurveyAnalysis

# Safe to use real survey ID here
analyzer = SurveyAnalysis("YOUR_SURVEY_ID")
analyzer.setup(enable_enhanced_output=True)
analyzer.process_all_questions()

# Analysis results saved in gitignored location
enhanced_results = analyzer.get_processed_responses(enhanced=True)
for qid, result in enhanced_results.items():
    print(f"Question {qid}: {result.viz_hints.optimal_chart}")
```

## **🎯 SYNTHETIC DATA FOR TESTS**

For committed tests, always use synthetic data:

```python
# File: tests/test_step1_integration.py (COMMITTED)
"""
Safe test using only synthetic data.
This file can be safely committed.
"""

@pytest.fixture
def mock_analyzer_with_data():
    """Create analyzer with SYNTHETIC data only"""
    analyzer = SurveyAnalysis("999999")  # Fake survey ID
    
    # Mock data - no real survey content
    analyzer.questions = pd.DataFrame({
        'qid': ['12345', '12346'],
        'title': ['Q1', 'Q2'],
        'question': ['Test Question 1?', 'Test Question 2?'],
        'question_theme_name': ['listradio', 'multiplechoice'],
        'mandatory': ['Y', 'N']
    })
    
    # Synthetic responses - no real user data
    analyzer.processed_responses = {
        '12345': pd.Series({'Option A': 10, 'Option B': 15}),
        '12346': pd.DataFrame({
            'option_text': ['Choice 1', 'Choice 2'],
            'absolute_counts': [8, 12],
            'response_rates': [0.4, 0.6]
        })
    }
    
    return analyzer
```

## **⚠️ EMERGENCY: Accidentally Committed Sensitive Data?**

If you accidentally commit real survey data:

```bash
# 1. DON'T PUSH to remote repository
# 2. Remove from git history immediately
git reset --soft HEAD~1  # Undo last commit (keep files)
git reset HEAD .          # Unstage everything
git status               # Verify sensitive files are unstaged

# 3. Move sensitive files to safe location
mkdir -p real_data/
mv *YOUR_SURVEY_ID* real_data/   # Move to gitignored directory
mv *survey_data* real_data/
mv *responses* real_data/

# 4. Commit safely
git add .
git status               # Double-check no sensitive files
git commit -m "Safe commit - moved sensitive data to gitignored location"
```

## **📋 PRE-COMMIT CHECKLIST**

Before every commit:

- [ ] Run `git status` and verify no files with survey IDs (YOUR_SURVEY_ID, etc.)
- [ ] Run `git diff --cached --name-only` to see exactly what's being committed
- [ ] Ensure no files contain real participant responses
- [ ] Verify no API credentials or authentication files
- [ ] Check that test files use only synthetic/mock data
- [ ] Confirm analysis outputs are in gitignored directories

## **🔧 AUTOMATED SAFETY**

Consider adding a pre-commit hook:

```bash
# File: .git/hooks/pre-commit
#!/bin/bash
# Check for potentially sensitive patterns
if git diff --cached --name-only | grep -E "(YOUR_SURVEY_ID|survey_data|responses)" > /dev/null; then
    echo "❌ BLOCKED: Potential sensitive data detected!"
    echo "Files containing survey data patterns:"
    git diff --cached --name-only | grep -E "(YOUR_SURVEY_ID|survey_data|responses)"
    echo ""
    echo "Move these files to gitignored directories before committing."
    exit 1
fi
echo "✅ Safety check passed"
```

Remember: **When in doubt, don't commit.** It's better to be overly cautious with survey data. 