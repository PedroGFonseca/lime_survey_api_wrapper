# LimeSurvey Analyzer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python client for LimeSurvey's RemoteControl 2 API that provides easy access to survey data and comprehensive analysis tools.

## 🚀 Quick Start

### Installation

```bash
pip install lime-survey-analyzer
```

### Setup

Create a configuration file with your LimeSurvey credentials:

```ini
# secrets/credentials.ini
[limesurvey]
url = https://your-limesurvey.com/admin/remotecontrol
username = your_username
password = your_password
```

### Basic Usage

```python
from lime_survey_analyzer import LimeSurveyClient, SurveyAnalysis

# Connect to LimeSurvey
api = LimeSurveyClient.from_config('secrets/credentials.ini')

# List surveys
surveys = api.surveys.list_surveys()
print(f"Found {len(surveys)} surveys")

# Export response data
survey_id = "123456"
responses = api.responses.export_responses(survey_id)
print(f"Exported {len(responses)} responses")
```

## 📊 Survey Analysis

For comprehensive survey analysis with automatic question processing:

```python
from lime_survey_analyzer import SurveyAnalysis

# Analyze a survey
analysis = SurveyAnalysis(survey_id)
analysis.setup()  # Load survey structure and responses
analysis.process_all_questions()  # Process all question types

# Get processed results
results = analysis.processed_responses
for question_id, result in results.items():
    print(f"Question {question_id}:")
    print(result)
    print("-" * 40)
```

## 🔧 Core Features

- **Survey Management**: List, get properties, summaries
- **Question Handling**: All question types (radio, multiple choice, ranking, text, arrays)
- **Response Export**: Complete response data with field mappings
- **Data Analysis**: Automatic processing of survey responses
- **Type Safety**: Comprehensive type hints and validation
- **Caching**: Intelligent caching for API calls

## 📖 API Overview

### Survey Operations
```python
# Get survey info
properties = api.surveys.get_survey_properties(survey_id)
summary = api.surveys.get_summary(survey_id)

# List questions and groups
questions = api.questions.list_questions(survey_id)
groups = api.questions.list_groups(survey_id)
```

### Response Data
```python
# Export all responses
responses = api.responses.export_responses(survey_id)

# Get field mappings
fieldmap = api.surveys.get_fieldmap(survey_id)

# Get statistics
stats = api.responses.get_summary(survey_id, "all")
```

### Question Analysis
```python
# Get detailed question structure
question = api.questions.get_question_structured(survey_id, question_id)

# Get answer mappings
mappings = question.get_complete_response_mapping()
```

## 🛠️ Data Safety

The library automatically protects sensitive data:
- Credentials are stored in gitignored `secrets/` directory
- Survey data patterns are automatically excluded from version control
- Built-in validation prevents committing sensitive information

## 📝 Requirements

- Python 3.8+
- LimeSurvey with RemoteControl 2 API enabled
- Valid LimeSurvey user account with API access

## 🤝 Contributing

This library provides a foundation for LimeSurvey integration. Core functionality includes robust API access, data export, and survey analysis capabilities.

## 📄 License

MIT License. See LICENSE file for details.
