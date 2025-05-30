# Getting Started with LimeSurvey API Client

This guide will help you get up and running with the LimeSurvey API client quickly and safely.

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
pip install requests
```

### 2. Set Up Credentials

Choose one of these methods:

#### Option A: Automated Setup (Recommended)
```bash
# Create credentials template
python3 setup_credentials.py --create-template

# Edit the file with your details
nano secrets/credentials.ini

# Test the connection
python3 setup_credentials.py --test-only
```

#### Option B: Command Line Setup
```bash
python3 setup_credentials.py \
  --url https://your-survey.com/admin/remotecontrol \
  --username your_username \
  --password your_password
```

#### Option C: Manual Setup
```bash
# Copy template
cp secrets/credentials.ini.template secrets/credentials.ini

# Edit with your LimeSurvey details
nano secrets/credentials.ini
```

### 3. Test Basic Functionality

```bash
# Run the simple demo
python3 examples/simple_api_demo.py
```

## 🔧 Basic Usage

```python
from lime_survey_analyzer import LimeSurveyClient

# Initialize from config file
api = LimeSurveyClient.from_config()

# List your surveys
surveys = api.surveys.list_surveys()
for survey in surveys:
    print(f"Survey {survey['sid']}: {survey['surveyls_title']}")

# Get survey details
survey_id = surveys[0]['sid']
properties = api.surveys.get_survey_properties(survey_id)
questions = api.questions.list_questions(survey_id)
responses = api.responses.export_responses(survey_id)

print(f"Survey: {properties['surveyls_title']}")
print(f"Questions: {len(questions)}")
print(f"Responses: {len(responses)}")
```

## 📊 Core Features Available

### ✅ Survey Operations
- `list_surveys()` - Get all surveys accessible to your user
- `get_survey_properties(survey_id)` - Get detailed survey information
- `get_summary(survey_id)` - Get response statistics
- `get_fieldmap(survey_id)` - Get field structure mapping

### ✅ Question Operations  
- `list_groups(survey_id)` - Get question groups
- `list_questions(survey_id)` - Get all questions
- `get_question_properties(question_id)` - Get question details

### ✅ Response Operations
- `export_responses(survey_id)` - Export response data
- `get_response_statistics(survey_id)` - Get response stats

### ✅ Participant Operations
- `list_participants(survey_id)` - Get participant list
- `get_participant_properties(survey_id, token)` - Get participant details

## 🛡️ Security Notes

### Credentials Are Protected
- All credential files are automatically git-ignored
- The `secrets/` directory is never committed to version control
- Only the template file (`credentials.ini.template`) is safe to commit

### Safe for GitHub
- No sensitive data will be accidentally committed
- Test credentials are kept local only
- All examples use placeholder data

## ❓ Common Issues

### Authentication Errors
```bash
# Check your credentials file
cat secrets/credentials.ini

# Test connection
python3 setup_credentials.py --test-only
```

### API Permission Errors
- Ensure your LimeSurvey user has API access enabled
- Check that you can access the RemoteControl API in LimeSurvey admin

### URL Issues
- Use the full URL: `https://your-survey.com/admin/remotecontrol`
- Ensure your LimeSurvey instance has the API enabled

## 📚 Next Steps

1. **Explore Examples**: Check the `examples/` directory for more use cases
2. **Read the API Reference**: See `README.md` for complete documentation
3. **Test with Your Data**: Start with `list_surveys()` and build from there

## 🔍 Development Mode

If you're developing or contributing to this package:

```bash
# Install in development mode
pip install -e .

# Run tests (if any surveys are available)
python3 examples/simple_api_demo.py
```

---

**Ready to access your LimeSurvey data programmatically!** 🎉 