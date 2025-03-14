#!/usr/bin/env python3

import pandas as pd
import numpy as np
import yfinance as yf
import math
from datetime import datetime, timedelta

class ThirtyMinRangeAnalyzer:
    def __init__(self):
        self.spx_data = None
        self.spx_symbol = "^SPX"
        
    def fetch_data(self, period="1y"):
        """Fetch SPX 30-minute data."""
        print(f"Fetching {self.spx_symbol} 30-minute data for period: {period}")
        spx = yf.Ticker(self.spx_symbol)
        self.spx_data = spx.history(period=period, interval="30m")
        self.spx_data = self.spx_data.reset_index()
        
        # Ensure we have the right column name for datetime
        # Yahoo Finance might return 'Date' or 'Datetime' or 'datetime'
        if 'Datetime' not in self.spx_data.columns and 'Date' in self.spx_data.columns:
            self.spx_data = self.spx_data.rename(columns={'Date': 'Datetime'})
        elif 'Datetime' not in self.spx_data.columns and 'datetime' in self.spx_data.columns:
            self.spx_data = self.spx_data.rename(columns={'datetime': 'Datetime'})
            
        # Print column names for debugging
        print(f"Available columns: {self.spx_data.columns.tolist()}")
        
        return self.spx_data
        
    def calculate_thirty_min_ranges(self):
        """Calculate 30-minute ranges with market profile letters."""
        if self.spx_data is None:
            raise ValueError("No data available. Call fetch_data() first.")
        
        # Handle the case where we can't get 30-minute data
        if len(self.spx_data) == 0:
            print("Warning: No data available for 30-minute intervals. Using simulated data.")
            return self._generate_sample_data()
            
        # Group data by date
        # Use the first column as the datetime column if 'Datetime' is not available
        datetime_col = 'Datetime' if 'Datetime' in self.spx_data.columns else self.spx_data.columns[0]
        self.spx_data['Date'] = pd.to_datetime(self.spx_data[datetime_col]).dt.date
        daily_data = self.spx_data.groupby('Date')
        
        # Market profile letters (A=9:30-10:00, B=10:00-10:30, etc.)
        letters = "ABCDEFGHIJKLMN"  # Enough for trading hours
        
        # For each day, calculate 30-min ranges with market profile letters
        daily_thirty_min_ranges = {}
        
        for date, day_data in daily_data:
            # Sort by datetime
            day_data = day_data.sort_values('Datetime')
            
            # Calculate 30-min ranges with market profile letters
            periods = []
            letter_idx = 0
            
            for _, period_data in day_data.iterrows():
                # Only assign letters during regular trading hours
                datetime_col = 'Datetime' if 'Datetime' in day_data.columns else day_data.columns[0]
                dt = pd.to_datetime(period_data[datetime_col])
                hour = dt.hour
                minute = dt.minute
                
                # Skip pre-market and after-hours
                if (hour < 9) or (hour == 9 and minute < 30) or (hour > 16):
                    continue
                    
                # Assign market profile letter
                if letter_idx < len(letters):
                    letter = letters[letter_idx]
                    letter_idx += 1
                else:
                    letter = "?"  # Fallback
                
                # Format time range
                datetime_col = 'Datetime' if 'Datetime' in day_data.columns else day_data.columns[0]
                dt = pd.to_datetime(period_data[datetime_col])
                start_time = dt.strftime('%H:%M')
                end_time = (dt + pd.Timedelta(minutes=30)).strftime('%H:%M')
                time_range = f"{start_time}-{end_time}"
                
                periods.append({
                    'period': letter,
                    'time': time_range,
                    'range': float(period_data['High'] - period_data['Low']),
                    'change': float(period_data['Close'] - period_data['Open'])
                })
            
            # Calculate daily total
            if len(day_data) > 0:
                daily_change = float(day_data['Close'].iloc[-1] - day_data['Open'].iloc[0])
                
                daily_thirty_min_ranges[date] = {
                    'periods': periods,
                    'daily_change': daily_change
                }
        
        return daily_thirty_min_ranges
    
    def generate_thirty_min_table_html(self, daily_thirty_min_ranges):
        """Generate HTML for the 30-minute range table with market profile letters."""
        # Extract dates and sort (most recent first)
        dates = sorted(daily_thirty_min_ranges.keys(), reverse=True)
        
        # Get all unique periods (A, B, C, etc.)
        all_periods = set()
        for date in dates:
            for period_data in daily_thirty_min_ranges[date]['periods']:
                all_periods.add(period_data['period'])
        all_periods = sorted(list(all_periods))
        
        # Find the global maximum range for better color scaling
        global_max_range = 0
        for date in dates:
            for period_data in daily_thirty_min_ranges[date]['periods']:
                global_max_range = max(global_max_range, period_data['range'])
        
        # Start building HTML table
        html = """
        <table class="thirty-min-table">
            <thead>
                <tr>
                    <th>Date</th>
        """
        
        # Add period columns with time ranges
        period_to_time = {}
        for date in dates:
            for period_data in daily_thirty_min_ranges[date]['periods']:
                period = period_data['period']
                time = period_data['time']
                if period not in period_to_time:
                    period_to_time[period] = time
        
        for period in all_periods:
            time_range = period_to_time.get(period, "")
            html += f"<th>{period}<br><span class='time-range'>{time_range}</span></th>"
        
        # Add total column
        html += "<th>Total +/-</th></tr></thead><tbody>"
        
        # Add data rows
        for date in dates:
            day_data = daily_thirty_min_ranges[date]
            date_str = date.strftime('%Y-%m-%d')
            
            html += f"<tr><td>{date_str}</td>"
            
            # Map of period to range value for this day
            period_to_range = {}
            period_to_change = {}
            for period_data in day_data['periods']:
                period_to_range[period_data['period']] = period_data['range']
                period_to_change[period_data['period']] = period_data['change']
            
            # Add cells for each period with improved color scaling
            for period in all_periods:
                range_val = period_to_range.get(period, 0)
                change_val = period_to_change.get(period, 0)
                
                # Use square root scaling for better visual differentiation
                if global_max_range > 0:
                    intensity = int(255 * (1 - math.sqrt(range_val / global_max_range)))
                else:
                    intensity = 255
                    
                # Use red shades instead of blue
                bg_color = f"rgb(255, {intensity}, {intensity})"
                
                # Add change value with color indicator
                change_color = "green" if change_val > 0 else "red" if change_val < 0 else "black"
                
                # Create a two-part cell layout with clear visual separation
                html += f"""
                <td style="padding: 0; vertical-align: top;">
                    <div style="background-color: {bg_color}; padding: 4px; border-radius: 4px 4px 0 0; text-align: center; font-weight: bold;">
                        {range_val:.2f}
                    </div>
                    <div style="background-color: white; color: {change_color}; padding: 4px; border-radius: 0 0 4px 4px; margin-top: 1px; text-align: center; font-weight: bold; border: 1px solid #eee;">
                        {change_val:+.2f}
                    </div>
                </td>
                """
            
            # Add total column with color based on positive/negative
            daily_change = day_data['daily_change']
            bg_color = "rgb(200, 255, 200)" if daily_change > 0 else "rgb(255, 200, 200)"
            text_color = "green" if daily_change > 0 else "red"
            html += f'<td style="padding: 0;"><div style="background-color: {bg_color}; padding: 8px; border-radius: 4px; text-align: center; font-weight: bold; color: {text_color};">{daily_change:+.2f}</div></td></tr>'
        
        html += "</tbody></table>"
        return html

    def _generate_sample_data(self):
        """Generate sample data for demonstration when real data is not available."""
        print("Generating sample 30-minute market profile data...")
        
        # Create sample dates (last 10 trading days)
        today = datetime.now().date()
        dates = [today - timedelta(days=i) for i in range(10)]
        
        # Filter out weekends
        dates = [date for date in dates if date.weekday() < 5]
        
        # Market profile letters
        letters = "ABCDEFGHIJKLMN"
        
        # Generate sample data
        daily_thirty_min_ranges = {}
        
        for date in dates:
            # Generate random periods for this day
            periods = []
            
            # Trading hours: 9:30 AM to 4:00 PM (13 30-minute periods)
            start_hour = 9
            start_minute = 30
            
            for i in range(13):
                # Calculate time for this period
                current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=start_hour, minutes=start_minute)
                current_time += timedelta(minutes=30 * i)
                
                # Skip if we're past 4:00 PM
                if current_time.hour > 16 or (current_time.hour == 16 and current_time.minute > 0):
                    continue
                
                # Format time range
                start_time = current_time.strftime('%H:%M')
                end_time = (current_time + timedelta(minutes=30)).strftime('%H:%M')
                time_range = f"{start_time}-{end_time}"
                
                # Generate random range and change values
                range_val = round(np.random.uniform(5, 25), 2)  # Random range between 5 and 25 points
                change_val = round(np.random.uniform(-10, 10), 2)  # Random change between -10 and 10 points
                
                periods.append({
                    'period': letters[i] if i < len(letters) else "?",
                    'time': time_range,
                    'range': float(range_val),
                    'change': float(change_val)
                })
            
            # Calculate daily total (sum of changes)
            daily_change = sum(period['change'] for period in periods)
            
            daily_thirty_min_ranges[date] = {
                'periods': periods,
                'daily_change': float(daily_change)
            }
        
        return daily_thirty_min_ranges

def main():
    """Example usage of the ThirtyMinRangeAnalyzer class."""
    analyzer = ThirtyMinRangeAnalyzer()
    
    try:
        # Fetch data
        analyzer.fetch_data(period="1y")
        
        # Calculate 30-minute ranges
        daily_thirty_min_ranges = analyzer.calculate_thirty_min_ranges()
        
        # Generate HTML table
        table_html = analyzer.generate_thirty_min_table_html(daily_thirty_min_ranges)
        
        # Print sample output
        print(table_html[:1000])  # Print first 1000 chars of HTML
    except Exception as e:
        print(f"Error: {e}")
        print("Falling back to sample data...")
        daily_thirty_min_ranges = analyzer._generate_sample_data()
        table_html = analyzer.generate_thirty_min_table_html(daily_thirty_min_ranges)
        print(table_html[:1000])  # Print first 1000 chars of HTML

if __name__ == "__main__":
    main()
