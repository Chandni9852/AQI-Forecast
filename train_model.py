import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("air_quality_dataset.csv", parse_dates=["datetime"])
df.set_index("datetime", inplace=True)
df.dropna(inplace=True)

# Predict next hour PM2.5
df["pm25_next"] = df["pm25"].shift(-1)
df.dropna(inplace=True)

X = df.drop(columns=["pm25_next"])
y = df["pm25_next"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

model = XGBRegressor(n_estimators=300, learning_rate=0.05, max_depth=6)
model.fit(X_train, y_train)

preds = model.predict(X_test)
mae = mean_absolute_error(y_test, preds)

print("MAE:", mae)
print("Model trained successfully.")
