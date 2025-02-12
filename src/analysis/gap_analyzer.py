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
    
    def _analyze_recent_gaps(self, n_days=20):
        """Analyze the most recent n trading days."""
        recent_gaps = self.gaps.head(n_days)  # Data is already sorted by date
        
        # Calculate percentiles for recent gaps
        percentiles = [10, 25, 50, 75, 90]
        gap_percentiles = recent_gaps['gap'].quantile([p/100 for p in percentiles])
        
        # Calculate separate percentiles for up and down gaps
        up_gaps = recent_gaps[recent_gaps['gap'] > 0]['gap']
        down_gaps = recent_gaps[recent_gaps['gap'] < 0]['gap']
        up_percentiles = up_gaps.quantile([p/100 for p in percentiles]) if len(up_gaps) > 0 else pd.Series([0]*len(percentiles))
        down_percentiles = down_gaps.quantile([p/100 for p in percentiles]) if len(down_gaps) > 0 else pd.Series([0]*len(percentiles))
        
        return {
            'total_gaps': len(recent_gaps),
            'avg_gap': recent_gaps['gap'].mean(),
            'median_gap': recent_gaps['gap'].median(),
            'std_gap': recent_gaps['gap'].std(),
            'max_gap_up': recent_gaps['gap'].max(),
            'max_gap_down': recent_gaps['gap'].min(),
            'fill_rate': (recent_gaps['gap_filled'].sum() / len(recent_gaps)) * 100,
            'avg_fill_percent': recent_gaps['gap_fill_percent'].mean(),
            'gap_up_count': len(up_gaps),
            'gap_down_count': len(down_gaps),
            'percentiles': {str(p): val for p, val in zip(percentiles, gap_percentiles)},
            'up_percentiles': {str(p): val for p, val in zip(percentiles, up_percentiles)},
            'down_percentiles': {str(p): val for p, val in zip(percentiles, down_percentiles)},
        }

    def analyze_gaps(self):
        """Generate comprehensive gap statistics."""
        if self.gaps is None:
            self.calculate_gaps()
            
        # Calculate percentiles for all gaps
        percentiles = [10, 25, 50, 75, 90]
        gap_percentiles = self.gaps['gap'].quantile([p/100 for p in percentiles])
        
        # Calculate separate percentiles for up and down gaps
        up_gaps = self.gaps[self.gaps['gap'] > 0]['gap']
        down_gaps = self.gaps[self.gaps['gap'] < 0]['gap']
        up_percentiles = up_gaps.quantile([p/100 for p in percentiles]) if len(up_gaps) > 0 else pd.Series([0]*len(percentiles))
        down_percentiles = down_gaps.quantile([p/100 for p in percentiles]) if len(down_gaps) > 0 else pd.Series([0]*len(percentiles))
        
        # Get recent gaps analysis
        recent_stats = self._analyze_recent_gaps()
        
        stats = {
            'recent_stats': recent_stats,  # Store recent stats in the main stats dictionary
            'total_gaps': len(self.gaps),
            'avg_gap': self.gaps['gap'].mean(),
            'median_gap': self.gaps['gap'].median(),
            'std_gap': self.gaps['gap'].std(),
            'max_gap_up': self.gaps['gap'].max(),
            'max_gap_down': self.gaps['gap'].min(),
            'fill_rate': (self.gaps['gap_filled'].sum() / len(self.gaps)) * 100,
            'avg_fill_percent': self.gaps['gap_fill_percent'].mean(),
            
            # Gap distribution
            'gap_up_count': len(up_gaps),
            'gap_down_count': len(down_gaps),
            
            # Percentile analysis
            'percentiles': {str(p): val for p, val in zip(percentiles, gap_percentiles)},
            'up_percentiles': {str(p): val for p, val in zip(percentiles, up_percentiles)},
            'down_percentiles': {str(p): val for p, val in zip(percentiles, down_percentiles)},
            
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
                'avg_gap': day_data['gap'].mean(),
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
                'Gap Size Box Plot',
                'Average Gap Size by Day',
                'Recent Gaps Analysis',
                'Gap Sizes Over Time',
                'Fill Percentages by Gap Size'
            )
        )
        
        # 1. Gap Size Distribution
        fig.add_trace(
            go.Histogram(x=self.gaps['gap'], name='Gap Size Distribution (Points)'),
            row=1, col=1
        )
        
        # 2. Box Plot of Gap Sizes
        fig.add_trace(
            go.Box(
                y=self.gaps['gap'],
                name='Gap Size Distribution',
                boxpoints='outliers'
            ),
            row=1, col=2
        )
        
        # 3. Average Gap Size by Day
        day_fill_rates = pd.DataFrame.from_dict(self.gap_stats['day_stats'], orient='index')
        fig.add_trace(
            go.Bar(
                x=day_fill_rates.index,
                y=day_fill_rates['avg_gap'],
                name='Avg Gap Size by Day (Points)'
            ),
            row=2, col=1
        )
        
        # 4. Recent Gaps Analysis
        recent_gaps = self.gaps.head(20)
        fig.add_trace(
            go.Scatter(
                x=recent_gaps['date'],
                y=recent_gaps['gap'],
                mode='lines+markers',
                name='Recent Gaps (Last 20 Days)',
                line=dict(color='red')
            ),
            row=2, col=2
        )
        
        # 5. Gap Sizes Over Time
        fig.add_trace(
            go.Scatter(
                x=self.gaps['date'],
                y=self.gaps['gap'],
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
        self._save_summary_stats(output_dir, self.gap_stats['recent_stats'])
    
    def _save_summary_stats(self, output_dir: str, recent_stats: dict):
        """Save summary statistics to a text file."""
        stats_file = os.path.join(output_dir, f"{self.ticker}_gap_stats.md")
        
        with open(stats_file, 'w') as f:
            f.write(f"# Gap Analysis Summary for {self.ticker}\n\n")
            
            f.write("## Overall Statistics\n\n")
            f.write(f"Total Gaps Analyzed: {self.gap_stats['total_gaps']}\n")
            f.write(f"Average Gap Size: {self.gap_stats['avg_gap']:.2f} points\n")
            f.write(f"Median Gap Size: {self.gap_stats['median_gap']:.2f} points\n")
            f.write(f"Gap Standard Deviation: {self.gap_stats['std_gap']:.2f} points\n")
            f.write(f"Maximum Gap Up: {self.gap_stats['max_gap_up']:.2f} points\n")
            f.write(f"Maximum Gap Down: {self.gap_stats['max_gap_down']:.2f} points\n")
            f.write(f"Overall Fill Rate: {self.gap_stats['fill_rate']:.2f}%\n")
            f.write(f"Average Fill Percentage: {self.gap_stats['avg_fill_percent']:.2f}%\n\n")
            
            f.write("## Percentile Analysis (All Gaps)\n\n")
            for percentile, value in self.gap_stats['percentiles'].items():
                f.write(f"{percentile}th percentile: {value:.2f} points\n")
            f.write("\n")
            
            f.write("## Percentile Analysis (Up Gaps)\n\n")
            for percentile, value in self.gap_stats['up_percentiles'].items():
                f.write(f"{percentile}th percentile: {value:.2f} points\n")
            f.write("\n")
            
            f.write("## Percentile Analysis (Down Gaps)\n\n")
            for percentile, value in self.gap_stats['down_percentiles'].items():
                f.write(f"{percentile}th percentile: {value:.2f} points\n")
            f.write("\n")
            
            f.write("## Gap Direction Distribution\n\n")
            f.write(f"Gap Up Count: {self.gap_stats['gap_up_count']}\n")
            f.write(f"Gap Down Count: {self.gap_stats['gap_down_count']}\n\n")
            
            f.write("## Recent Market Analysis (Last 20 Trading Days)\n\n")
            f.write(f"Total Recent Gaps: {recent_stats['total_gaps']}\n")
            f.write(f"Average Recent Gap Size: {recent_stats['avg_gap']:.2f} points\n")
            f.write(f"Recent Fill Rate: {recent_stats['fill_rate']:.2f}%\n")
            f.write(f"Recent Gap Up Count: {recent_stats['gap_up_count']}\n")
            f.write(f"Recent Gap Down Count: {recent_stats['gap_down_count']}\n\n")
            
            f.write("### Recent Percentile Analysis (All Gaps)\n\n")
            for percentile, value in recent_stats['percentiles'].items():
                f.write(f"{percentile}th percentile: {value:.2f} points\n")
            f.write("\n")
            
            f.write("### Recent Percentile Analysis (Up Gaps)\n\n")
            for percentile, value in recent_stats['up_percentiles'].items():
                f.write(f"{percentile}th percentile: {value:.2f} points\n")
            f.write("\n")
            
            f.write("### Recent Percentile Analysis (Down Gaps)\n\n")
            for percentile, value in recent_stats['down_percentiles'].items():
                f.write(f"{percentile}th percentile: {value:.2f} points\n")
            f.write("\n")
            
            f.write("## Recent Daily Summary (Last 20 Trading Days)\n\n")
            recent_gaps = self.gaps.head(20)
            for _, row in recent_gaps.iterrows():
                gap_direction = "UP" if row['gap'] > 0 else "DOWN"
                fill_status = "Filled" if row['gap_filled'] else "Not Filled"
                f.write(f"{row['date'].strftime('%b %d, %Y')}:\n")
                f.write(f"  - Gap: {row['gap']:+.2f} points ({gap_direction})\n")
                f.write(f"  - Status: {fill_status} ({row['gap_fill_percent']:.0f}% filled)\n")
                f.write(f"  - Previous Close: {row['prev_close']:.2f}\n")
                f.write(f"  - Open: {row['open']:.2f}\n")
                f.write("\n")
            
            f.write("## Day of Week Analysis\n\n")
            for day, stats in self.gap_stats['day_stats'].items():
                f.write(f"\n### {day}\n\n")
                f.write(f"  Count: {stats['count']}\n")
                f.write(f"  Average Gap: {stats['avg_gap']:.2f} points\n")
                f.write(f"  Fill Rate: {stats['fill_rate']:.2f}%\n")
                f.write(f"  Average Fill Percentage: {stats['avg_fill_percent']:.2f}%\n")
