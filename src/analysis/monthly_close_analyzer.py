#!/usr/bin/env python3

import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import pytz

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_connector import DatabaseConnector
from market_calendar import MarketCalendar

class MonthlyCloseAnalyzer:
    """
    Analyze 15-minute OHLC data for the last 30 minutes of trading
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
    
    def group_by_monthly_close(self, df: pd.DataFrame) -> Dict[datetime.date, pd.DataFrame]:
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
    
    def calculate_stats(self, grouped_data: Dict[datetime.date, pd.DataFrame]) -> pd.DataFrame:
        """
        Calculate statistics for each monthly close date.
        
        Args:
            grouped_data: Dictionary with monthly close dates as keys and DataFrames as values
            
        Returns:
            DataFrame with statistics for each date
        """
        if not grouped_data:
            return pd.DataFrame()
            
        stats = []
        for date, df in grouped_data.items():
            # Calculate price change
            first_open = df['open'].iloc[0]
            last_close = df['close'].iloc[-1]
            price_change = last_close - first_open
            percent_change = (price_change / first_open) * 100
            
            # Calculate range
            high = df['high'].max()
            low = df['low'].min()
            range_points = high - low
            range_percent = (range_points / low) * 100
            
            # Calculate volume stats
            total_volume = df['volume'].sum()
            avg_volume = df['volume'].mean()
            
            # Calculate volatility (standard deviation of returns)
            returns = df['close'].pct_change().dropna()
            volatility = returns.std() * 100  # Convert to percentage
            
            # Calculate directional consistency
            price_changes = df['close'].diff().dropna()
            positive_changes = (price_changes > 0).sum()
            negative_changes = (price_changes < 0).sum()
            flat_changes = (price_changes == 0).sum()
            
            if len(price_changes) > 0:
                directional_consistency = max(positive_changes, negative_changes) / len(price_changes)
            else:
                directional_consistency = 0
                
            # Calculate time of max and min
            # Find the index of max and min values
            high_idx = df['high'].idxmax()
            low_idx = df['low'].idxmin()
            
            # Get the corresponding eastern_time strings
            high_row = df.loc[high_idx]
            low_row = df.loc[low_idx]
            
            # Extract just the time portion
            max_time = high_row['eastern_time'].split()[1]
            min_time = low_row['eastern_time'].split()[1]
            
            stats.append({
                'date': date,
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
                'volatility': volatility,
                'positive_candles': positive_changes,
                'negative_candles': negative_changes,
                'flat_candles': flat_changes,
                'directional_consistency': directional_consistency,
                'max_time': max_time,
                'min_time': min_time,
                'num_candles': len(df)
            })
        
        return pd.DataFrame(stats).set_index('date')
    
    def analyze_patterns(self, stats_df: pd.DataFrame) -> Dict[str, float]:
        """
        Analyze patterns in the monthly close data.
        
        Args:
            stats_df: DataFrame with statistics for each date
            
        Returns:
            Dictionary with pattern analysis results
        """
        if stats_df.empty:
            return {}
            
        # Calculate percentage of positive vs negative closes
        positive_closes = (stats_df['percent_change'] > 0).sum()
        negative_closes = (stats_df['percent_change'] < 0).sum()
        flat_closes = (stats_df['percent_change'] == 0).sum()
        
        total_months = len(stats_df)
        
        # Calculate average and median statistics
        avg_percent_change = stats_df['percent_change'].mean()
        median_percent_change = stats_df['percent_change'].median()
        avg_range_percent = stats_df['range_percent'].mean()
        avg_volatility = stats_df['volatility'].mean()
        avg_directional_consistency = stats_df['directional_consistency'].mean()
        
        # Calculate correlation between volatility and absolute percent change
        corr_vol_change = stats_df['volatility'].corr(stats_df['percent_change'].abs())
        
        return {
            'total_months': total_months,
            'positive_closes_pct': (positive_closes / total_months) * 100 if total_months > 0 else 0,
            'negative_closes_pct': (negative_closes / total_months) * 100 if total_months > 0 else 0,
            'flat_closes_pct': (flat_closes / total_months) * 100 if total_months > 0 else 0,
            'avg_percent_change': avg_percent_change,
            'median_percent_change': median_percent_change,
            'avg_range_percent': avg_range_percent,
            'avg_volatility': avg_volatility,
            'avg_directional_consistency': avg_directional_consistency * 100,
            'corr_volatility_abs_change': corr_vol_change
        }
    
    def print_analysis(self, stats_df: pd.DataFrame, patterns: Dict[str, float]) -> None:
        """
        Print analysis results.
        
        Args:
            stats_df: DataFrame with statistics for each date
            patterns: Dictionary with pattern analysis results
        """
        if stats_df.empty:
            print("No data available for analysis")
            return
            
        print("\n" + "=" * 80)
        print(f"MONTHLY CLOSE (LAST 30 MINUTES) ANALYSIS")
        print("=" * 80)
        
        print(f"\nAnalyzed {patterns['total_months']} monthly closing periods")
        print(f"Positive closes: {patterns['positive_closes_pct']:.1f}%")
        print(f"Negative closes: {patterns['negative_closes_pct']:.1f}%")
        print(f"Flat closes: {patterns['flat_closes_pct']:.1f}%")
        
        print(f"\nAverage percent change: {patterns['avg_percent_change']:.3f}%")
        print(f"Median percent change: {patterns['median_percent_change']:.3f}%")
        print(f"Average price range: {patterns['avg_range_percent']:.3f}%")
        print(f"Average volatility: {patterns['avg_volatility']:.3f}%")
        print(f"Average directional consistency: {patterns['avg_directional_consistency']:.1f}%")
        
        print("\n" + "-" * 80)
        print("TOP 5 STRONGEST CLOSES")
        print("-" * 80)
        top_gains = stats_df.sort_values('percent_change', ascending=False).head(5)
        for date, row in top_gains.iterrows():
            print(f"{date.strftime('%Y-%m-%d')}: {row['percent_change']:.3f}% change, {row['range_percent']:.3f}% range")
        
        print("\n" + "-" * 80)
        print("TOP 5 WEAKEST CLOSES")
        print("-" * 80)
        top_losses = stats_df.sort_values('percent_change', ascending=True).head(5)
        for date, row in top_losses.iterrows():
            print(f"{date.strftime('%Y-%m-%d')}: {row['percent_change']:.3f}% change, {row['range_percent']:.3f}% range")
        
        print("\n" + "-" * 80)
        print("TOP 5 MOST VOLATILE CLOSES")
        print("-" * 80)
        top_volatile = stats_df.sort_values('volatility', ascending=False).head(5)
        for date, row in top_volatile.iterrows():
            print(f"{date.strftime('%Y-%m-%d')}: {row['volatility']:.3f}% volatility, {row['percent_change']:.3f}% change")
    
    def plot_monthly_changes(self, stats_df: pd.DataFrame, output_file: Optional[str] = None) -> None:
        """
        Plot monthly close changes.
        
        Args:
            stats_df: DataFrame with statistics for each date
            output_file: File path to save the plot (optional)
        """
        if stats_df.empty:
            print("No data available for plotting")
            return
            
        plt.figure(figsize=(12, 8))
        
        # Sort by date
        stats_df = stats_df.sort_index()
        
        # Plot percent changes
        plt.subplot(2, 1, 1)
        plt.bar(stats_df.index, stats_df['percent_change'], 
                color=[('green' if x > 0 else 'red') for x in stats_df['percent_change']])
        plt.title('Monthly Close - Last 30 Minutes Performance')
        plt.ylabel('Percent Change (%)')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Plot volatility
        plt.subplot(2, 1, 2)
        plt.plot(stats_df.index, stats_df['volatility'], 'b-', marker='o')
        plt.title('Monthly Close - Last 30 Minutes Volatility')
        plt.ylabel('Volatility (%)')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file)
            print(f"Plot saved to {output_file}")
        else:
            plt.show()

def main():
    parser = argparse.ArgumentParser(description='Analyze 15-minute OHLC data for the last 30 minutes of trading on monthly dates')
    parser.add_argument('--symbol', type=str, default='SPX', help='Symbol to analyze data for (default: SPX)')
    parser.add_argument('--start-year', type=int, default=datetime.now().year - 5, help='Starting year (default: 5 years ago)')
    parser.add_argument('--end-year', type=int, default=datetime.now().year, help='Ending year (default: current year)')
    parser.add_argument('--plot', action='store_true', help='Generate plots')
    parser.add_argument('--output', type=str, help='Output file for plot (requires --plot)')
    
    args = parser.parse_args()
    
    analyzer = MonthlyCloseAnalyzer()
    
    # Set date range
    start_date = datetime(args.start_year, 1, 1)
    end_date = datetime(args.end_year, 12, 31)
    
    print(f"Analyzing {args.symbol} monthly close data from {start_date.year} to {end_date.year}...")
    
    # Get data from database
    df = analyzer.get_monthly_close_data(args.symbol, start_date, end_date)
    
    if df.empty:
        print(f"No data found for {args.symbol} in the specified date range.")
        return
    
    # Group data by monthly close dates
    grouped_data = analyzer.group_by_monthly_close(df)
    
    # Calculate statistics
    stats_df = analyzer.calculate_stats(grouped_data)
    
    # Analyze patterns
    patterns = analyzer.analyze_patterns(stats_df)
    
    # Print analysis
    analyzer.print_analysis(stats_df, patterns)
    
    # Generate plot if requested
    if args.plot:
        analyzer.plot_monthly_changes(stats_df, args.output)

if __name__ == "__main__":
    main()
