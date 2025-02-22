#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
import sys
import os
from pathlib import Path

# Add parent directory to path to import range_analyzer
sys.path.append(str(Path(__file__).parent.parent))
from analysis.range_analyzer import RangeAnalyzer

app = Flask(__name__)
analyzer = RangeAnalyzer()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze SPX moves based on point change."""
    try:
        point_change = float(request.json.get('point_change', 0))
        
        # Fetch data if not already fetched
        if analyzer.data is None:
            analyzer.fetch_data(period="1y")
            analyzer.calculate_daily_metrics()
        
        # Analyze moves similar to the input
        # We'll consider moves within ±10 points of the target
        threshold = point_change
        tolerance = 10
        
        similar_moves = []
        for idx in range(len(analyzer.data) - 3):
            day_change = analyzer.data.loc[idx, 'daily_change']
            
            # Check if this move is similar to our target
            if abs(day_change - threshold) <= tolerance:
                next_days = analyzer.data.iloc[idx+1:idx+4]
                next_changes = next_days['daily_change'].tolist()
                cum_change = sum(next_changes)
                
                similar_moves.append({
                    'date': analyzer.data.loc[idx, 'Date'].strftime('%Y-%m-%d'),
                    'spx_close': round(analyzer.data.loc[idx, 'Close'], 2),
                    'trigger_change': round(day_change, 2),
                    'next_day_1': round(next_changes[0], 2),
                    'next_day_2': round(next_changes[1], 2),
                    'next_day_3': round(next_changes[2], 2),
                    'cumulative_3d': round(cum_change, 2)
                })
        
        # Calculate statistics
        if similar_moves:
            total_moves = len(similar_moves)
            positive_after = sum(1 for move in similar_moves if move['cumulative_3d'] > 0)
            avg_cum_change = sum(move['cumulative_3d'] for move in similar_moves) / total_moves
            
            stats = {
                'total_instances': total_moves,
                'positive_instances': positive_after,
                'negative_instances': total_moves - positive_after,
                'success_rate': round((positive_after / total_moves) * 100, 1),
                'avg_cum_change': round(avg_cum_change, 2)
            }
        else:
            stats = {
                'total_instances': 0,
                'positive_instances': 0,
                'negative_instances': 0,
                'success_rate': 0,
                'avg_cum_change': 0
            }
        
        return jsonify({
            'success': True,
            'moves': similar_moves,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # Create templates and static directories if they don't exist
    os.makedirs('src/web/templates', exist_ok=True)
    os.makedirs('src/web/static', exist_ok=True)
    
    # Initialize data
    print("Fetching initial SPX data...")
    analyzer.fetch_data(period="1y")
    analyzer.calculate_daily_metrics()
    print("Data ready!")
    
    app.run(debug=True, port=5000)