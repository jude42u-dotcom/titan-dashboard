import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==============================
# CONFIG
# ==============================

API_KEY = "PASTE_YOUR_API_KEY_HERE"
MIN_ROWS = 50

# ==============================
# DATA FETCH
# ==============================

def get_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=15min&outputsize=100&apikey={API_KEY}"
    
    try:
        r = requests.get(url)
        data = r.json()

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])

        # Convert
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.set_index("datetime")

        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.sort_index()

        # Rename for TITAN
        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close"
        }, inplace=True)

        return df

    except:
        return None


# ==============================
# VALIDATION LAYER
# ==============================

def validate(df):
    if df is None:
        return False, "NO DATA"

    if df.empty:
        return False, "EMPTY DATA"

    if len(df) < MIN_ROWS:
        return False, "INSUFFICIENT DATA"

    if df.isnull().any().any():
        return False, "NaN FOUND"

    if (df["High"] < df["Low"]).any():
        return False, "INVALID HIGH/LOW"

    if df.index.duplicated().any():
        return False, "DUPLICATE TIMESTAMPS"

    return True, "OK"


# ==============================
# TITAN CORE (SIMPLIFIED BASE)
# ==============================

def titan(df):
    last = df.iloc[-1]
    prev = df.iloc[-5]

    macro_bias = "BULLISH" if last["Close"] > prev["Close"] else "BEARISH"

    high = float(last["High"])
    low = float(last["Low"])
    close = float(last["Close"])

    range_ = high - low

    return {
        "bias": macro_bias,
        "sell_zone": close + range_ * 0.5,
        "buy_zone": close - range_ * 0.5,
        "tp1": close - range_ * 1.0,
        "tp2": close - range_ * 2.0,
        "tp3": close - range_ * 3.0
    }


# ==============================
# UI
# ==============================

st.set_page_config(page_title="TITAN PRO ENGINE", layout="centered")

st.title("🚀 TITAN PRO ENGINE (STABLE BUILD)")

spain_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"Spain Time: {spain_time}")

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    st.header(pair)

    df = get_data(pair)

    valid, reason = validate(df)

    if not valid:
        st.error(f"DATA REJECTED: {reason}")
        continue

    try:
        result = titan(df)

        st.success(f"Macro Bias: {result['bias']}")
        st.write(f"Primary Sell Zone: {result['sell_zone']:.5f}")
        st.write(f"Alternate Buy Zone: {result['buy_zone']:.5f}")

        st.write("Targets:")
        st.write(f"T1: {result['tp1']:.5f}")
        st.write(f"T2: {result['tp2']:.5f}")
        st.write(f"T3: {result['tp3']:.5f}")

    except Exception as e:
        st.error("Engine error")
        st.write(str(e))
