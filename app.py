import streamlit as st
import pandas as pd
import joblib

model = joblib.load("model.pkl")

df = pd.read_csv("air_quality_dataset.csv")
st.title("Air Quality Nowcast")

sample = df.tail(1).drop(columns=["pm25_next"], errors="ignore")
prediction = model.predict(sample)[0]

st.metric("Next Hour PM2.5 Prediction", f"{prediction:.2f} µg/m³")
