#!/usr/bin/env python3

import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from analysis.gap_analyzer import GapAnalyzer

def load_tickers():
    """Load tickers from config file."""
    config_path = os.path.join('config', 'tickers.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['tickers']

def generate_summary(all_stats, output_dir):
    """Generate a summary markdown file comparing all tickers."""
    summary_file = os.path.join(output_dir, 'all_tickers_summary.md')
    
    with open(summary_file, 'w') as f:
        f.write("# Gap Analysis Summary - All Tickers\n\n")
        
        # Overall Stats Table
        f.write("## Overall Statistics\n\n")
        f.write("| Ticker | Total Gaps | Avg Gap | Fill Rate | Up Gaps | Down Gaps |\n")
        f.write("|--------|------------|----------|-----------|----------|------------|\n")
        for ticker, stats in all_stats.items():
            f.write(f"| {ticker} | {stats['total_gaps']} | {stats['avg_gap']:.2f} | {stats['fill_rate']:.2f}% | {stats['gap_up_count']} | {stats['gap_down_count']} |\n")
        f.write("\n")
        
        # Recent Stats Table
        f.write("## Recent Performance (Last 20 Days)\n\n")
        f.write("| Ticker | Avg Gap | Fill Rate | Up Gaps | Down Gaps |\n")
        f.write("|--------|----------|-----------|----------|------------|\n")
        for ticker, stats in all_stats.items():
            recent = stats['recent_stats']
            f.write(f"| {ticker} | {recent['avg_gap']:.2f} | {recent['fill_rate']:.2f}% | {recent['gap_up_count']} | {recent['gap_down_count']} |\n")
        f.write("\n")
        
        # Day of Week Analysis
        f.write("## Day of Week Fill Rates\n\n")
        f.write("| Ticker | Monday | Tuesday | Wednesday | Thursday | Friday |\n")
        f.write("|--------|---------|----------|-----------|-----------|--------|\n")
        for ticker, stats in all_stats.items():
            day_stats = stats['day_stats']
            fill_rates = []
            for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                if day in day_stats:
                    fill_rates.append(f"{day_stats[day]['fill_rate']:.1f}%")
                else:
                    fill_rates.append("N/A")
            f.write(f"| {ticker} | {' | '.join(fill_rates)} |\n")

def main():
    output_dir = os.path.join('data', 'analysis', 'gaps')
    os.makedirs(output_dir, exist_ok=True)
    
    tickers = load_tickers()
    all_stats = {}
    
    for ticker in tickers:
        print(f"\nAnalyzing gaps for {ticker}...")
        data_path = os.path.join('data', 'historical', f'{ticker}.csv')
        
        # Initialize analyzer and calculate stats
        analyzer = GapAnalyzer(ticker, data_path)
        analyzer.calculate_gaps()
        stats = analyzer.analyze_gaps()
        all_stats[ticker] = stats
        
        # Save individual ticker stats
        stats_file = os.path.join(output_dir, f'{ticker}_gap_stats.md')
        with open(stats_file, 'w') as f:
            f.write(f"# Gap Analysis Summary for {ticker}\n\n")
            
            f.write("## Overall Statistics\n\n")
            f.write(f"Total Gaps Analyzed: {stats['total_gaps']}\n")
            f.write(f"Average Gap Size: {stats['avg_gap']:.2f} points\n")
            f.write(f"Median Gap Size: {stats['median_gap']:.2f} points\n")
            f.write(f"Gap Standard Deviation: {stats['std_gap']:.2f} points\n")
            f.write(f"Maximum Gap Up: {stats['max_gap_up']:.2f} points\n")
            f.write(f"Maximum Gap Down: {stats['max_gap_down']:.2f} points\n")
            f.write(f"Overall Fill Rate: {stats['fill_rate']:.2f}%\n")
            f.write(f"Average Fill Percentage: {stats['avg_fill_percent']:.2f}%\n\n")
            
            f.write("## Recent Daily Summary (Last 20 Trading Days)\n\n")
            f.write("| Date | Gap | Direction | Status | Fill % | Prev Close | Open |\n")
            f.write("|------|-----|-----------|---------|---------|------------|-------|\n")
            recent_gaps = analyzer.gaps.head(20)
            for _, row in recent_gaps.iterrows():
                gap_direction = "UP" if row['gap'] > 0 else "DOWN"
                fill_status = "Filled" if row['gap_filled'] else "Not Filled"
                f.write(f"| {row['date'].strftime('%b %d, %Y')} | {row['gap']:+.2f} | {gap_direction} | {fill_status} | {row['gap_fill_percent']:.0f}% | {row['prev_close']:.2f} | {row['open']:.2f} |\n")
            
            f.write("\n## Day of Week Analysis\n\n")
            f.write("| Day | Count | Avg Gap | Fill Rate | Avg Fill % |\n")
            f.write("|-----|-------|----------|-----------|------------|\n")
            for day, day_stats in stats['day_stats'].items():
                f.write(f"| {day} | {day_stats['count']} | {day_stats['avg_gap']:.2f} | {day_stats['fill_rate']:.2f}% | {day_stats['avg_fill_percent']:.2f}% |\n")
        
        print(f"Stats saved to {stats_file}")
    
    # Generate summary comparing all tickers
    generate_summary(all_stats, output_dir)
    print(f"\nAnalysis complete! Check {output_dir} for individual ticker stats")
    print(f"Summary comparison available in {output_dir}/all_tickers_summary.md")

if __name__ == "__main__":
    main()
