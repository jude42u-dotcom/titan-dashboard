import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import pytz

st.set_page_config(layout="wide")

SPAIN = pytz.timezone("Europe/Madrid")

# ---------------------------
# DATA
# ---------------------------
def get_ohlc(pair="EURUSD=X", interval="5m", period="5d"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}?interval={interval}&range={period}"
    r = requests.get(url).json()
    res = r["chart"]["result"][0]
    ts = res["timestamp"]
    ohlc = res["indicators"]["quote"][0]

    df = pd.DataFrame({
        "time": pd.to_datetime(ts, unit="s"),
        "open": ohlc["open"],
        "high": ohlc["high"],
        "low": ohlc["low"],
        "close": ohlc["close"],
    }).dropna()

    return df

# ---------------------------
# STRUCTURE ENGINE (LFHL / HFL)
# ---------------------------
def structure_engine(df):
    highs = df["high"].rolling(10).max()
    lows = df["low"].rolling(10).min()

    last_high = highs.iloc[-1]
    prev_high = highs.iloc[-20]
    last_low = lows.iloc[-1]
    prev_low = lows.iloc[-20]

    if last_high < prev_high and last_low < prev_low:
        return "LFHL", "bearish"
    elif last_high > prev_high and last_low > prev_low:
        return "HFL", "bullish"
    else:
        return "NEUTRAL", "neutral"

# ---------------------------
# REGIME (COMPRESSION / EXPANSION)
# ---------------------------
def regime_engine(df):
    rng = df["high"].iloc[-1] - df["low"].iloc[-1]
    avg = (df["high"] - df["low"]).rolling(20).mean().iloc[-1]

    if rng > avg:
        return "EXPANSION"
    else:
        return "COMPRESSION"

# ---------------------------
# TRSE (Delay Days)
# ---------------------------
def trse_engine(df):
    daily = df.resample("1D", on="time").agg({"high":"max","low":"min"}).dropna()
    ranges = daily["high"] - daily["low"]

    delay = 0
    for i in range(1, min(5, len(ranges))):
        if ranges.iloc[-i] < ranges.mean():
            delay += 1

    if delay >= 3:
        regime = f"RDS Day {delay}"
    else:
        regime = f"Trend Day {delay}"

    return delay, regime

# ---------------------------
# SCORING
# ---------------------------
def score_engine(structure, regime, delay):
    score = 0

    if structure == "HFL":
        score += 30
    elif structure == "LFHL":
        score += 30

    if regime == "EXPANSION":
        score += 30
    else:
        score += 10

    if delay >= 3:
        score += 30
    else:
        score += 10

    return min(score, 100)

# ---------------------------
# ZONES + TARGETS
# ---------------------------
def levels(df, bias):
    high = df["high"].iloc[-1]
    low = df["low"].iloc[-1]
    mid = (high + low) / 2

    if bias == "bullish":
        buy = mid - (high - low) * 0.25
        sell = high
        t1 = high + (high - low) * 0.5
        t2 = high + (high - low)
        t3 = high + (high - low) * 1.5
    elif bias == "bearish":
        sell = mid + (high - low) * 0.25
        buy = low
        t1 = low - (high - low) * 0.5
        t2 = low - (high - low)
        t3 = low - (high - low) * 1.5
    else:
        buy = low
        sell = high
        t1 = mid
        t2 = high
        t3 = low

    return buy, sell, t1, t2, t3

# ---------------------------
# TIME WINDOWS (SPAIN)
# ---------------------------
def time_windows():
    return {
        "London 1": "08:30–10:00",
        "London 2": "11:30–13:00",
        "NY": "14:30–16:30"
    }

# ---------------------------
# ENGINE
# ---------------------------
def run_pair(name, symbol):
    df = get_ohlc(symbol)

    structure, bias = structure_engine(df)
    regime = regime_engine(df)
    delay, trse = trse_engine(df)
    score = score_engine(structure, regime, delay)

    buy, sell, t1, t2, t3 = levels(df, bias)

    return {
        "pair": name,
        "structure": structure,
        "bias": bias,
        "regime": regime,
        "score": score,
        "delay": delay,
        "trse": trse,
        "buy": round(buy,5),
        "sell": round(sell,5),
        "t1": round(t1,5),
        "t2": round(t2,5),
        "t3": round(t3,5)
    }

# ---------------------------
# UI
# ---------------------------
st.title("🚀 TITAN FULL ENGINE")

now = datetime.now(SPAIN)
st.write(f"Spain Time: {now}")

eur = run_pair("EURUSD", "EURUSD=X")
gbp = run_pair("GBPUSD", "GBPUSD=X")

def display(d):
    st.header(d["pair"])

    st.write(f"Structure: {d['structure']}")
    st.write(f"Bias: {d['bias']}")
    st.write(f"Regime: {d['regime']}")
    st.write(f"Score: {d['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {d['buy']}")
    st.write(f"Sell: {d['sell']}")

    st.subheader("Targets")
    st.write(f"T1: {d['t1']}")
    st.write(f"T2: {d['t2']}")
    st.write(f"T3: {d['t3']}")

    st.subheader("TRSE")
    st.write(f"{d['trse']}")
    st.write(f"Delay: {d['delay']}")

    st.subheader("Time Windows")
    tw = time_windows()
    for k,v in tw.items():
        st.write(f"{k}: {v}")

display(eur)
st.divider()
display(gbp)
