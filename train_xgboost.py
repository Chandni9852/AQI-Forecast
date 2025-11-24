import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor

df = pd.read_csv("delhi_air_quality.csv", parse_dates=["datetime"])
df.set_index("datetime", inplace=True)

df["pm25_next"] = df["pm25"].shift(-1)

# Time features
df["hour"] = df.index.hour
df["day"] = df.index.day
df["weekday"] = df.index.weekday

df.dropna(inplace=True)

X = df[["pm25", "pm10", "no2", "o3", "hour", "day", "weekday"]]
y = df["pm25_next"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.03,
    max_depth=7,
    subsample=0.8,
    colsample_bytree=0.8
)

model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print("MAE:", mae)

