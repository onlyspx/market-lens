#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.market_data_fetcher import UnifiedDataFetcher

def test_database_connection():
    """Test database connectivity."""
    try:
        print("\nTesting database connection...")
        fetcher = UnifiedDataFetcher()
        
        # Test connection by executing a simple query
        query = "SELECT version(), current_timestamp"
        result = fetcher.db.execute_query(query)
        if result:
            print(f"Successfully connected to database")
            print(f"PostgreSQL version: {result[0][0]}")
            print(f"Current timestamp: {result[0][1]}")
            
            # Test market_data table
            print("\nChecking market_data table...")
            table_query = """
                SELECT table_name, column_names 
                FROM (
                    SELECT 
                        t.table_name,
                        string_agg(c.column_name, ', ' ORDER BY c.ordinal_position) as column_names
                    FROM information_schema.tables t
                    JOIN information_schema.columns c 
                        ON c.table_name = t.table_name
                    WHERE t.table_schema = 'public'
                    GROUP BY t.table_name
                ) sub
                WHERE table_name = 'market_data';
            """
            table_info = fetcher.db.execute_query(table_query)
            if table_info:
                print(f"Found market_data table with columns: {table_info[0][1]}")
            else:
                print("market_data table not found")
            
            print("\nDatabase connection test completed successfully!")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")

def test_yfinance_fetching():
    """Test yfinance data fetching."""
    try:
        print("\nTesting yfinance data fetching...")
        fetcher = UnifiedDataFetcher()
        
        # Test SPY daily data
        print("Fetching SPY daily data...")
        spy_daily = fetcher.fetch_data('SPY', interval='1d', period='1mo')
        if spy_daily is not None:
            print(f"Successfully fetched {len(spy_daily)} SPY daily records")
            print("\nSample SPY daily data:")
            print(spy_daily.head())
        
        # Test SPY hourly data
        print("\nFetching SPY hourly data...")
        spy_hourly = fetcher.fetch_data('SPY', interval='1h', period='1mo')
        if spy_hourly is not None:
            print(f"Successfully fetched {len(spy_hourly)} SPY hourly records")
            print("\nSample SPY hourly data:")
            print(spy_hourly.head())
        
        # Test VXX daily data
        print("\nFetching VXX daily data...")
        vxx_daily = fetcher.fetch_data('VXX', interval='1d', period='1mo')
        if vxx_daily is not None:
            print(f"Successfully fetched {len(vxx_daily)} VXX daily records")
            print("\nSample VXX daily data:")
            print(vxx_daily.head())
        
        # Test VXX hourly data
        print("\nFetching VXX hourly data...")
        vxx_hourly = fetcher.fetch_data('VXX', interval='1h', period='1mo')
        if vxx_hourly is not None:
            print(f"Successfully fetched {len(vxx_hourly)} VXX hourly records")
            print("\nSample VXX hourly data:")
            print(vxx_hourly.head())
            
    except Exception as e:
        print(f"Error testing yfinance fetching: {e}")

def test_data_insertion():
    """Test data insertion with a single record."""
    try:
        print("\nTesting data insertion...")
        fetcher = UnifiedDataFetcher()
        
        # Create a sample record
        from datetime import datetime
        import pandas as pd
        
        sample_data = pd.DataFrame({
            'Open': [100.0],
            'High': [101.0],
            'Low': [99.0],
            'Close': [100.5],
            'Volume': [1000000]
        }, index=[pd.Timestamp.now()])
        
        # Try to store the sample data
        fetcher._store_in_db('TEST', '1d', sample_data)
        print("Successfully inserted test record")
        
        # Verify the insertion
        result = fetcher.get_data('TEST', '1d')
        if not result.empty:
            print("Successfully retrieved test record:")
            print(result)
            
            # Clean up test data
            cleanup_query = "DELETE FROM market_data WHERE symbol = 'TEST'"
            fetcher.db.execute_query(cleanup_query)
            print("Cleaned up test data")
        
    except Exception as e:
        print(f"Error testing data insertion: {e}")

if __name__ == "__main__":
    test_database_connection()
    test_data_insertion()
    test_yfinance_fetching()
