# Market Lens

A tool for analyzing market data patterns and trends, with a focus on SPX hourly analysis.

## Features

- SPX first hour range analysis
- VIX correlation insights
- Day of week patterns
- Interactive visualizations
- Static site deployment

## Project Structure

```
market-lens/
├── src/
│   └── hourly_analysis/
│       ├── build.py           # Static site generator
│       ├── hourly_range_analyzer.py
│       └── templates/
│           └── index.html     # Static site template
├── build/                     # Generated static site
├── docs/                      # Documentation
└── vercel.json               # Vercel configuration
```

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/market-lens.git
cd market-lens
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Generate static site:
```bash
cd src/hourly_analysis
python build.py
```

4. The static site will be generated in the `build` directory. You can serve it locally using Python's built-in server:
```bash
cd ../../build
python -m http.server 8000
```

5. Open http://localhost:8000 in your browser

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Login to Vercel:
```bash
vercel login
```

3. Deploy:
```bash
vercel
```

The site will be automatically built and deployed according to the configuration in `vercel.json`.

### Manual Updates

To manually update the analysis:

1. Run the build script:
```bash
cd src/hourly_analysis
python build.py
```

2. Commit and push the changes:
```bash
git add build/
git commit -m "Update analysis data"
git push
```

Vercel will automatically deploy the updated site.

## Documentation

For more detailed documentation, see the [docs](./docs) directory:

- [Implementation Plan](./docs/implementation_plan.md)
- [Development Guide](./docs/development.md)
- [Deployment Guide](./docs/deployment.md)
- [Architecture Overview](./docs/architecture.md)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
