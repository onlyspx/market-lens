#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.market_data_fetcher import UnifiedDataFetcher

def fetch_historical_data():
    """Fetch one year of historical data for specified symbols."""
    # Map display symbols to fetch symbols (for special cases)
    symbol_map = {
        'SPX': {
            '1d': 'SPX',    # Use NASDAQ API
            '1h': '^SPX'    # Use yfinance with ^ prefix
        }
    }
    symbols = ['SPX', 'SPY', 'AAPL', 'NVDA']
    intervals = ['1d', '1h']
    period = '1y'
    
    fetcher = UnifiedDataFetcher()
    
    for symbol in symbols:
        print(f"\nProcessing {symbol}...")
        
        for interval in intervals:
            print(f"\nFetching {interval} data for {symbol}...")
            # Get the correct symbol for this interval
            fetch_symbol = symbol_map.get(symbol, {}).get(interval, symbol)
            data = fetcher.fetch_data(fetch_symbol, interval=interval, period=period)
            
            # Store results under original symbol regardless of fetch symbol
            if data is not None and fetch_symbol != symbol:
                # Update symbol in database
                query = """
                    UPDATE market_data 
                    SET symbol = %s 
                    WHERE symbol = %s AND interval = %s
                """
                fetcher.db.execute_query(query, (symbol, fetch_symbol, interval))
            
            if data is not None:
                print(f"Successfully fetched {len(data)} {interval} records for {symbol}")
                print("\nSample data:")
                print(data.head())
            else:
                print(f"Failed to fetch {interval} data for {symbol}")
            
            # Get data summary from database
            query = """
                SELECT COUNT(*) as count, 
                       MIN(time) as earliest,
                       MAX(time) as latest
                FROM market_data 
                WHERE symbol = %s AND interval = %s
            """
            result = fetcher.db.execute_query(query, (symbol, interval))
            if result and result[0][0] > 0:
                print(f"\nDatabase summary for {symbol} {interval}:")
                print(f"Total records: {result[0][0]}")
                print(f"Date range: {result[0][1]} to {result[0][2]}")
            
            print("-" * 80)

if __name__ == "__main__":
    fetch_historical_data()
