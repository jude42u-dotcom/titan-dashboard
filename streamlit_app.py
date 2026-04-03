import streamlit as st
import pandas as pd
import yfinance as yf
import json
import os
from datetime import datetime, time
import pytz

# =========================
# CONFIG
# =========================
SPAIN_TZ = pytz.timezone("Europe/Madrid")
SNAPSHOT_FILE = "titan_snapshot.json"
UPDATE_HOUR = 22
UPDATE_MINUTE = 50

# =========================
# TIME
# =========================
def spain_now():
    return datetime.now(SPAIN_TZ)

# =========================
# SAFE DATA FETCH (DAILY ONLY)
# =========================
def get_ohlc(symbol):
    try:
        df = yf.download(
            symbol,
            interval="1d",
            period="10d",
            progress=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.dropna()

        for col in ["Open", "High", "Low", "Close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna()

        return df

    except:
        return pd.DataFrame()

# =========================
# STRUCTURE ENGINE
# =========================
def detect_structure(df):
    if df is None or df.empty or len(df) < 3:
        return "UNKNOWN"

    highs = df["High"].tail(3).values
    lows = df["Low"].tail(3).values

    if highs[-1] > highs[-2] > highs[-3]:
        return "UPTREND"
    elif lows[-1] < lows[-2] < lows[-3]:
        return "DOWNTREND"
    else:
        return "RANGE"

# =========================
# SAFE FLOAT
# =========================
def f(x):
    try:
        return float(x)
    except:
        return 0.0

# =========================
# CORE ENGINE
# =========================
def run_pair(name, symbol):
    df = get_ohlc(symbol)

    if df.empty:
        return {
            "pair": name,
            "structure": "UNKNOWN",
            "bias": "neutral",
            "regime": "UNKNOWN",
            "first_extreme": "UNKNOWN",
            "score": 0,
            "buy": 0,
            "sell": 0,
            "t1": 0,
            "t2": 0,
            "t3": 0,
            "trse": "Unknown",
            "delay": 0
        }

    last = f(df["Close"].iloc[-1])
    high = f(df["High"].iloc[-1])
    low = f(df["Low"].iloc[-1])

    structure = detect_structure(df)

    bias = "neutral"
    if structure == "UPTREND":
        bias = "bullish"
    elif structure == "DOWNTREND":
        bias = "bearish"

    rng = high - low

    buy = low + 0.3 * rng
    sell = high - 0.3 * rng

    return {
        "pair": name,
        "structure": structure,
        "bias": bias,
        "regime": "ACTIVE",
        "first_extreme": "Daily Range",
        "score": 60 if structure != "UNKNOWN" else 0,
        "buy": f(buy),
        "sell": f(sell),
        "t1": f(last + rng * 0.5),
        "t2": f(last + rng * 1.0),
        "t3": f(last + rng * 1.5),
        "trse": "Rotation Day",
        "delay": 1
    }

# =========================
# SNAPSHOT LOGIC
# =========================
def should_update():
    now = spain_now()
    update_time = now.replace(hour=UPDATE_HOUR, minute=UPDATE_MINUTE, second=0, microsecond=0)
    return now >= update_time

def load_snapshot():
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return None

def save_snapshot(data):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(data, f)

def build_snapshot():
    eurusd = run_pair("EURUSD", "EURUSD=X")
    gbpusd = run_pair("GBPUSD", "GBPUSD=X")

    snapshot = {
        "time": str(spain_now()),
        "EURUSD": eurusd,
        "GBPUSD": gbpusd
    }

    save_snapshot(snapshot)
    return snapshot

def get_data():
    snapshot = load_snapshot()

    if snapshot is None:
        return build_snapshot()

    if should_update():
        return build_snapshot()

    return snapshot

# =========================
# UI
# =========================
st.set_page_config(layout="wide")

st.title("🚀 TITAN PRO ENGINE")
st.caption(f"Spain Time: {spain_now()}")

data = get_data()

def display(pair):
    st.header(pair["pair"])

    st.write(f"Structure: {pair['structure']}")
    st.write(f"Bias: {pair['bias']}")
    st.write(f"Regime: {pair['regime']}")
    st.write(f"First Extreme: {pair['first_extreme']}")
    st.write(f"Score: {pair['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {round(pair['buy'],5)}")
    st.write(f"Sell: {round(pair['sell'],5)}")

    st.subheader("Targets")
    st.write(f"T1: {round(pair['t1'],5)}")
    st.write(f"T2: {round(pair['t2'],5)}")
    st.write(f"T3: {round(pair['t3'],5)}")

    st.subheader("TRSE")
    st.write(pair["trse"])
    st.write(f"Delay: {pair['delay']}")

    st.subheader("Time Windows")
    st.write("London 1: 08:30–10:00")
    st.write("London 2: 11:30–13:00")
    st.write("NY: 14:30–16:30")

display(data["EURUSD"])
st.divider()
display(data["GBPUSD"])
