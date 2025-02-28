#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.market_data_fetcher import UnifiedDataFetcher

def create_first_hour_stats():
    """Create or replace the first_hour_stats materialized view."""
    fetcher = UnifiedDataFetcher()
    
    # Drop existing view if it exists
    print("Dropping existing materialized view if it exists...")
    drop_query = """
        DROP MATERIALIZED VIEW IF EXISTS first_hour_stats;
    """
    fetcher.db.execute_query(drop_query)
    
    # Create the materialized view
    print("Creating first_hour_stats materialized view...")
    create_query = """
        CREATE MATERIALIZED VIEW first_hour_stats AS
        WITH first_hour_data AS (
            SELECT 
                date_trunc('day', time) as date,
                symbol,
                open,
                high,
                low,
                close,
                ROW_NUMBER() OVER (
                    PARTITION BY symbol, date_trunc('day', time) 
                    ORDER BY time
                ) as row_num
            FROM market_data
            WHERE 
                interval = '1h'
                AND EXTRACT(hour FROM time AT TIME ZONE 'America/New_York') = 9  -- First trading hour (9 AM ET)
        )
        SELECT 
            date,
            symbol,
            open as first_hour_open,
            high as first_hour_high,
            low as first_hour_low,
            close as first_hour_close
        FROM first_hour_data
        WHERE row_num = 1
        ORDER BY date DESC, symbol;
    """
    fetcher.db.execute_query(create_query)
    print("View created successfully!")
    
    # Create index on the view
    print("Creating index on first_hour_stats...")
    index_query = """
        CREATE INDEX idx_first_hour_stats_date_symbol 
        ON first_hour_stats(date, symbol);
    """
    fetcher.db.execute_query(index_query)
    print("Index created!")
    
    # Verify the view
    verify_query = "SELECT COUNT(*) FROM first_hour_stats;"
    result = fetcher.db.execute_query(verify_query)
    count = result[0][0] if result else 0
    print(f"\nFirst hour stats contains {count} records")
    
    if count > 0:
        # Show sample of the stats
        sample_query = """
            SELECT date, symbol, 
                   first_hour_open, first_hour_high, 
                   first_hour_low, first_hour_close
            FROM first_hour_stats
            ORDER BY date DESC
            LIMIT 5;
        """
        results = fetcher.db.execute_query(sample_query)
        print("\nRecent first hour stats:")
        print("Date       | Symbol | Open    | High    | Low     | Close")
        print("-" * 60)
        for row in results:
            print(f"{row[0].date()} | {row[1]:<6} | {row[2]:<7.2f} | {row[3]:<7.2f} | {row[4]:<7.2f} | {row[5]:<7.2f}")

if __name__ == "__main__":
    create_first_hour_stats()
