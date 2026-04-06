import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz

# ============================================
# 🔒 LOCK MODE
# ============================================
SPAIN_TZ = pytz.timezone("Europe/Madrid")

def get_spain_date():
    return datetime.now(SPAIN_TZ).date()

if "titan_locked_date" not in st.session_state:
    st.session_state.titan_locked_date = None

if "red_streak" not in st.session_state:
    st.session_state.red_streak = 0

today_spain = get_spain_date()

if st.session_state.titan_locked_date == today_spain:
    st.warning("🔒 TITAN LOCKED FOR TODAY — Refresh disabled")
    st.stop()

# ============================================
# 🔐 API KEY (UNCHANGED)
# ============================================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"

# ============================================
# ⚙️ HEDGE CONFIG (NEW)
# ============================================
HEDGE_PIPS = 200

# ============================================
# 📅 EVENTS
# ============================================
MAJOR_EVENTS = {
    "2026-04-10": "US CPI",
    "2026-04-15": "FOMC",
    "2026-05-01": "NFP",
    "2026-12-25": "Christmas",
}

# ============================================
# 📅 JENKINS CALENDAR (RESTORED)
# ============================================
JENKINS_DATES = {
    "EUR/USD": [
        ("2026-04-20", "BUY"),
        ("2026-05-20", "SELL"),
        ("2026-06-04", "BUY"),
        ("2026-06-19", "SELL"),
    ],
    "GBP/USD": [
        ("2026-02-06", "SELL"),
        ("2026-03-08", "BUY"),
        ("2026-04-07", "SELL"),
        ("2026-05-07", "BUY"),
    ]
}

# ============================================
# 📡 LOAD DATA
# ============================================
@st.cache_data
def load_data(symbol):
    try:
        url = "https://api.twelvedata.com/time_series"
        params = {
            "symbol": symbol,
            "interval": "15min",
            "outputsize": 200,
            "apikey": API_KEY
        }
        r = requests.get(url, params=params).json()

        if "values" not in r:
            st.error(f"{symbol} API ERROR: {r}")
            return pd.DataFrame()

        df = pd.DataFrame(r["values"])
        df["time"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("time")
        df[["open","high","low","close"]] = df[["open","high","low","close"]].astype(float)

        return df

    except Exception as e:
        st.error(f"{symbol} DATA ERROR: {e}")
        return pd.DataFrame()

# ============================================
# 🧠 TITAN ENGINE (UNCHANGED)
# ============================================
def titan_engine(df):
    df = df.copy().sort_values("time")
    asia = df.tail(50)

    asia_high = asia["high"].max()
    asia_low = asia["low"].min()
    asia_mid = (asia_high + asia_low) / 2
    asia_range = max(asia_high - asia_low, 0.0001)

    root = np.sqrt(asia_mid)
    step = asia_range / root

    return {
        "macro": "Expansion structure → distribution",
        "probability": "LFH 60%",
        "session": "Asia → London → NY",
        "sell_zone": (asia_high + step, asia_high + step * 2),
        "buy_zone": (asia_low - step * 2, asia_low - step),
        "invalid_up": asia_high + (step * 3),
        "invalid_down": asia_low - (step * 3),
        "high_targets": [asia_low + step, asia_low, asia_low - step],
        "low_targets": [asia_high - step, asia_high, asia_high + step],
        "score": 80,
        "trse": {
            "regime": "RES",
            "delay": np.random.randint(1,6),
            "expectation": "Expansion Expected"
        }
    }

# ============================================
# 🔴 FAILURE FILTER (RESTORED)
# ============================================
def titan_failure_filter(df):
    score = 0
    recent = df.tail(20)
    range_val = recent["high"].max() - recent["low"].min()

    if range_val < 0.001:
        score += 30

    trend = recent["close"].iloc[-1] - recent["close"].iloc[0]
    if abs(trend) < 0.0005:
        score += 20

    return score

# ============================================
# 🧠 REGIME + NED + KILL (NEW)
# ============================================
def detect_regime(df):
    recent = df.tail(20)
    move = abs(recent["close"].iloc[-1] - recent["open"].iloc[0])
    range_ = recent["high"].max() - recent["low"].min()
    directional = sum(np.sign(recent["close"].diff().fillna(0)))

    if move > range_ * 0.8 and abs(directional) > 10:
        return "STRONG_TREND"
    if range_ < 0.001:
        return "DRIFT"
    if range_ > 0.004:
        return "EXPANSION"
    return "RANGE"

def ned_filter(df):
    recent = df.tail(10)
    volatility = recent["high"].max() - recent["low"].min()
    directional = sum(np.sign(recent["close"].diff().fillna(0)))
    return volatility > 0.004 or abs(directional) > 7

def kill_switch(regime):
    return regime in ["STRONG_TREND", "DRIFT"]

def titan_decision(regime, ned, kill):
    if kill:
        return "🔴 NO TRADE (KILL)"
    if ned:
        return "🔴 NO TRADE (NED)"
    if regime == "EXPANSION":
        return "🟡 CAUTION"
    return "🟢 TRADE"

# ============================================
# 🔥 GANN TIME (RESTORED)
# ============================================
def titan_time_pdf(df):
    last_price = float(df["close"].iloc[-1])
    root = np.sqrt(last_price)
    base_time = df["time"].iloc[-1]
    return [base_time + pd.Timedelta(minutes=root * a * 60) for a in [0.25,0.5,1,2]]

# ============================================
# 🔥 HARMONIC TIME (RESTORED)
# ============================================
def calculate_time_windows(df):
    recent = df.tail(100)
    low_time = recent.loc[recent["low"].idxmin()]["time"]
    high_time = recent.loc[recent["high"].idxmax()]["time"]
    now = df["time"].iloc[-1]

    diff_low = (now - low_time).total_seconds()/60
    diff_high = (now - high_time).total_seconds()/60

    harmonics = [0.125,0.167,0.25,0.333]

    return {
        "low":[low_time + pd.Timedelta(minutes=diff_low*h) for h in harmonics],
        "high":[high_time + pd.Timedelta(minutes=diff_high*h) for h in harmonics]
    }

# ============================================
# 🚀 UI
# ============================================
st.set_page_config(layout="wide")
st.title("🚀 TITAN FINAL INTEGRATED")

pairs = ["EUR/USD","GBP/USD"]

for pair in pairs:
    df = load_data(pair)
    if df.empty:
        continue

    result = titan_engine(df)

    regime = detect_regime(df)
    ned = ned_filter(df)
    kill = kill_switch(regime)
    decision = titan_decision(regime,ned,kill)

    gann = titan_time_pdf(df)
    harmonic = calculate_time_windows(df)

    st.header(pair)

    st.write("🧠 Decision:", decision)
    st.write("🧠 Regime:", regime)
    st.write("🧠 TRSE:", result["trse"])

    sz = result["sell_zone"]
    bz = result["buy_zone"]

    st.write(f"SELL: {sz}")
    st.write(f"BUY: {bz}")

    st.write("GANN:")
    for t in gann:
        st.write(t.strftime("%H:%M"))

    st.write("HARMONIC LOW:")
    for t in harmonic["low"]:
        st.write(t.strftime("%H:%M"))

    st.write("HARMONIC HIGH:")
    for t in harmonic["high"]:
        st.write(t.strftime("%H:%M"))

    st.markdown("---")

st.session_state.titan_locked_date = today_spain
