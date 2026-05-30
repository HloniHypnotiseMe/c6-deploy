from flask import Flask, jsonify, send_from_directory, request, Response
import json
import os
from pathlib import Path
from functools import wraps
import hashlib

app = Flask(__name__, static_folder='.', template_folder='.')

AGENT_OS_PATH = Path('/app')
MEMORY_FILE = AGENT_OS_PATH / 'memory_local.json'
DEALS_FILE = AGENT_OS_PATH / 'deals.json'

USERNAME = "admin"
PASSWORD = "C6Control2026"
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode()).hexdigest()

def check_auth(username, password):
    return username == USERNAME and hashlib.sha256(password.encode()).hexdigest() == PASSWORD_HASH

def authenticate():
    return Response(
        'Authentication required', 401,
        {'WWW-Authenticate': 'Basic realm="C6 Control Room"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

if not DEALS_FILE.exists():
    with open(DEALS_FILE, 'w') as f:
        json.dump([
            {"id": "1", "partner": "Vantage AI", "value": "R250k", "stage": "negotiation"},
            {"id": "2", "partner": "DataCore", "value": "R120k", "stage": "lead"},
            {"id": "3", "partner": "HealthTech SA", "value": "R1.2M", "stage": "proposal"}
        ], f, indent=2)

@app.route('/')
@requires_auth
def index():
    return send_from_directory('.', 'jarvis_dashboard.html')

@app.route('/api/status')
@requires_auth
def status():
    memory = {}
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, 'r') as f:
                memory = json.load(f)
        except:
            pass
    decisions = memory.get('decisions', [])
    with open(DEALS_FILE, 'r') as f:
        deals = json.load(f)
    return jsonify({
        'cycles': memory.get('cycles', 0),
        'last_trend': decisions[0].get('topic') if decisions else None,
        'ceo_running': False,
        'deals_count': len(deals),
        'trends': ['AI automation', 'faceless YouTube', 'crypto recovery', 'AI businesses', 'passive income AI']
    })

@app.route('/api/deals', methods=['GET'])
@requires_auth
def get_deals():
    with open(DEALS_FILE, 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/deals/add', methods=['POST'])
@requires_auth
def add_deal():
    data = request.json
    with open(DEALS_FILE, 'r') as f:
        deals = json.load(f)
    new_id = str(max([int(d.get('id', 0)) for d in deals]) + 1) if deals else '1'
    deals.append({'id': new_id, 'partner': data['partner'], 'value': data['value'], 'stage': data['stage']})
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)
    return jsonify({'status': 'ok'})

@app.route('/api/deals/delete', methods=['POST'])
@requires_auth
def delete_deal():
    data = request.json
    with open(DEALS_FILE, 'r') as f:
        deals = json.load(f)
    deals = [d for d in deals if d['id'] != data['id']]
    with open(DEALS_FILE, 'w') as f:
        json.dump(deals, f, indent=2)
    return jsonify({'status': 'ok'})

@app.route('/api/command', methods=['POST'])
@requires_auth
def command():
    data = request.json
    cmd = data.get('command', '').lower()
    assistant = data.get('assistant', 'general')
    
    if 'trends' in cmd:
        return jsonify({'reply': 'Top trends: AI automation, faceless YouTube, crypto recovery, AI businesses, passive income AI'})
    elif 'deals' in cmd:
        with open(DEALS_FILE, 'r') as f:
            deals = json.load(f)
        if deals:
            reply = 'Active deals:\n' + '\n'.join([f"- {d['partner']} ({d['value']}) - {d['stage']}" for d in deals])
            return jsonify({'reply': reply})
        return jsonify({'reply': 'No active deals yet.'})
    else:
        return jsonify({'reply': f"Command: '{cmd}'. Try 'trends', 'deals', 'help'."})

application = app
