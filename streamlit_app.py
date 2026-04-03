import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# ==============================
# DATA FETCH (STABLE)
# ==============================
def get_ohlc(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1h")

        if df is None or df.empty:
            return None

        return df

    except:
        return None


# ==============================
# STRUCTURE ENGINE (HF / LF)
# ==============================
def detect_structure(df):
    highs = df["High"].tail(5).values
    lows = df["Low"].tail(5).values

    if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        return "HFL"   # Higher High / Higher Low

    elif highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        return "LFHL"  # Lower High / Lower Low

    else:
        return "RANGE"


# ==============================
# REGIME ENGINE
# ==============================
def detect_regime(df):
    rng = df["High"].max() - df["Low"].min()

    if rng > 0.010:
        return "EXPANSION"
    else:
        return "COMPRESSION"


# ==============================
# SCORE ENGINE
# ==============================
def compute_score(structure, regime):
    score = 50

    if structure == "HFL":
        score += 15
    elif structure == "LFHL":
        score += 10

    if regime == "EXPANSION":
        score += 10

    return score


# ==============================
# TRSE ENGINE (DAY + DELAY)
# ==============================
def compute_trse(df):
    closes = df["Close"].tail(4).values

    if len(closes) < 4:
        return "Trend Day 0", 0

    if closes[-1] > closes[-2] > closes[-3]:
        return "Trend Day 2", 2

    elif closes[-1] < closes[-2] < closes[-3]:
        return "Trend Day 2", 2

    else:
        return "Rotation Day", 1


# ==============================
# ZONES + TARGETS
# ==============================
def compute_levels(df):
    high = df["High"].max()
    low = df["Low"].min()

    mid = (high + low) / 2

    return {
        "buy": round(low, 5),
        "sell": round(high, 5),
        "t1": round(mid, 5),
        "t2": round(mid + (high - mid) * 0.5, 5),
        "t3": round(high, 5)
    }


# ==============================
# RUN PAIR ENGINE
# ==============================
def run_pair(name, symbol):
    df = get_ohlc(symbol)

    if df is None:
        return {
            "pair": name,
            "error": "No data"
        }

    structure = detect_structure(df)
    regime = detect_regime(df)
    score = compute_score(structure, regime)
    trse_day, delay = compute_trse(df)
    levels = compute_levels(df)

    bias = "bullish" if structure == "HFL" else "bearish"

    return {
        "pair": name,
        "structure": structure,
        "bias": bias,
        "regime": regime,
        "score": score,
        "levels": levels,
        "trse": trse_day,
        "delay": delay
    }


# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(layout="wide")

st.title("🚀 TITAN FULL ENGINE (STABLE)")

spain_time = datetime.now()
st.write(f"Spain Time: {spain_time}")

# ==============================
# RUN ENGINE
# ==============================
eur = run_pair("EURUSD", "EURUSD=X")
gbp = run_pair("GBPUSD", "GBPUSD=X")


def display(pair):
    if "error" in pair:
        st.error(f"{pair['pair']} → No data available")
        return

    st.header(pair["pair"])

    st.write(f"Structure: {pair['structure']}")
    st.write(f"Bias: {pair['bias']}")
    st.write(f"Regime: {pair['regime']}")
    st.write(f"Score: {pair['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {pair['levels']['buy']}")
    st.write(f"Sell: {pair['levels']['sell']}")

    st.subheader("Targets")
    st.write(f"T1: {pair['levels']['t1']}")
    st.write(f"T2: {pair['levels']['t2']}")
    st.write(f"T3: {pair['levels']['t3']}")

    st.subheader("TRSE")
    st.write(pair["trse"])
    st.write(f"Delay: {pair['delay']}")

    st.subheader("Time Windows")
    st.write("London 1: 08:30–10:00")
    st.write("London 2: 11:30–13:00")
    st.write("NY: 14:30–16:30")

    st.divider()


# ==============================
# DISPLAY
# ==============================
display(eur)
display(gbp)
