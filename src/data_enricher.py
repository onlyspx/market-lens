#!/usr/bin/env python3

import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from market_calendar import MarketCalendar

class DataEnricher:
    """Enriches price data with market calendar events and economic data."""
    
    def __init__(self):
        self.market_calendar = MarketCalendar()
    
    def load_price_data(self, csv_path: str) -> pd.DataFrame:
        """Load price data from CSV and convert to DataFrame with proper date index."""
        df = pd.read_csv(csv_path)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)  # Ensure data is sorted by date
        return df
    
    def add_market_events(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add market event indicators to the DataFrame."""
        # Get date range from the data
        start_date = df.index.min()
        end_date = df.index.max()
        
        # Get all significant dates
        significant_dates = self.market_calendar.get_all_significant_dates(start_date, end_date)
        
        # Initialize event columns
        event_columns = [
            'is_weekly_opex', 'is_monthly_opex', 'is_quarterly_opex',
            'is_eom', 'is_eoq', 'is_eoy'
        ]
        for col in event_columns:
            df[col] = False
        
        # Mark events in the DataFrame
        for date in significant_dates['weekly_opex']:
            if date in df.index:
                df.loc[date, 'is_weekly_opex'] = True
                
        for date in significant_dates['monthly_opex']:
            if date in df.index:
                df.loc[date, 'is_monthly_opex'] = True
                
        for date in significant_dates['quarterly_opex']:
            if date in df.index:
                df.loc[date, 'is_quarterly_opex'] = True
                
        for date in significant_dates['eom']:
            if date in df.index:
                df.loc[date, 'is_eom'] = True
                
        for date in significant_dates['eoq']:
            if date in df.index:
                df.loc[date, 'is_eoq'] = True
                
        for date in significant_dates['eoy']:
            if date in df.index:
                df.loc[date, 'is_eoy'] = True
        
        return df
    
    def analyze_event_impact(self, df: pd.DataFrame, event_type: str, 
                           lookback_days: int = 5, lookforward_days: int = 5) -> Dict:
        """Analyze price behavior around specific event types."""
        if f'is_{event_type}' not in df.columns:
            raise ValueError(f"Event type '{event_type}' not found in data")
        
        # Calculate daily returns
        df['returns'] = df['close'].pct_change()
        
        event_dates = df[df[f'is_{event_type}'] == True].index
        if len(event_dates) == 0:
            return {
                'avg_pre_event_return': 0,
                'avg_post_event_return': 0,
                'avg_event_day_return': 0,
                'volatility_pre_event': 0,
                'volatility_post_event': 0,
                'sample_size': 0
            }
        
        results = {
            'pre_event_returns': [],
            'post_event_returns': [],
            'event_day_returns': [],
            'pre_event_volatility': [],
            'post_event_volatility': []
        }
        
        for date in event_dates:
            try:
                # Get the position of the event date
                event_idx = df.index.get_loc(date)
                
                # Calculate pre-event window
                start_idx = max(0, event_idx - lookback_days)
                pre_event_data = df.iloc[start_idx:event_idx]
                
                # Calculate post-event window
                end_idx = min(len(df), event_idx + lookforward_days + 1)
                post_event_data = df.iloc[event_idx + 1:end_idx]
                
                # Calculate metrics
                if len(pre_event_data) > 0:
                    results['pre_event_returns'].append(pre_event_data['returns'].mean())
                    results['pre_event_volatility'].append(pre_event_data['returns'].std())
                
                if len(post_event_data) > 0:
                    results['post_event_returns'].append(post_event_data['returns'].mean())
                    results['post_event_volatility'].append(post_event_data['returns'].std())
                
                results['event_day_returns'].append(df.iloc[event_idx]['returns'])
                
            except (KeyError, IndexError) as e:
                print(f"Warning: Error processing event date {date}: {str(e)}")
                continue
        
        # Aggregate results
        return {
            'avg_pre_event_return': pd.Series(results['pre_event_returns']).mean(),
            'avg_post_event_return': pd.Series(results['post_event_returns']).mean(),
            'avg_event_day_return': pd.Series(results['event_day_returns']).mean(),
            'volatility_pre_event': pd.Series(results['pre_event_volatility']).mean(),
            'volatility_post_event': pd.Series(results['post_event_volatility']).mean(),
            'sample_size': len(event_dates)
        }
    
    def generate_event_report(self, df: pd.DataFrame) -> Dict[str, Dict]:
        """Generate comprehensive analysis for all event types."""
        event_types = ['weekly_opex', 'monthly_opex', 'quarterly_opex', 'eom', 'eoq', 'eoy']
        report = {}
        
        for event_type in event_types:
            try:
                report[event_type] = self.analyze_event_impact(df, event_type)
            except Exception as e:
                print(f"Warning: Error analyzing {event_type}: {str(e)}")
                report[event_type] = {
                    'error': str(e),
                    'sample_size': 0
                }
        
        return report

def main():
    """Example usage of DataEnricher."""
    enricher = DataEnricher()
    
    # Load and enrich SPX data
    df = enricher.load_price_data('data/historical/SPX.csv')
    enriched_df = enricher.add_market_events(df)
    
    # Generate and print report
    report = enricher.generate_event_report(enriched_df)
    
    print("\nMarket Event Analysis Report:")
    for event_type, metrics in report.items():
        print(f"\n{event_type.upper()} Analysis:")
        for metric, value in metrics.items():
            if isinstance(value, float):
                print(f"{metric}: {value:.4f}")
            else:
                print(f"{metric}: {value}")

if __name__ == "__main__":
    main()