from flask import Flask, render_template, request
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Connect to the SQLite database
    conn = sqlite3.connect('f1_racing.db')

    # Load data into Pandas DataFrames
    drivers_df = pd.read_sql_query("SELECT * FROM drivers", conn)
    lap_times_df = pd.read_sql_query("SELECT * FROM lap_times", conn)
    tracks_df = pd.read_sql_query("SELECT * FROM tracks", conn)
    historical_wins_df = pd.read_sql_query("SELECT * FROM historical_wins", conn)

    # Track list for dropdown
    track_list = tracks_df['Track'].unique()

    if request.method == 'POST':
        # Get form data
        selected_track = request.form['track']
        prediction_type = request.form['prediction_type']

        # Filter data for the selected track
        track_data = tracks_df[tracks_df['Track'] == selected_track]

        # Merge with drivers and historical wins data
        data = pd.merge(track_data, drivers_df, on='DriverID')
        data = pd.merge(data, historical_wins_df, on='DriverID')

        # Prepare the features for prediction
        X = data[['Wins', 'LapTime']]
        y = np.random.randint(1, 21, size=len(X))  
        model = LinearRegression()
        model.fit(X, y)

        # Make a prediction
        data['PredictedRanking'] = model.predict(X)

        # Visualization and tabular data based on prediction type
        if prediction_type == 'team':
            data['TeamPrediction'] = data.groupby('Team')['PredictedRanking'].transform('mean')
            plt.figure(figsize=(10, 6))
            sns.barplot(x='Team', y='TeamPrediction', data=data)
            plt.title(f'Team Performance Prediction on {selected_track}')
            plt.xlabel('Team')
            plt.ylabel('Predicted Ranking')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('static/images/team_prediction.png')

            # Tabular data for teams
            team_summary = data.groupby('Team').agg({
                'Wins': 'sum',
                'TeamPrediction': 'mean'
            }).reset_index()

            return render_template('index.html', track_list=track_list, selected_track=selected_track, 
                                   prediction_type=prediction_type, team_summary=team_summary.to_dict(orient='records'))

        elif prediction_type == 'driver':
            plt.figure(figsize=(10, 6))
            sns.scatterplot(x='Wins', y='PredictedRanking', hue='DriverID', data=data)
            plt.title(f'Driver Performance Prediction on {selected_track}')
            plt.xlabel('Wins')
            plt.ylabel('Predicted Ranking')
            plt.savefig('static/images/driver_prediction.png')

            # Tabular data for drivers
            driver_summary = data[['Name', 'DriverID', 'Age', 'Wins', 'PredictedRanking']]

            return render_template('index.html', track_list=track_list, selected_track=selected_track, 
                                   prediction_type=prediction_type, driver_summary=driver_summary.to_dict(orient='records'))

    conn.close()
    return render_template('index.html', track_list=track_list)

if __name__ == '__main__':
    app.run(debug=True)
