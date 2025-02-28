#!/usr/bin/env python3

import argparse
from datetime import datetime
import pytz

from database.db_connector import DatabaseConnector

def main():
    parser = argparse.ArgumentParser(description='Print raw data from the database')
    parser.add_argument('--symbol', type=str, default='SPX', help='Symbol to query data for (default: SPX)')
    parser.add_argument('--interval', type=str, default='15m', help='Interval to query (default: 15m)')
    parser.add_argument('--limit', type=int, default=100, help='Maximum number of records to return (default: 100)')
    
    args = parser.parse_args()
    
    db = DatabaseConnector()
    
    # Simple query to get the raw data
    query = """
        SELECT time, symbol, open, high, low, close, volume, interval
        FROM market_data
        WHERE symbol = %s AND interval = %s
        ORDER BY time DESC
        LIMIT %s
    """
    
    results = db.execute_query(query, (args.symbol, args.interval, args.limit))
    
    if not results:
        print(f"No data found for {args.symbol} with interval {args.interval}")
        return
    
    # Print the raw data
    print(f"\nRaw data for {args.symbol} ({args.interval}):")
    print(f"{'Time':<30} {'Symbol':<6} {'Open':<10} {'High':<10} {'Low':<10} {'Close':<10} {'Volume':<12} {'Interval'}")
    print("-" * 100)
    
    eastern_tz = pytz.timezone('US/Eastern')
    
    for row in results:
        time_utc = row[0]
        
        # Convert to Eastern Time for display
        if time_utc.tzinfo is not None:
            time_et = time_utc.astimezone(eastern_tz)
        else:
            # If no timezone info, assume UTC
            time_utc = pytz.utc.localize(time_utc)
            time_et = time_utc.astimezone(eastern_tz)
        
        time_str = time_et.strftime('%Y-%m-%d %H:%M:%S %Z')
        
        print(f"{time_str:<30} {row[1]:<6} {row[2]:<10.2f} {row[3]:<10.2f} {row[4]:<10.2f} {row[5]:<10.2f} {row[6]:<12} {row[7]}")

if __name__ == "__main__":
    main()
