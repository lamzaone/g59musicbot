from flask import Flask, render_template
from flask_socketio import SocketIO
import sys


app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

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
    else:
        port = 5000
    socketio.run(app, host='0.0.0.0', port=port)
