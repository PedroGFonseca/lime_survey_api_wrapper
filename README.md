# LimeSurvey Analyzer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive, **read-only** Python client for LimeSurvey's RemoteControl 2 API. Easily access survey data, metadata, and analytics with an intuitive, organized interface.

## 🤔 What This Library Does & Doesn't Do

### ✅ **What It DOES:**
- **📖 Read survey data**: Export responses, get question details, survey metadata
- **📊 Access analytics**: Export statistics and summary reports  
- **🔍 Explore structure**: List surveys, questions, groups, and participants
- **📤 Export data**: Get your data in JSON, CSV, Excel, XML, or PDF formats
- **🔐 Secure access**: Multiple authentication methods with credential protection
- **🐍 Python integration**: Clean, type-safe interface for data science workflows

### ❌ **What It DOES NOT Do:**
- **✏️ Modify surveys**: Cannot create, edit, or delete surveys, questions, or responses
- **👥 Manage users**: Cannot add/remove users or change permissions
- **🔧 Admin functions**: Cannot modify LimeSurvey settings or configurations  
- **📈 Data analysis**: Does not perform statistical analysis (use pandas, scipy, etc. for that)
- **📊 Visualizations**: Does not create charts or graphs (use matplotlib, plotly, etc.)
- **🤖 AI/ML**: No built-in machine learning or artificial intelligence features

### 🎯 **Perfect For:**
- Data scientists extracting survey data for analysis
- Researchers downloading response data for academic studies  
- Analysts creating reports from survey statistics
- Developers building read-only survey dashboards
- Anyone needing to integrate LimeSurvey data into Python workflows

### 🚫 **Not Suitable For:**
- Survey creation or editing workflows
- User management or administrative tasks
- Real-time survey modifications
- Complete survey analysis solutions (this gets the data, you analyze it)

## ✨ Features

- 🏗️ **Organized API Access**: Logical grouping of operations through specialized managers (Survey, Question, Response, Participant)
- 🔒 **Multiple Authentication Methods**: Environment variables, config files, or interactive prompts
- 📊 **Comprehensive Data Export**: Get survey responses in JSON, CSV, Excel, PDF formats
- 📈 **Built-in Analytics**: Export detailed statistics and summaries
- 📊 **Graph Visualization**: Visualize conditional question logic and survey flow (optional)
- 🐍 **Pythonic & Type-Safe**: Clean interface with full type hints for better IDE support
- 🛡️ **Production Ready**: Robust error handling, automatic session management, and secure credential handling
- 🔄 **Context Manager Support**: Automatic cleanup of API sessions
- 🐛 **Debug Support**: Optional debug logging with sensitive data protection
- ✅ **Comprehensive Testing**: 70% test coverage with 48 automated tests

## 📦 Installation

### From Source (Local Development)

1. Clone the repository:
```bash
git clone <repository-url>
cd lime-survey-analyzer
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

### Install with Documentation Dependencies
```bash
pip install -e ".[docs]"
```

### Install with Development Dependencies
```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

**📋 Before running examples**: Make sure you've installed the package first with `pip install -e .` from the project root directory.

### 1. Using Environment Variables (Recommended)

Set your credentials as environment variables:
```bash
export LIMESURVEY_URL="https://your-limesurvey.com/admin/remotecontrol"
export LIMESURVEY_USERNAME="your_username"
export LIMESURVEY_PASSWORD="your_password"
```

Then use the API:
```python
from lime_survey_analyzer import LimeSurveyDirectAPI

# Create client from environment variables
api = LimeSurveyDirectAPI.from_env()

# Use context manager for automatic session management
with api:
    # Survey operations through surveys manager
    surveys = api.surveys.list_surveys()
    for survey in surveys:
        print(f"Survey {survey['sid']}: {survey['surveyls_title']}")
    
    # Get survey details
    survey_props = api.surveys.get_survey_properties("123456")
    print(f"Survey status: {survey_props['active']}")
    
    # Question operations through questions manager
    questions = api.questions.list_questions("123456")
    
    # Response operations through responses manager
    responses = api.responses.export_responses("123456", "json")
    
    # Statistics
    stats = api.responses.export_statistics("123456")
```

### 2. Using Configuration File

Create a `credentials.ini` file:
```ini
[limesurvey]
url = https://your-limesurvey.com/admin/remotecontrol
username = your_username
password = your_password
```

```python
from lime_survey_analyzer import LimeSurveyDirectAPI

api = LimeSurveyDirectAPI.from_config('credentials.ini')
with api:
    surveys = api.surveys.list_surveys()
```

