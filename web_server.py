from flask import Flask, render_template, jsonify
import json
from datetime import datetime

app = Flask(__name__)

def load_json_data(filename):
    """Loads a JSON file safely."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

@app.route('/')
def block_page():
    """Renders the main block page."""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Provides the current block status to the frontend."""
    status = load_json_data('block_status.json')
    if status and status.get('blocked'):
        expires_at = datetime.fromisoformat(status['expires_at_iso'])
        remaining_seconds = max(0, (expires_at - datetime.now()).total_seconds())
        return jsonify({
            'blocked': True,
            'type': status.get('type', 'temporary'),
            'remaining_seconds': remaining_seconds
        })
    return jsonify({'blocked': False, 'remaining_seconds': 0})

@app.route('/api/data')
def get_data():
    """Provides the latest productivity data to the frontend."""
    today_str = datetime.now().strftime('%Y-%m-%d')
    analysis_filename = f"user_behaviour_{today_str}.json"
    data = load_json_data(analysis_filename)
    if data:
        return jsonify(data)
    return jsonify({'error': 'No analysis data found for today.'}), 404

if __name__ == '__main__':
    # Listens on all network interfaces on port 80 (requires sudo)
    app.run(host='0.0.0.0', port=80, debug=False)