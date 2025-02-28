# Monthly Close Data Analysis

This documentation covers the functionality for fetching and analyzing 15-minute OHLC (Open, High, Low, Close) data for the last 30 minutes of trading on the last trading day of each month.

## Overview

The implementation consists of two main scripts:

1. `fetch_monthly_close_data.py` - Fetches and stores 15-minute OHLC data for the specified time window
2. `query_monthly_close_data.py` - Queries and displays the stored data

These scripts leverage the existing database infrastructure and market calendar functionality to provide a comprehensive solution for analyzing market behavior during the closing period of monthly trading sessions.

## Prerequisites

- Python 3.6+
- PostgreSQL/TimescaleDB database set up with the `market_data` table
- Required Python packages:
  - pandas
  - yfinance
  - pytz
  - psycopg2

## Database Schema

The data is stored in the `market_data` table with the following schema:

```sql
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    symbol TEXT NOT NULL,
    open DOUBLE PRECISION NOT NULL,
    high DOUBLE PRECISION NOT NULL,
    low DOUBLE PRECISION NOT NULL,
    close DOUBLE PRECISION NOT NULL,
    volume BIGINT NOT NULL,
    interval TEXT NOT NULL,
    PRIMARY KEY (time, symbol, interval)
);
```

## Fetching Data

The `fetch_monthly_close_data.py` script fetches 15-minute OHLC data for the last 30 minutes of trading (3:30 PM - 4:00 PM ET) on the last trading day of each month. This typically results in 2 candles per monthly close (3:30-3:45, 3:45-4:00).

### Usage

```bash
python src/fetch_monthly_close_data.py [options]
```

### Options

- `--symbol`: Symbol to fetch data for (default: SPX)
- `--start-year`: Starting year (default: 2 years ago)
- `--end-year`: Ending year (default: current year)

### Example

```bash
# Fetch SPX data for the last 5 years
python src/fetch_monthly_close_data.py --symbol SPX --start-year 2020 --end-year 2025

# Fetch data for a different symbol
python src/fetch_monthly_close_data.py --symbol QQQ --start-year 2022 --end-year 2025
```

## Querying Data

The `query_monthly_close_data.py` script allows you to query and analyze the stored data.

### Usage

```bash
python src/query_monthly_close_data.py [options]
```

### Options

- `--symbol`: Symbol to query data for (default: SPX)
- `--start-year`: Starting year (default: 2 years ago)
- `--end-year`: Ending year (default: current year)
- `--date`: Specific date to query (format: YYYY-MM-DD)
- `--summary`: Print summary only (omit detailed data)

### Example

```bash
# Query SPX data for the last 2 years (default)
python src/query_monthly_close_data.py

# Query data for a specific date
python src/query_monthly_close_data.py --date 2024-01-31

# Query data for a specific symbol and date range with summary only
python src/query_monthly_close_data.py --symbol QQQ --start-year 2023 --end-year 2024 --summary
```

## Data Format

The fetched data includes the following fields:

- `time`: Timestamp in UTC (displayed in Eastern Time when queried)
- `open`: Opening price for the 5-minute candle
- `high`: Highest price during the 5-minute candle
- `low`: Lowest price during the 5-minute candle
- `close`: Closing price for the 5-minute candle
- `volume`: Trading volume during the 5-minute candle

## Limitations

- Yahoo Finance (via yfinance) typically provides limited historical intraday data (approximately 60 days for 5-minute data, but potentially more for 15-minute data)
- Rate limiting may affect the ability to fetch large amounts of data in a single run
- Some trading days may have incomplete data due to market conditions or data availability

## Troubleshooting

If you encounter issues:

1. Check database connectivity and credentials
2. Verify that the symbol exists and has data available
3. For rate limiting issues, try reducing the date range or adding more delay between requests
4. Check the logs for specific error messages

## Future Enhancements

Potential enhancements for this functionality include:

1. Adding visualization capabilities for the monthly close data
2. Implementing statistical analysis of price movements during the closing period
3. Comparing the closing period behavior across different months or years
4. Extending the functionality to other significant time periods (e.g., market open, lunch hour)
