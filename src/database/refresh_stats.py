#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.market_data_fetcher import UnifiedDataFetcher

def refresh_first_hour_stats():
    """Refresh the first_hour_stats materialized view."""
    fetcher = UnifiedDataFetcher()
    
    print("Refreshing first_hour_stats materialized view...")
    query = "REFRESH MATERIALIZED VIEW first_hour_stats;"
    fetcher.db.execute_query(query)
    print("Refresh complete!")
    
    # Verify the refresh
    verify_query = "SELECT COUNT(*) FROM first_hour_stats;"
    result = fetcher.db.execute_query(verify_query)
    count = result[0][0] if result else 0
    print(f"First hour stats now contains {count} records")
    
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
    refresh_first_hour_stats()
