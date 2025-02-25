#!/usr/bin/env python3

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class HourlyRangeAnalyzer:
    def __init__(self):
        self.spx_data = None
        self.vix_data = None
        self.hourly_stats = None
        self.spx_symbol = "^SPX"
        self.vix_symbol = "^VIX"
        
    def fetch_data(self, period="1y"):
        """Fetch SPX hourly data and VIX daily data."""
        print(f"Fetching {self.spx_symbol} hourly data for period: {period}")
        spx = yf.Ticker(self.spx_symbol)
        self.spx_data = spx.history(period=period, interval="1h")
        self.spx_data = self.spx_data.reset_index()
        
        print(f"Fetching {self.vix_symbol} daily data for period: {period}")
        vix = yf.Ticker(self.vix_symbol)
        self.vix_data = vix.history(period=period)
        self.vix_data = self.vix_data.reset_index()
        
        return self.spx_data, self.vix_data
    
    def calculate_hourly_metrics(self):
        """Calculate hourly range metrics and correlate with VIX."""
        if self.spx_data is None or self.vix_data is None:
            raise ValueError("No data available. Call fetch_data() first.")
        
        # Add date column without time for grouping
        self.spx_data['Date'] = self.spx_data['Datetime'].dt.date
        
        # Calculate hourly ranges
        self.spx_data['hourly_range'] = self.spx_data['High'] - self.spx_data['Low']
        
        # Get first hour of each day
        first_hours = self.spx_data.sort_values('Datetime').groupby('Date').first()
        
        # Create daily stats
        daily_stats = pd.DataFrame({
            'first_hour_range': first_hours['hourly_range'],
            'first_hour_high': first_hours['High'],
            'first_hour_low': first_hours['Low'],
            'Datetime': first_hours['Datetime']
        })
        
        # Flatten MultiIndex columns
        daily_stats.columns = ['_'.join(col).strip() for col in daily_stats.columns.values]
        daily_stats = daily_stats.reset_index()
        
        # Add day of week
        daily_stats['day_of_week'] = pd.to_datetime(daily_stats['Date']).dt.day_name()
        
        # Merge with previous day's VIX close
        vix_closes = self.vix_data[['Date', 'Close']].copy()
        vix_closes['Date'] = vix_closes['Date'].dt.date
        vix_closes['next_date'] = vix_closes['Date'] + pd.Timedelta(days=1)
        vix_closes = vix_closes.rename(columns={'Close': 'prev_vix_close'})
        
        self.hourly_stats = pd.merge(
            daily_stats,
            vix_closes[['next_date', 'prev_vix_close']],
            left_on='Date',
            right_on='next_date',
            how='left'
        )
        
        # Calculate VIX categories based on percentiles
        vix_percentiles = self.hourly_stats['prev_vix_close'].quantile([0.2, 0.4, 0.6, 0.8])
        self.hourly_stats['vix_category'] = pd.cut(
            self.hourly_stats['prev_vix_close'],
            bins=[-float('inf')] + list(vix_percentiles) + [float('inf')],
            labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
        )
        
        return self.hourly_stats
    
    def analyze_by_vix_category(self):
        """Analyze hourly ranges grouped by VIX categories."""
        if self.hourly_stats is None:
            raise ValueError("No stats available. Call calculate_hourly_metrics() first.")
        
        vix_analysis = self.hourly_stats.groupby('vix_category').agg({
            'prev_vix_close': ['min', 'max', 'mean'],
            'first_hour_range': ['mean', 'median', 'min', 'max', 'std', 'count']
        }).round(2)
        
        return vix_analysis
    
    def analyze_by_day_of_week(self):
        """Analyze hourly ranges grouped by day of week."""
        if self.hourly_stats is None:
            raise ValueError("No stats available. Call calculate_hourly_metrics() first.")
        
        # Define weekday order
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # Group by day of week and calculate statistics
        dow_analysis = self.hourly_stats[
            self.hourly_stats['day_of_week'].isin(weekday_order)
        ].groupby('day_of_week').agg({
            'first_hour_range': ['mean', 'median', 'min', 'max', 'std', 'count']
        }).round(2)
        
        # Reorder index based on weekday_order
        dow_analysis = dow_analysis.reindex(weekday_order)
        
        return dow_analysis
    
    def get_recent_days_analysis(self):
        """Get analysis for the last 5 trading days."""
        if self.hourly_stats is None:
            raise ValueError("No stats available. Call calculate_hourly_metrics() first.")
        
        # Get last 5 trading days
        recent_stats = self.hourly_stats.sort_values('Date', ascending=False).head(5)
        
        # Format the analysis
        recent_analysis = []
        for _, day in recent_stats.iterrows():
            recent_analysis.append({
                'date': day['Date'].strftime('%Y-%m-%d'),
                'day_of_week': pd.to_datetime(day['Date']).strftime('%A'),
                'first_hour_range': float(day['first_hour_range']),
                'first_hour_high': float(day['first_hour_high']),
                'first_hour_low': float(day['first_hour_low']),
                'vix_close': float(day['prev_vix_close']) if pd.notna(day['prev_vix_close']) else None
            })
        
        return recent_analysis
    
    def plot_analysis(self):
        """Create interactive visualization of the analysis."""
        if self.hourly_stats is None:
            raise ValueError("No stats available. Call calculate_hourly_metrics() first.")
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'VIX vs Average Hourly Range',
                'Average Hourly Range by VIX Category',
                'Average Hourly Range by Day of Week',
                'Distribution of Hourly Ranges'
            ),
            vertical_spacing=0.15,
            horizontal_spacing=0.1
        )
        
        # Scatter plot of VIX vs Hourly Range
        fig.add_trace(
            go.Scatter(
                x=self.hourly_stats['prev_vix_close'],
                y=self.hourly_stats['first_hour_range'],
                mode='markers',
                name='VIX vs Range',
                marker=dict(
                    color=self.hourly_stats['first_hour_range'],
                    colorscale='Viridis',
                    showscale=True
                )
            ),
            row=1, col=1
        )
        
        # Bar chart of ranges by VIX category
        vix_cats = self.analyze_by_vix_category()
        fig.add_trace(
            go.Bar(
                x=vix_cats.index,
                y=vix_cats['first_hour_range']['mean'],
                name='Avg First Hour Range by VIX',
                text=vix_cats['first_hour_range']['mean'].round(2),
                textposition='auto',
            ),
            row=1, col=2
        )
        
        # Bar chart of ranges by day of week
        dow_stats = self.analyze_by_day_of_week()
        fig.add_trace(
            go.Bar(
                x=dow_stats.index,
                y=dow_stats['first_hour_range']['mean'],
                name='Avg First Hour Range by Day',
                text=dow_stats['first_hour_range']['mean'].round(2),
                textposition='auto',
            ),
            row=2, col=1
        )
        
        # Histogram of hourly ranges
        fig.add_trace(
            go.Histogram(
                x=self.hourly_stats['first_hour_range'],
                name='First Hour Range Distribution',
                nbinsx=30,
            ),
            row=2, col=2
        )
        
        # Update layout
        fig.update_layout(
            title='SPX Hourly Range Analysis',
            height=1000,
            showlegend=False,
            template='plotly_white'
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="VIX Close", row=1, col=1)
        fig.update_yaxes(title_text="Avg Hourly Range", row=1, col=1)
        
        fig.update_xaxes(title_text="VIX Category", row=1, col=2)
        fig.update_yaxes(title_text="Avg Hourly Range", row=1, col=2)
        
        fig.update_xaxes(title_text="Day of Week", row=2, col=1)
        fig.update_yaxes(title_text="Avg Hourly Range", row=2, col=1)
        
        fig.update_xaxes(title_text="Hourly Range", row=2, col=2)
        fig.update_yaxes(title_text="Frequency", row=2, col=2)
        
        return fig

