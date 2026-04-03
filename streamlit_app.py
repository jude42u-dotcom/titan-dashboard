import streamlit as st
import pandas as pd
import yfinance as yf
import json
from datetime import datetime
import pytz

# ==============================
# CONFIG
# ==============================
SPAIN_TZ = pytz.timezone("Europe/Madrid")
SNAPSHOT_FILE = "titan_snapshot.json"

# ==============================
# DATA FETCH
# ==============================
def get_ohlc(symbol):
    try:
        df = yf.download(
            symbol,
            interval="15m",
            period="5d",
            progress=False
        )

        # Fallback if weak data
        if df is None or df.empty or len(df) < 30:
            df = yf.download(
                symbol,
                interval="1h",
                period="5d",
                progress=False
            )

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.dropna()

        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC").tz_convert(SPAIN_TZ)
        else:
            df.index = df.index.tz_convert(SPAIN_TZ)

        return df

    except:
        return pd.DataFrame()

# ==============================
# STRUCTURE DETECTION (SAFE)
# ==============================
def detect_structure(df):
    if df is None or len(df) < 20:
        return "UNKNOWN"

    highs = df["High"]
    lows = df["Low"]

    try:
        if highs.iloc[-1] > highs.iloc[-5] and lows.iloc[-1] > lows.iloc[-5]:
            return "HHHL"
        elif highs.iloc[-1] < highs.iloc[-5] and lows.iloc[-1] < lows.iloc[-5]:
            return "LLLH"
        else:
            return "RANGE"
    except:
        return "UNKNOWN"

# ==============================
# ENGINE CORE
# ==============================
def run_pair(name, symbol):
    df = get_ohlc(symbol)

    if df.empty:
        return {
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

    structure = detect_structure(df)

    last = float(df["Close"].iloc[-1])
    high = float(df["High"].max())
    low = float(df["Low"].min())

    rng = high - low

    buy = round(low + rng * 0.25, 5)
    sell = round(high - rng * 0.25, 5)

    t1 = round((buy + sell) / 2, 5)
    t2 = round(t1 + (rng * 0.25), 5)
    t3 = round(sell, 5)

    bias = "bullish" if last > t1 else "bearish"

    return {
        "structure": structure,
        "bias": bias,
        "regime": "EXPANSION",
        "first_extreme": "London Sweep",
        "score": 70,
        "buy": float(buy),
        "sell": float(sell),
        "t1": float(t1),
        "t2": float(t2),
        "t3": float(t3),
        "trse": "Rotation Day",
        "delay": 1
    }

# ==============================
# SNAPSHOT SYSTEM
# ==============================
def save_snapshot(data):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_snapshot():
    try:
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    except:
        return None

def should_update():
    now = datetime.now(SPAIN_TZ)
    return now.hour == 22 and now.minute >= 50

# ==============================
# MAIN EXECUTION
# ==============================
snapshot = load_snapshot()

if should_update() or snapshot is None:
    eurusd = run_pair("EURUSD", "EURUSD=X")
    gbpusd = run_pair("GBPUSD", "GBPUSD=X")

    snapshot = {
        "time": str(datetime.now(SPAIN_TZ)),
        "EURUSD": eurusd,
        "GBPUSD": gbpusd
    }

    save_snapshot(snapshot)

data = snapshot

# ==============================
# UI
# ==============================
st.set_page_config(page_title="TITAN PRO ENGINE", layout="centered")

st.title("🚀 TITAN PRO ENGINE")

st.markdown(f"**Spain Time:** `{data['time']}`")

def display_pair(title, d):
    st.header(title)

    st.write(f"Structure: {d['structure']}")
    st.write(f"Bias: {d['bias']}")
    st.write(f"Regime: {d['regime']}")
    st.write(f"First Extreme: {d['first_extreme']}")
    st.write(f"Score: {d['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {d['buy']}")
    st.write(f"Sell: {d['sell']}")

    st.subheader("Targets")
    st.write(f"T1: {d['t1']}")
    st.write(f"T2: {d['t2']}")
    st.write(f"T3: {d['t3']}")

    st.subheader("TRSE")
    st.write(d["trse"])
    st.write(f"Delay: {d['delay']}")

    st.subheader("Time Windows")
    st.write("London 1: 08:30–10:00")
    st.write("London 2: 11:30–13:00")
    st.write("NY: 14:30–16:30")

display_pair("EURUSD", data["EURUSD"])
display_pair("GBPUSD", data["GBPUSD"])
