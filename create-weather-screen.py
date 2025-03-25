import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import re
from datetime import datetime
import cairosvg
import os

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"daily": ["weather_code", "sunset", "uv_index_max", "daylight_duration", "sunrise", "apparent_temperature_min", "apparent_temperature_max", "temperature_2m_max", "temperature_2m_min", "precipitation_hours", "wind_gusts_10m_max", "sunshine_duration", "precipitation_sum", "snowfall_sum", "wind_speed_10m_max", "shortwave_radiation_sum", "uv_index_clear_sky_max", "showers_sum", "wind_direction_10m_dominant", "precipitation_probability_max", "rain_sum", "et0_fao_evapotranspiration"],
	"hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation_probability", "precipitation", "weather_code", "wind_gusts_10m", "wind_speed_10m", "cloud_cover", "rain", "showers", "snowfall", "snow_depth", "wind_direction_10m"],
	"current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", "weather_code", "rain", "wind_gusts_10m", "wind_speed_10m", "wind_direction_10m", "cloud_cover", "showers", "snowfall", "pressure_msl", "surface_pressure"],
	"timezone": "Europe/Berlin",
	"forecast_days": 4
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
# print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation {response.Elevation()} m asl")
# print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
# print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

							
# Current values. The order of variables needs to be the same as requested.
# current = response.Current()
# current_temperature_2m = current.Variables(0).Value()
# current_relative_humidity_2m = current.Variables(1).Value()
# current_apparent_temperature = current.Variables(2).Value()
# current_is_day = current.Variables(3).Value()
# current_precipitation = current.Variables(4).Value()
# current_weather_code = current.Variables(5).Value()
# current_rain = current.Variables(6).Value()
# current_wind_gusts_10m = current.Variables(7).Value()
# current_wind_speed_10m = current.Variables(8).Value()
# current_wind_direction_10m = current.Variables(9).Value()
# current_cloud_cover = current.Variables(10).Value()
# current_showers = current.Variables(11).Value()
# current_snowfall = current.Variables(12).Value()
# current_pressure_msl = current.Variables(13).Value()
# current_surface_pressure = current.Variables(14).Value()

# print(f"Current time {current.Time()}")

# print(f"Current temperature_2m {current_temperature_2m}")
# print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
# print(f"Current apparent_temperature {current_apparent_temperature}")
# print(f"Current is_day {current_is_day}")
# print(f"Current precipitation {current_precipitation}")
# print(f"Current weather_code {current_weather_code}")
# print(f"Current rain {current_rain}")
# print(f"Current wind_gusts_10m {current_wind_gusts_10m}")
# print(f"Current wind_speed_10m {current_wind_speed_10m}")
# print(f"Current wind_direction_10m {current_wind_direction_10m}")
# print(f"Current cloud_cover {current_cloud_cover}")
# print(f"Current showers {current_showers}")
# print(f"Current snowfall {current_snowfall}")
# print(f"Current pressure_msl {current_pressure_msl}")
# print(f"Current surface_pressure {current_surface_pressure}")
# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_apparent_temperature = hourly.Variables(2).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(3).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(4).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(5).ValuesAsNumpy()
hourly_wind_gusts_10m = hourly.Variables(6).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(7).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(8).ValuesAsNumpy()
hourly_rain = hourly.Variables(9).ValuesAsNumpy()
hourly_showers = hourly.Variables(10).ValuesAsNumpy()
hourly_snowfall = hourly.Variables(11).ValuesAsNumpy()
hourly_snow_depth = hourly.Variables(12).ValuesAsNumpy()
hourly_wind_direction_10m = hourly.Variables(13).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["apparent_temperature"] = hourly_apparent_temperature
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["precipitation"] = hourly_precipitation
hourly_data["weather_code"] = hourly_weather_code
hourly_data["wind_gusts_10m"] = hourly_wind_gusts_10m
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["rain"] = hourly_rain
hourly_data["showers"] = hourly_showers
hourly_data["snowfall"] = hourly_snowfall
hourly_data["snow_depth"] = hourly_snow_depth
hourly_data["wind_direction_10m"] = hourly_wind_direction_10m

