import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

# =========================
# DATA ENGINE (FIXED)
# =========================
def get_ohlc(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1h", progress=False)

        if df is None or df.empty:
            return None

        # Flatten MultiIndex if exists
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Normalize columns
        df.columns = [c.lower() for c in df.columns]

        required = ["open", "high", "low", "close"]
        if not all(col in df.columns for col in required):
            return None

        df = df[required].astype(float).dropna()

        if df.empty:
            return None

        return df

    except:
        return None


# =========================
# STRUCTURE ENGINE
# =========================
def detect_structure(df):
    highs = df["high"].tail(5).values
    lows = df["low"].tail(5).values

    if highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        return "LFHL", "bearish"
    elif highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        return "HFHL", "bullish"
    else:
        return "RANGE", "neutral"


# =========================
# REGIME ENGINE
# =========================
def detect_regime(df):
    rng = df["high"].max() - df["low"].min()

    if rng > 0.010:
        return "EXPANSION", 70
    else:
        return "COMPRESSION", 60


# =========================
# LEVEL ENGINE
# =========================
def compute_levels(df):
    try:
        high = df["high"].max()
        low = df["low"].min()

        if high == 0 or low == 0:
            return None

        mid = (high + low) / 2

        return {
            "buy": round(low, 5),
            "sell": round(high, 5),
            "t1": round(mid, 5),
            "t2": round(mid + (high - mid) * 0.5, 5),
            "t3": round(high, 5)
        }

    except:
        return None


# =========================
# TRSE ENGINE
# =========================
def compute_trse(df):
    closes = df["close"].tail(3).values

    if len(closes) < 3:
        return "Unknown", 0

    if closes[-1] > closes[-2] > closes[-3]:
        return "Trend Day", 2
    elif closes[-1] < closes[-2] < closes[-3]:
        return "Trend Day", 2
    else:
        return "Rotation Day", 1


# =========================
# RUN ENGINE
# =========================
def run_pair(name, symbol):
    df = get_ohlc(symbol)

    if df is None:
        return None

    structure, bias = detect_structure(df)
    regime, score = detect_regime(df)
    levels = compute_levels(df)
    trse, delay = compute_trse(df)

    return {
        "pair": name,
        "structure": structure,
        "bias": bias,
        "regime": regime,
        "score": score,
        "levels": levels,
        "trse": trse,
        "delay": delay
    }


# =========================
# DISPLAY ENGINE
# =========================
def display(pair):
    if pair is None:
        st.error("Data not available")
        return

    st.header(pair["pair"])

    st.write(f"Structure: {pair['structure']}")
    st.write(f"Bias: {pair['bias']}")
    st.write(f"Regime: {pair['regime']}")
    st.write(f"Score: {pair['score']}")

    if pair["levels"] is None:
        st.warning("No valid price data")
        return

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


# =========================
# MAIN APP
# =========================
st.set_page_config(page_title="TITAN FULL ENGINE", layout="centered")

st.title("🚀 TITAN FULL ENGINE (STABLE)")
st.write("Spain Time:", datetime.now())

eur = run_pair("EURUSD", "EURUSD=X")
gbp = run_pair("GBPUSD", "GBPUSD=X")

display(eur)
st.divider()
display(gbp)
