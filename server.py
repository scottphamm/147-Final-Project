from flask import Flask, render_template, request, jsonify
import sqlite3
import matplotlib.pyplot as plt
import random
import time
import plotly.graph_objects as go


# connect to sql
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

# def populate_db_with_test_data():
#     conn = sqlite3.connect('plant_data.db')
#     cursor = conn.cursor()

#     for _ in range(10):
#         soil_moisture = random.randint(200, 250)
#         temperature = random.uniform(20, 30)
#         light_level = random.randint(0, 100)
#         humidity = random.uniform(40, 60)
#         cursor.execute('''
#             INSERT INTO sensor_data (soil_moisture, temperature, light_level, humidity)
#             VALUES (?, ?, ?, ?)
#         ''', (soil_moisture, temperature, light_level, humidity))

#         time.sleep(10)


#     conn.commit()
#     conn.close()

def clean_db():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM sensor_data
    ''')
    conn.commit()
    conn.close()



def create_interactive_plot():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()

    timestamps = []
    soil_moisture = []
    temperature = []
    light_level = []
    humidity = []

    for row in rows:

        timestamps.append(row[1]) 
        soil_moisture.append(row[2])
        temperature.append(row[3])
        light_level.append(row[4])
        humidity.append(row[5])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=soil_moisture, mode='lines+markers', name='Soil Moisture (%)'))
    fig.add_trace(go.Scatter(x=timestamps, y=temperature, mode='lines+markers', name='Temperature (°C)'))
    fig.add_trace(go.Scatter(x=timestamps, y=light_level, mode='lines+markers', name='Light Level (lux)'))
    fig.add_trace(go.Scatter(x=timestamps, y=humidity, mode='lines+markers', name='Humidity (%)'))

    fig.update_layout(
        title='Plant Monitoring Metrics Over Time',
        xaxis_title='Timestamp',
        yaxis_title='Measurement',
        xaxis=dict(
            tickmode='auto',
            nticks=20, 
            showgrid=True,
            tickangle=45 
        ),
        yaxis=dict(
            showgrid=True
        ),
        legend=dict(
            x=0.01,
            y=0.99
        ),
        hovermode='closest'
    )

    graph_html = fig.to_html(full_html=False)

    return graph_html



def create_static_plot():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data')
    rows = cursor.fetchall()
    conn.close()

    timestamps = [] 
    soil_moisture = []
    temperature = []
    light_level = []
    humidity = []

    for row in rows:
        timestamps.append(row[0]) 
        soil_moisture.append(row[1])
        temperature.append(row[2])
        light_level.append(row[3])
        humidity.append(row[4])

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, soil_moisture, label='Soil Moisture (%)', marker='o')
    plt.plot(timestamps, temperature, label='Temperature (°C)', marker='s')
    plt.plot(timestamps, light_level, label='Light Level (lux)', marker='^')
    plt.plot(timestamps, humidity, label='Humidity (%)', marker='d')

    plt.xlabel('Timestamp')
    plt.ylabel('Measurement')
    plt.title('Plant Monitoring Metrics Over Time')

    plt.legend(loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.savefig('static/images/plot.png')
    plt.close()


app = Flask(__name__)

@app.route('/')
def index():
    data = str(request.args.get("var"))
    html_plot = create_interactive_plot()
    return render_template('index.html', content=data, graph_content=html_plot)

@app.route('/get-data', methods=['GET'])
def get_data():
    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    return jsonify(rows)

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    data = request.get_json()

    soil_moisture = data.get('soil_moisture')
    temperature = data.get('temperature')
    light_level = data.get('light_level')
    humidity = data.get('humidity')

    conn = sqlite3.connect('plant_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sensor_data (soil_moisture, temperature, light_level, humidity)
        VALUES (?, ?, ?, ?)
    ''', (soil_moisture, temperature, light_level, humidity))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Data received and saved successfully'}), 200


if __name__ == '__main__':
    #init_db()
    # populate_db_with_test_data()
    # clean_db()
    app.run(host='0.0.0.0', port=8080)
    # create_static_plot()
    # create_interactive_plot()