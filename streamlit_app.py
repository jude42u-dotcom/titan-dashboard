import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ================================
# LOAD DATA (YOU MUST ADAPT THIS)
# ================================
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")  # <-- change to your source

    # REQUIRED COLUMNS: time, high, low, close
    df["time"] = pd.to_datetime(df["time"], utc=True)
    df["time"] = df["time"].dt.tz_convert("Europe/Madrid").dt.tz_localize(None)

    return df


# ================================
# TRSE ENGINE
# ================================
def trse_engine(df):

    df["date"] = df["time"].dt.date

    daily = df.groupby("date").agg({
        "high": "max",
        "low": "min",
        "close": "last"
    }).reset_index()

    if len(daily) < 5:
        return {"regime": "UNKNOWN", "delay": 0, "expectation": "None"}

    ranges = daily["high"] - daily["low"]
    recent = ranges.tail(3)

    compression = recent.max() < ranges.mean()
    expansion = recent.iloc[-1] > recent.mean()

    delay = 0
    for i in range(len(ranges)-1, 0, -1):
        if ranges.iloc[i] < ranges.iloc[i-1]:
            delay += 1
        else:
            break

    if compression:
        regime = f"RDS Day {min(delay,5)}"
        expectation = "Rotation"
    elif expansion:
        regime = "EXPANSION"
        expectation = "Trend"
    else:
        regime = "TRANSITION"
        expectation = "Mixed"

    return {
        "regime": regime,
        "delay": delay,
        "expectation": expectation
    }


# ================================
# WEEKLY BIAS
# ================================
def weekly_bias(df):

    df["week"] = df["time"].dt.isocalendar().week

    weekly = df.groupby("week").agg({
        "high": "max",
        "low": "min"
    }).reset_index()

    if len(weekly) < 3:
        return "Structural environment"

    last = weekly.iloc[-1]
    prev = weekly.iloc[-2]

    if last["high"] < prev["high"]:
        return "Weekly compression → bearish pressure"
    elif last["low"] > prev["low"]:
        return "Weekly compression → bullish pressure"
    else:
        return "Expansion structure"


# ================================
# SESSION MODEL
# ================================
def session_model(df):

    asia = df[(df["time"].dt.hour >= 0) & (df["time"].dt.hour < 7)]
    london = df[(df["time"].dt.hour >= 7) & (df["time"].dt.hour < 13)]

    if len(asia) < 5 or len(london) < 5:
        return "Standard flow"

    asia_range = asia["high"].max() - asia["low"].min()
    london_range = london["high"].max() - london["low"].min()

    if london_range > asia_range * 1.5:
        return "London expansion → continuation"
    elif london_range < asia_range:
        return "Asia drift → London trap → NY resolution"
    else:
        return "Balanced session flow"


# ================================
# TITAN CORE (FIXED)
# ================================
def titan_core(df):

    df = df.sort_values("time")

    asia_df = df[(df["time"].dt.hour >= 0) & (df["time"].dt.hour < 7)]

    # 🔥 CRITICAL FIX (fallback)
    if len(asia_df) < 10:
        asia_df = df.tail(50)

    asia_high = asia_df["high"].max()
    asia_low = asia_df["low"].min()
    asia_mid = (asia_high + asia_low) / 2

    anchor = asia_mid
    asia_range = max(asia_high - asia_low, 0.0005)

    root = np.sqrt(anchor)
    step = asia_range / root

    # GANN LEVELS
    g1 = (root + step) ** 2
    g2 = (root + 2*step) ** 2
    g3 = (root + 3*step) ** 2

    g_1 = (root - step) ** 2
    g_2 = (root - 2*step) ** 2
    g_3 = (root - 3*step) ** 2

    # DEM CAP
    max_ext = asia_range * 2.2
    cap = lambda x: max(min(x, anchor + max_ext), anchor - max_ext)

    g1, g2, g3 = cap(g1), cap(g2), cap(g3)
    g_1, g_2, g_3 = cap(g_1), cap(g_2), cap(g_3)

    last = df.iloc[-1]

    if abs(last["high"] - asia_high) > abs(last["low"] - asia_low):
        regime = "HFL"
    else:
        regime = "LFL"

    return {
        "regime": regime,
        "sell_zone": (g1, g2),
        "buy_zone": (g_2, g_1),
        "targets": [g1, g2, g3] if regime == "LFL" else [g_1, g_2, g_3],
        "asia_high": asia_high,
        "asia_low": asia_low,
        "range": asia_range
    }


# ================================
# FINAL ENGINE
# ================================
def titan_engine(df):

    core = titan_core(df)
    trse = trse_engine(df)
    macro = weekly_bias(df)
    session = session_model(df)

    invalid_up = core["asia_high"] + core["range"] * 0.3
    invalid_down = core["asia_low"] - core["range"] * 0.3

    score = 50
    if "compression" in macro:
        score += 10
    if core["regime"] == "HFL":
        score += 10
    if trse["delay"] >= 2:
        score += 10

    return {
        "macro": macro,
        "session": session,
        "regime": core["regime"],
        "sell_zone": core["sell_zone"],
        "buy_zone": core["buy_zone"],
        "targets": core["targets"],
        "invalid_up": invalid_up,
        "invalid_down": invalid_down,
        "london_windows": "08:30–09:30 / 11:00–12:30",
        "ny_window": "14:30–16:00",
        "score": min(score, 100),
        "trse": trse
    }


# ================================
# STREAMLIT UI
# ================================
st.title("🚀 TITAN ENGINE V3")

df = load_data()

st.write("Spain Time:", datetime.now())

try:
    result = titan_engine(df)
except Exception as e:
    st.error(f"ENGINE ERROR: {e}")
    st.stop()

if result is None:
    st.error("No valid output")
    st.stop()

# DISPLAY
st.header("EUR/USD")

st.write("Macro Bias:", result["macro"])
st.write("Session:", result["session"])
st.write("Regime:", result["regime"])

st.write("SELL:", result["sell_zone"])
st.write("BUY:", result["buy_zone"])

st.write("Invalidation Up:", result["invalid_up"])
st.write("Invalidation Down:", result["invalid_down"])

st.write("Targets:", result["targets"])

st.write("London:", result["london_windows"])
st.write("NY:", result["ny_window"])

st.write("Score:", result["score"])

st.subheader("TRSE")
st.write("Regime:", result["trse"]["regime"])
st.write("Delay:", result["trse"]["delay"])
st.write("Expectation:", result["trse"]["expectation"])