hourly_dataframe = pd.DataFrame(data = hourly_data)
#print(hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_sunset = daily.Variables(1).ValuesAsNumpy()
daily_uv_index_max = daily.Variables(2).ValuesAsNumpy()
daily_daylight_duration = daily.Variables(3).ValuesAsNumpy()
daily_sunrise = daily.Variables(4).ValuesAsNumpy()
daily_apparent_temperature_min = daily.Variables(5).ValuesAsNumpy()
daily_apparent_temperature_max = daily.Variables(6).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(7).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(8).ValuesAsNumpy()
daily_precipitation_hours = daily.Variables(9).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(10).ValuesAsNumpy()
daily_sunshine_duration = daily.Variables(11).ValuesAsNumpy()
daily_precipitation_sum = daily.Variables(12).ValuesAsNumpy()
daily_snowfall_sum = daily.Variables(13).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(14).ValuesAsNumpy()
daily_shortwave_radiation_sum = daily.Variables(15).ValuesAsNumpy()
daily_uv_index_clear_sky_max = daily.Variables(16).ValuesAsNumpy()
daily_showers_sum = daily.Variables(17).ValuesAsNumpy()
daily_wind_direction_10m_dominant = daily.Variables(18).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(19).ValuesAsNumpy()
daily_rain_sum = daily.Variables(20).ValuesAsNumpy()
daily_et0_fao_evapotranspiration = daily.Variables(21).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["weather_code"] = daily_weather_code
daily_data["sunset"] = daily_sunset
daily_data["uv_index_max"] = daily_uv_index_max
daily_data["daylight_duration"] = daily_daylight_duration
daily_data["sunrise"] = daily_sunrise
daily_data["apparent_temperature_min"] = daily_apparent_temperature_min
daily_data["apparent_temperature_max"] = daily_apparent_temperature_max
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["precipitation_hours"] = daily_precipitation_hours
daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
daily_data["sunshine_duration"] = daily_sunshine_duration
daily_data["precipitation_sum"] = daily_precipitation_sum
daily_data["snowfall_sum"] = daily_snowfall_sum
daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
daily_data["shortwave_radiation_sum"] = daily_shortwave_radiation_sum
daily_data["uv_index_clear_sky_max"] = daily_uv_index_clear_sky_max
daily_data["showers_sum"] = daily_showers_sum
daily_data["wind_direction_10m_dominant"] = daily_wind_direction_10m_dominant
daily_data["precipitation_probability_max"] = daily_precipitation_probability_max
daily_data["rain_sum"] = daily_rain_sum
daily_data["et0_fao_evapotranspiration"] = daily_et0_fao_evapotranspiration

daily_dataframe = pd.DataFrame(data = daily_data)
#print(daily_dataframe)


url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
	"latitude": 52.5244,
	"longitude": 13.4105,
	"hourly": ["pm10", "pm2_5", "european_aqi"],
	"current": "european_aqi",
	"timezone": "Europe/Berlin",
    "forecast_days": 4
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
# print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
# print(f"Elevation {response.Elevation()} m asl")
# print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
# print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

							
# Current values. The order of variables needs to be the same as requested.
current = response.Current()

current_european_aqi = current.Variables(0).Value()

# print(f"Current time {current.Time()}")

# print(f"Current european_aqi {current_european_aqi}")
# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_pm10 = hourly.Variables(0).ValuesAsNumpy()
hourly_pm2_5 = hourly.Variables(1).ValuesAsNumpy()
hourly_european_aqi = hourly.Variables(2).ValuesAsNumpy()

hourly_data_aq = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

# hourly_data["pm10"] = hourly_pm10
# hourly_data["pm2_5"] = hourly_pm2_5
# hourly_data["european_aqi"] = hourly_european_aqi

hourly_dataframe['european_aqi'] = hourly_european_aqi


