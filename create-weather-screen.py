import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
import re
from datetime import datetime
import cairosvg
import os

latitude = 52.508999
longitude = 13.553160
timezone = 'Europe/Berlin'
forecast_days = 3

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# The order of variables in hourly or daily is important to assign them correctly below
weather_url = "https://api.open-meteo.com/v1/forecast"
weather_params = {
	"latitude": latitude,
	"longitude": longitude,
	"daily": ["weather_code", "uv_index_max", "temperature_2m_max", "temperature_2m_min", "wind_gusts_10m_max", "wind_speed_10m_max", "precipitation_probability_max"],
	"hourly": ["relative_humidity_2m", "cloud_cover"],
    "timezone": timezone,
	"forecast_days": forecast_days
}
responses = openmeteo.weather_api(weather_url, params=weather_params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]

hourly = response.Hourly()
hourly_relative_humidity_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(1).ValuesAsNumpy()


hourly_data_index = pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
).tz_convert(timezone)

hourly_data_dict = {
    "date": hourly_data_index,
    "relative_humidity_2m": hourly_relative_humidity_2m,
    "cloud_cover": hourly_cloud_cover
}

hourly_dataframe = pd.DataFrame(data = hourly_data_dict)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_uv_index_max = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(2).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(3).ValuesAsNumpy()
daily_wind_gusts_10m_max = daily.Variables(4).ValuesAsNumpy()
daily_wind_speed_10m_max = daily.Variables(5).ValuesAsNumpy()
daily_precipitation_probability_max = daily.Variables(6).ValuesAsNumpy()

berlin_date_index = pd.date_range(
    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
    freq=pd.Timedelta(seconds=daily.Interval()),
    inclusive="left"
).tz_convert(timezone)

daily_data_dict = {
    "date": berlin_date_index,
    "weather_code": daily_weather_code,
    "uv_index_max": daily_uv_index_max,
    "temperature_2m_max": daily_temperature_2m_max,
    "temperature_2m_min": daily_temperature_2m_min,
    "wind_gusts_10m_max": daily_wind_gusts_10m_max,
    "wind_speed_10m_max": daily_wind_speed_10m_max,
    "precipitation_probability_max": daily_precipitation_probability_max
}

daily_dataframe = pd.DataFrame(data = daily_data_dict)

aqi_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
aqi_params = {
	"latitude": latitude,
	"longitude": longitude,
	"hourly": ["european_aqi"],
	"timezone": timezone,
    "forecast_days": forecast_days
}
responses = openmeteo.weather_api(aqi_url, params=aqi_params)

response = responses[0]

# Process hourly data. The order of variables needs to be the same as requested.
hourly = response.Hourly()
hourly_european_aqi = hourly.Variables(0).ValuesAsNumpy()

hourly_dataframe['european_aqi'] = hourly_european_aqi

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
icons_dir = os.path.join(script_dir, 'icons')

def get_icon_path(icon_name):
    """Returns full path to an icon file"""
    return os.path.join(icons_dir, icon_name)

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
        77: "climacell_snow_light.svg",
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

def load_icon(icon_info):
    """Loads SVG file"""
    full_path = get_icon_path(icon_info)

    with open(full_path, 'r') as f:
        svg_content = f.read()
        return svg_content
    
def extract_icon_group_content(icon_content):
    """Extracts just the <g> element and its children from icon SVG"""
    # Find the opening <g> tag with transform
    start = icon_content.find('<g')
    if start == -1:
        return ""
    
    # Find matching closing tag
    depth = 1
    pos = start + 2
    while depth > 0 and pos < len(icon_content):
        if icon_content.startswith('</g>', pos):
            depth -= 1
            pos += 4
        elif icon_content.startswith('<g', pos):
            depth += 1
            pos += 2
        else:
            pos += 1
    
    if depth == 0:
        return icon_content[start:pos]
    return ""
    
def adjust_icon_scale(icon_content, new_scale=3.8):
    """Adjusts the scale in the transform attribute"""
    # Simple regex replacement for the scale
    return re.sub(
        r'transform="[^"]*scale\(\s*[\d.]+\s*\)[^"]*"',
        f'transform="scale({new_scale})"',
        icon_content
    )

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


        # Handle icon - Simple version
        icon_info = get_weather_icon(day_data['weather_code'])
        icon_content = load_icon(icon_info)

        group_content = extract_icon_group_content(icon_content)
        adjusted_icon = adjust_icon_scale(group_content)
        template = template.replace(f'{{ICON_CONTENT{day_num}}}', adjusted_icon)


        # Replace color placeholders
        template = template.replace(f'{{HIGH{day_num}_COLOR}}', get_color(day_data['temperature_2m_max'], 30))
        template = template.replace(f'{{LOW{day_num}_COLOR}}', get_color(day_data['temperature_2m_min'], -5, 'black', 'red'))
        template = template.replace(f'{{POP{day_num}_COLOR}}', get_color(day_data['precipitation_probability_max'], 80))
        template = template.replace(f'{{WIND{day_num}_COLOR}}', get_color(day_data['wind_speed_10m_max'], 20))
        template = template.replace(f'{{HUMIDITY{day_num}_COLOR}}', get_color(daily_agg_data['relative_humidity_2m'].values[0], 80))
        template = template.replace(f'{{AQ{day_num}_COLOR}}', get_color(daily_agg_data['european_aqi'].values[0], 60))
        template = template.replace(f'{{CC{day_num}_COLOR}}', get_color(daily_agg_data['cloud_cover'].values[0], 70))
        template = template.replace(f'{{UV{day_num}_COLOR}}', get_color(day_data['uv_index_max'], 8))

    # Get the current system time when this part of the code runs
    current_execution_time = datetime.now().strftime('%d-%m-%Y %H:%M')

    template = template.replace(f'{{SUMMARY}}', f"Data is retrieved at {current_execution_time}.") 
    return template

# Read the SVG template from a file
with open('weather-template.svg', 'r') as file:
    svg_template = file.read()

# Replace placeholders with actual data
updated_svg = replace_placeholders(svg_template, daily_dataframe, hourly_dataframe)

# Convert SVG string to PNG
cairosvg.svg2png(bytestring=updated_svg.encode('utf-8'), write_to='weather-output.png', dpi=300, output_width=800,
    output_height=480)
