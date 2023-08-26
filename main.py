from flask import Flask, render_template
from weather_data_processing import process_data

app = Flask(__name__)

@app.route('/')
def weather_analysis():
    # Define the API key, city name, units, and database filename
    api_key = "97d5693b1b378dd1fc991c831ca1f970"
    city_name = "New York"
    units = "imperial"
    db_filename = "weather_data.db"

    # Process the data using the process_data function
    processed_data = process_data(api_key, city_name, units, db_filename)

    # Render the index.html template with the processed data
    return render_template('index.html', data=processed_data)

if __name__ == '__main__':
    app.run(debug=True)

