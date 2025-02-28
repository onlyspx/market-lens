#!/usr/bin/env python3

import yfinance as yf
import pandas as pd
import time
from urllib.request import urlopen
import json

def check_internet():
    """Test internet connectivity."""
    try:
        urlopen('https://www.google.com', timeout=5)
        return True
    except:
        return False

def test_direct_yfinance():
    """Test yfinance directly without our wrapper."""
    try:
        print("\nChecking internet connectivity...")
        if not check_internet():
            print("No internet connection available!")
            return
        print("Internet connection available")
        
        print("\nTesting direct yfinance fetching...")
        
        # Configure yfinance
        yf.set_tz_cache_location('.')
        
        # Test with different symbols
        symbols = ['SPY', 'QQQ', 'AAPL', '^GSPC', '^VIX']
        
        for symbol in symbols:
            print(f"\nTesting {symbol}...")
            try:
                # Add delay between requests
                time.sleep(2)
                
                # Configure ticker with custom headers
                ticker = yf.Ticker(symbol, session=None)
                ticker._base_url = "https://query1.finance.yahoo.com"
                
                # Try to get info first
                info = ticker.info
                print(f"Got ticker info: {info.get('shortName', 'N/A') if isinstance(info, dict) else 'No info'}")
                
                # Get historical data
                data = ticker.history(period='1d')  # Try just 1 day first
                if not data.empty:
                    print(f"Successfully fetched {len(data)} records")
                    print("\nSample data:")
                    print(data)
                else:
                    print("No data returned")
            except Exception as e:
                print(f"Error fetching {symbol}: {str(e)}")
                print(f"Error type: {type(e)}")
                
    except Exception as e:
        print(f"Error in test: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_direct_yfinance()
