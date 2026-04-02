from flask import Flask, jsonify
import socket
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from Flask inside Docker Container!"

@app.route('/api/info')
def info():
    return jsonify({
        "hostname": socket.gethostname(),
        "platform": os.name,
        "message": "Container is running successfully"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)