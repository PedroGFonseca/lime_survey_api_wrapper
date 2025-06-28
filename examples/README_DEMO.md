# Mock Data Dashboard Demo

This directory contains a comprehensive demonstration of the LimeSurvey Analyzer's visualization capabilities using completely mock data.

## What This Demo Does

The `mock_data_dashboard_demo.py` script demonstrates the complete survey analysis and visualization pipeline:

1. **🏭 Generates Realistic Mock Data** - Uses the enhanced data generator to create a complete survey dataset with:
   - 38 questions across 11 different question types
   - 359 completed responses + 296 incomplete responses  
   - 114 answer options across all questions
   - Realistic survey metadata and properties

2. **📊 Processes Survey Data** - Creates a SurveyAnalysis instance and processes all questions using the same analysis pipeline used for real surveys

3. **🎨 Creates Interactive Charts** - Generates beautiful, interactive charts for each question type:
   - Horizontal bar charts for radio button questions
   - Stacked bar charts for ranking questions  
   - Text response displays for open-ended questions
   - Multiple choice visualizations

4. **🌐 Launches Web Dashboard** - Creates a mobile-responsive Dash web application to display all charts in an organized, interactive interface

## Running the Demo

```bash
# From the project root directory
python examples/mock_data_dashboard_demo.py
```

The demo will:
- Generate mock survey data
- Process all questions  
- Create charts
- Launch a web server at http://127.0.0.1:8050

## Demo Output Example

```
🚀 Starting Mock Data Dashboard Demo
==================================================
🏭 Generating mock survey data...
✅ Generated mock data:
   📊 Survey: Mock Survey Analysis
   ❓ Questions: 38
   📝 Responses: 359 completed, 296 incomplete  
   🎯 Options: 114
   📋 Groups: 3

📊 Setting up analysis...

⚙️ Processing all questions...
✅ Processed 35 questions
⚠️ Failed to process 3 questions

🎨 Creating visualizations...
✅ Created 33 charts

🌐 Creating dashboard...

🎉 Dashboard ready!
📊 Chart breakdown:
   • Horizontal Bar: 17
   • Ranking Stacked: 8  
   • Text Responses: 7
   • Multiple Short Text: 1

==================================================
🌐 Starting web server...
📱 Dashboard will be available at: http://127.0.0.1:8050
🛑 Press Ctrl+C to stop the server
==================================================
```

## Features Demonstrated

### Question Types Supported
- ✅ **Radio Button Questions** (`listradio`) - Single choice questions with horizontal bar charts
- ✅ **Ranking Questions** (`ranking`) - Stacked bar charts showing ranking distributions  
- ✅ **Text Questions** (`longfreetext`, `shortfreetext`) - Collapsible text response viewers
- ✅ **Numerical Questions** (`numerical`) - Treated as text responses
- ✅ **Multiple Choice** (`multiplechoice`) - Multiple selection questions with bar charts
- ✅ **Multiple Short Text** (`multipleshorttext`) - Grouped text responses
- ✅ **Image Select** (`image_select-listradio`) - Image-based single choice
- ✅ **Array Questions** (`arrays/increasesamedecrease`) - Likert-style questions

### Dashboard Features
- 📱 **Mobile Responsive** - Works perfectly on phones, tablets, and desktops
- 🎨 **Modern UI** - Clean, professional interface with Bootstrap styling
- 🗂️ **Organized Sections** - Charts grouped into collapsible sections for easy navigation
- 📊 **Interactive Charts** - Hover effects, zooming, and responsive design
- 📝 **Text Response Handling** - Collapsible viewers for open-ended responses
- 📈 **Statistics Summary** - Overview showing chart counts by type

## Safety & Security

This demo is completely safe to run and commit to version control because:

- ✅ **No Real Data** - Uses only generated mock data
- ✅ **No API Calls** - Bypasses all external API connections  
- ✅ **No Credentials** - Doesn't require or use any authentication
- ✅ **No Network Dependencies** - Runs entirely offline
- ✅ **Deterministic** - Generates consistent, predictable test data

## Technical Architecture

The demo showcases the modular architecture of the LimeSurvey Analyzer:

```
Mock Data Generator → Survey Analysis → Chart Creation → Web Dashboard
     ↓                      ↓               ↓              ↓
Enhanced generator → MockSurveyAnalysis → Plotly charts → Dash app
```

### Key Components

1. **Enhanced Data Generator** (`tests/enhanced_data_generators.py`)
   - Generates realistic survey data matching real LimeSurvey patterns
   - Supports all major question types with proper distributions
   - Creates complete dataset with metadata, responses, and structure

2. **Mock Analysis Adapter** (`MockSurveyAnalysis` class)
   - Extends the main `SurveyAnalysis` class
   - Works with generated data instead of API connections
   - Processes questions using the same algorithms as real surveys

3. **Visualization System** (`src/lime_survey_analyzer/viz/`)
   - Creates publication-quality charts using Plotly
   - Handles different question types with appropriate visualizations
   - Mobile-responsive design with Bootstrap styling

4. **Dashboard Framework** (Dash integration)
   - Interactive web interface for exploring results
   - Organized, user-friendly presentation
   - Real-time interaction with chart data

## Use Cases

This demo is perfect for:

- 🧪 **Testing** - Validating visualization components without real data
- 📚 **Learning** - Understanding how the analysis pipeline works
- 🎨 **Development** - Iterating on chart designs and dashboard layouts
- 🔒 **Security** - Demonstrating capabilities without exposing sensitive data
- 📋 **Documentation** - Showing stakeholders what the system can do
- 🚀 **Deployment** - Testing the full stack before connecting to real surveys

## Next Steps

After running this demo, you can:

1. Explore the generated charts and dashboard interface
2. Modify the mock data generator to test different scenarios
3. Customize the chart styles and dashboard layout
4. Connect to real survey data using the same visualization pipeline
5. Deploy the dashboard with production data

The same visualization system that powers this demo works seamlessly with real LimeSurvey data - just replace the mock data generator with actual API connections. 