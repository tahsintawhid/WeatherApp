import matplotlib
matplotlib.use('Agg')  # Set the backend to 'Agg'

import requests
import sqlite3
import pandas as pd
import numpy as np
import base64
import io
import matplotlib.pyplot as plt

# Function to create the weather table in the database
def create_weather_table(db_filename):
    conn = sqlite3.connect(db_filename)
    cursor = conn.cursor()
    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY,
        city TEXT,
        temperature REAL,
        humidity REAL,
        precipitation REAL
    )
    """
    
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

# Retrieve weather data from the OpenWeatherMap API with error handling
def retrieve_weather_data(api_key, city_name, units):
    base_url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "units": units,
        "appid": api_key
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception if the request isn't successful
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving weather data: {e}")
        return None

# Insert weather data into the database
def insert_weather_data(conn, city_name, temperature, humidity):
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO weather (city, temperature, humidity, precipitation)
    VALUES (?, ?, ?, ?)
    """
    data_to_insert = (city_name, temperature, humidity, 0.0)
    cursor.execute(insert_query, data_to_insert)
    conn.commit()

# Retrieve and store weather data
def retrieve_and_store_weather(api_key, city_name, units, db_filename):
    weather_data = retrieve_weather_data(api_key, city_name, units)
    temperature = weather_data.get('main', {}).get('temp')
    humidity = weather_data.get('main', {}).get('humidity')

    conn = sqlite3.connect(db_filename)
    insert_weather_data(conn, city_name, temperature, humidity)
    conn.close()

# Fetch weather data from the database and return a DataFrame
def fetch_weather_data_as_dataframe(db_filename):
    conn = sqlite3.connect(db_filename)
    query = "SELECT * FROM weather"
    weather_df = pd.read_sql_query(query, conn)
    conn.close()
    return weather_df

# Clean weather data
def clean_weather_data(weather_df):
    # Drop rows with missing values
    weather_df.dropna(inplace=True)

    # Remove duplicates
    weather_df.drop_duplicates(inplace=True)

    return weather_df

# Function to generate histogram
def generate_histogram(cleaned_weather_df):
    plt.figure(figsize=(8, 6))
    plt.hist(cleaned_weather_df['temperature'], bins=20, color='blue', alpha=0.7)
    plt.xlabel('Temperature (°F)')
    plt.ylabel('Frequency')
    plt.title('Cleaned Temperature Distribution')

    # Save the plot to a BytesIO object
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png')
    img_stream.seek(0)
    img_base64 = base64.b64encode(img_stream.read()).decode('utf-8')
    plt.close()

    return img_base64

# Function to process data
def process_data(api_key, city_name, units, db_filename):
    create_weather_table(db_filename)
    retrieve_and_store_weather(api_key, city_name, units, db_filename)
    weather_df = fetch_weather_data_as_dataframe(db_filename)
    cleaned_weather_df = clean_weather_data(weather_df)

    temperature_data = cleaned_weather_df['temperature'].to_numpy()
    mean_temperature = np.mean(temperature_data)
    std_temperature = np.std(temperature_data)

    histogram_base64 = generate_histogram(cleaned_weather_df)

    return {
        'mean_temperature': mean_temperature,
        'std_temperature': std_temperature,
        'histogram_base64': histogram_base64
    }