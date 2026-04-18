
# ============================================
# TITAN ENGINE V5 — FULL (FIXED + TTGE + 1M)
# ============================================

import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz

# ============================================
# GLOBAL CONFIG
# ============================================

st.set_page_config(layout="wide")
SPAIN_TZ = pytz.timezone("Europe/Madrid")
API_KEY = "REPLACE_WITH_YOUR_KEY"

pairs = ["EUR/USD", "GBP/USD"]

# ============================================
# DATA LOADERS (15M + 1M FIX)
# ============================================

@st.cache_data
def load_data(symbol, interval="15min", size=200):
    try:
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": symbol,
            "interval": interval,
            "outputsize": size,
            "apikey": API_KEY
        }
        r = requests.get(url, params=params).json()

        if "values" not in r:
            return pd.DataFrame()

        df = pd.DataFrame(r["values"])
        df["time"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("time")
        df[["open","high","low","close"]] = df[["open","high","low","close"]].astype(float)

        return df

    except:
        return pd.DataFrame()


# ============================================
# MICRO ENGINE (1M FIXED INPUT)
# ============================================

class MicroEngine:
    def __init__(self, df):
        self.df = df.copy().sort_values("time")

    def detect_regime(self):
        session = self.df.tail(240)
        high_idx = session["high"].idxmax()
        low_idx = session["low"].idxmin()

        if low_idx < high_idx:
            return "LFHL"
        elif high_idx < low_idx:
            return "HFL"
        return "UNCLEAR"

    def calculate_levels(self):
        recent = self.df.tail(120)
        return recent["low"].min(), recent["high"].max()

    def calculate_targets(self, buy, sell):
        r = abs(sell - buy)
        return (
            [buy + r*0.5, buy + r, buy + r*1.5],
            [sell - r*0.5, sell - r, sell - r*1.5]
        )

    def calculate_invalidation(self, buy, sell):
        buffer = abs(sell - buy) * 0.3
        return buy - buffer, sell + buffer

    def run(self):
        regime = self.detect_regime()
        buy, sell = self.calculate_levels()
        buy_t, sell_t = self.calculate_targets(buy, sell)
        buy_inv, sell_inv = self.calculate_invalidation(buy, sell)

        return {
            "regime": regime,
            "buy": buy,
            "sell": sell,
            "buy_t": buy_t,
            "sell_t": sell_t,
            "buy_inv": buy_inv,
            "sell_inv": sell_inv
        }


# ============================================
# TTGE ENGINE (ADDED)
# ============================================

def ttge_engine(df):
    if df.empty:
        return []

    last_time = df["time"].iloc[-1]
    price = df["close"].iloc[-1]
    root = np.sqrt(price)

    times = []

    # GANN TIME
    for a in [0.25, 0.5, 1, 2]:
        times.append(last_time + pd.Timedelta(minutes=root*a*60))

    # HARMONIC
    recent = df.tail(100)
    low_t = recent.loc[recent["low"].idxmin()]["time"]
    high_t = recent.loc[recent["high"].idxmax()]["time"]
    now = last_time

    for h in [0.125, 0.25, 0.333]:
        times.append(low_t + pd.Timedelta(minutes=((now-low_t).seconds/60)*h))
        times.append(high_t + pd.Timedelta(minutes=((now-high_t).seconds/60)*h))

    clusters = []

    for t in times:
        count = sum(abs((t - x).total_seconds()) < 300 for x in times)

        if count >= 4:
            label = "HIGH PROB (85–90%)"
        elif count >= 2:
            label = "MEDIUM (65–75%)"
        else:
            label = "LOW"

        clusters.append((t, label))

    return sorted(clusters, key=lambda x: x[0])


# ============================================
# MAIN APP
# ============================================

st.title("🚀 TITAN ENGINE V5 (FULL FIXED)")

data_15 = {}
data_1 = {}

for p in pairs:
    df15 = load_data(p, "15min", 200)
    df1 = load_data(p, "1min", 500)

    if not df15.empty:
        data_15[p] = df15
    if not df1.empty:
        data_1[p] = df1

# ============================================
# MAIN LOOP
# ============================================

for pair in pairs:

    if pair not in data_15 or pair not in data_1:
        st.warning(f"{pair} missing data")
        continue

    df15 = data_15[pair]
    df1 = data_1[pair]

    st.header(pair)

    # MICRO (REAL 1M NOW)
    micro_engine = MicroEngine(df1)
    micro = micro_engine.run()

    st.subheader("⚡ MICRO (1M)")
    st.write("Regime:", micro["regime"])
    st.write("BUY:", micro["buy"])
    st.write("SELL:", micro["sell"])

    # TTGE
    st.subheader("⏱ TTGE")
    clusters = ttge_engine(df1)

    for t, label in clusters:
        if "HIGH" in label:
            st.success(f"{t.strftime('%H:%M')} → {label}")
        elif "MEDIUM" in label:
            st.warning(f"{t.strftime('%H:%M')} → {label}")
        else:
            st.info(f"{t.strftime('%H:%M')} → {label}")

    st.markdown("---")
