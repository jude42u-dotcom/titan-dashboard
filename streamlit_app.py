import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz

# =========================
# CONFIG
# =========================
API_KEY = "PASTE_YOUR_API_KEY_HERE"
MIN_ROWS = 50

# =========================
# TIME (SPAIN)
# =========================
def spain_time():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

# =========================
# DATA FETCH (TWELVEDATA)
# =========================
def get_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=15min&outputsize=100&apikey={API_KEY}"

    try:
        r = requests.get(url)
        data = r.json()

        # DEBUG (important)
        st.write(f"{symbol} RAW:", data)

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])
        df = df.rename(columns={
            "datetime": "Time",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close"
        })

        df["Time"] = pd.to_datetime(df["Time"])
        df = df.sort_values("Time")

        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.set_index("Time")

        return df

    except Exception as e:
        st.error(f"Fetch error: {e}")
        return None

# =========================
# VALIDATION LAYER
# =========================
def validate(df):
    if df is None or df.empty:
        return False, "NO DATA"

    if len(df) < MIN_ROWS:
        return False, "INSUFFICIENT DATA"

    if df.isnull().any().any():
        return False, "NaN FOUND"

    if (df["High"] < df["Low"]).any():
        return False, "INVALID HIGH/LOW"

    if df.index.duplicated().any():
        return False, "DUPLICATES"

    # Time continuity (15m)
    delta = df.index.to_series().diff().dropna()
    if not (delta == pd.Timedelta(minutes=15)).all():
        return False, "TIME GAPS"

    return True, "OK"

# =========================
# TITAN CORE (SAFE VERSION)
# =========================
def titan(df):
    try:
        highs = df["High"]
        lows = df["Low"]

        # Basic macro logic (replace later with full TITAN)
        if highs.iloc[-1] > highs.iloc[-5]:
            bias = "BULLISH"
        else:
            bias = "BEARISH"

        last_price = float(df["Close"].iloc[-1])

        return {
            "bias": bias,
            "price": last_price
        }

    except Exception as e:
        return {"error": str(e)}

# =========================
# DISPLAY ENGINE
# =========================
def run_pair(symbol):
    st.subheader(symbol)

    df = get_data(symbol)

    valid, reason = validate(df)

    if not valid:
        st.error(f"DATA REJECTED: {reason}")
        return

    result = titan(df)

    if "error" in result:
        st.error(f"ENGINE ERROR: {result['error']}")
        return

    st.success(f"Bias: {result['bias']}")
    st.write(f"Last Price: {result['price']}")

# =========================
# UI
# =========================
st.title("🚀 TITAN PRO ENGINE (STABLE BUILD)")

st.write("Spain Time:", spain_time())

# IMPORTANT: use correct symbols
pairs = ["EURUSD", "GBPUSD"]

for pair in pairs:
    run_pair(pair)
