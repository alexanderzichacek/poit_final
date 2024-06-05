from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO

# Import Adafruit DHT library
import Adafruit_DHT
import MySQLdb
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None)
thread = None
thread_lock = Lock()
sensor_enabled = False
sensor_thread = None

# Define MySQL connection parameters
myhost = 'localhost'
myuser = 'root'
mydb = 'zadanie'
mypasswd = ''

def background_thread():
    global sensor_enabled
    # Define DHT sensor type and pin
    sensor = Adafruit_DHT.DHT11
    pin = 21  # Adjust pin number according to your setup
    
    # Connect to MySQL database
    db = MySQLdb.connect(host=myhost, user=myuser, passwd=mypasswd, db=mydb)
    
    while True:
        if sensor_enabled:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
            if humidity is not None and temperature is not None:
                # If data is valid, emit it to clients
                socketio.emit('sensor_data', {'temperature': temperature, 'humidity': humidity}, namespace='/test')
                
                # Insert data into MySQL database
                cursor = db.cursor()
                cursor.execute("INSERT INTO sensor_data (time, temperature, humidity) VALUES (%s, %s, %s)", 
                               (datetime.now(), temperature, humidity))
                db.commit()
                cursor.close()
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

@app.route('/gauge')
def gauge():
    return render_template('gauge.html')

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            # Start background thread to read sensor data
            thread = socketio.start_background_task(target=background_thread)

@socketio.on('start_sensor', namespace='/test')
def start_sensor():
    global sensor_enabled, sensor_thread
    if not sensor_enabled:
        sensor_enabled = True
        sensor_thread = socketio.start_background_task(target=background_thread)

@socketio.on('stop_sensor', namespace='/test')
def stop_sensor():
    global sensor_enabled, sensor_thread
    sensor_enabled = False
    sensor_thread = None

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
