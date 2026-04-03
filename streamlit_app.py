import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# =========================
# CONFIG
# =========================
SPAIN_TZ = pytz.timezone("Europe/Madrid")

# =========================
# DATA FETCH
# =========================
def get_ohlc(symbol):
    try:
        df = yf.download(
            symbol,
            interval="15m",
            period="5d",
            progress=False
        )

        if df is None or df.empty:
            return pd.DataFrame()

        df = df.dropna()

        if len(df) < 50:
            return pd.DataFrame()

        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC").tz_convert(SPAIN_TZ)
        else:
            df.index = df.index.tz_convert(SPAIN_TZ)

        return df

    except:
        return pd.DataFrame()

# =========================
# SESSION SPLIT
# =========================
def get_sessions(df):
    try:
        if df is None or df.empty:
            return None, None

        df = df.copy()
        df['hour'] = df.index.hour

        asia = df[(df['hour'] >= 0) & (df['hour'] < 8)]
        london = df[(df['hour'] >= 8) & (df['hour'] < 14)]

        # fallback protection
        if asia.empty:
            asia = df.iloc[:20]

        if london.empty:
            london = df.iloc[-20:]

        return asia, london

    except:
        return None, None

# =========================
# STRUCTURE
# =========================
def detect_structure(df):
    try:
        highs = df['High'].tail(10)
        lows = df['Low'].tail(10)

        if len(highs) < 2 or len(lows) < 2:
            return "UNKNOWN"

        if highs.iloc[-1] > highs.iloc[0] and lows.iloc[-1] > lows.iloc[0]:
            return "HLHL"

        if highs.iloc[-1] < highs.iloc[0] and lows.iloc[-1] < lows.iloc[0]:
            return "LFHL"

        return "UNKNOWN"

    except:
        return "UNKNOWN"

# =========================
# REGIME
# =========================
def detect_regime(df):
    try:
        rng = df['High'].max() - df['Low'].min()

        if rng > 0.005:
            return "EXPANSION"
        else:
            return "COMPRESSION"

    except:
        return "UNKNOWN"

# =========================
# ENGINE
# =========================
def run_pair(name, symbol):
    df = get_ohlc(symbol)

    if df.empty:
        return {
            "structure": "UNKNOWN",
            "bias": "neutral",
            "regime": "UNKNOWN",
            "first_extreme": "UNKNOWN",
            "score": 0,
            "buy": 0,
            "sell": 0,
            "t1": 0,
            "t2": 0,
            "t3": 0,
            "trse": "Unknown",
            "delay": 0
        }

    asia, london = get_sessions(df)

    structure = detect_structure(df)
    regime = detect_regime(df)

    try:
        asia_low = asia['Low'].min()
        asia_high = asia['High'].max()

        london_low = london['Low'].min()
        london_high = london['High'].max()

        buy = asia_low
        sell = asia_high

        t1 = (asia_low + asia_high) / 2
        t2 = london_low
        t3 = london_high

    except:
        buy = sell = t1 = t2 = t3 = 0

    score = 70 if regime == "EXPANSION" else 60

    return {
        "structure": structure,
        "bias": "bearish" if structure == "LFHL" else (
                 "bullish" if structure == "HLHL" else "neutral"
        ),
        "regime": regime,
        "first_extreme": "London Sweep",
        "score": score,
        "buy": round(buy, 5),
        "sell": round(sell, 5),
        "t1": round(t1, 5),
        "t2": round(t2, 5),
        "t3": round(t3, 5),
        "trse": "Rotation Day",
        "delay": 1
    }

# =========================
# UI
# =========================
st.set_page_config(page_title="TITAN PRO ENGINE", layout="wide")

st.title("🚀 TITAN PRO ENGINE")

now = datetime.now(SPAIN_TZ)
st.write(f"Spain Time: `{now}`")

# =========================
# RUN PAIRS
# =========================
pairs = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X"
}

for name, symbol in pairs.items():
    data = run_pair(name, symbol)

    st.header(name)

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

    st.subheader("TRSE")
    st.write(data["trse"])
    st.write(f"Delay: {data['delay']}")

    st.subheader("Time Windows")
    st.write("London 1: 08:30–10:00")
    st.write("London 2: 11:30–13:00")
    st.write("NY: 14:30–16:30")

    st.markdown("---")