# svg_path = '/Users/i.topuz/Downloads/weather-template.svg'
# icon_path = '/Users/i.topuz/Downloads/'

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
icons_dir = os.path.join(script_dir, 'icons')

def get_icon_path(icon_name):
    """Returns full path to an icon file"""
    return os.path.join(icons_dir, icon_name)

# Get the current date
current_date = datetime.now().date()

daily_dataframe[daily_dataframe['date'] >= current_date.strftime('%Y-%m-%d')]

# Filter the daily dataframe to include only rows from the current date onward
daily_dataframe = daily_dataframe[daily_dataframe['date'] >= current_date.strftime('%Y-%m-%d')]

# Filter the hourly dataframe to include only rows from the current date onward
hourly_dataframe = hourly_dataframe[hourly_dataframe['date'].dt.date >= current_date]

def get_weather_icon(code):
    icons = {
        0: "climacell_clear_day.svg",
        1: "climacell_mostly_clear_day.svg",
        2: "climacell_partly_cloudy_day.svg",
        3: "climacell_cloudy.svg",
        45: "climacell_fog.svg",
        48: "climacell_fog_light.svg",
        51: "climacell_drizzle.svg",
        53: "climacell_drizzle.svg",
        55: "climacell_drizzle.svg",
        56: "climacell_freezing_drizzle.svg",
        57: "climacell_freezing_drizzle.svg",
        61: "climacell_rain_light.svg",
        63: "climacell_rain.svg",
        65: "climacell_rain_heavy.svg",
        66: "climacell_freezing_rain_light.svg",
        67: "climacell_freezing_rain_heavy.svg",
        71: "climacell_snow_light.svg",
        73: "climacell_snow.svg",
        75: "climacell_snow_heavy.svg",
        77: "climacell_snow_light.svg",  # Assuming snow grains are similar to light snowfall
        80: "climacell_rain_light.svg",
        81: "climacell_rain.svg",
        82: "climacell_rain_heavy.svg",
        85: "climacell_snow_light.svg",
        86: "climacell_snow_heavy.svg",
        95: "climacell_tstorm.svg",
        96: "climacell_tstorm.svg",
        99: "climacell_tstorm.svg"
    }
    return icons.get(code, "Unknown")


# Function to get the day name from a date
def get_day_name(date_str):
    date_str = date_str.strftime('%Y-%m-%d')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%A')

def format_date(date_str):
    date_str = date_str.strftime('%Y-%m-%d')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.strftime('%d %B %Y')

# Function to aggregate hourly data to daily data between 10 AM and 6 PM
def aggregate_hourly_data(hourly_df):
    hourly_df_1 = hourly_df.copy()
    hourly_df_1['datetime'] = hourly_df_1['date']
    hourly_df_1['time'] = hourly_df_1['datetime'].dt.time
    hourly_df_1['date'] = hourly_df_1['datetime'].dt.date
    filtered_data = hourly_df_1[(hourly_df_1['time'] >= pd.to_datetime('10:00:00').time()) &
                                    (hourly_df_1['time'] <= pd.to_datetime('18:00:00').time())]
    daily_data = filtered_data.groupby('date').agg({
        'relative_humidity_2m': 'max',
        'cloud_cover': 'mean',
        'european_aqi': 'max'
    }).reset_index()
    return daily_data

def extract_path_d_attributes(svg_content):
    """Extracts just the d attribute from all path elements"""
    # This pattern matches the d attribute value, handling both quotes and spaces
    pattern = r'<path[^>]*d\s*=\s*["\']([^"\']*)["\'][^>]*>'
    return re.findall(pattern, svg_content)

def load_icon_path_ds(icon_info):
    """Loads SVG file and extracts just the path d attributes"""
    full_path = get_icon_path(icon_info)

    with open(full_path, 'r') as f:
        svg_content = f.read()
        path_ds = extract_path_d_attributes(svg_content)
        return path_ds

