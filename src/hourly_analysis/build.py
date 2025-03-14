#!/usr/bin/env python3

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from hourly_range_analyzer import HourlyRangeAnalyzer
from thirty_min_analyzer import ThirtyMinRangeAnalyzer

class StaticSiteBuilder:
    def __init__(self):
        self.hourly_analyzer = HourlyRangeAnalyzer()
        self.thirty_min_analyzer = ThirtyMinRangeAnalyzer()
        root_dir = Path(__file__).parent.parent.parent
        self.first_hour_dir = root_dir / "public" / "first-hour"
        self.intraday_dir = root_dir / "public" / "intraday"
        self.thirty_min_dir = root_dir / "public" / "thirty-min"
        
        # First hour directories
        self.first_hour_static_dir = self.first_hour_dir / "static"
        self.first_hour_data_dir = self.first_hour_dir / "data"
        
        # Intraday directories
        self.intraday_static_dir = self.intraday_dir / "static"
        self.intraday_data_dir = self.intraday_dir / "data"
        
        # Thirty-minute directories
        self.thirty_min_static_dir = self.thirty_min_dir / "static"
        self.thirty_min_data_dir = self.thirty_min_dir / "data"
        
    def setup_directories(self):
        """Create necessary build directories without removing existing index.html files."""
        print("Setting up build directories...")
        
        # Create directories for first hour analysis (without removing existing files)
        self.first_hour_dir.mkdir(parents=True, exist_ok=True)
        self.first_hour_static_dir.mkdir(parents=True, exist_ok=True)
        self.first_hour_data_dir.mkdir(parents=True, exist_ok=True)
        (self.first_hour_static_dir / "css").mkdir(parents=True, exist_ok=True)
        (self.first_hour_static_dir / "js").mkdir(parents=True, exist_ok=True)
        
        # Create directories for intraday table (without removing existing files)
        self.intraday_dir.mkdir(parents=True, exist_ok=True)
        self.intraday_static_dir.mkdir(parents=True, exist_ok=True)
        self.intraday_data_dir.mkdir(parents=True, exist_ok=True)
        (self.intraday_static_dir / "css").mkdir(parents=True, exist_ok=True)
        (self.intraday_static_dir / "js").mkdir(parents=True, exist_ok=True)
        
        # Create directories for thirty-minute market profile (without removing existing files)
        self.thirty_min_dir.mkdir(parents=True, exist_ok=True)
        self.thirty_min_static_dir.mkdir(parents=True, exist_ok=True)
        self.thirty_min_data_dir.mkdir(parents=True, exist_ok=True)
        (self.thirty_min_static_dir / "css").mkdir(parents=True, exist_ok=True)
        (self.thirty_min_static_dir / "js").mkdir(parents=True, exist_ok=True)
        
    def generate_intraday_table(self):
        """Generate intraday table visualization."""
        print("Generating intraday table...")
        
        # Calculate daily hourly ranges
        daily_hourly_ranges = self.hourly_analyzer.calculate_daily_hourly_ranges()
        
        # Generate HTML table
        table_html = self.hourly_analyzer.generate_intraday_table_html(daily_hourly_ranges)
        
        # Convert date objects to strings for JSON serialization
        serializable_data = {}
        for date, data in daily_hourly_ranges.items():
            date_str = date.strftime('%Y-%m-%d')
            serializable_data[date_str] = data
        
        # Save data as JSON for potential client-side rendering
        table_data = {
            "dates": [date.strftime('%Y-%m-%d') for date in sorted(daily_hourly_ranges.keys(), reverse=True)],
            "hourly_data": serializable_data,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.intraday_data_dir / "intraday_table.json", "w") as f:
            json.dump(table_data, f, indent=2)
        
        # Create the full HTML page
        with open(self.intraday_static_dir / "intraday_table.html", "w") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SPX Intraday Range Table</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                    }}
                    h1 {{
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .intraday-table {{
                        border-collapse: collapse;
                        width: 100%;
                        font-family: Arial, sans-serif;
                    }}
                    .intraday-table th, .intraday-table td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: right;
                    }}
                    .intraday-table th {{
                        background-color: #f2f2f2;
                        position: sticky;
                        top: 0;
                        z-index: 10;
                    }}
                    .intraday-table tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    .intraday-table tr:hover {{
                        background-color: #f1f1f1;
                    }}
                    .intraday-table td:first-child {{
                        position: sticky;
                        left: 0;
                        background-color: #f2f2f2;
                        text-align: left;
                        z-index: 5;
                    }}
                    .intraday-table tr:nth-child(even) td:first-child {{
                        background-color: #e9e9e9;
                    }}
                    .table-container {{
                        max-height: 800px;
                        overflow-y: auto;
                        overflow-x: auto;
                    }}
                    .last-updated {{
                        text-align: right;
                        font-size: 0.9em;
                        color: #666;
                        margin-top: 10px;
                    }}
                </style>
            </head>
            <body>
                <h1>SPX Intraday Range Table</h1>
                <div class="table-container">
                    {table_html}
                </div>
                <div class="last-updated">
                    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </body>
            </html>
            """)
    
    def generate_thirty_min_table(self):
        """Generate thirty-minute market profile table visualization."""
        print("Generating thirty-minute market profile table...")
        
        # Fetch data if not already fetched
        if self.thirty_min_analyzer.spx_data is None:
            # Yahoo Finance limits 30-minute data to the last 60 days
            self.thirty_min_analyzer.fetch_data(period="60d")
        
        # Calculate thirty-minute ranges with market profile letters
        daily_thirty_min_ranges = self.thirty_min_analyzer.calculate_thirty_min_ranges()
        
        # Generate HTML table
        table_html = self.thirty_min_analyzer.generate_thirty_min_table_html(daily_thirty_min_ranges)
        
        # Convert date objects to strings for JSON serialization
        serializable_data = {}
        for date, data in daily_thirty_min_ranges.items():
            date_str = date.strftime('%Y-%m-%d')
            # Convert period data to serializable format
            periods = []
            for period in data['periods']:
                periods.append({
                    'period': period['period'],
                    'time': period['time'],
                    'range': float(period['range']),
                    'change': float(period['change'])
                })
            
            serializable_data[date_str] = {
                'periods': periods,
                'daily_change': float(data['daily_change'])
            }
        
        # Save data as JSON for potential client-side rendering
        table_data = {
            "dates": [date.strftime('%Y-%m-%d') for date in sorted(daily_thirty_min_ranges.keys(), reverse=True)],
            "thirty_min_data": serializable_data,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(self.thirty_min_data_dir / "thirty_min_table.json", "w") as f:
            json.dump(table_data, f, indent=2)
        
        # Create the full HTML page
        with open(self.thirty_min_static_dir / "thirty_min_table.html", "w") as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>SPX 30-Minute Market Profile</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 20px;
                    }}
                    h1 {{
                        text-align: center;
                        margin-bottom: 20px;
                    }}
                    .thirty-min-table {{
                        border-collapse: collapse;
                        width: 100%;
                        font-family: Arial, sans-serif;
                    }}
                    .thirty-min-table th, .thirty-min-table td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: right;
                    }}
                    .thirty-min-table th {{
                        background-color: #f2f2f2;
                        position: sticky;
                        top: 0;
                        z-index: 10;
                    }}
                    .thirty-min-table tr:nth-child(even) {{
                        background-color: #f9f9f9;
                    }}
                    .thirty-min-table tr:hover {{
                        background-color: #f1f1f1;
                    }}
                    .thirty-min-table td:first-child {{
                        position: sticky;
                        left: 0;
                        background-color: #f2f2f2;
                        text-align: left;
                        z-index: 5;
                    }}
                    .thirty-min-table tr:nth-child(even) td:first-child {{
                        background-color: #e9e9e9;
                    }}
                    .time-range {{
                        font-size: 0.8em;
                        color: #666;
                    }}
                    .table-container {{
                        max-height: 800px;
                        overflow-y: auto;
                        overflow-x: auto;
                    }}
                    .last-updated {{
                        text-align: right;
                        font-size: 0.9em;
                        color: #666;
                        margin-top: 10px;
                    }}
                </style>
            </head>
            <body>
                <h1>SPX 30-Minute Market Profile</h1>
                <div class="table-container">
                    {table_html}
                </div>
                <div class="last-updated">
                    Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </div>
            </body>
            </html>
            """)

    def generate_first_hour_data(self):
        """Generate static JSON data files for first hour analysis."""
        print("Generating first hour analysis data...")
        
        # Fetch and analyze data
        self.hourly_analyzer.fetch_data(period="1y")
        self.hourly_analyzer.calculate_hourly_metrics()
        
        # Generate analyses
        vix_analysis = self.hourly_analyzer.analyze_by_vix_category()
        dow_analysis = self.hourly_analyzer.analyze_by_day_of_week()
        recent_days = self.hourly_analyzer.get_recent_days_analysis()
        
        # Create data files
        # Get full date range from SPX data
        date_range = {
            "start": self.hourly_analyzer.spx_data['Date'].min().strftime('%Y-%m-%d'),
            "end": self.hourly_analyzer.spx_data['Date'].max().strftime('%Y-%m-%d')
        }
        
        data = {
            "vix_analysis": self._convert_vix_analysis(vix_analysis),
            "dow_analysis": self._convert_dow_analysis(dow_analysis),
            "recent_days": recent_days,
            "last_updated": datetime.now().isoformat(),
            "date_range": date_range
        }
        
        # Save data
        with open(self.first_hour_data_dir / "analysis.json", "w") as f:
            json.dump(data, f, indent=2)
            
        # Generate and save visualization with CDN to reduce file size
        fig = self.hourly_analyzer.plot_analysis()
        fig.write_html(
            self.first_hour_static_dir / "visualization.html",
            include_plotlyjs='cdn',  # Use CDN instead of embedding the full library
            full_html=True,          # Keep as a standalone HTML file
            config={'responsive': True}  # Make it responsive
        )
        
    def _convert_vix_analysis(self, vix_analysis):
        """Convert VIX analysis to JSON-friendly format."""
        result = []
        for cat in vix_analysis.index:
            result.append({
                "category": cat,
                "vix_min": float(vix_analysis[("prev_vix_close", "min")][cat]),
                "vix_max": float(vix_analysis[("prev_vix_close", "max")][cat]),
                "range_mean": float(vix_analysis[("first_hour_range", "mean")][cat]),
                "range_median": float(vix_analysis[("first_hour_range", "median")][cat]),
                "count": int(vix_analysis[("first_hour_range", "count")][cat])
            })
        return result
    
    def _convert_dow_analysis(self, dow_analysis):
        """Convert day of week analysis to JSON-friendly format."""
        result = []
        for day in dow_analysis.index:
            result.append({
                "day": day,
                "range_mean": float(dow_analysis[("first_hour_range", "mean")][day]),
                "range_median": float(dow_analysis[("first_hour_range", "median")][day]),
                "count": int(dow_analysis[("first_hour_range", "count")][day])
            })
        return result
    
    def copy_static_assets(self):
        """Copy static assets to build directories, but preserve existing index.html files."""
        print("Checking for static assets...")
        
        # Copy template files only if they don't exist
        templates_dir = Path(__file__).parent / "templates"
        if templates_dir.exists():
            # Check first hour index.html
            first_hour_index = self.first_hour_dir / "index.html"
            if not first_hour_index.exists():
                print("Creating new first-hour/index.html (file didn't exist)")
                for template in templates_dir.glob("index.html"):
                    first_hour_index.parent.mkdir(exist_ok=True)
                    shutil.copy2(template, first_hour_index)
            else:
                print("Preserving existing first-hour/index.html")
            
            # Check intraday index.html
            intraday_index = self.intraday_dir / "index.html"
            if not intraday_index.exists():
                print("Creating new intraday/index.html (file didn't exist)")
                for template in templates_dir.glob("intraday_table.html"):
                    intraday_index.parent.mkdir(exist_ok=True)
                    shutil.copy2(template, intraday_index)
            else:
                print("Preserving existing intraday/index.html")
                
            # Check thirty-min index.html
            thirty_min_index = self.thirty_min_dir / "index.html"
            if not thirty_min_index.exists():
                print("Creating new thirty-min/index.html (file didn't exist)")
                for template in templates_dir.glob("thirty_min_table.html"):
                    thirty_min_index.parent.mkdir(exist_ok=True)
                    shutil.copy2(template, thirty_min_index)
            else:
                print("Preserving existing thirty-min/index.html")
    
    def build(self):
        """Run the complete build process."""
        print("Starting build process...")
        
        # Setup
        self.setup_directories()
        
        # Generate data and assets
        self.generate_first_hour_data()
        self.generate_intraday_table()
        self.generate_thirty_min_table()
        self.copy_static_assets()
        
        print(f"\nBuild complete!")
        print(f"First Hour Analysis: {self.first_hour_dir.absolute()}")
        print(f"Intraday Table: {self.intraday_dir.absolute()}")
        print(f"30-Min Market Profile: {self.thirty_min_dir.absolute()}")
        print("\nTo deploy:")
        print("1. Commit the build directories")
        print("2. Push to your repository")
        print("3. Configure Vercel to deploy from the build directories")

def main():
    builder = StaticSiteBuilder()
    builder.build()

if __name__ == "__main__":
    main()
