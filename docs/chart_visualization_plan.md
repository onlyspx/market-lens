# SPX Hourly Chart Visualization Plan

## Project Overview

Create an interactive, TradingView-style chart visualization for SPX hourly data, deployed on Vercel. The chart will provide a professional-grade view of market data with features like candlestick/bar charts, volume analysis, and interactive tools.

## Architecture & File Structure

```
market-lens/
├── public/
│   └── charts/
│       ├── index.html      # Main chart page
│       ├── data/
│       │   └── spx.json    # Pre-generated data
│       └── static/
│           ├── css/
│           │   └── chart.css
│           └── js/
│               ├── chart.js
│               └── indicators.js
├── src/
│   └── charts/
│       ├── __init__.py
│       ├── build.py        # Generates static files
│       ├── data_prep.py    # Prepares data for charts
│       └── templates/
│           └── index.html
└── vercel.json
```

## Chart Design & Features

### 1. Main Price Window (70% height)
- Candlestick/bar chart showing hourly OHLC
- Y-axis: Price scale with dynamic range
- X-axis: Time (hourly) with proper timezone handling
- Grid lines for both axes
- Crosshair with synchronized price/time info
- Zoom and pan controls

Example bar for one hour:
```
High ($5992.65) ─┬─
Open ($5982.73) ─┤
Close ($5955.25) ┤
Low ($5908.49) ──┴─
```

### 2. Volume Window (30% height)
- Volume bars aligned with price bars
- Color-coded based on price direction (green/red)
- Y-axis: Volume scale with K/M/B formatting
- Shared X-axis grid with price chart

### 3. Interactive Features
- Hover tooltips showing:
  ```
  Time: 09:30 ET
  Open: $5982.73
  High: $5992.65
  Low: $5908.49
  Close: $5955.25
  Volume: 1.2M
  ```
- Time period selector:
  - 1D (7 hours)
  - 1W (35 hours)
  - 1M (~140 hours)
  - 3M, 6M, 1Y
- Zoom/pan controls
- Optional technical indicators

## Data Flow

1. Data Generation
   ```python
   # build.py
   - Connect to TimescaleDB
   - Fetch SPX hourly data
   - Transform to optimized JSON format
   - Generate static files
   ```

2. Data Format
   ```json
   {
     "symbol": "SPX",
     "interval": "1h",
     "timezone": "America/New_York",
     "data": [
       {
         "time": "2025-02-26T09:30:00-05:00",
         "open": 5982.73,
         "high": 5992.65,
         "low": 5908.49,
         "close": 5955.25,
         "volume": 1234567
       },
       // ... more bars
     ]
   }
   ```

3. Client-Side Rendering
   - Load JSON data
   - Initialize chart with default view (1D)
   - Handle user interactions
   - Update view based on selections

## Implementation Steps

1. Setup & Infrastructure
   - Create directory structure
   - Configure Vercel deployment
   - Setup build pipeline

2. Data Pipeline
   - Implement data fetching from TimescaleDB
   - Create data transformation logic
   - Setup automated builds

3. Chart Development
   - Create base chart components
   - Implement interactive features
   - Add technical indicators
   - Style and polish UI

4. Testing & Optimization
   - Test with various data ranges
   - Optimize performance
   - Cross-browser testing

## Technical Stack

- Frontend:
  - HTML5 Canvas for chart rendering
  - Vanilla JavaScript for core functionality
  - CSS for styling and layout

- Build Tools:
  - Python for data preparation
  - Node.js for Vercel deployment

- Data Storage:
  - Static JSON files
  - Efficient data format for quick loading

## Next Steps

1. Review and finalize design
2. Set up project structure
3. Begin implementation with basic chart rendering
4. Iterate on features and design

This plan will be revisited and updated as we progress with the implementation.
