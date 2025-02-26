
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

@app.route('/hourly')
def hourly():
    """Redirect to static hourly analysis page."""
    try:
        hourly_dir = os.path.join(root_dir, 'src', 'hourly_analysis', 'build')
        return send_from_directory(hourly_dir, 'index.html')
    except Exception as e:
        print(f"Error serving hourly analysis: {str(e)}")
        return f"Error: {str(e)}", 500

@app.route('/hourly/<path:path>')
def hourly_static(path):
    """Serve static files for hourly analysis."""
    try:
        hourly_dir = os.path.join(root_dir, 'src', 'hourly_analysis', 'build')
        return send_from_directory(hourly_dir, path)
    except Exception as e:
        print(f"Error serving {path}: {str(e)}")
        return f"Error: {str(e)}", 404

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
    app.run(debug=True, port=5003)  # Use a different port
