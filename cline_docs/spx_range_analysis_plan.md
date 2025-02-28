# SPX Daily Range Analysis Plan

## Overview
Create a comprehensive analysis system for SPX daily ranges and post-significant-move patterns.

## Components

### 1. Data Infrastructure
- Add yfinance to requirements.txt
- Create new SPX data fetcher using yfinance API
- Implement daily data refresh mechanism
- Store historical data in CSV format with OHLCV data

### 2. Analysis Module
- Calculate and store daily statistics:
  - Daily range (High-Low spread)
  - Daily returns
  - Rolling statistics (avg range, volatility)
- Identify significant moves:
  - Define -2% or greater down days
  - Calculate next 3-day returns after significant moves
  - Analyze pattern frequencies and probabilities

### 3. Visualization Dashboard
- Create interactive dashboard with:
  - Daily range distribution chart
  - Range vs. Volatility analysis
  - Post-significant-move pattern analysis
  - Statistical summary tables

## Implementation Steps

1. Setup & Data (Day 1)
   - Add yfinance dependency
   - Implement SPX data fetcher
   - Create initial data pipeline

2. Analysis Engine (Day 2)
   - Implement range calculations
   - Create pattern detection logic
   - Build statistical analysis functions

3. Visualization (Day 2-3)
   - Design interactive dashboard
   - Implement charts and tables
   - Add user controls for analysis parameters

## Technical Specifications

### Data Structure
```python
# Daily data format
{
    'date': datetime,
    'open': float,
    'high': float,
    'low': float,
    'close': float,
    'volume': int,
    'daily_range': float,  # high - low
    'daily_return': float, # percentage return
}
```

### Key Metrics
- Daily Range = High - Low
- Daily Return = (Close - Previous Close) / Previous Close
- Significant Move = Daily Return <= -2%
- Post-Move Analysis = Next 3 days' returns after significant moves

### Tools & Libraries
- yfinance: Data fetching
- pandas: Data manipulation
- numpy: Numerical computations
- plotly: Interactive visualizations