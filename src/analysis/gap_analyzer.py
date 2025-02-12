#!/usr/bin/env python3

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os

class GapAnalyzer:
    def __init__(self, ticker: str, data_path: str):
        """Initialize the gap analyzer for a specific ticker."""
        self.ticker = ticker
        self.data = self._load_data(data_path)
        self.gaps = None
        self.gap_stats = None
        
    def _load_data(self, data_path: str) -> pd.DataFrame:
        """Load and prepare the historical data."""
        df = pd.read_csv(data_path)
        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.day_name()
        df = df.sort_values('date')
        return df
    
    def calculate_gaps(self):
        """Calculate gaps between each day's open and previous day's close."""
        df = self.data.copy()
        df['prev_close'] = df['close'].shift(-1)  # Shift because data is in reverse chronological order
        df['gap'] = df['open'] - df['prev_close']
        df['gap_percent'] = (df['gap'] / df['prev_close']) * 100
        df['gap_filled'] = df.apply(self._check_gap_fill, axis=1)
        df['gap_fill_percent'] = df.apply(self._calculate_fill_percent, axis=1)
        
        # Remove the last row as it won't have a previous close
        self.gaps = df.iloc[:-1].copy()
        return self.gaps
    
    def _check_gap_fill(self, row) -> bool:
        """Check if the gap was filled during the day."""
        if pd.isna(row['gap']) or row['gap'] == 0:
            return False
            
        if row['gap'] > 0:  # Gap up
            return row['low'] <= row['prev_close']
        else:  # Gap down
            return row['high'] >= row['prev_close']
    
    def _calculate_fill_percent(self, row) -> float:
        """Calculate what percentage of the gap was filled."""
        if pd.isna(row['gap']) or row['gap'] == 0:
            return 0.0
            
        if row['gap'] > 0:  # Gap up
            if row['low'] <= row['prev_close']:
                return 100.0
            fill_amount = row['open'] - row['low']
            return min((fill_amount / row['gap']) * 100, 100.0)
        else:  # Gap down
            if row['high'] >= row['prev_close']:
                return 100.0
            fill_amount = row['high'] - row['open']
            return min((fill_amount / abs(row['gap'])) * 100, 100.0)
    
    def analyze_gaps(self):
        """Generate comprehensive gap statistics."""
        if self.gaps is None:
            self.calculate_gaps()
            
        stats = {
            'total_gaps': len(self.gaps),
            'avg_gap_percent': self.gaps['gap_percent'].mean(),
            'median_gap_percent': self.gaps['gap_percent'].median(),
            'std_gap_percent': self.gaps['gap_percent'].std(),
            'max_gap_up': self.gaps['gap_percent'].max(),
            'max_gap_down': self.gaps['gap_percent'].min(),
            'fill_rate': (self.gaps['gap_filled'].sum() / len(self.gaps)) * 100,
            'avg_fill_percent': self.gaps['gap_fill_percent'].mean(),
            
            # Gap distribution
            'gap_up_count': len(self.gaps[self.gaps['gap'] > 0]),
            'gap_down_count': len(self.gaps[self.gaps['gap'] < 0]),
            
            # Day of week analysis
            'day_stats': self._analyze_day_of_week()
        }
        
        self.gap_stats = stats
        return stats
    
    def _analyze_day_of_week(self) -> dict:
        """Analyze gap patterns by day of the week."""
        day_stats = {}
        for day in self.gaps['day_of_week'].unique():
            day_data = self.gaps[self.gaps['day_of_week'] == day]
            day_stats[day] = {
                'count': len(day_data),
                'avg_gap_percent': day_data['gap_percent'].mean(),
                'fill_rate': (day_data['gap_filled'].sum() / len(day_data)) * 100,
                'avg_fill_percent': day_data['gap_fill_percent'].mean()
            }
        return day_stats
    
    def generate_report(self, output_dir: str):
        """Generate an HTML report with interactive visualizations."""
        if self.gap_stats is None:
            self.analyze_gaps()
            
        # Create the main figure with subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                'Gap Size Distribution',
                'Gap Fill Rate by Day',
                'Average Gap Size by Day',
                'Gap Fill Success Rate',
                'Gap Sizes Over Time',
                'Fill Percentages by Gap Size'
            )
        )
        
        # 1. Gap Size Distribution
        fig.add_trace(
            go.Histogram(x=self.gaps['gap_percent'], name='Gap Size Distribution'),
            row=1, col=1
        )
        
        # 2. Gap Fill Rate by Day
        day_fill_rates = pd.DataFrame.from_dict(self.gap_stats['day_stats'], orient='index')
        fig.add_trace(
            go.Bar(
                x=day_fill_rates.index,
                y=day_fill_rates['fill_rate'],
                name='Fill Rate by Day'
            ),
            row=1, col=2
        )
        
        # 3. Average Gap Size by Day
        fig.add_trace(
            go.Bar(
                x=day_fill_rates.index,
                y=day_fill_rates['avg_gap_percent'],
                name='Avg Gap Size by Day'
            ),
            row=2, col=1
        )
        
        # 4. Gap Fill Success Rate vs Gap Size
        fig.add_trace(
            go.Scatter(
                x=self.gaps['gap_percent'],
                y=self.gaps['gap_fill_percent'],
                mode='markers',
                name='Fill Success vs Gap Size'
            ),
            row=2, col=2
        )
        
        # 5. Gap Sizes Over Time
        fig.add_trace(
            go.Scatter(
                x=self.gaps['date'],
                y=self.gaps['gap_percent'],
                mode='lines+markers',
                name='Gap Sizes Over Time'
            ),
            row=3, col=1
        )
        
        # 6. Fill Percentages Distribution
        fig.add_trace(
            go.Histogram(
                x=self.gaps['gap_fill_percent'],
                name='Fill Percentage Distribution'
            ),
            row=3, col=2
        )
        
        # Update layout
        fig.update_layout(
            title_text=f"Gap Analysis for {self.ticker}",
            height=1200,
            showlegend=False
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the plot
        fig.write_html(os.path.join(output_dir, f"{self.ticker}_gap_analysis.html"))
        
        # Generate summary statistics file
        self._save_summary_stats(output_dir)
    
    def _save_summary_stats(self, output_dir: str):
        """Save summary statistics to a text file."""
        stats_file = os.path.join(output_dir, f"{self.ticker}_gap_stats.txt")
        
        with open(stats_file, 'w') as f:
            f.write(f"Gap Analysis Summary for {self.ticker}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("Overall Statistics:\n")
            f.write(f"Total Gaps Analyzed: {self.gap_stats['total_gaps']}\n")
            f.write(f"Average Gap Size: {self.gap_stats['avg_gap_percent']:.2f}%\n")
            f.write(f"Median Gap Size: {self.gap_stats['median_gap_percent']:.2f}%\n")
            f.write(f"Gap Standard Deviation: {self.gap_stats['std_gap_percent']:.2f}%\n")
            f.write(f"Maximum Gap Up: {self.gap_stats['max_gap_up']:.2f}%\n")
            f.write(f"Maximum Gap Down: {self.gap_stats['max_gap_down']:.2f}%\n")
            f.write(f"Overall Fill Rate: {self.gap_stats['fill_rate']:.2f}%\n")
            f.write(f"Average Fill Percentage: {self.gap_stats['avg_fill_percent']:.2f}%\n\n")
            
            f.write("Gap Direction Distribution:\n")
            f.write(f"Gap Up Count: {self.gap_stats['gap_up_count']}\n")
            f.write(f"Gap Down Count: {self.gap_stats['gap_down_count']}\n\n")
            
            f.write("Day of Week Analysis:\n")
            for day, stats in self.gap_stats['day_stats'].items():
                f.write(f"\n{day}:\n")
                f.write(f"  Count: {stats['count']}\n")
                f.write(f"  Average Gap: {stats['avg_gap_percent']:.2f}%\n")
                f.write(f"  Fill Rate: {stats['fill_rate']:.2f}%\n")
                f.write(f"  Average Fill Percentage: {stats['avg_fill_percent']:.2f}%\n")
