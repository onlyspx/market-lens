from flask import Flask, render_template

app = Flask(__name__, 
    static_url_path='', 
    static_folder='static',
    template_folder='templates'
)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Handle all routes."""
    try:
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
    except Exception as e:
        return str(e), 500

app = app.wsgi_app
