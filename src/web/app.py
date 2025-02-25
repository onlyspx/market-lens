from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Handle all routes."""
    if path == '':
        return render_template('landing.html')
    elif path == 'hourly':
        return render_template('hourly.html')
    elif path == 'gaps':
        return render_template('gaps.html')
    elif path == 'events':
        return render_template('events.html')
    else:
        return render_template('landing.html')

def handler(environ, start_response):
    """WSGI handler for Vercel."""
    return app.wsgi_app(environ, start_response)
