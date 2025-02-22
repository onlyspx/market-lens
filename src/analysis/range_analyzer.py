#!/usr/bin/env python3

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class RangeAnalyzer:
    def __init__(self):
        self.data = None
        self.symbol = "^SPX"  # SPX ticker symbol
        
    def fetch_data(self, period="1y"):
        """Fetch SPX data using yfinance."""
        print(f"Fetching {self.symbol} data for period: {period}")
        ticker = yf.Ticker(self.symbol)
        self.data = ticker.history(period=period)
        self.data = self.data.reset_index()
        return self.data
    
    def calculate_daily_metrics(self):
        """Calculate daily range and point changes."""
        if self.data is None:
            raise ValueError("No data available. Call fetch_data() first.")
            
        # Calculate daily range in points
        self.data['daily_range'] = self.data['High'] - self.data['Low']
        
        # Calculate daily point change
        self.data['daily_change'] = self.data['Close'] - self.data['Close'].shift(1)
        
        # Calculate rolling metrics
        self.data['avg_range_5d'] = self.data['daily_range'].rolling(window=5).mean()
        self.data['avg_range_20d'] = self.data['daily_range'].rolling(window=20).mean()
        
        return self.data
    
    def analyze_significant_moves(self, threshold=-100):
        """Analyze patterns after significant down moves (in points)."""
        if 'daily_change' not in self.data.columns:
            self.calculate_daily_metrics()
            
        # Identify significant down days
        sig_moves = self.data[self.data['daily_change'] <= threshold].copy()
        
        results = []
        for idx in sig_moves.index:
            if idx + 3 >= len(self.data):
                continue
                
            # Get next 3 days changes
            next_days = self.data.iloc[idx+1:idx+4]
            next_changes = next_days['daily_change'].tolist()
            cum_change = sum(next_changes)
            
            results.append({
                'trigger_date': self.data.loc[idx, 'Date'],
                'trigger_close': self.data.loc[idx, 'Close'],
                'trigger_change': self.data.loc[idx, 'daily_change'],
                'next_day_1': next_changes[0],
                'next_day_2': next_changes[1],
                'next_day_3': next_changes[2],
                'cumulative_3d': cum_change
            })
            
        return pd.DataFrame(results)
    
    def plot_analysis(self):
        """Create interactive visualization of the analysis."""
        if self.data is None:
            raise ValueError("No data available. Call fetch_data() first.")
            
        # Create subplots
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Daily Range (Points)', 'Daily Point Changes', 'Rolling Average Ranges'),
            vertical_spacing=0.1,
            row_heights=[0.4, 0.3, 0.3]
        )
        
        # Daily Range Plot
        fig.add_trace(
            go.Scatter(x=self.data['Date'], y=self.data['daily_range'],
                      name='Daily Range', mode='lines'),
            row=1, col=1
        )
        
        # Daily Changes Plot
        fig.add_trace(
            go.Scatter(x=self.data['Date'], y=self.data['daily_change'],
                      name='Daily Change', mode='lines'),
            row=2, col=1
        )
        
        # Add horizontal line at -100 points
        fig.add_hline(y=-100, line_dash="dash", line_color="red",
                      annotation_text="Significant Move Threshold (-100 points)",
                      row=2, col=1)
        
        # Rolling Averages
        fig.add_trace(
            go.Scatter(x=self.data['Date'], y=self.data['avg_range_5d'],
                      name='5-day Avg Range', mode='lines'),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=self.data['Date'], y=self.data['avg_range_20d'],
                      name='20-day Avg Range', mode='lines'),
            row=3, col=1
        )
        
        # Update layout
        fig.update_layout(
            title='SPX Range Analysis (in Points)',
            height=1000,
            showlegend=True,
            template='plotly_white'
        )
        
        return fig
    
    def generate_summary_stats(self):
        """Generate summary statistics for the analysis."""
        if self.data is None:
            raise ValueError("No data available. Call fetch_data() first.")
            
        stats = {
            'avg_daily_range': self.data['daily_range'].mean(),
            'median_daily_range': self.data['daily_range'].median(),
            'max_daily_range': self.data['daily_range'].max(),
            'min_daily_range': self.data['daily_range'].min(),
            'std_daily_range': self.data['daily_range'].std(),
            'significant_down_days': len(self.data[self.data['daily_change'] <= -100]),
            'total_days': len(self.data)
        }
        
        return pd.Series(stats)

def main():
    """Example usage of the RangeAnalyzer class."""
    analyzer = RangeAnalyzer()
    
    # Fetch data
    data = analyzer.fetch_data(period="1y")
    
    # Calculate metrics
    analyzer.calculate_daily_metrics()
    
    # Analyze significant moves
    sig_moves = analyzer.analyze_significant_moves()
    
    # Generate stats
    stats = analyzer.generate_summary_stats()
    
    # Create visualization
    fig = analyzer.plot_analysis()
    
    # Save results
    fig.write_html("data/analysis/ranges/SPX_range_analysis.html")
    
    # Format significant moves for better readability
    if not sig_moves.empty:
        print("\nSignificant Down Moves (-100 points or more) Analysis:")
        print("\nTrigger Day Analysis:")
        for _, row in sig_moves.iterrows():
            print(f"\nDate: {row['trigger_date'].strftime('%Y-%m-%d')}")
            print(f"SPX Close: {row['trigger_close']:.2f}")
            print(f"Day's Change: {row['trigger_change']:.2f} points")
            print("Next 3 Days:")
            print(f"  Day 1: {row['next_day_1']:+.2f} points")
            print(f"  Day 2: {row['next_day_2']:+.2f} points")
            print(f"  Day 3: {row['next_day_3']:+.2f} points")
            print(f"3-Day Cumulative: {row['cumulative_3d']:+.2f} points")
    else:
        print("\nNo significant down moves (-100 points or more) found in the period.")
    
    print("\nSummary Statistics:")
    print(stats)

if __name__ == "__main__":
    main()