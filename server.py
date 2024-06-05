from threading import Lock
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import Adafruit_DHT
import MySQLdb
from datetime import datetime
import csv

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=None)
thread = None
thread_lock = Lock()
sensor_enabled = False
sensor_thread = None
csv_file = None
csv_writer = None

# Define MySQL connection parameters
myhost = 'localhost'
myuser = 'zichacek'
mydb = 'zadanie'
mypasswd = 'password'

def background_thread():
    global sensor_enabled, csv_writer
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

                if csv_writer:
                    save_to_csv({'time': datetime.now(), 'temperature': temperature, 'humidity': humidity})

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

@app.route('/database')
def database():
    return render_template('database.html')

@app.route('/get_data')
def get_data():
    # Connect to MySQL database
    db = MySQLdb.connect(host=myhost, user=myuser, passwd=mypasswd, db=mydb)
    
    # Fetch last 50 rows from sensor_data table
    cursor = db.cursor()
    cursor.execute("SELECT * FROM sensor_data ORDER BY time DESC LIMIT 50")
    rows = cursor.fetchall()
    cursor.close()
    db.close()

    # Return the rows as JSON
    data = [{'id': row[0], 'time': row[1], 'temperature': row[2], 'humidity': row[3]} for row in rows]
    return jsonify(data)

def save_to_csv(data):
    global csv_writer
    if csv_writer:
        csv_writer.writerow(data)

@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            # Start background thread to read sensor data
            thread = socketio.start_background_task(target=background_thread)

@socketio.on('start_sensor', namespace='/test')
def start_sensor():
    global sensor_enabled, sensor_thread, csv_file, csv_writer
    if not sensor_enabled:
        sensor_enabled = True
        sensor_thread = socketio.start_background_task(target=background_thread)
        current_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        csv_file = f'sensor_data_{current_datetime}.csv'
        csvfile = open(csv_file, 'a', newline='')
        fieldnames = ['time', 'temperature', 'humidity']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()

@socketio.on('stop_sensor', namespace='/test')
def stop_sensor():
    global sensor_enabled, sensor_thread, csv_writer
    sensor_enabled = False
    sensor_thread = None
    if csv_writer:
        csv_writer = None

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
