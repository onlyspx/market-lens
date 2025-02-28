
from flask import Flask, render_template, send_from_directory
import os

import sys

# Get absolute paths
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
template_dir = os.path.join(root_dir, 'src', 'web', 'templates')
static_dir = os.path.join(root_dir, 'src', 'web', 'static')

app = Flask(__name__, 
    static_url_path='',
    static_folder=static_dir,
    template_folder=template_dir
)

print(f"Root directory: {root_dir}")
print(f"Template directory: {template_dir}")
print(f"Template files: {os.listdir(template_dir)}")

@app.route('/')
def landing():
    """Render landing page."""
    return render_template('landing.html')

@app.route('/first-hour')
def first_hour():
    """Redirect to static first hour analysis page."""
    try:
        first_hour_dir = os.path.join(root_dir, 'public', 'first-hour')
        return send_from_directory(first_hour_dir, 'index.html')
    except Exception as e:
        print(f"Error serving first hour analysis: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/first-hour/<path:path>')
def first_hour_static(path):
    """Serve static files for first hour analysis."""
    try:
        first_hour_dir = os.path.join(root_dir, 'public', 'first-hour')
        return send_from_directory(first_hour_dir, path)
    except Exception as e:
        print(f"Error serving {path}: {str(e)}")
        return f"Error: {str(e)}", 404

@app.route('/intraday')
def intraday():
    """Redirect to static intraday table page."""
    try:
        intraday_dir = os.path.join(root_dir, 'public', 'intraday')
        return send_from_directory(intraday_dir, 'index.html')
    except Exception as e:
        print(f"Error serving intraday table: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/intraday/<path:path>')
def intraday_static(path):
    """Serve static files for intraday table."""
    try:
        intraday_dir = os.path.join(root_dir, 'public', 'intraday')
        return send_from_directory(intraday_dir, path)
    except Exception as e:
        print(f"Error serving {path}: {str(e)}")
        return f"Error: {str(e)}", 404
        
# Keep the old hourly route for backward compatibility
@app.route('/hourly')
def hourly():
    """Redirect to first hour analysis page."""
    return first_hour()

@app.route('/hourly/<path:path>')
def hourly_static(path):
    """Redirect to first hour static files."""
    return first_hour_static(path)

@app.route('/gaps')
def gaps():
    """Render gap analysis page."""
    try:
        print("Loading gaps.html from:", os.path.join(template_dir, 'gaps.html'))
        return render_template('gaps.html')
    except Exception as e:
        print(f"Error loading gaps.html: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/events')
def events():
    """Render market events page."""
    try:
        print("Loading events.html from:", os.path.join(template_dir, 'events.html'))
        return render_template('events.html')
    except Exception as e:
        print(f"Error loading events.html: {str(e)}")
        return f"Error: {str(e)}", 500

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('landing.html'), 404

# For Vercel deployment
app.wsgi_app = app.wsgi_app

if __name__ == '__main__':
    app.run(debug=True, port=5004)  # Use a different port
