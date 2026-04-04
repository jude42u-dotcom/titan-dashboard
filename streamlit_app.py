import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# ==============================
# 🔐 API KEY (PUT YOUR KEY HERE)
# ==============================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"  # <-- YOUR KEY ALREADY INSERTED

# ==============================
# ⏰ SPAIN TIME
# ==============================
def get_spain_time():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

# ==============================
# 📡 FETCH DATA
# ==============================
def get_data(symbol="EUR/USD"):
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": "15min",
        "outputsize": 100,
        "apikey": API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "status" in data and data["status"] == "error":
        return None, data

    if "values" not in data:
        return None, data

    df = pd.DataFrame(data["values"])

    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime")
    df = df.sort_index()

    for col in ["open", "high", "low", "close"]:
        df[col] = df[col].astype(float)

    df = df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close"
    })

    return df, data

# ==============================
# 🧪 VALIDATION
# ==============================
def validate(df):
    if df is None or df.empty:
        return False, "NO DATA"

    if len(df) < 20:
        return False, "INSUFFICIENT DATA"

    if df.isnull().any().any():
        return False, "NaN FOUND"

    if (df["High"] < df["Low"]).any():
        return False, "INVALID HIGH/LOW"

    if df.index.duplicated().any():
        return False, "DUPLICATE TIMESTAMPS"

    return True, "OK"

# ==============================
# 🧠 TITAN ENGINE
# ==============================
def titan(df):
    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    recent_high = high.iloc[-5:].max()
    recent_low = low.iloc[-5:].min()

    prev_high = high.iloc[-10:-5].max()
    prev_low = low.iloc[-10:-5].min()

    if recent_high > prev_high and recent_low > prev_low:
        structure = "UPTREND"
    elif recent_high < prev_high and recent_low < prev_low:
        structure = "DOWNTREND"
    else:
        structure = "RANGE"

    momentum = close.iloc[-1] - close.iloc[-4]
    pressure = "BUY" if momentum > 0 else "SELL"

    ranges = high - low
    recent_range = ranges.iloc[-1]
    avg_range = ranges.iloc[-10:].mean()

    volatility = "EXPANSION" if recent_range > avg_range * 1.2 else "COMPRESSION"

    speed = abs(close.iloc[-1] - close.iloc[-3])
    time_state = "ACCELERATION" if speed > avg_range else "NORMAL"

    score = 0
    score += 2 if structure == "UPTREND" else -2 if structure == "DOWNTREND" else 0
    score += 1 if pressure == "BUY" else -1

    if volatility == "EXPANSION":
        score += 1 if pressure == "BUY" else -1

    if time_state == "ACCELERATION":
        score += 1 if pressure == "BUY" else -1

    if score >= 2:
        bias = "BULLISH"
    elif score <= -2:
        bias = "BEARISH"
    else:
        bias = "NEUTRAL"

    return {
        "bias": bias,
        "score": score,
        "structure": structure,
        "pressure": pressure,
        "volatility": volatility,
        "time_state": time_state,
        "last_price": close.iloc[-1]
    }

# ==============================
# 🎯 UI
# ==============================
st.title("🚀 TITAN PRO ENGINE (STABLE BUILD)")
st.write(f"Spain Time: {get_spain_time()}")

pairs = ["EUR/USD", "GBP/USD"]

for symbol in pairs:

    st.header(symbol)

    df, raw = get_data(symbol)

    valid, reason = validate(df)

    if not valid:
        st.error(f"DATA REJECTED: {reason}")
        continue

    result = titan(df)

    if result["bias"] == "BULLISH":
        st.success(f"Bias: {result['bias']}")
    elif result["bias"] == "BEARISH":
        st.error(f"Bias: {result['bias']}")
    else:
        st.warning(f"Bias: {result['bias']}")

    st.write(f"Score: {result['score']}")
    st.write(f"Structure: {result['structure']}")
    st.write(f"Pressure: {result['pressure']}")
    st.write(f"Volatility: {result['volatility']}")
    st.write(f"Time State: {result['time_state']}")
    st.write(f"Last Price: {result['last_price']}")
