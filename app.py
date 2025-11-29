import os
import pandas as pd
import numpy as np
import streamlit as st
import joblib
from streamlit.components.v1 import html
import random

ROAST_LINES = {
    "Good": [
        "Breathe all you want, the air won’t fight back.",
        "Delhi? Who turned on the giant air purifier?",
        "Enjoy it… this won’t last.",
        "Your lungs are finally smiling."
    ],
    "Satisfactory": [
        "Your lungs won’t file complaints… yet.",
        "Mask optional. Flex only.",
        "Breathable. Kinda. Sorta.",
        "Air quality: ‘thik thak hai’ vibes."
    ],
    "Moderate": [
        "Your lungs: ‘We’ve seen worse.’",
        "Not great, not terrible — peak mid.",
        "Manage kar lenge… probably.",
        "This air failed chemistry class."
    ],
    "Poor": [
        "Your lungs are typing a resignation letter.",
        "This air can season your food.",
        "Breathing is now a side quest.",
        "Outside = slow cooker for lungs."
    ],
    "Very Poor": [
        "Congrats, you're smoking without smoking.",
        "Even plants are coughing.",
        "One inhale = 3 cigarettes.",
        "Air quality: boss fight mode."
    ],
    "Severe": [
        "Don’t go out. Air is trying to kill you.",
        "This isn’t oxygen… this is revenge.",
        "Your lungs entered HARDCORE MODE.",
        "Outside air = instant regret DLC."
    ]
}


# --------------------------------------------------
# PAGE CONFIG (LIGHT THEME)
# --------------------------------------------------
st.set_page_config(
    page_title="AirNowCast - Prototype AQI Nowcast",
    layout="wide",
    page_icon="🌤️"
)

# Colors
LIGHT_BG = "#f8f9fa"
CARD_BG = "#ffffff"
TEXT_COLOR = "#333333"
SUBTEXT = "#6c757d"
BORDER = "#e0e0e0"

# --------------------------------------------------
# HEADING
# --------------------------------------------------
st.markdown(
    f"""
<h1 style='text-align:center; color:#ffffff; margin-bottom:5px;'>
    AirNowCast
</h1>
<p style='text-align:center; color:{SUBTEXT}; font-size:17px;'>
    Model-based AQI estimate to help plan outdoor activity (Prototype)
</p>
    """,
    unsafe_allow_html=True
)

# --------------------------------------------------
# SAFE LOADS
# --------------------------------------------------
if not os.path.exists("air_quality_dataset.csv"):
    st.error("air_quality_dataset.csv not found. Run fetch_data.py first.")
    st.stop()

if not os.path.exists("model.pkl"):
    st.error("model.pkl not found. Run train_model.py first.")
    st.stop()

df = pd.read_csv("air_quality_dataset.csv", parse_dates=["datetime"])
df.set_index("datetime", inplace=True)
df.dropna(inplace=True)

model = joblib.load("model.pkl")

# --------------------------------------------------
# AQI HELPERS
# --------------------------------------------------
def pm25_to_aqi(pm):
    breakpoints = [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 350, 401, 500)
    ]
    for c_low, c_high, a_low, a_high in breakpoints:
        if c_low <= pm <= c_high:
            return round(((pm - c_low) / (c_high - c_low)) * (a_high - a_low) + a_low)
    return 500

def aqi_label_and_color(aqi):
    if aqi <= 50: return "Good", "#2ecc71"
    if aqi <= 100: return "Satisfactory", "#7bed9f"
    if aqi <= 200: return "Moderate", "#f1c40f"
    if aqi <= 300: return "Poor", "#e67e22"
    if aqi <= 400: return "Very Poor", "#e74c3c"
    return "Severe", "#8e44ad"


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------
latest = df.tail(1)
feature_cols = [c for c in df.columns if c != "pm25_next" and df[c].dtype.kind in "if"]
sample = latest[feature_cols]

