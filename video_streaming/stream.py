from flask import Flask, Response, render_template, request
from flask_socketio import SocketIO
from flask_cors import CORS, cross_origin  # Import CORS
from flask_cors import CORS
from flask import jsonify


import sys
import requests

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy   dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/*": {"origins": "http://localhost:port"}})

@app.route('/foo', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def foo():
    return request.json['inputVar']

app.config['CORS_HEADERS'] = 'Content-Type'

url = ""

def add_headers_to_fontawesome_static_files(response):
    """
    Fix for font-awesome files: after Flask static send_file() does its
    thing, but before the response is sent, add an
    Access-Control-Allow-Origin: *
    HTTP header to the response (otherwise browsers complain).
    """

    if (request.path):
        response.headers.add('Access-Control-Allow-Origin', '*')

    return response

if app.debug:
    app.after_request(add_headers_to_fontawesome_static_files)

@app.route('/')
def index():
    return render_template('index.html', url=url)
@app.route('/')
def example():
    response = jsonify({'message': 'Hello, CORS!'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

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
