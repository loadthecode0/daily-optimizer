import os
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)
    url = "https://api.open-meteo.com/v1/forecast"
    # Parameters for Open-Meteo API (customize location and date as needed)
    params = {
        'latitude': 55.67,  # Example: Copenhagen
        'longitude': 12.56,
        'hourly': ["temperature_2m", "precipitation_probability"]
    }
    responses = openmeteo.weather_api(url, params=params)
    
    # # Fetch data from Open-Meteo API
    # response = requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    
    # if response.status_code == 200:
    #     data = response.json()
        
    #     # Optionally, store the response in a file or database
    #     with open('weather_data.json', 'w') as f:
    #         f.write(response.text)
        
    #     return jsonify(data)  # Send data to frontend as JSON
    # else:
    #     return jsonify({'error': 'Failed to fetch data'}), 500
    # Process first location. Add a for-loop for multiple locations or weather models
    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m
    hourly_data["precipitation_probability"] = hourly_precipitation_probability

    hourly_dataframe = pd.DataFrame(data = hourly_data)
    print(hourly_dataframe)
    
    result = hourly_dataframe.to_dict(orient='records')

    # if response.status_code == 200:

    data = jsonify(result)
        
        # Optionally, store the response in a file or database
    with open('weather_data.json', 'w') as f:
        f.write(data.get_data(as_text=True))
    
    return data  # Send data to frontend as JSON
    # else:
    #     return jsonify({'error': 'Failed to fetch data'}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 1000))  # Use PORT env variable or default to 5000
    app.run(host='0.0.0.0', port=port)
