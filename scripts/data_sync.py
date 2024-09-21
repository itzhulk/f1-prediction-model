import os
import sqlite3
import pandas as pd
import random

# CSV File paths
DATA_DIR = os.path.join(os.getcwd(), 'data')
TRACKS_CSV = os.path.join(DATA_DIR, 'tracks.csv')
DRIVERS_CSV = os.path.join(DATA_DIR, 'drivers.csv')
HISTORY_CSV = os.path.join(DATA_DIR, 'history.csv')

# SQLite Database path
DB_PATH = os.path.join(os.getcwd(), 'f1_racing.db')

# Real-world data for tracks and teams
REAL_TRACKS = [
    ("Monza", "Italy"), ("Silverstone", "UK"), ("Spa-Francorchamps", "Belgium"),
    ("Suzuka", "Japan"), ("Monaco", "Monaco"), ("Circuit de Catalunya", "Spain"),
    ("Hungaroring", "Hungary"), ("Interlagos", "Brazil"), ("Bahrain International Circuit", "Bahrain"),
    ("Yas Marina", "UAE"), ("Red Bull Ring", "Austria"), ("Zandvoort", "Netherlands"),
    ("Imola", "Italy"), ("Hockenheim", "Germany"), ("Marina Bay", "Singapore"),
    ("Albert Park", "Australia"), ("Circuit of the Americas", "USA"), ("Shanghai", "China"),
    ("Sochi", "Russia"), ("Sepang", "Malaysia"), ("Istanbul Park", "Turkey"), 
    ("Baku City Circuit", "Azerbaijan"), ("Las Vegas Street Circuit", "USA"), ("Miami International", "USA")
]

REAL_DRIVERS = [
    (1, "Lewis Hamilton", 38, "Mercedes"), (2, "George Russell", 25, "Mercedes"),
    (3, "Max Verstappen", 26, "Red Bull"), (4, "Sergio Perez", 34, "Red Bull"),
    (5, "Charles Leclerc", 26, "Ferrari"), (6, "Carlos Sainz", 29, "Ferrari"),
    (7, "Fernando Alonso", 42, "Aston Martin"), (8, "Lance Stroll", 25, "Aston Martin"),
    (9, "Lando Norris", 24, "McLaren"), (10, "Oscar Piastri", 23, "McLaren"),
    (11, "Esteban Ocon", 27, "Alpine"), (12, "Pierre Gasly", 28, "Alpine"),
    (13, "Valtteri Bottas", 34, "Alfa Romeo"), (14, "Zhou Guanyu", 25, "Alfa Romeo"),
    (15, "Kevin Magnussen", 31, "Haas"), (16, "Nico Hulkenberg", 36, "Haas"),
    (17, "Yuki Tsunoda", 24, "AlphaTauri"), (18, "Liam Lawson", 21, "AlphaTauri"),
    (19, "Alexander Albon", 28, "Williams"), (20, "Logan Sargeant", 23, "Williams"),
    (21, "Nyck de Vries", 28, "AlphaTauri"), (22, "Mick Schumacher", 25, "Haas")
]

# Function to generate initial data
def generate_data():
    # Tracks
    tracks_data = REAL_TRACKS
    
    # Drivers
    drivers_data = REAL_DRIVERS
    
    # History
    history_data = []
    for year in range(2014, 2025):
        for track in REAL_TRACKS:
            track_name = track[0]
            rankings = random.sample(range(1, 23), 22)  # Random ranking for 22 drivers
            # Generate ascending lap times based on ranking
            base_lap_time = random.uniform(60, 80)  # Base time for the fastest lap
            lap_times = [round(base_lap_time + (i * 0.5), 2) for i in range(22)]  # Ascending lap times
            
            for i, driver in enumerate(REAL_DRIVERS):
                driver_id, _, _, team = driver
                ranking = rankings[i]
                lap_time = lap_times[ranking - 1]  # Assign lap time based on ranking
                history_data.append((driver_id, year, track_name, team, ranking, lap_time))

    # Create DataFrames
    tracks_df = pd.DataFrame(tracks_data, columns=['Tracks', 'Location'])
    drivers_df = pd.DataFrame(drivers_data, columns=['DriverID', 'Name', 'Age', 'Team'])
    history_df = pd.DataFrame(history_data, columns=['DriverID', 'Year', 'Tracks', 'Team', 'Ranking', 'LapTime'])

    # Write to CSV
    tracks_df.to_csv(TRACKS_CSV, index=False)
    drivers_df.to_csv(DRIVERS_CSV, index=False)
    history_df.to_csv(HISTORY_CSV, index=False)

# Function to recreate the database from CSVs
def recreate_database():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tracks (
        Tracks TEXT PRIMARY KEY,
        Location TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS drivers (
        DriverID INTEGER PRIMARY KEY,
        Name TEXT,
        Age INTEGER,
        Team TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        DriverID INTEGER,
        Year INTEGER,
        Tracks TEXT,
        Team TEXT,
        Ranking INTEGER,
        LapTime REAL,
        FOREIGN KEY (DriverID) REFERENCES drivers(DriverID),
        FOREIGN KEY (Tracks) REFERENCES tracks(Tracks)
    )
    ''')

    # Load data from CSVs
    tracks_df = pd.read_csv(TRACKS_CSV)
    drivers_df = pd.read_csv(DRIVERS_CSV)
    history_df = pd.read_csv(HISTORY_CSV)

    # Insert into database
    tracks_df.to_sql('tracks', conn, if_exists='append', index=False)
    drivers_df.to_sql('drivers', conn, if_exists='append', index=False)
    history_df.to_sql('history', conn, if_exists='append', index=False)

    conn.commit()
    conn.close()

# Function to update the database and CSVs based on changes
def update_database_and_csv():
    conn = sqlite3.connect(DB_PATH)
    
    # Load CSVs
    tracks_df = pd.read_csv(TRACKS_CSV)
    drivers_df = pd.read_csv(DRIVERS_CSV)
    history_df = pd.read_csv(HISTORY_CSV)
    
    # Load database tables
    db_tracks = pd.read_sql("SELECT * FROM tracks", conn)
    db_drivers = pd.read_sql("SELECT * FROM drivers", conn)
    db_history = pd.read_sql("SELECT * FROM history", conn)

    # Check for differences between CSV and DB, update as necessary
    if not tracks_df.equals(db_tracks):
        print("Updating Tracks table...")
        tracks_df.to_sql('tracks', conn, if_exists='replace', index=False)
        db_tracks.to_csv(TRACKS_CSV, index=False)

    if not drivers_df.equals(db_drivers):
        print("Updating Drivers table...")
        drivers_df.to_sql('drivers', conn, if_exists='replace', index=False)
        db_drivers.to_csv(DRIVERS_CSV, index=False)

    if not history_df.equals(db_history):
        print("Updating History table...")
        history_df.to_sql('history', conn, if_exists='replace', index=False)
        db_history.to_csv(HISTORY_CSV, index=False)

    conn.commit()
    conn.close()

# Main function to prompt user for action
def main():
    print("F1 Racing Data Management Script")
    action = input("Do you want to (1) recreate the data or (2) update the data? Enter 1 or 2: ")

    if action == '1':
        print("Recreating data...")
        generate_data()
        recreate_database()
        print("Data recreated successfully.")
    elif action == '2':
        print("Updating data...")
        update_database_and_csv()
        print("Data updated successfully.")
    else:
        print("Invalid option. Exiting.")
        

if __name__ == '__main__':
    main()
