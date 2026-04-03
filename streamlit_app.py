import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import math

# =========================
# TIME ENGINE (FOREVER)
# =========================
def calculate_time_windows(anchor_time):
    harmonics = [0.125, 0.167, 0.25, 0.333]

    windows = []
    for h in harmonics:
        delta = timedelta(hours=24 * h)
        t = anchor_time + delta
        windows.append((t - timedelta(minutes=45), t + timedelta(minutes=45)))

    return windows


# =========================
# GEOMETRY ENGINE (ANGLES)
# =========================
def detect_angle(price_move, time_move):
    slope = price_move / time_move if time_move != 0 else 0

    if abs(slope) < 0.5:
        return "1x2"
    elif abs(slope) < 1.2:
        return "1x1"
    else:
        return "2x1"


# =========================
# STRUCTURE ENGINE (SAM)
# =========================
def calculate_targets(p1, p2):
    r = p2 - p1

    return {
        "T1": p2 + r,
        "T2": p2 + 1.272 * r,
        "T3": p2 + 1.618 * r
    }


# =========================
# TRSE ENGINE
# =========================
def classify_trse(df):
    highs = df['high']
    lows = df['low']

    failures = 0

    for i in range(1, len(df)):
        if highs[i] < highs[i-1] and lows[i] > lows[i-1]:
            failures += 1

    if failures <= 1:
        return "RES", 0, "Rotation Expected"
    elif failures <= 5:
        return f"RDS Day {failures}", failures, "Rotation Building"
    else:
        return "PCS", failures, "Continuation Likely"


# =========================
# DEM / RPI
# =========================
def volatility_state(df):
    ranges = df['high'] - df['low']
    avg = ranges.mean()
    last = ranges.iloc[-1]

    if last > avg * 1.2:
        return "Expansion"
    elif last < avg * 0.8:
        return "Compression"
    else:
        return "Normal"


# =========================
# LECE PROBABILITY
# =========================
def confluence_score(volatility, trse_state):
    score = 50

    if volatility == "Expansion":
        score += 20
    if "RDS" in trse_state:
        score += 10
    if "RES" in trse_state:
        score += 20

    return min(score, 100)


# =========================
# MAIN TITAN ENGINE
# =========================
def run_titan(pair):

    # MOCK DATA (replace later with API)
    prices = np.random.rand(10) * 0.01 + (1.08 if pair=="EURUSD" else 1.26)
    df = pd.DataFrame({
        "high": prices + 0.002,
        "low": prices - 0.002
    })

    # TRSE
    regime, day, expectation = classify_trse(df)

    # Volatility
    vol = volatility_state(df)

    # Structure
    p1 = df['low'].iloc[-2]
    p2 = df['high'].iloc[-1]

    targets = calculate_targets(p1, p2)

    # Time
    now = datetime.now(pytz.timezone("Europe/Madrid"))
    windows = calculate_time_windows(now)

    # Score
    score = confluence_score(vol, regime)

    return {
        "pair": pair,
        "regime": regime,
        "day": day,
        "expectation": expectation,
        "targets": targets,
        "score": score,
        "windows": windows,
        "buy": p1,
        "sell": p2
    }


# =========================
# STREAMLIT UI
# =========================
st.set_page_config(layout="wide")

st.title("🚀 TITAN PRO ENGINE")

now = datetime.now(pytz.timezone("Europe/Madrid"))
st.write(f"Spain Time: {now}")

pairs = ["EURUSD", "GBPUSD"]

for pair in pairs:
    data = run_titan(pair)

    st.header(pair)

    st.write(f"Structure: {data['regime']}")
    st.write(f"Score: {data['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {round(data['buy'],5)}")
    st.write(f"Sell: {round(data['sell'],5)}")

    st.subheader("Targets")
    st.write(data["targets"])

    st.subheader("Time Windows")
    for w in data["windows"]:
        st.write(f"{w[0].time()} - {w[1].time()}")

    st.subheader("TRSE")
    st.write(f"{data['regime']} | Day {data['day']}")
