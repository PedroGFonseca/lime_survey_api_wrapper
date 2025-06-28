# Visualization Module

The `lime_survey_analyzer.viz` module provides clean, modular visualization capabilities for survey data with a focus on maintainability and extensibility.

## Features

- **Clean Architecture**: Separation between data adapters, chart creation, and orchestration
- **Configurable Styling**: Centralized configuration with easy customization
- **Multiple Chart Types**: Horizontal bar charts and stacked ranking charts
- **Multiple Output Formats**: HTML (interactive) and PNG (static)
- **Interactive Dashboard**: Dash app displaying charts in survey order
- **Optional Verbosity**: All output can be controlled with `verbose=True/False`
- **Pure Functions**: Chart creation functions are library-agnostic and easily testable

## Quick Start

### Static Charts
```python
from lime_survey_analyzer.viz import create_survey_visualizations

# Simple usage - creates all supported charts
charts_created = create_survey_visualizations(
    credentials_path='secrets/credentials.ini',
    verbose=True
)
```

### Interactive Dashboard
```python
from lime_survey_analyzer.viz import run_survey_dashboard

# Run interactive dashboard
run_survey_dashboard(
    credentials_path='secrets/credentials.ini',
    verbose=True
)
# Opens at http://127.0.0.1:8050
```

## Advanced Usage

### Custom Styling

```python
custom_config = {
    'chart_style': {
        'font_family': 'Arial',
        'primary_color': '#FF6B6B',
        'chart_width': 1000
    },
    'output_settings': {
        'plots_dir': 'custom_plots',
        'default_format': 'png'
    }
}

create_survey_visualizations(
    credentials_path='secrets/credentials.ini',
    config=custom_config,
    verbose=True
)
```

### Selective Chart Generation

```python
# Only create horizontal bar charts
create_survey_visualizations(
    credentials_path='secrets/credentials.ini',
    question_types=['listradio'],
    verbose=True
)

# Only create ranking charts
create_survey_visualizations(
    credentials_path='secrets/credentials.ini',
    question_types=['ranking'],
    verbose=True
)
```

### Dashboard with Custom Settings

```python
# Dashboard with custom styling
run_survey_dashboard(
    credentials_path='secrets/credentials.ini',
    config=custom_config,
    host='0.0.0.0',  # Allow external access
    port=8080,
    verbose=True
)
```

### Pure Chart Functions

For custom workflows, you can use the pure chart functions directly:

```python
import pandas as pd
from lime_survey_analyzer.viz import create_horizontal_bar_chart, get_config

# Your data
data = pd.Series({'Option A': 25, 'Option B': 15, 'Option C': 10})
config = get_config()

# Create chart
fig = create_horizontal_bar_chart(data, "My Survey Question", config)

# Save manually
fig.write_html('my_chart.html')
```

## Architecture

The module is organized into clean layers:

### 1. Configuration Layer (`config.py`)
- Centralized settings for all visualization components
- Easy customization through configuration dictionaries
- Validation and default value management

### 2. Pure Visualization Layer (`charts/`)
- Library-agnostic chart creation functions
- No dependencies on lime_survey_analyzer data structures
- Easy to test and extend

### 3. Data Adapter Layer (`adapters/`)
- lime_survey_analyzer specific data extraction
- Converts survey data to formats expected by chart functions
- Isolated from visualization logic

### 4. Orchestration Layer (`core.py`)
- Simple coordination between adapters and charts
- File output management
- Progress reporting and error handling

### 5. Dashboard Layer (`dashboard.py`)
- Minimal Dash app for interactive viewing
- Displays charts in survey order
- Uses same chart functions as static generation

### 6. Utilities (`utils/`)
- Text processing (HTML cleaning, wrapping)
- File handling
- Reusable helper functions

## Supported Question Types

- **listradio**: Creates horizontal bar charts
- **ranking**: Creates stacked horizontal bar charts

## Configuration Options

### Chart Style
- `font_family`: Font family for all text
- `primary_color`: Main color for bars
- `text_color`: Color for text inside bars
- `title_color`: Color for chart titles
- `chart_width`/`chart_height`: Chart dimensions
- `ranking_colors`: Color gradient for ranking charts

### Ranking Settings
- `text_threshold_min`: Minimum value to show internal text
- `text_threshold_percent`: Minimum percentage to show text
- `wrap_length`: Text wrapping length for ranking charts
- `left_margin`: Left margin for long labels

### Output Settings
- `plots_dir`: Output directory for charts
- `default_format`: 'html' or 'png'
- `supported_formats`: List of supported formats

## Dashboard Features

- **Survey Order**: Charts displayed in the order they appear in the survey
- **Interactive**: Full Plotly interactivity (zoom, pan, hover)
- **Responsive**: Works on desktop and mobile
- **Minimal**: Clean, focused interface without bloat
- **Configurable**: Same styling options as static charts

## Testing

The module includes comprehensive tests:

```bash
python -m pytest tests/viz/ -v
```

## Extending

To add new chart types:

1. Create a new chart function in `charts/`
2. Add data extraction logic in `adapters/`
3. Update the orchestration in `core.py` and `dashboard.py`
4. Add configuration options in `config.py`
5. Write tests

The clean architecture makes it easy to add new chart types, data sources, or output formats without affecting existing functionality. 