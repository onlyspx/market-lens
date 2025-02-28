#!/usr/bin/env python3

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from hourly_range_analyzer import HourlyRangeAnalyzer

class StaticSiteBuilder:
    def __init__(self):
        self.analyzer = HourlyRangeAnalyzer()
        root_dir = Path(__file__).parent.parent.parent
        self.build_dir = root_dir / "public" / "hourly"
        self.static_dir = self.build_dir / "static"
        self.data_dir = self.build_dir / "data"
        
    def setup_directories(self):
        """Create necessary build directories."""
        print("Setting up build directories...")
        # Remove existing build directory if it exists
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            
        # Create fresh directories
        self.build_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories for assets
        (self.static_dir / "css").mkdir(exist_ok=True)
        (self.static_dir / "js").mkdir(exist_ok=True)
        
    def generate_intraday_table(self):
        """Generate intraday table visualization."""
        print("Generating intraday table...")
        
        # Calculate daily hourly ranges
        daily_hourly_ranges = self.analyzer.calculate_daily_hourly_ranges()
        
        # Generate HTML table
        table_html = self.analyzer.generate_intraday_table_html(daily_hourly_ranges)
        
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
        
        with open(self.data_dir / "intraday_table.json", "w") as f:
            json.dump(table_data, f, indent=2)
        
        # Create the full HTML page
        with open(self.static_dir / "intraday_table.html", "w") as f:
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
    
    def generate_data(self):
        """Generate static JSON data files."""
        print("Generating analysis data...")
        
        # Fetch and analyze data
        self.analyzer.fetch_data(period="1y")
        self.analyzer.calculate_hourly_metrics()
        
        # Generate analyses
        vix_analysis = self.analyzer.analyze_by_vix_category()
        dow_analysis = self.analyzer.analyze_by_day_of_week()
        recent_days = self.analyzer.get_recent_days_analysis()
        
        # Create data files
        # Get full date range from SPX data
        date_range = {
            "start": self.analyzer.spx_data['Date'].min().strftime('%Y-%m-%d'),
            "end": self.analyzer.spx_data['Date'].max().strftime('%Y-%m-%d')
        }
        
        data = {
            "vix_analysis": self._convert_vix_analysis(vix_analysis),
            "dow_analysis": self._convert_dow_analysis(dow_analysis),
            "recent_days": recent_days,
            "last_updated": datetime.now().isoformat(),
            "date_range": date_range
        }
        
        # Save data
        with open(self.data_dir / "analysis.json", "w") as f:
            json.dump(data, f, indent=2)
            
        # Generate and save visualization
        fig = self.analyzer.plot_analysis()
        fig.write_html(self.static_dir / "visualization.html")
        
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
        """Copy static assets to build directory."""
        print("Copying static assets...")
        
        # Copy template files
        templates_dir = Path(__file__).parent / "templates"
        if templates_dir.exists():
            for template in templates_dir.glob("**/*"):
                if template.is_file():
                    rel_path = template.relative_to(templates_dir)
                    dest_path = self.build_dir / rel_path
                    dest_path.parent.mkdir(exist_ok=True)
                    shutil.copy2(template, dest_path)
    
    def build(self):
        """Run the complete build process."""
        print("Starting build process...")
        
        # Setup
        self.setup_directories()
        
        # Generate data and assets
        self.generate_data()
        self.generate_intraday_table()
        self.copy_static_assets()
        
        print(f"\nBuild complete! Output directory: {self.build_dir.absolute()}")
        print("To deploy:")
        print("1. Commit the build directory")
        print("2. Push to your repository")
        print("3. Configure Vercel to deploy from the build directory")

def main():
    builder = StaticSiteBuilder()
    builder.build()

if __name__ == "__main__":
    main()
