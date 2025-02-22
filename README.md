# Market Lens

An intelligent market data collection and analysis platform that provides deep insights into stock market movements.

## Features

✅ Implemented:
- Daily data collection for specified tickers
- Local and automated GitHub Actions data fetching
- CSV storage format with basic data structure
- Command-line interface for manual data fetching
- Basic error handling
- SPX Range Analysis:
  - Daily range calculations
  - Significant move detection (-100 points or more)
  - Next 3-day pattern analysis
  - Interactive visualizations

🚧 Planned for Future:
- Advanced error handling and retries
- Data validation and integrity checks
- Email notifications for failures
- Additional analysis tools
- Historical data backfilling
- Performance optimizations
- Monitoring dashboard
- Unit tests

## Project Structure
```
market-lens/
├── config/
│   └── tickers.json       # List of tickers to track
├── data/
│   ├── historical/        # CSV files for each ticker
│   └── analysis/
│       └── ranges/        # Range analysis results
├── src/
│   ├── data_fetcher.py   # Main script for fetching data
│   └── analysis/
│       ├── gap_analyzer.py    # Gap analysis module
│       └── range_analyzer.py  # Range analysis module
├── requirements.txt
└── .github/
    └── workflows/
        └── fetch_stock_data.yml
```

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd market-lens
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure tickers in `config/tickers.json`
```json
{
    "tickers": ["SPY", "QQQ", "SPX", "AAPL", "NVDA", "TSLA"]
}
```

## Usage

### Local Data Fetching

1. Fetch all tickers from config:
```bash
python src/data_fetcher.py
```

2. Fetch specific tickers:
```bash
python src/data_fetcher.py --tickers SPY AAPL
```

3. Fetch multiple days of historical data:
```bash
python src/data_fetcher.py --days 5
```

### Range Analysis

1. Run SPX range analysis:
```bash
python src/analysis/range_analyzer.py
```

This will:
- Fetch latest SPX data using yfinance
- Calculate daily ranges and point changes
- Identify significant moves (-100 points or more)
- Analyze next 3-day patterns after big drops
- Generate interactive visualizations
- Save results to data/analysis/ranges/

The analysis provides:
- Daily range statistics
- Detailed analysis of significant down moves
- Next 3-day price action patterns
- Interactive charts in HTML format

### Automated Data Collection

The project uses GitHub Actions to automatically fetch data every weekday at 9:15 AM ET. The workflow:
- Runs on schedule
- Downloads latest data
- Commits and pushes to the repository
- Reports status of the operation

## Data Format

Each ticker's data is stored in a separate CSV file under `data/historical/` with the following format:
```
date,open,high,low,close,volume
2024-02-11,450.32,452.10,449.95,451.20,1234567
```

### Range Analysis Output

Range analysis results are stored in `data/analysis/ranges/` with:
- SPX_range_analysis.html: Interactive visualization dashboard
- Detailed console output showing:
  - Significant down moves (-100 points or more)
  - Next 3-day price action
  - Summary statistics

## GitHub Actions Setup

1. Enable GitHub Actions in your repository settings
2. Ensure the repository has permissions to commit changes
3. The workflow will automatically start running on schedule

## Error Handling

Basic error handling is implemented for:
- Network failures
- Invalid ticker symbols
- Missing data
- File system operations

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - See LICENSE file for details
