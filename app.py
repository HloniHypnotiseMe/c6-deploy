from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'C6 is alive'

@app.route('/control')
def control():
    return open('dashboard/jarvis_dashboard.html').read()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
