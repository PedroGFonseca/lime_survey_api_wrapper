# LimeSurvey API Client

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for LimeSurvey's RemoteControl 2 API that provides simple, reliable access to your survey data.

## 🚀 Quick Start

### 1. Installation

```bash
pip install lime-survey-analyzer
```

### 2. Setup Credentials

```bash
# Create credentials file
python3 setup_credentials.py --create-template

# Edit with your LimeSurvey details
nano secrets/credentials.ini

# Test connection
python3 setup_credentials.py --test-only
```

Or see [GETTING_STARTED.md](GETTING_STARTED.md) for detailed setup instructions.

### 3. Your First API Call

```python
from lime_survey_analyzer import LimeSurveyClient

# Initialize and connect
api = LimeSurveyClient.from_config()

# List your surveys
surveys = api.surveys.list_surveys()
for survey in surveys:
    print(f"Survey {survey['sid']}: {survey['surveyls_title']}")
```

## 📊 Getting Response Data (The Main Use Case)

Most users want to **export and analyze response data**. Here's the complete journey:

### Step 1: Find Your Survey
```python
from lime_survey_analyzer import LimeSurveyClient

api = LimeSurveyClient.from_config()

# List all surveys you have access to
surveys = api.surveys.list_surveys()

for survey in surveys:
    sid = survey['sid']
    title = survey['surveyls_title'] 
    status = "Active" if survey.get('active') == 'Y' else "Inactive"
    print(f"[{sid}] {title} - {status}")

# Pick your survey ID
survey_id = "123456"  # Replace with your survey ID
```

### Step 2: Check Survey Status
```python
# Get survey details and response count
properties = api.surveys.get_survey_properties(survey_id)
summary = api.surveys.get_summary(survey_id)

print(f"Survey: {properties['surveyls_title']}")
print(f"Language: {properties['language']}")
print(f"Completed responses: {summary.get('completed', 0)}")
print(f"Incomplete responses: {summary.get('incomplete', 0)}")
```

### Step 3: Understand Survey Structure
```python
# Get question structure
groups = api.questions.list_groups(survey_id)
questions = api.questions.list_questions(survey_id)

print(f"Question groups: {len(groups)}")
print(f"Total questions: {len(questions)}")

# Show question details
for q in questions[:3]:  # First 3 questions
    print(f"Q{q['qid']} ({q['type']}): {q['title']}")
    print(f"  Text: {q['question'][:100]}...")
```

### Step 4: Export Response Data
```python
# Export all responses (most common)
responses = api.responses.export_responses(survey_id)
print(f"Exported {len(responses)} responses")

# Each response is a dictionary with field names as keys
if responses:
    first_response = responses[0]
    print(f"Response fields: {list(first_response.keys())}")
    print(f"Sample response: {first_response}")
```

### Step 5: Work with Field Names
```python
# Get field mapping to understand column names
fieldmap = api.surveys.get_fieldmap(survey_id)

print("Field mapping:")
for field_name, field_info in fieldmap.items():
    if field_info.get('qid'):  # Skip metadata fields
        qid = field_info['qid']
        qtype = field_info.get('type', 'Unknown')
        question = field_info.get('question', 'No text')[:50]
        print(f"  {field_name} -> Q{qid} ({qtype}): {question}...")
```

### Step 6: Export Specific Data
```python
# Export only specific fields
key_fields = ['id', 'submitdate', 'Q1', 'Q2', 'Q3']
filtered_responses = api.responses.export_responses(
    survey_id, 
    fields=key_fields
)

# Export in different format
short_responses = api.responses.export_responses(
    survey_id, 
    response_type='short'  # or 'long'
)

# Save to file
import json
with open(f'survey_{survey_id}_responses.json', 'w') as f:
    json.dump(responses, f, indent=2)

print(f"Responses saved to survey_{survey_id}_responses.json")
```

## 📋 Complete API Reference

### 🗂️ Survey Operations (`api.surveys`)

#### `list_surveys(username=None)`
Get all surveys accessible to your user.

```python
surveys = api.surveys.list_surveys()
# Returns: List of survey dictionaries
# Each survey has: sid, surveyls_title, startdate, expires, active
```

#### `get_survey_properties(survey_id, language=None)`
Get detailed information about a specific survey.

```python
props = api.surveys.get_survey_properties("123456")
# Returns: Dictionary with survey settings, title, admin, dates, etc.
# Key fields: surveyls_title, language, admin, datecreated, active
```

#### `get_summary(survey_id, stat_name="all")`
Get response statistics for a survey.

```python
summary = api.surveys.get_summary("123456")
# Returns: Dictionary with response counts
# Key fields: completed, incomplete, full_responses
```

#### `get_fieldmap(survey_id, language=None)`
Get field mapping that shows how database columns relate to questions.

```python
fieldmap = api.surveys.get_fieldmap("123456")
# Returns: Dictionary mapping field names to question metadata
# Essential for understanding response data structure
```

### ❓ Question Operations (`api.questions`)

#### `list_groups(survey_id)`
Get question groups (sections) in a survey.

```python
groups = api.questions.list_groups("123456")
# Returns: List of group dictionaries
# Each group has: gid, group_name, group_order, description
```

#### `list_questions(survey_id)`
Get all questions in a survey.

```python
questions = api.questions.list_questions("123456")
# Returns: List of question dictionaries  
# Each question has: qid, title, question, type, gid, mandatory
```

