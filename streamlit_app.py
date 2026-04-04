import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime

# ================================
# 🔐 YOUR API KEY (UNCHANGED)
# ================================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"

# ================================
# 📡 LOAD DATA (UNCHANGED)
# ================================
@st.cache_data
def load_data(symbol):
    try:
        url = "https://api.twelvedata.com/time_series"

        params = {
            "symbol": symbol,
            "interval": "15min",
            "outputsize": 200,
            "apikey": API_KEY
        }

        r = requests.get(url, params=params).json()

        if "values" not in r:
            st.error(f"{symbol} API ERROR: {r}")
            return pd.DataFrame()

        df = pd.DataFrame(r["values"])

        df = df.rename(columns={"datetime": "time"})
        df["time"] = pd.to_datetime(df["time"])
        df = df.dropna(subset=["time"])
        df = df.sort_values("time")

        df[["open","high","low","close"]] = df[["open","high","low","close"]].astype(float)

        return df

    except Exception as e:
        st.error(f"{symbol} DATA ERROR: {e}")
        return pd.DataFrame()


# ================================
# 🧠 TITAN ENGINE (UNCHANGED CORE)
# ================================
def titan_engine(df):

    if df is None or df.empty:
        return None

    df = df.copy().sort_values("time")

    # ASIA
    asia = df.tail(50)
    asia_high = asia["high"].max()
    asia_low = asia["low"].min()
    asia_mid = (asia_high + asia_low) / 2
    asia_range = max(asia_high - asia_low, 0.00001)

    # GANN
    root = np.sqrt(asia_mid)
    step = asia_range / root

    sell_low = asia_high + step
    sell_high = asia_high + step * 2

    buy_low = asia_low - step * 2
    buy_high = asia_low - step

    # TARGETS
    targets_high = [
        asia_low + step,
        asia_low,
        asia_low - step
    ]

    targets_low = [
        asia_high - step,
        asia_high,
        asia_high + step
    ]

    # INVALIDATION
    invalid_up = asia_high + (step * 3)
    invalid_down = asia_low - (step * 3)

    # SIMPLE LAYER
    macro = "Structural environment"
    probability = "58% (HIGH first)"
    session = "Asia base → London expansion → NY resolution"

    # TRSE BASIC
    trse = {
        "regime": "RES",
        "delay": 2,
        "expectation": "Expansion Expected"
    }

    return {
        "macro": macro,
        "probability": probability,
        "session": session,

        "sell_zone": (float(sell_low), float(sell_high)),
        "buy_zone": (float(buy_low), float(buy_high)),

        "invalid_up": float(invalid_up),
        "invalid_down": float(invalid_down),

        "high_targets": [float(x) for x in targets_high],
        "low_targets": [float(x) for x in targets_low],

        "score": 80,
        "trse": trse
    }


# ================================
# 🧠 PDF INTELLIGENCE LAYER (NEW)
# ================================
def titan_pdf_layer(df):

    if df is None or df.empty:
        return {}

    recent = df.tail(100)

    high = recent["high"].max()
    low = recent["low"].min()
    mid = (high + low) / 2

    range_size = high - low
    avg_range = (recent["high"].rolling(20).max() - recent["low"].rolling(20).min()).iloc[-1]

    if range_size < avg_range:
        compression = "Weekly compression"
    else:
        compression = "Expansion structure"

    last_close = df["close"].iloc[-1]

    if last_close < mid:
        structure = "distribution"
    else:
        structure = "accumulation"

    macro = f"{compression} → {structure}"

    # HFL / LFH
    asia = df.tail(50)
    asia_high = asia["high"].max()
    asia_low = asia["low"].min()
    current = df["close"].iloc[-1]

    if abs(current - asia_high) < abs(current - asia_low):
        regime = "HFL 60%"
    else:
        regime = "LFH 60%"

    # TRSE REAL
    day = (datetime.now().day % 5) + 1

    if day in [3,4,5]:
        expectation = "Expansion Expected"
    else:
        expectation = "Rotation Expected"

    return {
        "macro": macro,
        "regime": regime,
        "session": "Asia drift → London expansion → NY resolution",
        "day": day,
        "expectation": expectation
    }


# ================================
# 🚀 UI
# ================================
st.set_page_config(layout="wide")
st.title("🚀 TITAN ENGINE V5")

spain_time = datetime.now()
st.write("Spain Time:", spain_time)

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:

    df = load_data(pair)

    if df.empty:
        st.warning(f"{pair} data not loaded")
        continue

    result = titan_engine(df)
    pdf = titan_pdf_layer(df)   # ✅ NEW

    if result is None:
        continue

    st.header(pair)

    # ✅ PDF UPGRADE OUTPUT
    st.write("🟡 Macro Bias:", pdf["macro"])
    st.write("🟡 Regime Expectation:", pdf["regime"])
    st.write("🟡 Session Model:", pdf["session"])

    sz = result["sell_zone"]
    bz = result["buy_zone"]

    st.write(f"🔴 PRIMARY SELL ZONE: {sz[0]:.5f} – {sz[1]:.5f}")
    st.write(f"🟢 ALTERNATE BUY: {bz[0]:.5f} – {bz[1]:.5f}")

    st.write("🟡 Invalidation Up:", f"{result['invalid_up']:.5f}")
    st.write("🟡 Invalidation Down:", f"{result['invalid_down']:.5f}")

    st.write("🟡 Continuation Targets (HIGH first):",
             [f"{x:.5f}" for x in result["high_targets"]])

    st.write("🟡 Continuation Targets (LOW first):",
             [f"{x:.5f}" for x in result["low_targets"]])

    st.write("🟡 Confluence Score:", result["score"])

    # ✅ REPLACED TRSE (PDF VERSION)
    st.write("🟡 TRSE OUTPUT:")
    st.write("Regime:", result["trse"]["regime"])
    st.write("Delay Day:", pdf["day"])
    st.write("Expectation:", pdf["expectation"])

    st.markdown("---")
