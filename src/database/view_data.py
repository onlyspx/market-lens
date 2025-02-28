#!/usr/bin/env python3

import os
import sys
from datetime import datetime, timedelta
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.market_data_fetcher import UnifiedDataFetcher

def print_menu():
    """Print the main menu options."""
    print("\nMarket Data Viewer")
    print("=================")
    print("1. View data summary by symbol")
    print("2. View recent data for a symbol")
    print("3. View data for date range")
    print("4. View first hour statistics")
    print("5. Exit")
    return input("\nSelect an option (1-5): ")

def view_data_summary(fetcher):
    """Show summary of data by symbol and interval."""
    query = """
        SELECT 
            symbol, 
            interval,
            COUNT(*) as records,
            MIN(time) as earliest,
            MAX(time) as latest
        FROM market_data
        GROUP BY symbol, interval
        ORDER BY symbol, interval;
    """
    results = fetcher.db.execute_query(query)
    if not results:
        print("No data found in database")
        return
        
    print("\nData Summary")
    print("===========")
    for row in results:
        print(f"\nSymbol: {row[0]}")
        print(f"Interval: {row[1]}")
        print(f"Records: {row[2]}")
        print(f"Date Range: {row[3]} to {row[4]}")

def view_recent_data(fetcher):
    """Show recent data for a specific symbol."""
    symbol = input("\nEnter symbol (e.g., SPY): ").upper()
    interval = input("Enter interval (1d or 1h): ")
    limit = int(input("Number of records to show: "))
    
    query = """
        SELECT time, open, high, low, close, volume
        FROM market_data
        WHERE symbol = %s AND interval = %s
        ORDER BY time DESC
        LIMIT %s;
    """
    results = fetcher.db.execute_query(query, (symbol, interval, limit))
    if not results:
        print(f"No data found for {symbol}")
        return
        
    df = pd.DataFrame(results, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df.set_index('time', inplace=True)
    print(f"\nRecent {interval} data for {symbol}:")
    print(df)

def view_date_range(fetcher):
    """Show data for a specific date range."""
    symbol = input("\nEnter symbol (e.g., SPY): ").upper()
    interval = input("Enter interval (1d or 1h): ")
    days = int(input("Number of days to look back: "))
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    data = fetcher.get_data(symbol, interval, start_time, end_time)
    if data.empty:
        print(f"No data found for {symbol} in specified date range")
        return
        
    print(f"\n{interval} data for {symbol} from {start_time.date()} to {end_time.date()}:")
    print(data)

def view_first_hour_stats(fetcher):
    """Show first hour trading statistics."""
    query = """
        SELECT 
            date,
            symbol,
            first_hour_open,
            first_hour_high,
            first_hour_low,
            first_hour_close
        FROM first_hour_stats
        ORDER BY date DESC, symbol
        LIMIT 20;
    """
    results = fetcher.db.execute_query(query)
    if not results:
        print("No first hour statistics found")
        return
        
    df = pd.DataFrame(results, columns=['date', 'symbol', 'open', 'high', 'low', 'close'])
    df.set_index(['date', 'symbol'], inplace=True)
    print("\nFirst Hour Trading Statistics:")
    print(df)

def main():
    """Main function to run the data viewer."""
    fetcher = UnifiedDataFetcher()
    
    while True:
        choice = print_menu()
        
        if choice == '1':
            view_data_summary(fetcher)
        elif choice == '2':
            view_recent_data(fetcher)
        elif choice == '3':
            view_date_range(fetcher)
        elif choice == '4':
            view_first_hour_stats(fetcher)
        elif choice == '5':
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