pred_pm25 = float(model.predict(sample)[0])
pred_aqi = pm25_to_aqi(pred_pm25)
aqi_label, aqi_color = aqi_label_and_color(pred_aqi)

roast = random.choice(ROAST_LINES.get(aqi_label, [""]))

# Current values
cur_pm25 = latest["pm25"].values[0]
cur_pm10 = latest["pm10"].values[0]
cur_no2  = latest["no2"].values[0]
cur_o3   = latest["o3"].values[0]
cur_co   = latest["co"].values[0]

cur_temp = latest["temp"].values[0]
cur_hum  = latest["humidity"].values[0]
cur_wind = latest["wind_speed"].values[0]
cur_pres = latest["pressure"].values[0]

# --------------------------------------------------
# MAIN AQI + WEATHER CARD
# --------------------------------------------------
left, right = st.columns([2, 1])

with left:

    aqi_html = f"""
<div style="background-color:{CARD_BG}; border-radius:15px; padding:25px; border:1px solid {BORDER};">
    <div style="font-size:18px; color:{SUBTEXT};">Next-Hour AQI (Model Estimate)</div>

    <div style="display:flex; align-items:center; justify-content:space-between; margin-top:15px;">

        <!-- LEFT SIDE: AQI -->
        <div>
            <div style="font-size:55px; font-weight:bold; color:{aqi_color};">
                {pred_aqi}
            </div>

            <div style="font-size:20px; color:{TEXT_COLOR};">
                {aqi_label}
            </div>

            <div style="font-size:14px; margin-top:6px; color:{SUBTEXT}; font-style:italic;">
                {roast}
            </div>

            <div style="margin-top:12px; color:{SUBTEXT};">
                Predicted PM2.5: {pred_pm25:.2f} µg/m³
            </div>
        </div>

        <!-- RIGHT SIDE: WEATHER -->
        <div style="text-align:right;">
            <div style="font-size:32px; color:#333333;">{cur_temp:.1f}°C</div>
            <div style="color:#6c757d;">Current Weather</div>
            <div style="margin-top:10px; font-size:14px; color:#333333;">
                Humidity: {cur_hum:.0f}%<br/>
                Wind: {cur_wind:.1f} km/h<br/>
                Pressure: {cur_pres:.0f} hPa
            </div>
        </div>

    </div>
</div>
"""
    html(aqi_html, height=280)


