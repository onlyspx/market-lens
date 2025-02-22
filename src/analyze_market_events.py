#!/usr/bin/env python3

import pandas as pd
from market_calendar import MarketCalendar
from data_enricher import DataEnricher
import plotly.graph_objects as go
from datetime import datetime, timedelta

def create_event_visualization(df: pd.DataFrame, title: str = "SPX with Market Events"):
    """Create an interactive visualization of price data with market events."""
    fig = go.Figure()

    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='SPX'
    ))

    # Add markers for different events
    events = {
        'Monthly OpEx': ('is_monthly_opex', 'red'),
        'Quarterly OpEx': ('is_quarterly_opex', 'purple'),
        'End of Month': ('is_eom', 'blue'),
        'End of Quarter': ('is_eoq', 'green'),
    }

    for event_name, (event_col, color) in events.items():
        event_dates = df[df[event_col]].index
        if len(event_dates) > 0:
            fig.add_trace(go.Scatter(
                x=event_dates,
                y=df.loc[event_dates, 'high'],
                mode='markers',
                marker=dict(
                    symbol='triangle-down',
                    size=12,
                    color=color,
                ),
                name=event_name
            ))

    # Update layout
    fig.update_layout(
        title=title,
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark'
    )

    return fig

def analyze_market_events():
    """Analyze and visualize SPX data with market events."""
    # Initialize our classes
    enricher = DataEnricher()
    
    # Load and enrich SPX data
    print("Loading and enriching SPX data...")
    df = enricher.load_price_data('data/historical/SPX.csv')
    enriched_df = enricher.add_market_events(df)
    
    # Generate analysis report
    print("\nGenerating market event analysis report...")
    report = enricher.generate_event_report(enriched_df)
    
    # Print report
    print("\nMarket Event Analysis Report:")
    for event_type, metrics in report.items():
        print(f"\n{event_type.upper()}:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
    
    # Create visualization
    print("\nCreating visualization...")
    fig = create_event_visualization(enriched_df)
    
    # Save the visualization
    output_path = 'data/analysis/market_events/SPX_market_events.html'
    print(f"\nSaving visualization to {output_path}")
    
    # Ensure directory exists
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig.write_html(output_path)
    
    # Save enriched data
    csv_output = 'data/analysis/market_events/SPX_enriched.csv'
    enriched_df.to_csv(csv_output)
    print(f"Saved enriched data to {csv_output}")
    
    return output_path

def main():
    """Main execution function."""
    try:
        output_path = analyze_market_events()
        print(f"\nAnalysis complete! Open {output_path} to view the visualization.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    main()