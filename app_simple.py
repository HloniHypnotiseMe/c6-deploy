from flask import Flask, jsonify, send_file
import json
from pathlib import Path

app = Flask(__name__)

# Load deals data
DEALS_FILE = Path('deals.json')
if not DEALS_FILE.exists():
    with open(DEALS_FILE, 'w') as f:
        json.dump([{"id": "1", "partner": "Vantage AI", "value": "R250k", "stage": "negotiation"}], f)

@app.route('/')
def home():
    return 'C6 Control Room API is running'

@app.route('/api/status')
def status():
    with open(DEALS_FILE, 'r') as f:
        deals = json.load(f)
    return jsonify({
        'cycles': 0,
        'last_trend': 'AI automation',
        'ceo_running': False,
        'deals_count': len(deals),
        'trends': ['AI automation', 'faceless YouTube', 'crypto recovery']
    })

@app.route('/control')
def control():
    return send_file('dashboard/jarvis_dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
