#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database.nasdaq_fetcher import NasdaqFetcher
import json

def test_nasdaq_fetcher():
    """Test NASDAQ API fetching with detailed response inspection."""
    fetcher = NasdaqFetcher()
    test_symbols = {
        'stocks': ['SPY', 'QQQ', 'AAPL'],
        'indices': ['SPX', 'NDX', 'RUT'],
        'etfs': ['XLK', 'XLF', 'XLE']
    }
    
    for category, symbols in test_symbols.items():
        print(f"\nTesting {category}...")
        for symbol in symbols:
            print(f"\nFetching data for {symbol}...")
            
            # Get the URL that would be used
            from_date = fetcher._get_from_date(5)  # Last 5 days
            asset_class = fetcher._get_asset_class(symbol)
            url = fetcher.base_url.format(symbol.lower(), asset_class, from_date)
            print(f"URL: {url}")
            
            # Fetch and inspect raw response
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json',
                    'Referer': 'https://www.nasdaq.com/',
                    'Origin': 'https://www.nasdaq.com'
                }
                import requests
                response = requests.get(url, headers=headers, timeout=30)
                print(f"Status Code: {response.status_code}")
                print(f"Content Type: {response.headers.get('content-type', 'Not specified')}")
                
                if response.ok:
                    json_data = response.json()
                    print("\nResponse structure:")
                    print(json.dumps(json_data, indent=2)[:500] + "...")  # First 500 chars
                    
                    # Try to fetch using the fetcher
                    df = fetcher.fetch_data(symbol, days=5)
                    if df is not None:
                        print(f"\nSuccessfully processed data for {symbol}:")
                        print(df.head())
                    else:
                        print(f"\nFailed to process data for {symbol}")
                
            except Exception as e:
                print(f"Error testing {symbol}: {str(e)}")
            
            print("-" * 80)

if __name__ == "__main__":
    test_nasdaq_fetcher()
