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
        # Convert day of week analysis to simple format
        dow_stats = []
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
            stats = {
                'day_of_week': day,
                'mean': float(dow_analysis[('hourly_range_mean', 'mean')][day]),
                'median': float(dow_analysis[('hourly_range_mean', 'median')][day]),
                'min': float(dow_analysis[('hourly_range_mean', 'min')][day]),
                'max': float(dow_analysis[('hourly_range_mean', 'max')][day]),
                'count': int(dow_analysis[('hourly_range_mean', 'count')][day])
            }
            dow_stats.append(stats)
        
        # Convert VIX analysis to simple format
        vix_stats = []
        for cat in vix_analysis.index:
            stats = {
                'vix_category': cat,
                'vix_min': float(vix_analysis[('prev_vix_close', 'min')][cat]),
                'vix_max': float(vix_analysis[('prev_vix_close', 'max')][cat]),
                'mean': float(vix_analysis[('hourly_range_mean', 'mean')][cat]),
                'count': int(vix_analysis[('hourly_range_mean', 'count')][cat])
            }
            vix_stats.append(stats)
        
        # Save visualization to static directory
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        os.makedirs(static_dir, exist_ok=True)
        plot_path = os.path.join(static_dir, 'spx_hourly_analysis.html')
        fig.write_html(plot_path)
        
        # Get date range
        start_date = analyzer.spx_data['Date'].min().strftime('%Y-%m-%d')
        end_date = analyzer.spx_data['Date'].max().strftime('%Y-%m-%d')
        
        # Get recent days analysis
        recent_days = analyzer.get_recent_days_analysis()
        
        return jsonify({
            'success': True,
            'vix_analysis': vix_stats,
            'dow_analysis': dow_stats,
            'recent_days': recent_days,
            'plot_url': '/static/spx_hourly_analysis.html',
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Create static directory
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Initialize data
    print("Fetching initial data...")
    analyzer.fetch_data(period="1y")
    analyzer.calculate_hourly_metrics()
    print("Data ready!")
    
    app.run(debug=True, port=5001)  # Use different port than main app
