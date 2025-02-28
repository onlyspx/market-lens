#!/usr/bin/env python3

import argparse
from datetime import datetime
import pytz
from collections import defaultdict
import statistics

from database.db_connector import DatabaseConnector

def main():
    parser = argparse.ArgumentParser(description='Simple analysis of monthly close data')
    parser.add_argument('--symbol', type=str, default='SPX', help='Symbol to analyze data for (default: SPX)')
    parser.add_argument('--start-year', type=int, default=datetime.now().year - 2, help='Starting year (default: 2 years ago)')
    parser.add_argument('--end-year', type=int, default=datetime.now().year, help='Ending year (default: current year)')
    
    args = parser.parse_args()
    
    db = DatabaseConnector()
    eastern_tz = pytz.timezone('US/Eastern')
    
    # Query to get the data for the specified years
    query = """
        SELECT time, open, high, low, close, volume
        FROM market_data
        WHERE symbol = %s AND interval = '5m'
        AND EXTRACT(YEAR FROM time) BETWEEN %s AND %s
        ORDER BY time
    """
    
    results = db.execute_query(query, (args.symbol, args.start_year, args.end_year))
    
    if not results:
        print(f"No data found for {args.symbol} between {args.start_year} and {args.end_year}")
        return
    
    # Group data by month
    monthly_data = defaultdict(list)
    
    for row in results:
        time_utc = row[0]
        
        # Convert to Eastern Time for display
        if time_utc.tzinfo is not None:
            time_et = time_utc.astimezone(eastern_tz)
        else:
            # If no timezone info, assume UTC
            time_utc = pytz.utc.localize(time_utc)
            time_et = time_utc.astimezone(eastern_tz)
        
        # Extract year and month for grouping
        year_month = time_et.strftime('%Y-%m')
        
        # Store the data
        monthly_data[year_month].append({
            'time': time_et,
            'open': row[1],
            'high': row[2],
            'low': row[3],
            'close': row[4],
            'volume': row[5]
        })
    
    # Calculate statistics for each month
    monthly_stats = {}
    
    for year_month, candles in monthly_data.items():
        # Sort candles by time
        candles.sort(key=lambda x: x['time'])
        
        # Calculate price change from first candle open to last candle close
        first_open = candles[0]['open']
        last_close = candles[-1]['close']
        price_change = last_close - first_open
        percent_change = (price_change / first_open) * 100
        
        # Calculate range
        high = max(candle['high'] for candle in candles)
        low = min(candle['low'] for candle in candles)
        range_points = high - low
        range_percent = (range_points / low) * 100
        
        # Calculate volume stats
        total_volume = sum(candle['volume'] for candle in candles)
        avg_volume = total_volume / len(candles)
        
        # Find time of high and low
        high_candle = max(candles, key=lambda x: x['high'])
        low_candle = min(candles, key=lambda x: x['low'])
        high_time = high_candle['time'].strftime('%H:%M:%S')
        low_time = low_candle['time'].strftime('%H:%M:%S')
        
        # Store the stats
        monthly_stats[year_month] = {
            'date': candles[0]['time'].strftime('%Y-%m-%d'),
            'num_candles': len(candles),
            'first_open': first_open,
            'last_close': last_close,
            'price_change': price_change,
            'percent_change': percent_change,
            'high': high,
            'low': low,
            'range_points': range_points,
            'range_percent': range_percent,
            'total_volume': total_volume,
            'avg_volume': avg_volume,
            'high_time': high_time,
            'low_time': low_time
        }
    
    # Print summary
    print(f"\nMonthly Close Analysis for {args.symbol} ({args.start_year}-{args.end_year})")
    print(f"{'Date':<10} {'# Candles':<10} {'% Change':<10} {'Range %':<10} {'High Time':<10} {'Low Time':<10}")
    print("-" * 70)
    
    # Sort by date
    for year_month in sorted(monthly_stats.keys()):
        stats = monthly_stats[year_month]
        print(f"{stats['date']:<10} {stats['num_candles']:<10} {stats['percent_change']:>+.2f}%{' ':<5} {stats['range_percent']:.2f}%{' ':<5} {stats['high_time']:<10} {stats['low_time']:<10}")
    
    # Calculate overall statistics
    percent_changes = [stats['percent_change'] for stats in monthly_stats.values()]
    range_percents = [stats['range_percent'] for stats in monthly_stats.values()]
    
    positive_months = sum(1 for pc in percent_changes if pc > 0)
    negative_months = sum(1 for pc in percent_changes if pc < 0)
    flat_months = sum(1 for pc in percent_changes if pc == 0)
    total_months = len(percent_changes)
    
    print("\nOverall Statistics:")
    print(f"Total months analyzed: {total_months}")
    print(f"Positive months: {positive_months} ({positive_months/total_months*100:.1f}%)")
    print(f"Negative months: {negative_months} ({negative_months/total_months*100:.1f}%)")
    print(f"Flat months: {flat_months} ({flat_months/total_months*100:.1f}%)")
    print(f"Average percent change: {sum(percent_changes)/total_months:+.2f}%")
    print(f"Median percent change: {statistics.median(percent_changes):+.2f}%")
    print(f"Average range percent: {sum(range_percents)/total_months:.2f}%")
    print(f"Median range percent: {statistics.median(range_percents):.2f}%")
    
    # Print top gainers and losers
    print("\nTop 5 Strongest Closes:")
    top_gainers = sorted([(year_month, monthly_stats[year_month]['percent_change']) 
                         for year_month in monthly_stats], 
                         key=lambda x: x[1], reverse=True)[:5]
    for year_month, percent_change in top_gainers:
        stats = monthly_stats[year_month]
        print(f"{stats['date']}: {percent_change:+.2f}% change, {stats['range_percent']:.2f}% range")
    
    print("\nTop 5 Weakest Closes:")
    top_losers = sorted([(year_month, monthly_stats[year_month]['percent_change']) 
                        for year_month in monthly_stats], 
                        key=lambda x: x[1])[:5]
    for year_month, percent_change in top_losers:
        stats = monthly_stats[year_month]
        print(f"{stats['date']}: {percent_change:+.2f}% change, {stats['range_percent']:.2f}% range")

if __name__ == "__main__":
    main()
