import requests
import pandas as pd

# --- Change this city name only ---
CITY = "Delhi"

# Step 1: Get coordinates for the city (Open-Meteo geocoding)
geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={CITY}&count=1"
geo_res = requests.get(geo_url).json()

if "results" not in geo_res or len(geo_res["results"]) == 0:
    raise Exception("City not found.")

lat = geo_res["results"][0]["latitude"]
lon = geo_res["results"][0]["longitude"]

print(f"Fetched location: {CITY} -> lat:{lat}, lon:{lon}")

# Step 2: Fetch AQI + PM2.5 + PM10 + NO2 + O3 + Weather (100% free)
aq_url = (
    f"https://air-quality-api.open-meteo.com/v1/air-quality?"
    f"latitude={lat}&longitude={lon}&hourly=pm10,pm2_5,carbon_monoxide,"
    f"nitrogen_dioxide,ozone,uv_index,uv_index_clear_sky"
)

weather_url = (
    f"https://api.open-meteo.com/v1/forecast?"
    f"latitude={lat}&longitude={lon}&hourly=temperature_2m,"
    f"relativehumidity_2m,pressure_msl,windspeed_10m"
)

aq_data = requests.get(aq_url).json()
weather_data = requests.get(weather_url).json()

# Convert AQI
aq_df = pd.DataFrame({
    "datetime": aq_data["hourly"]["time"],
    "pm25": aq_data["hourly"]["pm2_5"],
    "pm10": aq_data["hourly"]["pm10"],
    "no2": aq_data["hourly"]["nitrogen_dioxide"],
    "o3": aq_data["hourly"]["ozone"],
    "co": aq_data["hourly"]["carbon_monoxide"],
})
aq_df["datetime"] = pd.to_datetime(aq_df["datetime"])
aq_df.set_index("datetime", inplace=True)

# Convert weather
w_df = pd.DataFrame({
    "datetime": weather_data["hourly"]["time"],
    "temp": weather_data["hourly"]["temperature_2m"],
    "humidity": weather_data["hourly"]["relativehumidity_2m"],
    "pressure": weather_data["hourly"]["pressure_msl"],
    "wind_speed": weather_data["hourly"]["windspeed_10m"],
})
w_df["datetime"] = pd.to_datetime(w_df["datetime"])
w_df.set_index("datetime", inplace=True)

# Merge both
df = aq_df.join(w_df, how="inner")

# Save
df.to_csv("air_quality_dataset.csv")
print("Dataset saved as air_quality_dataset.csv")
print(df.head())
