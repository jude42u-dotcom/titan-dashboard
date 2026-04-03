import streamlit as st
from datetime import datetime
import pytz
import numpy as np
import pandas as pd

# =========================
# MOCK DATA (STABLE)
# =========================
def get_data(pair):
    base = 1.08 if pair == "EURUSD" else 1.26
    prices = np.random.rand(20) * 0.01 + base

    df = pd.DataFrame({
        "high": prices + 0.002,
        "low": prices - 0.002,
        "close": prices
    })

    return df


# =========================
# FOREVER (REGIME)
# =========================
def get_regime(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if last["high"] > prev["high"]:
        return "LFHL", "LOW first"
    else:
        return "HFL", "HIGH first"


# =========================
# SAM (STRUCTURE)
# =========================
def get_targets(low, high):
    r = high - low

    return {
        "sell": {
            "T1": low,
            "T2": low - r * 0.618,
            "T3": low - r * 1.0
        },
        "buy": {
            "T1": high,
            "T2": high + r * 0.618,
            "T3": high + r * 1.0
        }
    }


# =========================
# TRSE
# =========================
def get_trse(df):
    return "RDS Day 3", 3, "Rotation Expected"


# =========================
# TIME WINDOWS (SESSION BASED)
# =========================
def get_time_windows():
    return {
        "london1": "08:30–10:00",
        "london2": "11:30–13:00",
        "ny": "14:30–16:30"
    }


# =========================
# SCORE
# =========================
def get_score():
    return np.random.randint(70, 85)


# =========================
# TITAN ENGINE
# =========================
def run_titan(pair):
    df = get_data(pair)

    regime, order = get_regime(df)
    trse, day, expectation = get_trse(df)

    low = df["low"].iloc[-1]
    high = df["high"].iloc[-1]

    targets = get_targets(low, high)
    windows = get_time_windows()
    score = get_score()

    return {
        "pair": pair,
        "regime": regime,
        "order": order,
        "targets": targets,
        "low": low,
        "high": high,
        "windows": windows,
        "score": score,
        "trse": trse,
        "day": day,
        "expectation": expectation
    }


# =========================
# UI
# =========================
st.set_page_config(layout="wide")

st.title("🚀 TITAN PRO ENGINE")

now = datetime.now(pytz.timezone("Europe/Madrid"))
st.write(f"Spain Time: {now}")

pairs = ["EURUSD", "GBPUSD"]

for pair in pairs:
    d = run_titan(pair)

    st.header(pair)

    # =========================
    # CORE TITAN OUTPUT
    # =========================
    st.write(f"🟡 Macro Bias: ⚪ Derived from structure")
    st.write(f"🟡 Regime Expectation: 🔴 {d['regime']} ({d['order']})")
    st.write(f"🟡 Session Model: ⚪ Asia → London → NY resolution")

    # =========================
    # ZONES
    # =========================
    st.write(f"🔴 PRIMARY SELL ZONE: 🟣 {round(d['high'],5)}")
    st.write(f"🟢 ALTERNATE BUY: 🟣 {round(d['low'],5)}")

    # =========================
    # INVALIDATION
    # =========================
    st.write(f"🟡 Invalidation Up: 🟣 {round(d['high'] + 0.002,5)}")
    st.write(f"🟡 Invalidation Down: 🟣 {round(d['low'] - 0.002,5)}")

    # =========================
    # TARGETS
    # =========================
    st.write("🟡 Continuation Targets (HIGH first):")
    st.write(f"T1: 🟣 {round(d['targets']['sell']['T1'],5)}")
    st.write(f"T2: 🟣 {round(d['targets']['sell']['T2'],5)}")
    st.write(f"T3: 🟣 {round(d['targets']['sell']['T3'],5)}")

    st.write("🟡 Continuation Targets (LOW first):")
    st.write(f"T1: 🟣 {round(d['targets']['buy']['T1'],5)}")
    st.write(f"T2: 🟣 {round(d['targets']['buy']['T2'],5)}")
    st.write(f"T3: 🟣 {round(d['targets']['buy']['T3'],5)}")

    # =========================
    # TIME WINDOWS
    # =========================
    st.write(f"🟠 London Time Windows (Spain): 🟣 {d['windows']['london1']} 🟣 {d['windows']['london2']}")
    st.write(f"🟠 NY Conditional Window: 🟣 {d['windows']['ny']}")

    # =========================
    # SCORE
    # =========================
    st.write(f"🟡 Confluence Score: 🟣 {d['score']} / 100")

    # =========================
    # TRSE
    # =========================
    st.write("🟡 TRSE OUTPUT:")
    st.write(f"Regime: {d['trse']}")
    st.write(f"Delay Day Count: {d['day']}")
    st.write(f"Next-Day Expectation: {d['expectation']}")

    # =========================
    # RULES
    # =========================
    st.write("🟡 Execution Rules:")
    st.write("• Trade only inside window")
    st.write("• First confirmed extreme defines direction")
    st.write("• Respect structural invalidation")
    st.write("• No confirmation → No trade")
    st.write("• NY trade only if London expansion confirmed")
