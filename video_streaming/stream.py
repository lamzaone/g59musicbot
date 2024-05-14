from flask import Flask, Response, render_template
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS

import sys
import requests

app = Flask(__name__)
socketio = SocketIO(app)
CORS(app)  # Add this line to enable CORS for all routes
app.config['CORS_HEADERS'] = 'Content-Type'

url = ""

@app.route('/')
def index():
    return render_template('index.html', url=url)

@socketio.on('update_video_state')
def update_video_state(data):
    socketio.emit('update_video_state', data)

@socketio.on('play_video')
def play_video():
    socketio.emit('play_video')

@socketio.on('pause_video')
def pause_video():
    socketio.emit('pause_video')

@socketio.on('seek_video')
def seek_video(data):
    socketio.emit('seek_video', data)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        url = sys.argv[2]
        print(url)
    else:
        port = 5000
    socketio.run(app, host='0.0.0.0', port=port)
