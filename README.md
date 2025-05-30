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
- 🐍 **Pythonic & Type-Safe**: Clean interface with full type hints for better IDE support
- 🛡️ **Production Ready**: Robust error handling, automatic session management, and secure credential handling
- 🔄 **Context Manager Support**: Automatic cleanup of API sessions
- 🐛 **Debug Support**: Optional debug logging with sensitive data protection

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

## 💡 Why Use This Library?

### 🎯 **Organized & Intuitive**
Instead of memorizing dozens of API methods, operations are logically grouped by purpose. Need survey info? Use `api.surveys`. Working with responses? Use `api.responses`.

### 🔍 **Type-Safe Development**
Full type hints mean your IDE can help you with autocompletion, parameter validation, and catching errors before runtime.

### 📊 **Rich Data Export Options**
Get your data in the format you need - JSON for programmatic processing, CSV for spreadsheets, PDF for reports, or Excel for advanced analysis.

### 🛡️ **Production Ready**
Built-in security best practices, automatic session management, comprehensive error handling, and support for multiple authentication methods.

### 🔒 **Secure by Default**
Multiple secure credential handling options, automatic credential sanitization in logs, and HTTPS validation.

## 🔒 Security Best Practices

1. **Never hardcode credentials** in your source code
2. **Use HTTPS** for production environments
3. **Store credentials securely** using environment variables or encrypted config files
4. **Regularly rotate** API credentials
5. **Monitor API access** logs for unauthorized usage
6. **Use virtual environments** to isolate dependencies

## 🔧 Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src tests
isort src tests
```

### Type Checking
```bash
mypy src
```

### Building Documentation
```bash
cd docs
make html
```

The documentation will be available at `docs/_build/html/index.html`.

## 📚 Documentation

Full documentation is available in the `docs/` directory. To build and view:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation
cd docs
make html

# Open in browser
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

## ⚙️ Requirements

- Python 3.8+
- requests >= 2.25.0
- LimeSurvey instance with RemoteControl API enabled

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

For support and questions:

- Check the [documentation](docs/)
- Review existing [issues](https://github.com/example/lime-survey-analyzer/issues)
- Create a new issue for bugs or feature requests

## 📝 Changelog

### Version 1.0.0
- ✅ Complete LimeSurvey RemoteControl API coverage with 13 reliable methods
- ✅ Manager-based architecture for organized access to different operation types
- ✅ Multiple secure authentication methods (environment variables, config files, interactive)
- ✅ Comprehensive data export capabilities (JSON, CSV, Excel, PDF, XML)
- ✅ Full type hints and modern Python features
- ✅ Production-ready error handling and session management
- ✅ Extensive documentation and examples 