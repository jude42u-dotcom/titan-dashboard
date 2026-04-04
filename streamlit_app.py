import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# =========================
# TIME
# =========================
def spain_time():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

# =========================
# DATA
# =========================
def get_data(pair):
    df = yf.download(pair, period="7d", interval="15m")
    df = df.dropna()
    return df

# =========================
# MACRO STRUCTURE
# =========================
def macro_bias(df):
    highs = df["High"]

    if len(highs) < 5:
        return "NEUTRAL"

    if highs.iloc[-1] < highs.iloc[-5]:
        return "BEARISH"
    elif highs.iloc[-1] > highs.iloc[-5]:
        return "BULLISH"
    else:
        return "NEUTRAL"

# =========================
# ZONES (PRECISION LOCKED)
# =========================
def compute_zones(df):
    high = df["High"].iloc[-1]
    low = df["Low"].iloc[-1]

    buy = low + (high - low) * 0.25
    sell = high - (high - low) * 0.25

    return buy, sell

# =========================
# TARGETS (NO ROUNDING)
# =========================
def compute_targets(price):
    return {
        "T1": price * 0.998,
        "T2": price * 0.996,
        "T3": price * 0.994
    }

def compute_targets_up(price):
    return {
        "T1": price * 1.002,
        "T2": price * 1.004,
        "T3": price * 1.006
    }

# =========================
# TIME WINDOWS (DYNAMIC)
# =========================
def compute_time_windows():
    now = spain_time()

    base = now.replace(hour=0, minute=0, second=0, microsecond=0)

    windows = []
    offsets = [52, 112, 232, 351]  # minutes (example cycle spacing)

    for o in offsets:
        start = base + timedelta(minutes=o)
        end = start + timedelta(minutes=90)
        windows.append((start.time(), end.time()))

    return windows

# =========================
# TRSE ENGINE
# =========================
def trse():
    return {
        "regime": "RDS Day 3",
        "delay": 3,
        "next": "Rotation Expected"
    }

# =========================
# CORE TITAN ENGINE
# =========================
def titan(pair):
    df = get_data(pair)

    macro = macro_bias(df)

    buy, sell = compute_zones(df)

    targets_down = compute_targets(sell)
    targets_up = compute_targets_up(buy)

    windows = compute_time_windows()

    trse_out = trse()

    return {
        "macro": macro,
        "buy": buy,
        "sell": sell,
        "targets_down": targets_down,
        "targets_up": targets_up,
        "windows": windows,
        "trse": trse_out
    }

# =========================
# DISPLAY
# =========================
def show(pair):
    r = titan(pair)

    st.header(pair)

    st.write(f"🟡 Macro Bias: {r['macro']}")
    st.write(f"🔴 PRIMARY SELL ZONE: {r['sell']}")
    st.write(f"🟢 ALTERNATE BUY: {r['buy']}")

    st.write(f"🟡 Invalidation Up: {r['sell'] * 1.002}")
    st.write(f"🟡 Invalidation Down: {r['buy'] * 0.998}")

    st.write("🟡 Continuation Targets (HIGH first):")
    for k, v in r["targets_down"].items():
        st.write(f"{k}: {v}")

    st.write("🟡 Continuation Targets (LOW first):")
    for k, v in r["targets_up"].items():
        st.write(f"{k}: {v}")

    st.write("🟠 Time Windows:")
    for w in r["windows"]:
        st.write(f"{w[0]} - {w[1]}")

    st.write("🟡 TRSE OUTPUT:")
    st.write(f"Regime: {r['trse']['regime']}")
    st.write(f"Delay Day Count: {r['trse']['delay']}")
    st.write(f"Next-Day Expectation: {r['trse']['next']}")

    st.write("🟡 Execution Rules:")
    st.write("• Trade only inside window")
    st.write("• First confirmed extreme defines direction")
    st.write("• Respect structural invalidation")
    st.write("• No confirmation → No trade")
    st.write("• NY trade only if London expansion confirmed")

# =========================
# APP
# =========================
st.title("🚀 TITAN PRO ENGINE")

st.write(f"Spain Time: {spain_time()}")

show("EURUSD=X")
show("GBPUSD=X")
