from flask import Flask, make_response, request, current_app
from datetime import timedelta
from functools import update_wrapper
from flask_socketio import SocketIO
from flask_cors import CORS  # Import CORS
from flask_cors import CORS
from flask import jsonify


import sys
import requests

app = Flask(__name__)
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/foo', methods=['GET','POST','OPTIONS'])
@crossdomain(origin="*")
def foo():
    return request.json['inputVar']
socketio = SocketIO(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

url = ""

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
