import pandas as pd
from faker import Faker
import random

# Initialize Faker
fake = Faker()

# Define teams and nationalities
teams = [
    'Mercedes', 'Red Bull', 'Ferrari', 'McLaren', 'Alpine',
    'Aston Martin', 'AlphaTauri', 'Williams', 'Alfa Romeo', 'Haas'
]
nationalities = [
    'British', 'Dutch', 'German', 'French', 'Spanish',
    'Australian', 'Canadian', 'Finnish', 'Italian', 'Brazilian'
]

# Generate driver data
def generate_drivers(num_drivers=30):
    data = []
    for driver_id in range(1, num_drivers + 1):
        name = fake.name()
        team = random.choice(teams)
        nationality = random.choice(nationalities)
        age = random.randint(20, 40)
        data.append({
            'DriverID': driver_id,
            'Name': name,
            'Team': team,
            'Nationality': nationality,
            'Age': age
        })
    return pd.DataFrame(data)

if __name__ == "__main__":
    drivers_df = generate_drivers(30)
    drivers_df.to_csv('drivers.csv', index=False)
    print("drivers.csv has been generated with 30 drivers.")