### 3. Interactive Prompts

```python
from lime_survey_analyzer import LimeSurveyDirectAPI

# Will prompt for credentials
api = LimeSurveyDirectAPI.from_prompt()
with api:
    surveys = api.surveys.list_surveys()
```

## 📋 API Reference

The API is organized into specialized managers for different types of operations:

### 📊 Survey Manager (`api.surveys`)

Access survey-level information and metadata:

- `list_surveys()` - Get all surveys you have access to with basic metadata
- `get_survey_properties(survey_id)` - Get comprehensive survey settings, status, and configuration
- `get_summary(survey_id)` - Get response count, completion statistics, and survey summary

### ❓ Question Manager (`api.questions`)

Explore survey structure and question details:

- `list_groups(survey_id)` - Get question groups with titles, descriptions, and ordering
- `get_group_properties(group_id)` - Get detailed group configuration and settings
- `list_questions(survey_id)` - Get all questions with types, codes, and basic properties
- `get_question_properties(question_id)` - Get complete question metadata including validation rules and display logic
- `list_conditions(survey_id, question_id=None)` - Get legacy condition rules that control question visibility
- `get_conditions(survey_id, question_id)` - Get detailed condition information for specific questions

**Conditional Questions**: LimeSurvey supports two systems for conditional logic:
- **Modern**: Relevance equations (found in `get_question_properties()` under 'relevance')
- **Legacy**: Condition rules (retrieved via `list_conditions()` and `get_conditions()`)

Both systems control when questions are shown to respondents based on previous answers.

### 📊 Response Manager (`api.responses`)

Export and analyze survey response data:

- `export_responses(survey_id, format="json")` - Export responses in various formats (JSON, CSV, Excel, PDF)
- `export_responses_by_token(survey_id, token, format="json")` - Export responses for specific participants
- `export_statistics(survey_id, format="pdf")` - Generate statistical summaries and reports
- `get_response_ids(survey_id, token)` - Get response IDs for a specific participant token
- `get_all_response_ids(survey_id)` - Get ALL response IDs in the survey (uses export method internally)

**Note**: The LimeSurvey `get_response_ids` API method requires a participant token. Use `get_all_response_ids()` to get all response IDs without needing specific tokens.

### 👥 Participant Manager (`api.participants`)

Manage participant data (when participant tables are enabled):

- `list_participants(survey_id)` - Get participant list with contact information and status
- `get_participant_properties(survey_id, query)` - Get detailed participant metadata and custom attributes

**Note**: Many surveys use anonymous responses and don't have participant tables, which will result in "No survey participants table" errors. This is normal behavior for anonymous surveys.

## 📊 Graph Visualization (Optional)

**NEW**: Visualize conditional question dependencies as interactive graphs!

The conditional nature of LimeSurvey questions forms a directed graph where:
- **Nodes**: Questions (colored by type: mandatory=red, hidden=gray, optional=blue)
- **Edges**: Conditional dependencies with logic labels
- **Groups**: Questions grouped by survey sections

### 🔧 Installation (Optional)

Graph visualization requires Graphviz:

```bash
# macOS
brew install graphviz
pip3 install graphviz

# Linux (Ubuntu/Debian)
sudo apt-get install graphviz
pip3 install graphviz

# Linux (RHEL/CentOS)
sudo yum install graphviz
pip3 install graphviz
```

### 📊 Usage

```python
from lime_survey_analyzer.visualizations import create_survey_graph

# Create complete conditional graph
results = create_survey_graph(api, survey_id, output_path="my_survey_graph")

# Results include:
# - PNG/SVG visualization (if Graphviz available)
# - JSON data export (always available)
# - Graph analysis statistics
```

**Graceful Fallbacks**: If Graphviz isn't installed, the system:
- ✅ Still exports JSON data for other visualization tools
- ✅ Provides helpful installation instructions
- ✅ Never breaks your main workflow

## ⚠️ Permissions & Limitations

This library only includes API methods that:
- ✅ Are **read-only** (safe and non-destructive)
- ✅ Work with **standard user permissions** (not admin-only)
- ✅ Are **reliably available** across different LimeSurvey setups

**Removed methods** (due to permission issues or unreliability):
- Site administration functions (require super-admin access)
- File management operations (often restricted)
- User management functions (admin-only)

If you encounter "Permission denied" errors, your LimeSurvey user account may not have sufficient privileges for certain operations. Contact your LimeSurvey administrator to request additional permissions if needed.