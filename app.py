import os
import sqlite3
import pandas as pd
from flask import Flask, render_template, request
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

# Paths for CSVs and database
DATA_DIR = os.path.join(os.getcwd(), 'data')
DB_PATH = os.path.join(os.getcwd(), 'f1_racing.db')

# Function to fetch drivers and tracks from the database
def get_drivers_and_tracks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get drivers
    cursor.execute("SELECT DriverID, Name FROM drivers")
    drivers = cursor.fetchall()

    # Get tracks
    cursor.execute("SELECT Tracks FROM tracks")
    tracks = cursor.fetchall()

    conn.close()
    return drivers, tracks

# Function to get driver history on a selected track
def get_driver_performance(driver_id, track_name):
    conn = sqlite3.connect(DB_PATH)
    query = '''SELECT Year, Ranking, LapTime FROM history
               WHERE DriverID = ? AND Tracks = ? ORDER BY Year ASC'''
    data = pd.read_sql_query(query, conn, params=(driver_id, track_name))
    conn.close()
    return data

# Function to train model and predict
def predict_driver_performance(driver_id, track_name):
    # Get data from history
    data = get_driver_performance(driver_id, track_name)

    if data.empty:
        return None, None

    # Prepare data for prediction
    X = data['Year'].values.reshape(-1, 1)
    y_rank = data['Ranking'].values
    y_lap = data['LapTime'].values

    # Train ranking model
    rank_model = LinearRegression().fit(X, y_rank)

    # Train lap time model
    lap_model = LinearRegression().fit(X, y_lap)

    # Predict ranking and lap time for 2025
    year_2025 = np.array([[2025]])
    predicted_rank = rank_model.predict(year_2025)[0]
    predicted_lap = lap_model.predict(year_2025)[0]

    return predicted_rank, predicted_lap

# Route for homepage and predictions
@app.route('/', methods=['GET', 'POST'])
def index():
    drivers, tracks = get_drivers_and_tracks()
    selected_track = None
    selected_driver = None
    prediction_result = None
    driver_history = None

    if request.method == 'POST':
        selected_driver = int(request.form['driver'])
        selected_track = request.form['track']
        driver_history = get_driver_performance(selected_driver, selected_track)

        # Generate performance prediction
        predicted_rank, predicted_lap = predict_driver_performance(selected_driver, selected_track)
        prediction_result = {
            'predicted_rank': predicted_rank,
            'predicted_lap': predicted_lap
        }

        # Generate visualizations
        if not driver_history.empty:
            years = driver_history['Year']
            rankings = driver_history['Ranking']
            lap_times = driver_history['LapTime']

            plt.figure(figsize=(10, 5))

            # Plot rankings
            plt.subplot(1, 2, 1)
            plt.plot(years, rankings, marker='o', color='b')
            plt.gca().invert_yaxis()  # Invert y-axis to have rank 1 at the top
            plt.title(f'Ranking Trend for Driver {selected_driver} on {selected_track}')
            plt.xlabel('Year')
            plt.ylabel('Ranking')
            plt.grid(True)

            # Plot lap times
            plt.subplot(1, 2, 2)
            plt.plot(years, lap_times, marker='o', color='r')
            plt.title(f'Lap Time Trend for Driver {selected_driver} on {selected_track}')
            plt.xlabel('Year')
            plt.ylabel('Lap Time (seconds)')
            plt.grid(True)

            plt.tight_layout()
            plt.savefig(os.path.join('static', 'images', 'performance_visualization.png'))
            plt.close()

    return render_template('index.html', drivers=drivers, tracks=tracks, selected_track=selected_track,
                           selected_driver=selected_driver, prediction_result=prediction_result,
                           driver_history=driver_history)

if __name__ == '__main__':
    app.run(debug=True)
