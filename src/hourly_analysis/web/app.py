#!/usr/bin/env python3

from flask import Flask, render_template, jsonify
import sys
import os
from pathlib import Path

# Add parent directory to path to import hourly_range_analyzer
sys.path.append(str(Path(__file__).parent.parent.parent))
from hourly_analysis.hourly_range_analyzer import HourlyRangeAnalyzer

app = Flask(__name__)
analyzer = HourlyRangeAnalyzer()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/analyze')
def analyze():
    """Analyze SPX hourly ranges and VIX correlation."""
    try:
        # Fetch and analyze data
        analyzer.fetch_data(period="1y")
        analyzer.calculate_hourly_metrics()
        
        # Generate analyses
        vix_analysis = analyzer.analyze_by_vix_category()
        dow_analysis = analyzer.analyze_by_day_of_week()
        
        # Create visualization
        fig = analyzer.plot_analysis()
        
        # Convert analyses to JSON-friendly format
        vix_stats = vix_analysis.to_dict()
        dow_stats = dow_analysis.to_dict()
        
        # Save visualization
        fig.write_html("data/analysis/hourly/spx_hourly_analysis.html")
        
        return jsonify({
            'success': True,
            'vix_analysis': vix_stats,
            'dow_analysis': dow_stats,
            'plot_url': '/data/analysis/hourly/spx_hourly_analysis.html'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data/analysis/hourly', exist_ok=True)
    
    # Initialize data
    print("Fetching initial data...")
    analyzer.fetch_data(period="1y")
    analyzer.calculate_hourly_metrics()
    print("Data ready!")
    
    app.run(debug=True, port=5001)  # Use different port than main app
