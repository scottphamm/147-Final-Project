from flask import Flask, render_template, request, jsonify
import sqlite3


# Connect to SQLite database
def init_db():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            soil_moisture INTEGER,
            temperature REAL,
            light_level INTEGER,
            humidity REAL
        )
    ''')
    conn.commit()
    conn.close()

def populate_db_with_test_data():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (soil_moisture, temperature, light_level, humidity)
        VALUES (50, 25.5, 100, 50.5)
    ''')
    conn.commit()
    conn.close()

def clean_db():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM sensor_data
    ''')
    conn.commit()
    conn.close()


app = Flask(__name__)

@app.route('/')
def index():
    data = str(request.args.get("var"))
    return render_template('index.html', content = data)

@app.route('/get-data', methods=['GET'])
def get_data():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

if __name__ == '__main__':
    #init_db()
    # populate_db_with_test_data()
    #clean_db_and_delete_db()
    app.run(host='0.0.0.0', port=8080)