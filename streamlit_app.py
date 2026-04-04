import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime, timedelta

# ==============================
# 🔐 YOUR API KEY
# ==============================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"

# ==============================
# 📡 LOAD DATA (LIVE API)
# ==============================
@st.cache_data
def load_data():
    try:
        url = "https://api.twelvedata.com/time_series"

        params = {
            "symbol": "EUR/USD",
            "interval": "15min",
            "outputsize": 200,
            "apikey": API_KEY
        }

        r = requests.get(url, params=params).json()

        if "values" not in r:
            st.error(f"API ERROR: {r}")
            return pd.DataFrame()

        df = pd.DataFrame(r["values"])

        df = df.rename(columns={
            "datetime": "time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close"
        })

        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])
        df = df.sort_values("time")

        df[["open","high","low","close"]] = df[["open","high","low","close"]].astype(float)

        return df

    except Exception as e:
        st.error(f"DATA ERROR: {e}")
        return pd.DataFrame()

# ==============================
# 🧠 TITAN V5 ENGINE
# ==============================
def titan_engine(df):

    if df is None or df.empty:
        return None

    df = df.copy().sort_values("time")

    # =========================
    # 1. ASIA STRUCTURE
    # =========================
    asia = df.tail(50)

    asia_high = asia["high"].max()
    asia_low = asia["low"].min()
    asia_mid = (asia_high + asia_low) / 2
    asia_range = max(asia_high - asia_low, 0.0005)

    # =========================
    # 2. GANN GEOMETRY
    # =========================
    root = np.sqrt(asia_mid)
    step = asia_range / root

    angles = {
        "45°": (root + step) ** 2,
        "90°": (root + 2*step) ** 2,
        "135°": (root + 3*step) ** 2,
        "-45°": (root - step) ** 2,
        "-90°": (root - 2*step) ** 2,
        "-135°": (root - 3*step) ** 2
    }

    # CAP EXTREME LEVELS
    cap_range = asia_range * 2.2
    def cap(x):
        return max(min(x, asia_mid + cap_range), asia_mid - cap_range)

    angles = {k: round(cap(v),5) for k,v in angles.items()}

    # =========================
    # 3. REGIME
    # =========================
    last = df.iloc[-1]

    move_up = abs(last["high"] - asia_high)
    move_down = abs(last["low"] - asia_low)

    if move_up > move_down:
        regime = "HFL"
        probability = 58
    else:
        regime = "LFL"
        probability = 62

    # =========================
    # 4. ZONES
    # =========================
    sell_zone = (angles["45°"], angles["90°"])
    buy_zone = (angles["-90°"], angles["-45°"])

    sell_reason = "45°–90° Gann resistance + Asia high"
    buy_reason = "-90°–-45° Gann support + Asia low"

    # =========================
    # 5. TARGETS
    # =========================
    high_targets = [
        angles["-45°"],
        angles["-90°"],
        angles["-135°"]
    ]

    low_targets = [
        angles["45°"],
        angles["90°"],
        angles["135°"]
    ]

    # =========================
    # 6. INVALIDATION
    # =========================
    invalid_up = round(asia_high + asia_range * 0.3,5)
    invalid_down = round(asia_low - asia_range * 0.3,5)

    # =========================
    # 7. TRSE
    # =========================
    ranges = (df["high"] - df["low"]).tail(8)

    delay = 0
    for i in range(len(ranges)-1, 0, -1):
        if ranges.iloc[i] < ranges.iloc[i-1]:
            delay += 1
        else:
            break

    if delay >= 3:
        trse_regime = f"RDS Day {delay}"
        expectation = "Rotation Expected"
    else:
        trse_regime = "RES"
        expectation = "Expansion Expected"

    # =========================
    # 8. SESSION
    # =========================
    session = "Asia base → London expansion → NY resolution"

    # =========================
    # 9. SCORE
    # =========================
    score = 0

    score += 20  # structure

    if abs(asia_mid - angles["45°"]) < asia_range:
        score += 15

    if probability >= 60:
        score += 15
    else:
        score += 10

    if delay >= 2:
        score += 15

    if asia_range > 0.001:
        score += 15

    if abs(last["close"] - asia_mid) < asia_range:
        score += 20

    score = min(score, 100)

    # =========================
    # OUTPUT
    # =========================
    return {
        "macro": "Structural environment",
        "probability": f"{probability}% ({'HIGH' if regime=='HFL' else 'LOW'} first)",
        "session": session,
        "regime": regime,

        "sell_zone": sell_zone,
        "sell_reason": sell_reason,

        "buy_zone": buy_zone,
        "buy_reason": buy_reason,

        "invalid_up": invalid_up,
        "invalid_down": invalid_down,

        "high_targets": high_targets,
        "low_targets": low_targets,

        "score": score,

        "trse": {
            "regime": trse_regime,
            "delay": delay,
            "expectation": expectation
        }
    }

# ==============================
# UI
# ==============================
st.title("🚀 TITAN V5 — INSTITUTIONAL ENGINE")

st.write("Spain Time:", datetime.utcnow() + timedelta(hours=2))

df = load_data()

if df.empty:
    st.error("No data loaded")
    st.stop()

result = titan_engine(df)

if result is None:
    st.error("Engine failed")
    st.stop()

# DISPLAY
st.subheader("EUR/USD")

st.write("🟡 Macro Bias:", result["macro"])
st.write("🟡 Regime Expectation:", result["probability"])
st.write("🟡 Session Model:", result["session"])

st.write("🔴 PRIMARY SELL ZONE:", result["sell_zone"], "(", result["sell_reason"], ")")
st.write("🟢 ALTERNATE BUY:", result["buy_zone"], "(", result["buy_reason"], ")")

st.write("🟡 Invalidation Up:", result["invalid_up"])
st.write("🟡 Invalidation Down:", result["invalid_down"])

st.write("🟡 Continuation Targets (HIGH first):", result["high_targets"])
st.write("🟡 Continuation Targets (LOW first):", result["low_targets"])

st.write("🟡 Confluence Score:", result["score"], "/ 100")

st.write("🟡 TRSE OUTPUT:")
st.write("Regime:", result["trse"]["regime"])
st.write("Delay Day:", result["trse"]["delay"])
st.write("Expectation:", result["trse"]["expectation"])
