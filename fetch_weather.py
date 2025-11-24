# ...existing code...
import requests
import pandas as pd
import time

API_KEY = "4f5a6a1dda0f7250ee65874b3a6d2d6a"
lat = 28.6517178
lon = 77.2219388

end = int(time.time())
days = 5

pollution_records = []
weather_records = []

print("Fetching data...")

for i in range(days):
    print(f"Day {i+1}/{days}: Fetching...")
    day_end = end - i * 86400
    day_start = day_end - 86399

    # Air pollution history
    try:
        air_url = (
            f"http://api.openweathermap.org/data/3.0/air_pollution/history"
            f"?lat={lat}&lon={lon}&start={day_start}&end={day_end}&appid={API_KEY}"
        )
        resp = requests.get(air_url, timeout=10)
        resp.raise_for_status()
        air_data = resp.json()
        for item in air_data.get("list", []):
            comp = item.get("components", {})
            pollution_records.append({
                "datetime": pd.to_datetime(item["dt"], unit="s"),
                "pm2_5": comp.get("pm2_5"),
                "pm10": comp.get("pm10"),
                "no2": comp.get("no2"),
                "o3": comp.get("o3"),
                "co": comp.get("co"),
                "so2": comp.get("so2")
            })
    except Exception as e:
        print("Air API error:", e)

    time.sleep(1)

    # ...existing code...
# limit days to allowed timemachine window
days = min(days, 5)

# ...existing code...
    # Hourly weather (timemachine)
try:
        tm_url = (
            f"https://api.openweathermap.org/data/3.0/onecall/timemachine"
            f"?lat={lat}&lon={lon}&dt={day_end}&appid={API_KEY}&units=metric"
        )
        resp = requests.get(tm_url, timeout=10)

        # Debug: print status and a truncated response to diagnose failures
        print("Weather API status:", resp.status_code)
        print("Weather API response (truncated):", resp.text[:1000])

        resp.raise_for_status()
        tm_data = resp.json()

        for hour in tm_data.get("hourly", []):
            weather_records.append({
                "datetime": pd.to_datetime(hour["dt"], unit="s"),
                "temp": hour.get("temp"),
                "humidity": hour.get("humidity"),
                "wind_speed": hour.get("wind_speed"),
                "pressure": hour.get("pressure")
            })
except Exception as e:
        print("Weather API error:", e)

time.sleep(1)
# ...existing code...

# Build DataFrames
df_poll = pd.DataFrame(pollution_records)
df_weather = pd.DataFrame(weather_records)

if df_poll.empty and df_weather.empty:
    raise RuntimeError("No data retrieved. Check API key, quota, or endpoints.")

if not df_poll.empty:
    df_poll.set_index("datetime", inplace=True)
    df_poll = df_poll.resample("1h").mean()

if not df_weather.empty:
    df_weather.set_index("datetime", inplace=True)
    df_weather = df_weather.resample("1h").mean()

# Merge
if not df_poll.empty and not df_weather.empty:
    df = df_poll.join(df_weather, how="outer")
elif not df_poll.empty:
    df = df_poll
else:
    df = df_weather

df.sort_index(inplace=True)
df.to_csv("weather_delhi.csv")
print("Weather & pollution dataset saved → weather_delhi.csv")
# ...existing code...