import requests
import pandas as pd
from datetime import datetime

API_KEY = "YOUR_OPENWEATHER_KEY"
city = "Delhi"

# 1) Pollution from OpenAQ (free)
aq_url = f"https://api.openaq.org/v2/measurements?city={city}&limit=10000"
aq_resp = requests.get(aq_url).json()

poll_records = []
for r in aq_resp.get("results", []):
    poll_records.append({
        "datetime": pd.to_datetime(r["date"]["utc"]),
        "pm25": r["value"] if r["parameter"] == "pm25" else None,
        "pm10": r["value"] if r["parameter"] == "pm10" else None,
        "no2": r["value"] if r["parameter"] == "no2" else None,
        "o3": r["value"] if r["parameter"] == "o3" else None
    })

df_poll = pd.DataFrame(poll_records)
df_poll.set_index("datetime", inplace=True)
df_poll = df_poll.groupby("datetime").mean()    # combine duplicate timestamps

# 2) Weather forecast (5 days)
weather_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
weather_resp = requests.get(weather_url).json()

weather_records = []
for w in weather_resp.get("list", []):
    dt = datetime.fromtimestamp(w["dt"])
    m = w["main"]
    ws = w["wind"]["speed"]

    weather_records.append({
        "datetime": dt,
        "temp": m["temp"],
        "humidity": m["humidity"],
        "pressure": m["pressure"],
        "wind_speed": ws
    })

df_weather = pd.DataFrame(weather_records)
df_weather.set_index("datetime", inplace=True)
df_weather = df_weather.resample("1H").interpolate()

# 3) Merge
df = df_poll.join(df_weather, how="inner")
df.to_csv("delhi_air_quality.csv")

print("✔ CSV created → delhi_air_quality.csv")
print(df.head())
