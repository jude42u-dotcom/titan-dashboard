import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# -----------------------------
# TIME
# -----------------------------
def get_spain_time():
    try:
        tz = pytz.timezone("Europe/Madrid")
        return datetime.now(tz)
    except:
        return datetime.now()

# -----------------------------
# DATA FETCH (SAFE)
# -----------------------------
def get_ohlc(symbol):
    try:
        df = yf.download(symbol, interval="15m", period="2d", progress=False)

        if df is None or df.empty:
            return pd.DataFrame()

        df.dropna(inplace=True)

        return df
    except:
        return pd.DataFrame()

# -----------------------------
# SESSION SPLIT
# -----------------------------
def get_sessions(df):
    try:
        if df is None or df.empty:
            return None, None

        df = df.copy()
        df['hour'] = df.index.hour

        asia = df[(df['hour'] >= 0) & (df['hour'] < 7)]
        london = df[(df['hour'] >= 7) & (df['hour'] < 13)]

        return asia, london
    except:
        return None, None

# -----------------------------
# STRUCTURE (SAFE)
# -----------------------------
def detect_structure(df):
    try:
        if df is None or len(df) < 10:
            return "UNKNOWN"

        highs = df['High'].tail(5)
        lows = df['Low'].tail(5)

        if len(highs) < 2 or len(lows) < 2:
            return "UNKNOWN"

        h0 = highs.iloc[0]
        h1 = highs.iloc[-1]

        l0 = lows.iloc[0]
        l1 = lows.iloc[-1]

        if h1 < h0 and l1 < l0:
            return "LFHL"
        elif h1 > h0 and l1 > l0:
            return "HLHL"
        else:
            return "MIXED"

    except:
        return "UNKNOWN"

# -----------------------------
# FIRST EXTREME (SAFE)
# -----------------------------
def detect_first_extreme(df):
    try:
        if df is None or len(df) < 20:
            return "UNKNOWN"

        early = df.iloc[:20]

        if early.empty:
            return "UNKNOWN"

        high_time = early['High'].idxmax()
        low_time = early['Low'].idxmin()

        if high_time < low_time:
            return "HFL"
        else:
            return "LFHL"

    except:
        return "UNKNOWN"

# -----------------------------
# REGIME
# -----------------------------
def detect_regime(df):
    try:
        if df is None or df.empty:
            return "UNKNOWN"

        rng = df['High'].max() - df['Low'].min()

        if rng > 0.005:
            return "EXPANSION"
        else:
            return "COMPRESSION"
    except:
        return "UNKNOWN"

# -----------------------------
# ZONES (SMART)
# -----------------------------
def compute_zones(df):
    try:
        asia, london = get_sessions(df)

        if asia is None or london is None:
            return 0, 0

        if asia.empty or london.empty:
            return 0, 0

        asia_low = asia['Low'].min()
        london_high = london['High'].max()

        return float(asia_low), float(london_high)

    except:
        return 0, 0

# -----------------------------
# TARGETS
# -----------------------------
def compute_targets(buy, sell):
    try:
        if buy == 0 or sell == 0:
            return 0, 0, 0

        mid = (buy + sell) / 2

        t1 = mid
        t2 = sell - (sell - buy) * 0.25
        t3 = sell

        return round(t1, 5), round(t2, 5), round(t3, 5)

    except:
        return 0, 0, 0

# -----------------------------
# SCORING
# -----------------------------
def compute_score(structure, regime, extreme):
    try:
        score = 0

        if structure == "LFHL":
            score += 25

        if regime == "EXPANSION":
            score += 25

        if extreme == "HFL":
            score += 25

        score += 20

        return min(score, 100)

    except:
        return 0

# -----------------------------
# TRSE (BASIC)
# -----------------------------
def compute_trse(df):
    try:
        if df is None or len(df) < 30:
            return "Rotation Day", 1

        rng = df['High'].max() - df['Low'].min()

        if rng > 0.006:
            return "Trend Day", 0
        else:
            return "Rotation Day", 1

    except:
        return "Unknown", 0

# -----------------------------
# RUN PAIR
# -----------------------------
def run_pair(name, symbol):
    try:
        df = get_ohlc(symbol)

        if df.empty:
            return None

        structure = detect_structure(df)
        regime = detect_regime(df)
        extreme = detect_first_extreme(df)

        buy, sell = compute_zones(df)
        t1, t2, t3 = compute_targets(buy, sell)

        score = compute_score(structure, regime, extreme)
        trse_day, delay = compute_trse(df)

        return {
            "pair": name,
            "structure": structure,
            "bias": "bearish" if structure == "LFHL" else "bullish",
            "regime": regime,
            "extreme": extreme,
            "score": score,
            "buy": round(buy, 5),
            "sell": round(sell, 5),
            "t1": t1,
            "t2": t2,
            "t3": t3,
            "trse": trse_day,
            "delay": delay
        }

    except:
        return None

# -----------------------------
# UI
# -----------------------------
st.set_page_config(layout="wide")

st.title("🚀 TITAN PRO ENGINE")

now = get_spain_time()
st.write(f"Spain Time: `{now}`")

pairs = [
    ("EURUSD", "EURUSD=X"),
    ("GBPUSD", "GBPUSD=X")
]

for name, symbol in pairs:
    data = run_pair(name, symbol)

    if data is None:
        st.error(f"{name} data failed")
        continue

    st.header(name)

    st.write(f"Structure: {data['structure']}")
    st.write(f"Bias: {data['bias']}")
    st.write(f"Regime: {data['regime']}")
    st.write(f"First Extreme: {data['extreme']}")
    st.write(f"Score: {data['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {data['buy']}")
    st.write(f"Sell: {data['sell']}")

    st.subheader("Targets")
    st.write(f"T1: {data['t1']}")
    st.write(f"T2: {data['t2']}")
    st.write(f"T3: {data['t3']}")

    st.subheader("TRSE")
    st.write(f"{data['trse']}")
    st.write(f"Delay: {data['delay']}")

    st.subheader("Time Windows")
    st.write("London 1: 08:30–10:00")
    st.write("London 2: 11:30–13:00")
    st.write("NY: 14:30–16:30")

    st.markdown("---")
