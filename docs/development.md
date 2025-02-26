# Development Guide

This guide covers the development process for the Market Lens hourly analysis static site generator.

## Project Structure

```
market-lens/
├── src/
│   └── hourly_analysis/
│       ├── build.py                 # Static site generator
│       ├── hourly_range_analyzer.py # Core analysis logic
│       └── templates/
│           └── index.html          # Static site template
├── build/                          # Generated static site
│   ├── data/                      # Generated JSON data
│   ├── static/                    # Static assets
│   └── index.html                 # Main page
└── docs/                          # Documentation
```

## Development Setup

1. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Local Development**
   ```bash
   # Generate static site
   cd src/hourly_analysis
   python build.py
   
   # Serve locally
   cd ../../build
   python -m http.server 8000
   ```

## Component Overview

### 1. Static Site Generator (build.py)

The `build.py` script handles:
- Setting up build directories
- Generating analysis data
- Creating static HTML files
- Managing assets

Key classes and methods:
```python
class StaticSiteBuilder:
    def setup_directories(self)    # Creates build structure
    def generate_data(self)        # Generates JSON data
    def copy_static_assets(self)   # Copies templates and assets
    def build(self)               # Orchestrates build process
```

### 2. Analysis Logic (hourly_range_analyzer.py)

The core analysis component:
- Fetches market data
- Calculates metrics
- Generates visualizations

Key functionality:
```python
class HourlyRangeAnalyzer:
    def fetch_data(self)           # Gets market data
    def calculate_hourly_metrics() # Processes data
    def analyze_by_vix_category() # VIX analysis
    def analyze_by_day_of_week()  # Day of week analysis
```

### 3. Frontend Template (templates/index.html)

The static site template:
- Loads data from JSON files
- Renders tables and charts
- Handles responsive layout

## Development Workflow

1. **Making Changes**

   a. Modifying Analysis:
   ```python
   # Edit hourly_range_analyzer.py
   # Add new analysis methods
   # Update data processing
   ```

   b. Updating Templates:
   ```html
   <!-- Edit templates/index.html -->
   <!-- Add new components -->
   <!-- Modify styling -->
   ```

   c. Changing Build Process:
   ```python
   # Edit build.py
   # Modify build configuration
   # Add new build steps
   ```

2. **Testing Changes**

   a. Run the build:
   ```bash
   python build.py
   ```

   b. Check generated files:
   ```bash
   ls -R build/
   ```

   c. Verify data:
   ```bash
   cat build/data/analysis.json
   ```

   d. Test locally:
   ```bash
   python -m http.server 8000
   ```

3. **Best Practices**

   a. Code Organization:
   - Keep analysis logic separate from build process
   - Use clear function and variable names
   - Add comments for complex logic

   b. Data Handling:
   - Validate data before processing
   - Handle missing data gracefully
   - Use appropriate data types

   c. Error Handling:
   - Add try-catch blocks for data fetching
   - Validate file operations
   - Log errors appropriately

## Adding New Features

1. **New Analysis**
   ```python
   # Add new method to HourlyRangeAnalyzer
   def analyze_new_metric(self):
       # Implementation
       pass
   
   # Update build.py to include new data
   def generate_data(self):
       data["new_metric"] = self.analyzer.analyze_new_metric()
   ```

2. **New Visualizations**
   ```javascript
   // Add to index.html
   function renderNewChart(data) {
       // Implementation
   }
   ```

3. **New Build Steps**
   ```python
   # Add to StaticSiteBuilder
   def new_build_step(self):
       # Implementation
       pass
   ```

## Troubleshooting

1. **Build Issues**
   - Check Python environment
   - Verify file permissions
   - Check disk space

2. **Data Issues**
   - Verify API access
   - Check data format
   - Validate calculations

3. **Template Issues**
   - Check file paths
   - Verify JSON structure
   - Test responsive layout

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Create pull request

## Resources

- [Plotly Documentation](https://plotly.com/python/)
- [yfinance Documentation](https://pypi.org/project/yfinance/)
- [Python Documentation](https://docs.python.org/3/)
