# Deployment Guide

This guide covers the deployment process for the Market Lens hourly analysis static site.

## Vercel Deployment

### Prerequisites

1. Node.js and npm installed
2. Vercel CLI installed (`npm install -g vercel`)
3. A Vercel account
4. Python 3.x installed

### Initial Setup

1. Login to Vercel:
```bash
vercel login
```

2. Link your repository:
```bash
vercel link
```

### Configuration

The project includes a `vercel.json` configuration file that handles:
- Build command execution
- Output directory specification
- Static file serving
- Route configuration

```json
{
  "version": 2,
  "buildCommand": "cd src/hourly_analysis && python3 build.py",
  "outputDirectory": "build",
  "builds": [
    {
      "src": "build/**",
      "use": "@vercel/static"
    }
  ]
}
```

### Deployment Process

1. **Local Testing**
   ```bash
   # Generate static site
   cd src/hourly_analysis
   python build.py
   
   # Test locally
   cd ../../build
   python -m http.server 8000
   ```

2. **Deploy to Vercel**
   ```bash
   vercel
   ```

3. **Production Deployment**
   ```bash
   vercel --prod
   ```

### Environment Variables

If needed, set up environment variables in Vercel:

1. Go to your project settings in Vercel dashboard
2. Navigate to "Environment Variables"
3. Add any required variables (e.g., API keys)

### Automatic Deployments

Vercel automatically deploys:
- When you push to the main branch
- When you create a pull request (preview deployment)

### Manual Updates

To manually update the analysis:

1. Run the build script:
```bash
cd src/hourly_analysis
python build.py
```

2. Commit and push changes:
```bash
git add build/
git commit -m "Update analysis data"
git push
```

## Future: GitHub Pages Deployment

### Setup Process

1. Create a `gh-pages` branch:
```bash
git checkout -b gh-pages
```

2. Configure GitHub Pages:
- Go to repository settings
- Navigate to "Pages"
- Select `gh-pages` branch and `/docs` folder
- Save configuration

3. Update build script to output to docs/:
```bash
# Modify build.py to use docs/ instead of build/
self.build_dir = Path("docs")
```

4. Deploy to GitHub Pages:
```bash
# Generate site
python src/hourly_analysis/build.py

# Commit and push to gh-pages branch
git add docs/
git commit -m "Update site"
git push origin gh-pages
```

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Python dependencies are installed
   - Verify build command path is correct
   - Check environment variables are set

2. **Static Asset Issues**
   - Verify file paths in HTML are correct
   - Check asset files are included in build
   - Confirm MIME types are correct

3. **Data Updates**
   - Verify build script can fetch data
   - Check JSON file generation
   - Validate data format

### Getting Help

1. Check the [Vercel documentation](https://vercel.com/docs)
2. Review project issues on GitHub
3. Contact the development team

## Maintenance

### Regular Tasks

1. Monitor build logs
2. Update dependencies
3. Verify data freshness
4. Check site performance

### Security

1. Keep dependencies updated
2. Review access controls
3. Monitor for unusual activity
4. Regularly update credentials
