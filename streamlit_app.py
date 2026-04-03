import streamlit as st
import pandas as pd
import requests
import json
import os
from datetime import datetime
import pytz

SNAPSHOT_FILE = "titan_snapshot.json"

# =========================
# TIME (SPAIN)
# =========================
def spain_time():
    return datetime.now(pytz.timezone("Europe/Madrid"))

# =========================
# FETCH REAL DATA (WORKING API)
# =========================
def get_daily_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}=X?range=5d&interval=1d"
        r = requests.get(url)
        data = r.json()

        closes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        df = pd.DataFrame(closes, columns=["Close"]).dropna()

        return df
    except:
        return pd.DataFrame()

# =========================
# TITAN ENGINE (DAILY MODE)
# =========================
def run_pair(symbol):
    df = get_daily_data(symbol)

    if df.empty or len(df) < 2:
        return None

    last = df["Close"].iloc[-1]
    prev = df["Close"].iloc[-2]

    if last > prev:
        structure = "UPTREND"
        bias = "BUY"
    elif last < prev:
        structure = "DOWNTREND"
        bias = "SELL"
    else:
        structure = "RANGE"
        bias = "NEUTRAL"

    buy = round(last * 0.995, 5)
    sell = round(last * 1.005, 5)

    return {
        "structure": structure,
        "bias": bias,
        "regime": "DAILY LOCK",
        "first_extreme": "YESTERDAY",
        "score": 80,
        "buy": buy,
        "sell": sell,
        "t1": round(last * 1.002, 5),
        "t2": round(last * 1.004, 5),
        "t3": round(last * 1.006, 5)
    }

# =========================
# SNAPSHOT SAVE
# =========================
def save_snapshot(data):
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(data, f)

# =========================
# SNAPSHOT LOAD
# =========================
def load_snapshot():
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return None

# =========================
# MAIN LOGIC
# =========================
now = spain_time()
snapshot = load_snapshot()

# Only update at 22:50
if now.hour == 22 and now.minute >= 50:
    eur = run_pair("EURUSD")
    gbp = run_pair("GBPUSD")

    if eur and gbp:
        snapshot = {
            "time": str(now),
            "EURUSD": eur,
            "GBPUSD": gbp
        }
        save_snapshot(snapshot)

# =========================
# UI
# =========================
st.title("🚀 TITAN PRO ENGINE")

st.write(f"Spain Time: {now}")

if snapshot is None:
    st.error("No snapshot yet. Wait for 22:50 Spain time.")
    st.stop()

def display(pair, data):
    st.header(pair)
    st.write(f"Structure: {data['structure']}")
    st.write(f"Bias: {data['bias']}")
    st.write(f"Regime: {data['regime']}")
    st.write(f"First Extreme: {data['first_extreme']}")
    st.write(f"Score: {data['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {data['buy']}")
    st.write(f"Sell: {data['sell']}")

    st.subheader("Targets")
    st.write(f"T1: {data['t1']}")
    st.write(f"T2: {data['t2']}")
    st.write(f"T3: {data['t3']}")

display("EURUSD", snapshot["EURUSD"])
display("GBPUSD", snapshot["GBPUSD"])
