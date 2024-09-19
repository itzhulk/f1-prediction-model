from flask import Flask, render_template
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

@app.route('/train')
def train_model():
    # Connect to the database
    conn = sqlite3.connect('f1_racing.db')

    # Load data into Pandas DataFrames
    drivers_df = pd.read_sql_query("SELECT * FROM drivers", conn)
    wins_df = pd.read_sql_query("SELECT * FROM historical_wins", conn)
    lap_times_df = pd.read_sql_query("SELECT * FROM lap_times", conn)

    # Merge DataFrames for the prediction model
    data = pd.merge(wins_df, lap_times_df, on='DriverID')
    data = pd.merge(data, drivers_df[['DriverID', 'Age']], on='DriverID')

    # Prepare data for training
    X = data[['Wins', 'LapTime', 'Age']]
    y = np.random.randint(1, 21, size=len(X))  # Random ranking as placeholder

    # Train the model
    model = LinearRegression()
    model.fit(X, y)

    # Make a prediction
    predictions = model.predict(X)
    data['PredictedRanking'] = predictions

    # Print or return the predictions
    print(data[['DriverID', 'Wins', 'LapTime', 'Age', 'PredictedRanking']])

    conn.close()
    return "Model trained and predictions made!"

if __name__ == '__main__':
    app.run(debug=True)