with right:
    st.markdown(
        f"""
<div style="background-color:{CARD_BG}; padding:20px; border-radius:15px; border:1px solid {BORDER};">
    <h4 style="color:{TEXT_COLOR}; margin-top:0;">Prototype Note</h4>
    <p style="color:{SUBTEXT}; font-size:15px;">
        This is a prototype demonstration.<br><br>
        Predictions are based on <b>forecast API data</b>, not real CPCB/WAQI sensor readings.<br><br>
        The aim is to demonstrate the working ML pipeline for next-hour AQI estimation.
    </p>
</div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# POLLUTANT CARDS
# --------------------------------------------------
st.subheader("Current Pollutant Levels")

c1, c2, c3, c4, c5 = st.columns(5)

for col, name, value in [
    (c1, "PM2.5", cur_pm25),
    (c2, "PM10", cur_pm10),
    (c3, "NO₂", cur_no2),
    (c4, "O₃", cur_o3),
    (c5, "CO", cur_co),
]:
    col.markdown(
        f"""
<div style="background-color:{CARD_BG}; padding:15px; border-radius:15px; border:1px solid {BORDER}; text-align:center;">
    <div style="color:{SUBTEXT}; font-size:13px;">{name}</div>
    <div style="color:{TEXT_COLOR}; font-size:22px; font-weight:bold;">{value:.1f}</div>
    <div style="color:{SUBTEXT}; font-size:11px;">µg/m³</div>
</div>
        """,
        unsafe_allow_html=True
    )

st.caption("*Pollutant values are from forecast-based dataset (Prototype).*")

# --------------------------------------------------
# TREND CHART
# --------------------------------------------------
st.subheader("PM2.5 Trend (Last 48 Hours)")
if len(df) > 1:
    st.line_chart(df["pm25"].tail(48))
else:
    st.info("Not enough data available yet.")

# --------------------------------------------------
# OUTDOOR TASK PLANNER
# --------------------------------------------------
st.subheader("Outdoor Task Planner (Based on AQI Model Estimate)")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

task = st.text_input("Add a task you want to do outdoors today:")

if st.button("Add Task"):
    if task.strip():
        st.session_state.tasks.append(task)
        st.success("Task added!")
    else:
        st.error("Please enter a valid task.")

def task_recommendation(aqi):
    if aqi <= 100:
        return "🟢 Safe to do", "#2ecc71"
    elif aqi <= 200:
        return "🟡 Caution advised", "#f1c40f"
    return "🔴 Avoid outdoors now", "#e74c3c"

for t in st.session_state.tasks:
    advice, badge_color = task_recommendation(pred_aqi)
    st.markdown(
        f"""
<div style="background-color:{CARD_BG}; border-radius:10px; padding:12px; border:1px solid {BORDER};
display:flex; justify-content:space-between; margin-bottom:8px;">
    <span style="color:{TEXT_COLOR}; font-size:15px;">{t}</span>
    <span style="background-color:{badge_color}; color:white; padding:5px 12px;
    border-radius:20px; font-size:13px;">{advice}</span>
</div>
        """,
        unsafe_allow_html=True
    )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.markdown(
    f"""
<p style='text-align:center; color:{SUBTEXT}; margin-top:20px;'>
    This application is a prototype nowcast system.<br>
    Accuracy will improve significantly when trained on real CPCB/WAQI sensor data.
</p>
    """,
    unsafe_allow_html=True
)





















# import streamlit as st
# import pandas as pd
# import joblib
# import os

# st.markdown(
#     """
#     <p style='text-align:center; font-size:18px; color:#ccc;'>
#     This dashboard predicts next-hour air quality to help you plan outdoor activity safely.
#     </p>
#     """,
#     unsafe_allow_html=True
# )

# # -------------------------------
# # SAFE LOAD MODEL
# # -------------------------------
# if not os.path.exists("model.pkl"):
#     st.error(" model.pkl not found. Run train_model.py first.")
#     st.stop()

# model = joblib.load("model.pkl")

# # -------------------------------
# # LOAD DATASET
# # -------------------------------
# if not os.path.exists("air_quality_dataset.csv"):
#     st.error(" Dataset air_quality_dataset.csv not found. Run fetch_data.py first.")
#     st.stop()

# df = pd.read_csv("air_quality_dataset.csv", parse_dates=["datetime"])
# df.set_index("datetime", inplace=True)
# df.dropna(inplace=True)

# # Get last row (current real measurements)
# latest = df.tail(1)

# # Prepare sample for prediction
# sample = latest.select_dtypes(include=["float64", "int64"])

# pred_pm25 = model.predict(sample)[0]

# # -------------------------------
# # AQI CALCULATION (Indian NAQI)
# # -------------------------------
# def pm25_to_aqi_value(pm):
#     breakpoints = [
#         (0, 30, 0, 50),
#         (31, 60, 51, 100),
#         (61, 90, 101, 200),
#         (91, 120, 201, 300),
#         (121, 250, 301, 400),
#         (251, 350, 401, 500),
#     ]

#     for (c_low, c_high, a_low, a_high) in breakpoints:
#         if c_low <= pm <= c_high:
#             aqi = ((pm - c_low) / (c_high - c_low)) * (a_high - a_low) + a_low
#             return round(aqi)

#     return 500  # severe overflow

# def aqi_category(aqi):
#     if aqi <= 50:
#         return "Good", "#2ecc71"
#     elif aqi <= 100:
#         return "Satisfactory", "#7bed9f"
#     elif aqi <= 200:
#         return "Moderate", "#f1c40f"
#     elif aqi <= 300:
#         return "Poor", "#e67e22"
#     elif aqi <= 400:
#         return "Very Poor", "#e74c3c"
#     else:
#         return "Severe", "#8e44ad"

# aqi_value = pm25_to_aqi_value(pred_pm25)
# aqi_label, aqi_color = aqi_category(aqi_value)

# # -------------------------------
# # STREAMLIT PAGE CONFIG
# # -------------------------------
# st.set_page_config(page_title="AQI Nowcast", layout="centered")

# st.markdown("<h1 style='text-align:center;'>Air Quality Nowcast</h1>", unsafe_allow_html=True)

# # -------------------------------
# # AQI CARD
# # -------------------------------
# st.markdown(
#     f"""
#     <div style="padding:25px; border-radius:15px; background-color:{aqi_color}; text-align:center; margin-bottom:20px;">
#         <h2 style="color:white;">Next Hour AQI Prediction</h2>
#         <h1 style="color:white; font-size:50px;">{aqi_value}</h1>
#         <h3 style="color:white;">Category: {aqi_label}</h3>
#         <p style="color:white; font-size:20px;">PM2.5 Contribution: {pred_pm25:.2f} µg/m³</p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# st.caption("AQI scale: Good → Satisfactory → Moderate → Poor → Very Poor → Severe")

# # -------------------------------
# # OUTDOOR ACTIVITY RECOMMENDATION
# # -------------------------------

# def outdoor_advice(aqi):
#     if aqi <= 50:
#         return ("Safe to go outside ", "#2ecc71")
#     elif aqi <= 100:
#         return ("Mostly safe. Mild caution advised ", "#f1c40f")
#     elif aqi <= 200:
#         return ("Limit outdoor activity ", "#e67e22")
#     elif aqi <= 300:
#         return ("Avoid outdoor activity ", "#e74c3c")
#     else:
#         return ("Highly unsafe! Stay indoors ", "#8e44ad")

# advice_text, advice_color = outdoor_advice(aqi_value)

# st.markdown(
#     f"""
#     <div style="padding:20px; border-radius:12px; background-color:{advice_color}; text-align:center;">
#         <h3 style="color:white;">Outdoor Activity Recommendation</h3>
#         <p style="color:white; font-size:20px;">{advice_text}</p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )


# # -------------------------------
# # CURRENT AIR POLLUTANTS
# # -------------------------------
# st.subheader("Current Air Pollutants")

# col1, col2, col3 = st.columns(3)

# col1.metric("PM2.5", f"{latest['pm25'].values[0]:.2f} µg/m³")
# col2.metric("PM10", f"{latest['pm10'].values[0]:.2f} µg/m³")
# col3.metric("NO₂", f"{latest['no2'].values[0]:.2f} µg/m³")

# col4, col5 = st.columns(2)

# col4.metric("O₃", f"{latest['o3'].values[0]:.2f} µg/m³")
# col5.metric("CO", f"{latest['co'].values[0]:.2f} µg/m³")

# st.subheader("Health Impact (Based on Predicted AQI)")

# def health_impact(aqi):
#     if aqi <= 50:
#         return "Air quality is ideal for everyone."
#     elif aqi <= 100:
#         return "Acceptable; sensitive groups may feel slight irritation."
#     elif aqi <= 200:
#         return "Sensitive people may experience breathing discomfort."
#     elif aqi <= 300:
#         return "General public may experience discomfort; avoid exertion."
#     else:
#         return "Severe health effects; stay indoors."

# st.write(f"**{health_impact(aqi_value)}**")

# # -------------------------------
# # TREND CHART
# # -------------------------------
# st.subheader("PM2.5 Trend (Last 48 Hours)")
# st.line_chart(df["pm25"].tail(48))

