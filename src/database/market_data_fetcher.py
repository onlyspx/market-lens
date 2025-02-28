#!/usr/bin/env python3

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import time
import pytz
from .db_connector import DatabaseConnector
from .nasdaq_fetcher import NasdaqFetcher

# Configure yfinance
yf.set_tz_cache_location('.')

class UnifiedDataFetcher:
    """Fetches and stores market data using NASDAQ API for daily data and yfinance for hourly data."""
    
    def __init__(self):
        self.db = DatabaseConnector()
        self.nasdaq = NasdaqFetcher()
        
    def fetch_data(self, symbol: str, interval: str = '1d', period: str = '1y') -> Optional[pd.DataFrame]:
        """
        Smart data fetching that only downloads missing or new data.
        
        Args:
            symbol: Stock/Index symbol (e.g., 'SPY', '^VIX')
            interval: Data interval ('1h' or '1d')
            period: Historical data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
        """
        # Get latest data point from DB
        latest_time = self._get_latest_time(symbol, interval)
        
        try:
            if interval == '1d':
                # Try NASDAQ API first for daily data
                days = self._period_to_days(period)
                data = self.nasdaq.fetch_data(symbol, days=days)
                
                if data is None:
                    print(f"NASDAQ API failed for {symbol}, falling back to yfinance...")
                    data = self._fetch_from_yfinance(symbol, interval, period, latest_time)
            else:
                # Use yfinance for hourly data
                data = self._fetch_from_yfinance(symbol, interval, period, latest_time)
            
            if data is not None and not data.empty:
                self._store_in_db(symbol, interval, data)
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            print(f"Error type: {type(e)}")
            return None
    
    def _fetch_from_yfinance(self, symbol: str, interval: str, period: str, 
                           latest_time: Optional[datetime]) -> Optional[pd.DataFrame]:
        """Fetch data from yfinance."""
        try:
            # Configure ticker with improved settings
            ticker = yf.Ticker(symbol, session=None)
            ticker._base_url = "https://query1.finance.yahoo.com"
            
            # Try to get info first to validate symbol
            try:
                info = ticker.info
                print(f"Got info for {symbol}: {info.get('shortName', 'N/A')}")
            except Exception as e:
                print(f"Warning: Could not get info for {symbol}: {e}")
            
            # Add small delay to avoid rate limiting
            time.sleep(1)
            
            if latest_time is None:
                # No data in DB, fetch full period
                print(f"Fetching full {period} of {interval} data for {symbol}")
                data = ticker.history(period=period, interval=interval)
            else:
                # Calculate period needed for new data only
                delta_kwargs = self._get_interval_delta(interval)
                start_time = latest_time.replace(tzinfo=pytz.UTC) + pd.Timedelta(**delta_kwargs)
                current_time = pd.Timestamp.now(pytz.UTC)
                
                if start_time >= current_time:
                    print(f"Data for {symbol} is already up to date")
                    return None
                
                print(f"Fetching {interval} data for {symbol} since {start_time}")
                data = ticker.history(start=start_time, interval=interval)
            
            return data if not data.empty else None
            
        except Exception as e:
            print(f"Error fetching from yfinance: {e}")
            return None
    
    def _get_latest_time(self, symbol: str, interval: str) -> Optional[datetime]:
        """Get the timestamp of the latest data point in DB."""
        query = """
            SELECT MAX(time) 
            FROM market_data 
            WHERE symbol = %s AND interval = %s
        """
        result = self.db.execute_query(query, (symbol, interval))
        return result[0][0] if result and result[0][0] else None
    
    def _get_interval_delta(self, interval: str) -> dict:
        """Convert interval string to timedelta kwargs."""
        mapping = {
            '1h': {'hours': 1},
            '1d': {'days': 1},
            # Add more intervals as needed
        }
        return mapping.get(interval, {'days': 1})
    
    def _period_to_days(self, period: str) -> int:
        """Convert period string to number of days."""
        mapping = {
            '1d': 1,
            '5d': 5,
            '1mo': 30,
            '3mo': 90,
            '6mo': 180,
            '1y': 365,
            '2y': 730,
            '5y': 1825,
            '10y': 3650,
            'ytd': 365,  # Approximate
            'max': 3650  # Cap at 10 years
        }
        return mapping.get(period, 365)
    
    def _store_in_db(self, symbol: str, interval: str, data: pd.DataFrame) -> None:
        """Transform and store data in TimescaleDB."""
        # Prepare data for insertion
        params_list = []
        for timestamp, row in data.iterrows():
            # Ensure timestamp is timezone-aware
            if timestamp.tzinfo is None:
                timestamp = timestamp.tz_localize('UTC')
            
            params_list.append((
                timestamp,
                symbol,
                float(row['Open']),
                float(row['High']),
                float(row['Low']),
                float(row['Close']),
                int(row['Volume']),
                interval
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
    
    def get_data(self, symbol: str, interval: str, start_time: Optional[datetime] = None, 
                 end_time: Optional[datetime] = None) -> pd.DataFrame:
        """
        Retrieve data from the database.
        
        Args:
            symbol: Stock/Index symbol
            interval: Data interval ('1h' or '1d')
            start_time: Start of data range (optional)
            end_time: End of data range (optional)
        """
        query = """
            SELECT time, open, high, low, close, volume
            FROM market_data
            WHERE symbol = %s AND interval = %s
        """
        params = [symbol, interval]
        
        if start_time:
            query += " AND time >= %s"
            params.append(start_time)
        if end_time:
            query += " AND time <= %s"
            params.append(end_time)
            
        query += " ORDER BY time"
        
        results = self.db.execute_query(query, tuple(params))
        if not results:
            return pd.DataFrame()
            
        # Convert to DataFrame
        df = pd.DataFrame(results, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        df.set_index('time', inplace=True)
        return df
