#!/usr/bin/env python3

import os
from analysis.gap_analyzer import GapAnalyzer

def main():
    # Initialize analyzer for SPX
    data_path = os.path.join('data', 'historical', 'SPX.csv')
    output_dir = os.path.join('data', 'analysis', 'gaps')
    
    print(f"Analyzing gaps for SPX...")
    analyzer = GapAnalyzer('SPX', data_path)
    
    # Calculate gaps and generate statistics
    analyzer.calculate_gaps()
    stats = analyzer.analyze_gaps()
    
    # Generate report
    analyzer.generate_report(output_dir)
    print(f"\nAnalysis complete! Reports saved in {output_dir}")
    print(f"Check {output_dir}/SPX_gap_analysis.html for interactive visualizations")
    print(f"Check {output_dir}/SPX_gap_stats.txt for detailed statistics")
    
    # Print key statistics to console
    print("\nKey Statistics:")
    print(f"Total Gaps Analyzed: {stats['total_gaps']}")
    print(f"Average Gap Size: {stats['avg_gap_percent']:.2f}%")
    print(f"Overall Fill Rate: {stats['fill_rate']:.2f}%")
    print(f"Gap Up Count: {stats['gap_up_count']}")
    print(f"Gap Down Count: {stats['gap_down_count']}")
    
    print("\nDay of Week Fill Rates:")
    for day, day_stats in stats['day_stats'].items():
        print(f"{day}: {day_stats['fill_rate']:.2f}% ({day_stats['count']} gaps)")

if __name__ == "__main__":
    main()
