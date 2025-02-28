#!/usr/bin/env python3

import os
import sys
import json
import time
from datetime import datetime, timedelta
import requests
import pandas as pd
from typing import Optional, Dict, Any

class NasdaqFetcher:
    """Fetches daily market data from NASDAQ API."""
    
    def __init__(self):
        self.base_url = "https://api.nasdaq.com/api/quote/{}/historical?assetclass={}&fromdate={}&limit=365"
        
    def _get_from_date(self, days: int) -> str:
        """Get the from date string for the API request."""
        return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
    def fetch_data(self, symbol: str, days: int = 365) -> Optional[pd.DataFrame]:
        """
        Fetch historical daily data for a given symbol.
        
        Args:
            symbol: Stock/Index symbol
            days: Number of days of historical data to fetch
            
        Returns:
            DataFrame with columns: [date, open, high, low, close, volume]
            or None if fetch fails
        """
        print(f"Fetching NASDAQ data for {symbol}...")
        
        # Determine asset class based on symbol
        asset_class = self._get_asset_class(symbol)
        from_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        url = self.base_url.format(symbol.lower(), asset_class, from_date)
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Referer': 'https://www.nasdaq.com/',
                'Origin': 'https://www.nasdaq.com'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            if not response.headers.get('content-type', '').startswith('application/json'):
                print(f"Unexpected content type from NASDAQ API for {symbol}")
                return None
                
            json_data = response.json()
            
            # Extract data from JSON response
            if 'data' in json_data:
                data_obj = json_data['data']
                
                # Handle different response formats
                if isinstance(data_obj, dict):
                    # Format 1: Index data
                    if 'tradesTable' in data_obj and 'rows' in data_obj['tradesTable']:
                        rows = []
                        for row in data_obj['tradesTable']['rows']:
                            processed_row = self._process_row(row)
                            if processed_row:
                                rows.append(processed_row)
                    # Format 2: Stock/ETF data
                    elif 'chart' in data_obj and 'rows' in data_obj['chart']:
                        rows = []
                        for row in data_obj['chart']['rows']:
                            processed_row = self._process_row(row)
                            if processed_row:
                                rows.append(processed_row)
                    else:
                        print(f"Unrecognized data format for {symbol}")
                        return None
                        
                    if not rows:
                        print(f"No valid data rows found for {symbol}")
                        return None
                        
                    # Create DataFrame
                    df = pd.DataFrame(rows)
                    df.set_index('date', inplace=True)
                    
                    # Rename columns to match yfinance format
                    df.columns = [col.title() for col in df.columns]  # Capitalize first letter
                    df.index.name = 'Date'  # Match yfinance index name
                    
                    print(f"Successfully fetched {len(df)} records for {symbol}")
                    return df
                
            print(f"Unexpected JSON format from NASDAQ API for {symbol}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching NASDAQ data for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching NASDAQ data for {symbol}: {e}")
            return None
    
    def _get_asset_class(self, symbol: str) -> str:
        """Determine asset class based on symbol."""
        symbol = symbol.upper()
        if symbol in ["SPX", "NDX", "RUT"]:
            return "index"
        elif symbol in ["SPY", "QQQ"] or symbol.startswith("X"):  # Common ETFs
            return "etf"
        else:
            return "stocks"
    
    def _process_row(self, row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single row of data from NASDAQ API response."""
        try:
            # Clean and validate date
            date_str = row.get('date', '')
            try:
                date = pd.to_datetime(date_str)
            except:
                print(f"Invalid date format: {date_str}")
                return None
            
            # Clean price values
            def clean_price(val: Any) -> float:
                if isinstance(val, (int, float)):
                    return float(val)
                if isinstance(val, str):
                    val = val.replace('$', '').replace(',', '')
                    try:
                        return float(val)
                    except:
                        return None
                return None
            
            # Extract and clean values
            open_price = clean_price(row.get('open', row.get('openPrice', '')))
            high_price = clean_price(row.get('high', row.get('highPrice', '')))
            low_price = clean_price(row.get('low', row.get('lowPrice', '')))
            close_price = clean_price(row.get('close', row.get('closePrice', '')))
            
            # Clean volume
            volume_str = str(row.get('volume', row.get('numberOfShares', '0'))).replace(',', '')
            try:
                volume = int(volume_str) if volume_str != '--' else 0
            except:
                volume = 0
            
            # Validate all required values are present
            if all(v is not None for v in [open_price, high_price, low_price, close_price]):
                return {
                    'date': date,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume
                }
            
            return None
            
        except Exception as e:
            print(f"Error processing row: {e}")
            return None

if __name__ == "__main__":
    # Test the fetcher
    fetcher = NasdaqFetcher()
    test_symbols = ['SPY', 'QQQ', 'SPX', 'XLK']
    
    for symbol in test_symbols:
        print(f"\nTesting {symbol}...")
        df = fetcher.fetch_data(symbol, days=5)
        if df is not None:
            print(f"\nSample data for {symbol}:")
            print(df.head())
        time.sleep(1)  # Rate limiting
