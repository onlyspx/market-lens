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
        self.build_dir = Path("build")
        self.static_dir = self.build_dir / "static"
        self.data_dir = self.build_dir / "data"
        
    def setup_directories(self):
        """Create necessary build directories."""
        print("Setting up build directories...")
        # Remove existing build directory if it exists
        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            
        # Create fresh directories
        self.build_dir.mkdir(exist_ok=True)
        self.static_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for assets
        (self.static_dir / "css").mkdir(exist_ok=True)
        (self.static_dir / "js").mkdir(exist_ok=True)
        
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
        data = {
            "vix_analysis": self._convert_vix_analysis(vix_analysis),
            "dow_analysis": self._convert_dow_analysis(dow_analysis),
            "recent_days": recent_days,
            "last_updated": datetime.now().isoformat(),
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
