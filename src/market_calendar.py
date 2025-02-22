#!/usr/bin/env python3

import calendar
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

class MarketCalendar:
    """Handles market-significant dates including options expiration, economic events, and period endings."""
    
    def __init__(self):
        self.holidays = self._get_market_holidays()
    
    def _get_market_holidays(self) -> List[datetime]:
        """Returns major US market holidays."""
        # TODO: Implement comprehensive holiday calendar
        # This would include:
        # - New Year's Day
        # - Martin Luther King Jr. Day
        # - Presidents Day
        # - Good Friday
        # - Memorial Day
        # - Independence Day
        # - Labor Day
        # - Thanksgiving Day
        # - Christmas Day
        return []

    def is_business_day(self, date: datetime) -> bool:
        """Check if given date is a business day (weekday and not a holiday)."""
        return (date.weekday() < 5 and  # Monday = 0, Friday = 4
                date not in self.holidays)

    def get_monthly_opex(self, year: int, month: int) -> datetime:
        """Get monthly options expiration (3rd Friday of the month)."""
        c = calendar.monthcalendar(year, month)
        # Find the third Friday
        for week in c:
            friday = week[calendar.FRIDAY]
            if friday != 0:
                if c.index(week) >= 2:  # Third week or later
                    return datetime(year, month, friday)
        return None

    def get_quarterly_opex(self, year: int) -> List[datetime]:
        """Get quarterly options expiration dates (March, June, September, December)."""
        quarterly_months = [3, 6, 9, 12]
        return [self.get_monthly_opex(year, month) for month in quarterly_months]

    def get_weekly_opex(self, start_date: datetime, end_date: datetime) -> List[datetime]:
        """Get all weekly options expiration dates (Fridays) between start and end date."""
        fridays = []
        current = start_date
        while current <= end_date:
            if current.weekday() == calendar.FRIDAY:
                fridays.append(current)
            current += timedelta(days=1)
        return fridays

    def get_period_endings(self, start_date: datetime, end_date: datetime) -> Dict[str, List[datetime]]:
        """Get end of month, quarter, and year dates between start and end date."""
        # Using updated frequency aliases as per pandas deprecation warning
        dates = pd.date_range(start_date, end_date, freq='D')
        eom_dates = pd.date_range(start_date, end_date, freq='BME')  # Business Month End
        eoq_dates = pd.date_range(start_date, end_date, freq='BQE')  # Business Quarter End
        eoy_dates = pd.date_range(start_date, end_date, freq='BYE')  # Business Year End
        
        return {
            'eom': eom_dates.tolist(),
            'eoq': eoq_dates.tolist(),
            'eoy': eoy_dates.tolist()
        }

    def get_economic_events(self, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict]]:
        """Get economic events between start and end date."""
        # TODO: Implement API calls to fetch:
        # - FOMC meetings and decisions
        # - CPI releases
        # - NFP releases
        # - Other significant economic indicators
        return {
            'fomc': [],
            'cpi': [],
            'nfp': [],
            'other': []
        }

    def get_all_significant_dates(self, start_date: datetime, end_date: datetime) -> Dict[str, List]:
        """Get all significant market dates between start and end date."""
        weekly_opex = self.get_weekly_opex(start_date, end_date)
        monthly_opex = []
        current = start_date
        while current <= end_date:
            monthly = self.get_monthly_opex(current.year, current.month)
            if monthly:
                monthly_opex.append(monthly)
            current = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
        
        period_endings = self.get_period_endings(start_date, end_date)
        economic_events = self.get_economic_events(start_date, end_date)
        
        return {
            'weekly_opex': weekly_opex,
            'monthly_opex': monthly_opex,
            'quarterly_opex': [d for d in monthly_opex if d.month in [3, 6, 9, 12]],
            'eom': period_endings['eom'],
            'eoq': period_endings['eoq'],
            'eoy': period_endings['eoy'],
            'economic_events': economic_events
        }

def main():
    """Example usage of MarketCalendar."""
    calendar = MarketCalendar()
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    significant_dates = calendar.get_all_significant_dates(start_date, end_date)
    
    # Print example output
    print("\nWeekly OpEx dates (first 5):")
    for date in significant_dates['weekly_opex'][:5]:
        print(date.strftime('%Y-%m-%d'))
    
    print("\nMonthly OpEx dates (first 5):")
    for date in significant_dates['monthly_opex'][:5]:
        print(date.strftime('%Y-%m-%d'))
    
    print("\nQuarterly OpEx dates:")
    for date in significant_dates['quarterly_opex']:
        print(date.strftime('%Y-%m-%d'))

if __name__ == "__main__":
    main()