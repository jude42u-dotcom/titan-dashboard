import streamlit as st
import requests
import pandas as pd
import json
import os
from datetime import datetime
import pytz

# IMPORT TITAN CORE
from titan_engine import run_titan_full

# ==========================================
# CONFIG
# ==========================================
API_KEY = "e7636f5efb884afc9f706a6834e716f6"
BASE_URL = "https://api.twelvedata.com/time_series"
SPAIN_TZ = pytz.timezone("Europe/Madrid")
SAVE_FILE = "titan_output.json"

# ==========================================
# DATA ENGINE
# ==========================================
def fetch(symbol, interval, output):
    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": output,
        "apikey": API_KEY
    }

    r = requests.get(BASE_URL, params=params).json()

    if "values" not in r:
        return None

    df = pd.DataFrame(r["values"]).astype(float)
    return df.iloc[::-1]


def get_data(pair):
    return {
        "w": fetch(pair, "1week", 5),
        "d": fetch(pair, "1day", 9),
        "h1": fetch(pair, "1h", 24),
        "m1": fetch(pair, "1min", 1440)
    }

# ==========================================
# LOCK SYSTEM (10:50 SPAIN)
# ==========================================
def should_run():
    now = datetime.now(SPAIN_TZ)
    return now.hour == 22 and now.minute >= 50


def save(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)


def load():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        return json.load(f)

# ==========================================
# RUN TITAN (ONCE PER DAY)
# ==========================================
if should_run():
    result = {
        "EURUSD": run_titan_full(get_data("EUR/USD")),
        "GBPUSD": run_titan_full(get_data("GBP/USD")),
        "timestamp": str(datetime.now(SPAIN_TZ))
    }
    save(result)

data = load()

# ==========================================
# UI
# ==========================================
st.set_page_config(layout="wide")
st.title("🔱 TITAN ENGINE — FULL SYSTEM")

if data is None:
    st.warning("⏳ Waiting for 22:50 Spain execution...")
else:
    tabs = st.tabs(["EURUSD", "GBPUSD"])

    for i, pair in enumerate(["EURUSD", "GBPUSD"]):
        with tabs[i]:
            d = data[pair]

            if d:
                st.header(pair)

                st.write("🧠 Regime:", d["regime"])
                st.write("🔁 TRSE:", d["trse"], "| Delay:", d["delay"])

                st.write("💰 Price:", d["price"])

                st.write("🟢 Buy Zone:", d["buy_zone"])
                st.write("🔴 Sell Zone:", d["sell_zone"])

                st.write("⛔ Invalidation Up:", d["inv_up"])
                st.write("⛔ Invalidation Down:", d["inv_down"])

                st.write("🎯 Targets:", d["targets"])

                st.write("🕒 London Windows:", d["london"])
                st.write("🕒 NY Window:", d["ny"])

                st.write("📊 Confluence Score:", d["score"])
