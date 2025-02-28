#!/usr/bin/env python3

import argparse
import pandas as pd
import yfinance as yf
import pytz
import numpy as np
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import time

from database.db_connector import DatabaseConnector
from market_calendar import MarketCalendar

class MonthlyCloseDataFetcher:
    """
    Fetches 5-minute OHLC data for the last 30 minutes of trading
    on the last trading day of each month.
    """
    
    def __init__(self, simulate: bool = False):
        """
        Initialize the fetcher.
        
        Args:
            simulate: If True, generate simulated data when real data is not available
        """
        self.simulate = simulate
        self.db = DatabaseConnector()
        self.calendar = MarketCalendar()
        self.eastern_tz = pytz.timezone('US/Eastern')
        self.utc_tz = pytz.UTC
        
        # Market close time (4:00 PM ET)
        self.market_close_time = datetime.strptime("16:00", "%H:%M").time()
        
    def get_last_trading_days(self, start_year: int, end_year: int) -> List[datetime]:
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
    
    def fetch_intraday_data(self, symbol: str, date: datetime) -> Optional[pd.DataFrame]:
        """
        Fetch 5-minute intraday data for a specific date.
        
        Args:
            symbol: Stock/Index symbol (e.g., 'SPX', '^GSPC')
            date: The date to fetch data for
            
        Returns:
            DataFrame with 5-minute OHLC data or None if data not available
        """
        # For SPX, we need to use the Yahoo Finance symbol ^GSPC
        if symbol.upper() == 'SPX':
            yf_symbol = '^GSPC'
        else:
            yf_symbol = symbol
            
        # Set the date range to cover the full trading day
        # Yahoo Finance requires datetime objects in the local timezone
        start_date = date.replace(hour=9, minute=30)  # Market open (9:30 AM ET)
        end_date = date.replace(hour=16, minute=0) + timedelta(minutes=10)  # Market close + buffer
        
        try:
            # Configure ticker with improved settings
            ticker = yf.Ticker(yf_symbol)
            
            # Add small delay to avoid rate limiting
            time.sleep(1)
            
            # Fetch 5-minute data for the specified date
            data = ticker.history(
                start=start_date,
                end=end_date,
                interval="5m"
            )
            
            if data.empty:
                print(f"No 5-minute data available for {symbol} on {date.strftime('%Y-%m-%d')}")
                if self.simulate:
                    print(f"Generating simulated data for {symbol} on {date.strftime('%Y-%m-%d')}")
                    return self._generate_simulated_data(symbol, date)
                return None
                
            return data
            
        except Exception as e:
            print(f"Error fetching intraday data for {symbol} on {date.strftime('%Y-%m-%d')}: {str(e)}")
            if self.simulate:
                print(f"Generating simulated 5-minute data for {symbol} on {date.strftime('%Y-%m-%d')}")
                return self._generate_simulated_data(symbol, date)
            return None
            
    def _generate_simulated_data(self, symbol: str, date: datetime) -> pd.DataFrame:
        """
        Generate simulated 5-minute OHLC data for the last 30 minutes of trading.
        
        Args:
            symbol: Stock/Index symbol
            date: The trading date
            
        Returns:
            DataFrame with simulated 10-minute OHLC data
        """
        # Set seed based on date and symbol for reproducibility
        seed = int(date.timestamp()) + sum(ord(c) for c in symbol)
        np.random.seed(seed)
        
        # Get a base price for the symbol (use SPX ~5000 as default)
        base_price = 5000.0
        if symbol.upper() == 'QQQ':
            base_price = 400.0
        elif symbol.upper() == 'AAPL':
            base_price = 180.0
        elif symbol.upper() == 'MSFT':
            base_price = 400.0
        
        # Generate timestamps for the last 30 minutes (6 5-minute candles)
        close_time = datetime.combine(date.date(), self.market_close_time)
        close_time = self.eastern_tz.localize(close_time)
        
        timestamps = [
            close_time - timedelta(minutes=30),  # 3:30 PM
            close_time - timedelta(minutes=25),  # 3:35 PM
            close_time - timedelta(minutes=20),  # 3:40 PM
            close_time - timedelta(minutes=15),  # 3:45 PM
            close_time - timedelta(minutes=10),  # 3:50 PM
            close_time - timedelta(minutes=5),   # 3:55 PM
        ]
        
        # Generate OHLC data with realistic price movements
        data = []
        current_price = base_price * (1 + np.random.normal(0, 0.001))  # Small random offset
        
        for i, ts in enumerate(timestamps):
            # Generate realistic price movements
            volatility = 0.0005  # 0.05% volatility per candle
            open_price = current_price
            
            # Higher volatility in the last candle
            if i == 2:
                volatility *= 1.5
                
            # Generate high, low, close with realistic relationships
            high_offset = abs(np.random.normal(0, volatility))
            low_offset = abs(np.random.normal(0, volatility))
            close_offset = np.random.normal(0, volatility)
            
            high_price = open_price * (1 + high_offset)
            low_price = open_price * (1 - low_offset)
            close_price = open_price * (1 + close_offset)
            
            # Ensure high >= open, close and low <= open, close
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Generate realistic volume
            volume = int(np.random.normal(1000000, 300000))
            if volume < 100000:
                volume = 100000
                
            # Add more volume to the last candle (closing auction)
            if i == 2:
                volume *= 2
            
            data.append({
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'Volume': volume
            })
            
            # Update current price for next candle
            current_price = close_price
        
        # Create DataFrame
        df = pd.DataFrame(data, index=timestamps)
        return df
    
    def extract_last_30min(self, data: pd.DataFrame, date: datetime) -> pd.DataFrame:
        """
        Extract the last 30 minutes of trading data (3 10-minute candles).
        
        Args:
            data: DataFrame with intraday data
            date: The trading date
            
        Returns:
            DataFrame with only the last 30 minutes of trading data
        """
        if data is None or data.empty:
            return pd.DataFrame()
            
        # Calculate the start and end times for the 30-minute window
        # Market close is at 4:00 PM ET
        close_time = datetime.combine(date.date(), self.market_close_time)
        close_time = self.eastern_tz.localize(close_time)
        start_time = close_time - timedelta(minutes=30)
        
        # Filter the data to include only the last 30 minutes
        # We use a small buffer to ensure we capture the right candles
        filtered_data = data[
            (data.index >= start_time - timedelta(minutes=1)) & 
            (data.index <= close_time + timedelta(minutes=1))
        ]
        
        return filtered_data
    
    def store_in_db(self, symbol: str, data: pd.DataFrame) -> None:
        """
        Store the 5-minute data in the database.
        
        Args:
            symbol: Stock/Index symbol
            data: DataFrame with OHLC data
        """
        if data is None or data.empty:
            print(f"No data to store for {symbol}")
            return
            
        # Prepare data for insertion
        params_list = []
        for timestamp, row in data.iterrows():
            # Ensure timestamp is timezone-aware and convert to UTC
            if timestamp.tzinfo is None:
                timestamp = timestamp.tz_localize('UTC')
            else:
                timestamp = timestamp.astimezone(self.utc_tz)
            
            params_list.append((
                timestamp,
                symbol,
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                int(row['Volume']),
                '5m'  # 5-minute interval
            ))
        
        # Upsert query to handle overlapping data points
        query = """
            INSERT INTO market_data (time, symbol, open, high, low, close, volume, interval)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (time, symbol, interval) 
            DO UPDATE SET
                open = EXCLUDED.open,
                high = EXCLUDED.high,
                low = EXCLUDED.low,
                close = EXCLUDED.close,
                volume = EXCLUDED.volume
        """
        
        self.db.execute_many(query, params_list)
        print(f"Stored {len(params_list)} records for {symbol}")
    
    def process_symbol(self, symbol: str, start_year: int, end_year: int) -> None:
        """
        Process a symbol to fetch and store 30-min pre-close data for monthly dates.
        
        Args:
            symbol: Stock/Index symbol
            start_year: Starting year
            end_year: Ending year
        """
        # Get the last trading day of each month
        monthly_dates = self.get_last_trading_days(start_year, end_year)
        
        print(f"Processing {symbol} for {len(monthly_dates)} monthly dates from {start_year} to {end_year}")
        
        for date in monthly_dates:
            print(f"Processing {date.strftime('%Y-%m-%d')}...")
            
            # Fetch intraday data for the date
            intraday_data = self.fetch_intraday_data(symbol, date)
            
            if intraday_data is not None and not intraday_data.empty:
                # Extract the last 30 minutes of trading
                last_30min_data = self.extract_last_30min(intraday_data, date)
                
                if not last_30min_data.empty:
                    # Store the data in the database
                    self.store_in_db(symbol, last_30min_data)
                    print(f"Successfully processed {symbol} for {date.strftime('%Y-%m-%d')}")
                    print(f"Found {len(last_30min_data)} 5-minute candles for the last 30 minutes")
                else:
                    print(f"No 30-minute pre-close data available for {symbol} on {date.strftime('%Y-%m-%d')}")
            
            # Add delay to avoid rate limiting
            time.sleep(2)

def main():
    parser = argparse.ArgumentParser(description='Fetch 5-minute OHLC data for the last 30 minutes of trading on monthly dates')
    parser.add_argument('--symbol', type=str, default='SPX', help='Symbol to fetch data for (default: SPX)')
    parser.add_argument('--start-year', type=int, default=datetime.now().year - 2, help='Starting year (default: 2 years ago)')
    parser.add_argument('--end-year', type=int, default=datetime.now().year, help='Ending year (default: current year)')
    parser.add_argument('--simulate', action='store_true', help='Generate simulated data when real data is not available')
    
    args = parser.parse_args()
    
    fetcher = MonthlyCloseDataFetcher(simulate=args.simulate)
    fetcher.process_symbol(args.symbol, args.start_year, args.end_year)

if __name__ == "__main__":
    main()