def main():
    """Example usage of the HourlyRangeAnalyzer class."""
    analyzer = HourlyRangeAnalyzer()
    
    # Fetch data
    analyzer.fetch_data(period="1y")
    
    # Calculate metrics
    analyzer.calculate_hourly_metrics()
    
    # Generate analyses
    vix_analysis = analyzer.analyze_by_vix_category()
    dow_analysis = analyzer.analyze_by_day_of_week()
    
    # Create visualization
    fig = analyzer.plot_analysis()
    
    # Save results
    fig.write_html("data/analysis/hourly/spx_hourly_analysis.html")
    
    # Save analyses to markdown
    with open("data/analysis/hourly/vix_category_analysis.md", "w") as f:
        f.write("# SPX Hourly Range Analysis by VIX Category\n\n")
        f.write(vix_analysis.to_markdown())
        
    with open("data/analysis/hourly/day_of_week_analysis.md", "w") as f:
        f.write("# SPX Hourly Range Analysis by Day of Week\n\n")
        f.write(dow_analysis.to_markdown())
    
    print("\nAnalysis complete. Results saved to data/analysis/hourly/")
    print("- spx_hourly_analysis.html (Interactive visualization)")
    print("- vix_category_analysis.md (VIX category analysis)")
    print("- day_of_week_analysis.md (Day of week analysis)")

if __name__ == "__main__":
    main()