#### `get_question_properties(question_id)`
Get detailed properties for a specific question.

```python
props = api.questions.get_question_properties("456")
# Returns: Dictionary with question settings, validation, etc.
```

### 📥 Response Operations (`api.responses`)

#### `export_responses(survey_id, response_type='short', fields=None, **kwargs)`
**The main method for getting response data.**

```python
# Export all responses
responses = api.responses.export_responses("123456")

# Export specific format
responses = api.responses.export_responses("123456", response_type='long')

# Export only certain fields
responses = api.responses.export_responses(
    "123456", 
    fields=['id', 'submitdate', 'Q1', 'Q2']
)

# Additional options
responses = api.responses.export_responses(
    "123456",
    response_type='short',
    language='en',
    completion_status='complete'  # or 'incomplete', 'all'
)
```

**Return format:** List of dictionaries, where each dictionary is one response with field names as keys.

#### `get_response_statistics(survey_id)`
Get statistics about responses.

```python
stats = api.responses.get_response_statistics("123456")
# Returns: Dictionary with statistical information
```

### 👥 Participant Operations (`api.participants`)

#### `list_participants(survey_id, **kwargs)`
Get participant list (if survey uses invitation tokens).

```python
participants = api.participants.list_participants("123456")
# Returns: List of participant dictionaries
# Each participant has: tid, token, firstname, lastname, email
```

#### `get_participant_properties(survey_id, token)`
Get detailed participant information.

```python
info = api.participants.get_participant_properties("123456", "TOKEN123")
# Returns: Dictionary with participant details
```

## 🔧 Common Patterns

### Analyzing Multiple Surveys
```python
api = LimeSurveyClient.from_config()

for survey in api.surveys.list_surveys():
    sid = survey['sid']
    title = survey['surveyls_title']
    
    # Check if survey has responses
    summary = api.surveys.get_summary(sid)
    response_count = summary.get('completed', 0)
    
    if response_count > 0:
        print(f"\n=== {title} ({response_count} responses) ===")
        
        # Get structure
        questions = api.questions.list_questions(sid)
        print(f"Questions: {len(questions)}")
        
        # Export data
        responses = api.responses.export_responses(sid)
        print(f"Exported: {len(responses)} responses")
        
        # Save to file
        filename = f"survey_{sid}_data.json"
        with open(filename, 'w') as f:
            json.dump({
                'survey_info': survey,
                'questions': questions,
                'responses': responses
            }, f, indent=2)
        print(f"Saved: {filename}")
```

### Data Processing Pipeline
```python
import pandas as pd

# 1. Get response data
responses = api.responses.export_responses(survey_id)

# 2. Convert to pandas DataFrame
df = pd.DataFrame(responses)

# 3. Get field mapping for better column names
fieldmap = api.surveys.get_fieldmap(survey_id)

# 4. Create mapping of database fields to question titles
field_to_question = {}
for field, info in fieldmap.items():
    if info.get('qid'):
        title = info.get('title', f"Q{info['qid']}")
        field_to_question[field] = title

# 5. Rename columns
df_renamed = df.rename(columns=field_to_question)

# 6. Basic analysis
print(f"Total responses: {len(df)}")
print(f"Response fields: {list(df.columns)}")
print(f"First response:\n{df.iloc[0]}")
```

### Error Handling Best Practices
```python
from lime_survey_analyzer.exceptions import (
    AuthenticationError, APIError, ConfigurationError
)

def safe_export_responses(api, survey_id):
    """Safely export responses with comprehensive error handling."""
    try:
        # Check survey exists and get info
        properties = api.surveys.get_survey_properties(survey_id)
        print(f"Survey: {properties['surveyls_title']}")
        
        # Check if survey has responses
        summary = api.surveys.get_summary(survey_id)
        completed = summary.get('completed', 0)
        
        if completed == 0:
            print("No completed responses found")
            return []
        
        print(f"Exporting {completed} responses...")
        
        # Export responses
        responses = api.responses.export_responses(survey_id)
        print(f"Successfully exported {len(responses)} responses")
        
        return responses
        
    except ConfigurationError:
        print("❌ Configuration error - check credentials file")
    except AuthenticationError:
        print("❌ Authentication failed - check username/password")
    except APIError as e:
        print(f"❌ API error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    return []

# Usage
api = LimeSurveyClient.from_config()
responses = safe_export_responses(api, "123456")
```

## 🛡️ Security & Best Practices

### Credential Management
- ✅ Store credentials in `secrets/credentials.ini` (git-ignored)
- ✅ Use HTTPS URLs for production  
- ✅ Regularly rotate API credentials
- ✅ Limit API user permissions to minimum required

### Performance Tips
- Use persistent sessions for multiple API calls
- Export only needed fields when dealing with large surveys
- Cache survey structure data (questions, fieldmap) as it rarely changes

### Common Issues
- **"Invalid session key"**: Session expired, reconnect with `api.connect()`
- **"No permission"**: Check user has access to survey in LimeSurvey admin
- **"Survey not found"**: Verify survey ID and that survey is active

## 🤝 Contributing

We welcome contributions! Priority areas:
1. Additional API endpoints
2. Better error handling and recovery
3. Performance optimizations
4. More usage examples

## 📄 License

MIT License - see LICENSE file for details.

---

**Simple, reliable access to your LimeSurvey data in Python** 🚀
