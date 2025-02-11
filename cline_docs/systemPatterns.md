# System Patterns

## Architecture
- Modular Python script design
- Configuration-driven approach
- File-based data storage
- Automated and manual execution modes

## Key Technical Decisions
1. Data Fetching
   - Direct NASDAQ API integration
   - HTTP requests with proper headers
   - Fallback to sample data on failure
   - Rate limiting between requests

2. Data Storage
   - CSV format for accessibility
   - One file per ticker
   - Historical data directory structure
   - Daily data appending

3. Error Handling
   - Network failure recovery
   - Invalid ticker handling
   - Missing data fallback
   - File system error handling

4. Automation
   - GitHub Actions for scheduling
   - Daily execution at market close
   - Automated commits for data updates
   - Status reporting

## Design Patterns
- Singleton DataFetcher class
- Configuration management
- Factory pattern for data storage
- Strategy pattern for data sources (API vs fallback)
