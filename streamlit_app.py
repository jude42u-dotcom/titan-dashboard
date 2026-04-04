import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_KEY = st.secrets["TWELVEDATA_API_KEY"]

# ---------------- DATA ---------------- #
def get_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=15min&outputsize=200&apikey={API_KEY}"
    r = requests.get(url).json()

    if "values" not in r:
        return None

    df = pd.DataFrame(r["values"])
    df = df.astype(float)
    df = df.iloc[::-1]
    return df

# ---------------- CORE ENGINE ---------------- #

def detect_structure(df):
    highs = df["high"]
    lows = df["low"]

    last_high = highs.iloc[-1]
    prev_high = highs.iloc[-5]

    last_low = lows.iloc[-1]
    prev_low = lows.iloc[-5]

    if last_high > prev_high and last_low > prev_low:
        return "BULLISH_STRUCTURE"
    elif last_high < prev_high and last_low < prev_low:
        return "BEARISH_STRUCTURE"
    else:
        return "RANGE"

def volatility_state(df):
    rng = df["high"].max() - df["low"].min()
    avg = (df["high"] - df["low"]).mean()

    if rng > avg * 8:
        return "EXPANSION"
    return "COMPRESSION"

def regime_expectation(df):
    # simplified LFHL / HFL model
    recent = df.tail(20)
    highs = recent["high"]
    lows = recent["low"]

    if highs.idxmax() < lows.idxmin():
        return "HFL"
    return "LFHL"

def build_zones(df):
    high = df["high"].max()
    low = df["low"].min()
    mid = (high + low) / 2

    return {
        "sell_zone": (high - (high-mid)*0.3, high),
        "buy_zone": (low, low + (mid-low)*0.3),
        "mid": mid
    }

def targets(zone, direction):
    z_low, z_high = zone

    if direction == "HIGH_FIRST":
        return [
            round(z_low * 0.998, 5),
            round(z_low * 0.995, 5),
            round(z_low * 0.992, 5),
        ]
    else:
        return [
            round(z_high * 1.002, 5),
            round(z_high * 1.005, 5),
            round(z_high * 1.008, 5),
        ]

def trse_logic(volatility):
    if volatility == "EXPANSION":
        return "RDS", 1, "Trend Continuation Expected"
    return "RES", 0, "Rotation Expected"

def confluence(structure, volatility):
    score = 50

    if structure == "BULLISH_STRUCTURE":
        score += 15
    elif structure == "BEARISH_STRUCTURE":
        score += 15

    if volatility == "EXPANSION":
        score += 20
    else:
        score -= 10

    return max(0, min(100, score))

# ---------------- UI ---------------- #

st.set_page_config(layout="wide")

st.title("🚀 TITAN ENGINE")

st.write("Spain Time:", datetime.now())

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    df = get_data(pair)

    if df is None:
        st.error("DATA ERROR")
        continue

    structure = detect_structure(df)
    volatility = volatility_state(df)
    regime = regime_expectation(df)
    zones = build_zones(df)

    direction = "HIGH_FIRST" if regime == "HFL" else "LOW_FIRST"

    sell_zone = zones["sell_zone"]
    buy_zone = zones["buy_zone"]

    t_high = targets(sell_zone, "HIGH_FIRST")
    t_low = targets(buy_zone, "LOW_FIRST")

    trse_regime, delay, expectation = trse_logic(volatility)

    score = confluence(structure, volatility)

    # ---------------- DISPLAY ---------------- #

    st.header(pair)

    st.write("Macro Bias:", structure)
    st.write("Regime Expectation:", regime)
    st.write("Session Model: Asia → London → NY")

    st.write(f"🔴 PRIMARY SELL ZONE: {sell_zone[0]:.5f} – {sell_zone[1]:.5f}")
    st.write(f"🟢 PRIMARY BUY ZONE: {buy_zone[0]:.5f} – {buy_zone[1]:.5f}")

    st.write("Invalidation Up:", round(sell_zone[1]*1.001,5))
    st.write("Invalidation Down:", round(buy_zone[0]*0.999,5))

    st.write("Continuation Targets (HIGH first):")
    st.write("T1:", t_high[0], "T2:", t_high[1], "T3:", t_high[2])

    st.write("Continuation Targets (LOW first):")
    st.write("T1:", t_low[0], "T2:", t_low[1], "T3:", t_low[2])

    st.write("London Windows: 08:10–09:40 / 10:30–11:50")
    st.write("NY Window: 14:30–15:45")

    st.write("Confluence Score:", score, "/ 100")

    st.write("TRSE OUTPUT:")
    st.write("Regime:", trse_regime)
    st.write("Delay Day:", delay)
    st.write("Expectation:", expectation)

    st.divider()
