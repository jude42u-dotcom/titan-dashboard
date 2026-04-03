import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import pytz

# -----------------------------
# TIME
# -----------------------------
def get_spain_time():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

# -----------------------------
# DATA FETCH
# -----------------------------
def get_ohlc(symbol):
    try:
        df = yf.download(symbol, interval="15m", period="2d", progress=False)
        df.dropna(inplace=True)
        return df
    except:
        return pd.DataFrame()

# -----------------------------
# SESSION ENGINE
# -----------------------------
def get_sessions(df):
    if df.empty:
        return None, None

    df = df.copy()
    df['hour'] = df.index.hour

    asia = df[(df['hour'] >= 0) & (df['hour'] < 7)]
    london = df[(df['hour'] >= 7) & (df['hour'] < 13)]

    return asia, london

# -----------------------------
# STRUCTURE
# -----------------------------
def detect_structure(df):
    if len(df) < 10:
        return "UNKNOWN"

    highs = df['High'].tail(5)
    lows = df['Low'].tail(5)

    if highs.iloc[-1] < highs.iloc[0] and lows.iloc[-1] < lows.iloc[0]:
        return "LFHL"
    elif highs.iloc[-1] > highs.iloc[0] and lows.iloc[-1] > lows.iloc[0]:
        return "HLHL"
    else:
        return "MIXED"

# -----------------------------
# FIRST EXTREME
# -----------------------------
def detect_first_extreme(df):
    if len(df) < 20:
        return "UNKNOWN"

    early = df.iloc[:20]

    high_time = early['High'].idxmax()
    low_time = early['Low'].idxmin()

    if high_time < low_time:
        return "HFL"  # High First
    else:
        return "LFHL" # Low First

# -----------------------------
# REGIME
# -----------------------------
def detect_regime(df):
    rng = df['High'].max() - df['Low'].min()

    if rng > 0.005:
        return "EXPANSION"
    else:
        return "COMPRESSION"

# -----------------------------
# SMART ZONES
# -----------------------------
def compute_zones(df):
    asia, london = get_sessions(df)

    if asia is None or london is None or asia.empty or london.empty:
        return 0, 0

    asia_low = asia['Low'].min()
    asia_high = asia['High'].max()

    london_high = london['High'].max()
    london_low = london['Low'].min()

    # Smart zones (not full range)
    buy_zone = asia_low
    sell_zone = london_high

    return buy_zone, sell_zone

# -----------------------------
# TARGETS
# -----------------------------
def compute_targets(buy, sell):
    if buy == 0 or sell == 0:
        return 0, 0, 0

    mid = (buy + sell) / 2

    t1 = mid
    t2 = sell - (sell - buy) * 0.25
    t3 = sell

    return round(t1, 5), round(t2, 5), round(t3, 5)

# -----------------------------
# SCORING ENGINE
# -----------------------------
def compute_score(structure, regime, extreme):
    score = 0

    if structure == "LFHL":
        score += 25

    if regime == "EXPANSION":
        score += 25

    if extreme == "HFL":
        score += 25

    # Always add base confidence
    score += 20

    return min(score, 100)

# -----------------------------
# RUN PAIR
# -----------------------------
def run_pair(name, symbol):
    df = get_ohlc(symbol)

    if df.empty:
        return None

    structure = detect_structure(df)
    regime = detect_regime(df)
    extreme = detect_first_extreme(df)

    buy, sell = compute_zones(df)
    t1, t2, t3 = compute_targets(buy, sell)

    score = compute_score(structure, regime, extreme)

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
        "t3": t3
    }

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

    st.markdown("---")
