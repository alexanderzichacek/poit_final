from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO

# Import Adafruit DHT library
import Adafruit_DHT

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None)
thread = None
thread_lock = Lock()

def background_thread():
    # Define DHT sensor type and pin
    sensor = Adafruit_DHT.DHT11
    pin = 21  # Adjust pin number according to your setup

    while True:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        if humidity is not None and temperature is not None:
            # If data is valid, emit it to clients
            socketio.emit('sensor_data', {'temperature': temperature, 'humidity': humidity}, namespace='/test')
        socketio.sleep(2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/numeric')
def numeric():
    return render_template('numeric.html')

@app.route('/graph')
def graph():
    return render_template('graph.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            # Start background thread to read sensor data
            thread = socketio.start_background_task(target=background_thread)

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