# Function to replace placeholders in the SVG template
def replace_placeholders(template, data, hourly_df):

    # Aggregate hourly data to daily data
    daily_aggregated_data = aggregate_hourly_data(hourly_df)

    # Define the thresholds for colors
    def get_color(value, threshold, above_color='red', below_color='black'):
        return above_color if value > threshold else below_color


    for i in range(3):
        day_data = data.iloc[i]
        day_num = i + 1

        # Get the formatted date and day name
        formatted_date = format_date(day_data['date'])
        day_name = get_day_name(day_data['date'])

        # Get the aggregated data for the current day
        daily_agg_data = daily_aggregated_data[daily_aggregated_data['date'] == pd.to_datetime(day_data['date']).date()]

        # Replace placeholders for the current day
        template = template.replace(f'{{DATE{day_num}}}', formatted_date)
        template = template.replace(f'{{DAY{day_num}}}', day_name)
        template = template.replace(f'{{HIGH{day_num}}}', f"{day_data['temperature_2m_max']:.1f}")
        template = template.replace(f'{{LOW{day_num}}}', f"{day_data['temperature_2m_min']:.1f}")
        template = template.replace(f'{{POP{day_num}}}', f"{day_data['precipitation_probability_max']}")
        template = template.replace(f'{{WIND{day_num}}}', f"{int(round(day_data['wind_speed_10m_max']))}")
        template = template.replace(f'{{GUST{day_num}}}', f"{int(round(day_data['wind_gusts_10m_max']))}")
        template = template.replace(f'{{HUMIDITY{day_num}}}', f"{daily_agg_data['relative_humidity_2m'].values[0]}")
        template = template.replace(f'{{AQ{day_num}}}', f"{int(round(daily_agg_data['european_aqi'].values[0]))}")
        template = template.replace(f'{{CC{day_num}}}', f"{int(round(daily_agg_data['cloud_cover'].values[0]))}")
        template = template.replace(f'{{UV{day_num}}}', f"{day_data['uv_index_max']:.1f}")


        # Handle icon paths
        icon_info = get_weather_icon(day_data['weather_code'])
        template = template.replace(f'{{ICON_ID{day_num}}}', icon_info)
        
        # Get just the path data (d attribute values)
        path_ds = load_icon_path_ds(icon_info)
        
        # Replace each path data placeholder
        for path_index, d_value in enumerate(path_ds, 1):
            # Properly escape the path data for XML
            escaped_d = d_value.replace('"', '&quot;')
            template = template.replace(
                f'{{ICON{day_num}_PATH{path_index}}}', 
                escaped_d
            )

        # Replace color placeholders
        template = template.replace(f'{{HIGH{day_num}_COLOR}}', get_color(day_data['temperature_2m_max'], 30))
        template = template.replace(f'{{LOW{day_num}_COLOR}}', get_color(day_data['temperature_2m_min'], -5, 'black', 'red'))
        template = template.replace(f'{{POP{day_num}_COLOR}}', get_color(day_data['precipitation_probability_max'], 80))
        template = template.replace(f'{{WIND{day_num}_COLOR}}', get_color(day_data['wind_speed_10m_max'], 20))
        template = template.replace(f'{{HUMIDITY{day_num}_COLOR}}', get_color(daily_agg_data['relative_humidity_2m'].values[0], 80))
        template = template.replace(f'{{AQ{day_num}_COLOR}}', get_color(daily_agg_data['european_aqi'].values[0], 60))
        template = template.replace(f'{{CC{day_num}_COLOR}}', get_color(daily_agg_data['cloud_cover'].values[0], 70))
        template = template.replace(f'{{UV{day_num}_COLOR}}', get_color(day_data['uv_index_max'], 8))

    return template

# Read the SVG template from a file
with open('weather-template.svg', 'r') as file:
    svg_template = file.read()

# Replace placeholders with actual data
updated_svg = replace_placeholders(svg_template, daily_dataframe, hourly_dataframe)

# Print the updated SVG
# print(updated_svg)

# Convert SVG string to PNG
cairosvg.svg2png(bytestring=updated_svg.encode('utf-8'), write_to='weather-output.png', dpi=300, output_width=800,
    output_height=480)
