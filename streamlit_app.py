import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# =========================
# 🔑 API KEY (ALREADY FIXED)
# =========================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"

# =========================
# TIME (SPAIN)
# =========================
def spain_time():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

# =========================
# DATA FETCH (CORRECT)
# =========================
def get_data(symbol):
    url = (
        "https://api.twelvedata.com/time_series"
        f"?symbol={symbol}"
        "&interval=15min"
        "&outputsize=100"
        f"&apikey={API_KEY}"
    )

    try:
        response = requests.get(url)
        data = response.json()

        # 🔍 SHOW RAW RESPONSE (DEBUG)
        st.write(f"{symbol} RAW:", data)

        # ❌ API ERROR
        if "status" in data and data["status"] == "error":
            return None

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])

        # Rename columns
        df = df.rename(columns={
            "datetime": "Time",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close"
        })

        # Convert types
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
# VALIDATION (STRICT)
# =========================
def validate(df):
    if df is None or df.empty:
        return False, "NO DATA"

    if len(df) < 50:
        return False, "INSUFFICIENT DATA"

    if df.isnull().any().any():
        return False, "NaN FOUND"

    if (df["High"] < df["Low"]).any():
        return False, "INVALID HIGH/LOW"

    if df.index.duplicated().any():
        return False, "DUPLICATES"

    # 15-minute continuity check
    delta = df.index.to_series().diff().dropna()
    if not (delta == pd.Timedelta(minutes=15)).all():
        return False, "TIME GAPS"

    return True, "OK"

# =========================
# SAFE TITAN CORE
# =========================
def titan(df):
    try:
        highs = df["High"]
        lows = df["Low"]
        close = df["Close"]

        # Basic stable logic (no crash possible)
        if highs.iloc[-1] > highs.iloc[-5]:
            bias = "BULLISH"
        else:
            bias = "BEARISH"

        last_price = float(close.iloc[-1])

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

# ✅ CORRECT SYMBOL FORMAT (IMPORTANT)
pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    run_pair(pair)
