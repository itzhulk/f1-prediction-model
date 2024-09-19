import pandas as pd
import random

# Parameters
start_year = 2015
end_year = 2024
drivers_count = 30  # Should match the number of drivers in drivers.csv

def generate_historical_wins(start_year, end_year, drivers_count):
    data = []
    for year in range(start_year, end_year + 1):
        for driver_id in range(1, drivers_count + 1):
            # Randomly decide if the driver participated this year
            participated = random.choice([True, False])
            if participated:
                wins = random.randint(0, 10)  # Assuming max 10 wins per season
                data.append({
                    'DriverID': driver_id,
                    'Year': year,
                    'Wins': wins
                })
    return pd.DataFrame(data)

if __name__ == "__main__":
    historical_wins_df = generate_historical_wins(start_year, end_year, drivers_count)
    historical_wins_df.to_csv('historical_wins.csv', index=False)
    print("historical_wins.csv has been generated.")