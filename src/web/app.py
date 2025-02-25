#!/usr/bin/env python3

from flask import Flask, render_template, redirect
import sys
import os
from pathlib import Path

# Add parent directory to path to import analyzers
sys.path.append(str(Path(__file__).parent.parent))
from hourly_analysis.hourly_range_analyzer import HourlyRangeAnalyzer
from analysis.gap_analyzer import GapAnalyzer
from analysis.range_analyzer import RangeAnalyzer

app = Flask(__name__)

# Initialize analyzers
hourly_analyzer = HourlyRangeAnalyzer()  # This one is fine as is
gap_analyzer = GapAnalyzer(ticker="^SPX", data_path="data/historical/SPX.csv")
range_analyzer = RangeAnalyzer()  # This one is fine as is

@app.route('/')
def landing():
    """Render the landing page."""
    return render_template('landing.html')

@app.route('/hourly')
def hourly():
    """Redirect to hourly analysis app."""
    return redirect('http://127.0.0.1:5001')

@app.route('/gaps')
def gaps():
    """Render the gap analysis page."""
    return render_template('gaps.html')

@app.route('/events')
def events():
    """Render the market events analysis page."""
    return render_template('events.html')

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('src/web/templates', exist_ok=True)
    os.makedirs('src/web/static', exist_ok=True)
    
    # Initialize data
    print("Starting Market Lens server...")
    
    app.run(debug=True, port=5000)
