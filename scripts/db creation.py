import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect('f1_racing.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE drivers (
    DriverID INTEGER PRIMARY KEY,
    Name TEXT,
    Team TEXT,
    Nationality TEXT,
    Age INTEGER
)
''')

cursor.execute('''
CREATE TABLE historical_wins (
    DriverID INTEGER,
    Year INTEGER,
    Wins INTEGER,
    FOREIGN KEY (DriverID) REFERENCES drivers(DriverID)
)
''')

cursor.execute('''
CREATE TABLE lap_times (
    DriverID INTEGER,
    Track TEXT,
    LapTime REAL,
    FOREIGN KEY (DriverID) REFERENCES drivers(DriverID)
)
''')

cursor.execute('''
CREATE TABLE tracks (
    Track TEXT PRIMARY KEY,
    Location TEXT,
    Length REAL,
    Turns INTEGER
)
''')

# Load CSV data into the database
drivers_df = pd.read_csv('drivers.csv')
historical_wins_df = pd.read_csv('historical_wins.csv')
lap_times_df = pd.read_csv('lap_times.csv')
tracks_df = pd.read_csv('tracks.csv')

drivers_df.to_sql('drivers', conn, if_exists='append', index=False)
historical_wins_df.to_sql('historical_wins', conn, if_exists='append', index=False)
lap_times_df.to_sql('lap_times', conn, if_exists='append', index=False)
tracks_df.to_sql('tracks', conn, if_exists='append', index=False)

# Commit changes and close the connection
conn.commit()
conn.close()
