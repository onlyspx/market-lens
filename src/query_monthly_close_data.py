#!/usr/bin/env python3

import argparse
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
import pytz

from database.db_connector import DatabaseConnector
from market_calendar import MarketCalendar

class MonthlyCloseDataQuery:
    """
    Query and analyze 15-minute OHLC data for the last 30 minutes of trading
    on the last trading day of each month.
    """
    
    def __init__(self):
        self.db = DatabaseConnector()
        self.calendar = MarketCalendar()
        self.eastern_tz = pytz.timezone('US/Eastern')
        self.utc_tz = pytz.UTC
    
    def get_monthly_close_data(self, symbol: str, start_date: Optional[datetime] = None, 
                              end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Retrieve 15-minute OHLC data for the last 30 minutes of trading on monthly close dates.
        
        Args:
            symbol: Stock/Index symbol
            start_date: Start date for data retrieval (optional)
            end_date: End date for data retrieval (optional)
            
        Returns:
            DataFrame with 5-minute OHLC data
        """
        query = """
            SELECT time, open, high, low, close, volume
            FROM market_data
            WHERE symbol = %s AND interval = '15m'
        """
        params = [symbol]
        
        if start_date:
            query += " AND time >= %s"
            params.append(start_date)
        if end_date:
            query += " AND time <= %s"
            params.append(end_date)
            
        query += " ORDER BY time"
        
        results = self.db.execute_query(query, tuple(params))
        if not results:
            print(f"No data found for {symbol}")
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert timezone-aware datetime objects to strings for easier handling
        if not df.empty:
            # Convert datetime objects to Eastern Time strings
            eastern_times = []
            for dt in df['time']:
                if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                    # Already timezone-aware, convert to Eastern
                    eastern_dt = dt.astimezone(self.eastern_tz)
                else:
                    # Assume UTC if no timezone info
                    utc_dt = pytz.utc.localize(dt)
                    eastern_dt = utc_dt.astimezone(self.eastern_tz)
                eastern_times.append(eastern_dt)
            
            # Create a string representation for display
            df['eastern_time'] = [dt.strftime('%Y-%m-%d %H:%M:%S') for dt in eastern_times]
            
            # Keep the original time as index for database operations
            df.set_index('time', inplace=True)
        
        return df
    
    def get_monthly_dates(self, start_year: int, end_year: int) -> List[datetime]:
        """
        Get the last trading day of each month for the specified year range.
        
        Args:
            start_year: Starting year
            end_year: Ending year
            
        Returns:
            List of datetime objects representing the last trading day of each month
        """
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        
        # Get end-of-month business days
        period_endings = self.calendar.get_period_endings(start_date, end_date)
        return period_endings['eom']
    
    def group_by_monthly_close(self, df: pd.DataFrame) -> dict:
        """
        Group the 15-minute data by monthly close dates.
        
        Args:
            df: DataFrame with 15-minute OHLC data
            
        Returns:
            Dictionary with monthly close dates as keys and DataFrames as values
        """
        if df.empty:
            return {}
            
        # Group by date
        grouped_data = {}
        
        # Convert index to datetime if it's not already
        if not isinstance(df.index, pd.DatetimeIndex):
            try:
                df.index = pd.to_datetime(df.index)
            except Exception as e:
                print(f"Warning: Could not convert index to datetime: {e}")
                return {}
        
        # Group by date using a safer approach with string dates
        try:
            # Use the eastern_time string for grouping by date
            df['date_str'] = [dt.split()[0] for dt in df['eastern_time']]
            for date_str, group in df.groupby('date_str'):
                date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                grouped_data[date_obj] = group
            return grouped_data
        except Exception as e:
            print(f"Warning: Error grouping by date: {e}")
            return {}
    
    def print_summary(self, grouped_data: dict) -> None:
        """
        Print a summary of the monthly close data.
        
        Args:
            grouped_data: Dictionary with monthly close dates as keys and DataFrames as values
        """
        if not grouped_data:
            print("No data available")
            return
            
        print(f"\nSummary of Monthly Close Data:")
        print(f"{'Date':<12} {'# Candles':<10} {'Time Range':<25} {'OHLC Range'}")
        print("-" * 80)
        
        for date, df in sorted(grouped_data.items()):
            # Extract time portion from the eastern_time strings
            times = [t.split()[1] for t in df['eastern_time']]
            time_range = f"{min(times)} - {max(times)}"
            price_range = f"{df['low'].min():.2f} - {df['high'].max():.2f}"
            print(f"{date.strftime('%Y-%m-%d'):<12} {len(df):<10} {time_range:<25} {price_range}")
    
    def print_detailed_data(self, grouped_data: dict, date: Optional[datetime] = None) -> None:
        """
        Print detailed data for a specific date or all dates.
        
        Args:
            grouped_data: Dictionary with monthly close dates as keys and DataFrames as values
            date: Specific date to print data for (optional)
        """
        if not grouped_data:
            print("No data available")
            return
            
        if date:
            # Print data for specific date
            date_key = date.date()
            if date_key in grouped_data:
                df = grouped_data[date_key]
                print(f"\nDetailed Data for {date_key.strftime('%Y-%m-%d')}:")
                print(df[['open', 'high', 'low', 'close', 'volume']])
            else:
                print(f"No data available for {date.strftime('%Y-%m-%d')}")
        else:
            # Print data for all dates
            for date_key, df in sorted(grouped_data.items()):
                print(f"\nDetailed Data for {date_key.strftime('%Y-%m-%d')}:")
                print(df[['open', 'high', 'low', 'close', 'volume']])
                print("\n" + "-" * 80)

def main():
    parser = argparse.ArgumentParser(description='Query 15-minute OHLC data for the last 30 minutes of trading on monthly dates')
    parser.add_argument('--symbol', type=str, default='SPX', help='Symbol to query data for (default: SPX)')
    parser.add_argument('--start-year', type=int, default=datetime.now().year - 2, help='Starting year (default: 2 years ago)')
    parser.add_argument('--end-year', type=int, default=datetime.now().year, help='Ending year (default: current year)')
    parser.add_argument('--date', type=str, help='Specific date to query (format: YYYY-MM-DD)')
    parser.add_argument('--summary', action='store_true', help='Print summary only')
    
    args = parser.parse_args()
    
    query = MonthlyCloseDataQuery()
    
    # Set date range
    start_date = datetime(args.start_year, 1, 1)
    end_date = datetime(args.end_year, 12, 31)
    
    # If specific date is provided, use it
    specific_date = None
    if args.date:
        try:
            specific_date = datetime.strptime(args.date, '%Y-%m-%d')
            start_date = specific_date - timedelta(days=1)
            end_date = specific_date + timedelta(days=1)
        except ValueError:
            print(f"Invalid date format: {args.date}. Please use YYYY-MM-DD.")
            return
    
    # Get data from database
    df = query.get_monthly_close_data(args.symbol, start_date, end_date)
    
    if df.empty:
        print(f"No data found for {args.symbol} in the specified date range.")
        return
    
    # Group data by monthly close dates
    grouped_data = query.group_by_monthly_close(df)
    
    # Print summary
    query.print_summary(grouped_data)
    
    # Print detailed data if requested
    if not args.summary:
        query.print_detailed_data(grouped_data, specific_date)

if __name__ == "__main__":
    main()
