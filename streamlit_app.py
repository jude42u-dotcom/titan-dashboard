import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz

# ============================================
# 🔒 LOCK MODE (ADDED)
# ============================================
SPAIN_TZ = pytz.timezone("Europe/Madrid")

def get_spain_date():
    return datetime.now(SPAIN_TZ).date()

if "titan_locked_date" not in st.session_state:
    st.session_state.titan_locked_date = None

# 🔴 RED STREAK MEMORY (NEW)
if "red_streak" not in st.session_state:
    st.session_state.red_streak = 0

today_spain = get_spain_date()

if st.session_state.titan_locked_date == today_spain:
    st.warning("🔒 TITAN LOCKED FOR TODAY — Refresh disabled")
    st.stop()

# ============================================
# 🔐 YOUR API KEY (UNCHANGED)
# ============================================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"

# ============================================
# 🛡 HEDGE LEVEL (NEW)
# ============================================
HEDGE_PIPS = 200

# ============================================
# 📅 STATIC EVENT CALENDAR (NEW)
# ============================================
MAJOR_EVENTS = {
    "2026-04-10": "US CPI",
    "2026-04-15": "FOMC",
    "2026-05-01": "NFP",
    "2026-12-25": "Christmas",
}

# ============================================
# 📅 JENKINS CALENDAR (UNCHANGED)
# ============================================
JENKINS_DATES = {
    "EUR/USD": [
        ("2026-04-20", "BUY"),
        ("2026-05-20", "SELL"),
        ("2026-06-04", "BUY"),
        ("2026-06-19", "SELL"),
    ],
    "GBP/USD": [
        ("2026-02-06", "SELL"),
        ("2026-03-08", "BUY"),
        ("2026-04-07", "SELL"),
        ("2026-05-07", "BUY"),
    ]
}

# ============================================
# 📡 LOAD DATA (UNCHANGED)
# ============================================
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
        df["time"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("time")
        df[["open","high","low","close"]] = df[["open","high","low","close"]].astype(float)

        return df

    except Exception as e:
        st.error(f"{symbol} DATA ERROR: {e}")
        return pd.DataFrame()

# ============================================
# 🧠 TITAN ENGINE (UNCHANGED)
# ============================================
def titan_engine(df):

    if df is None or df.empty:
        return None

    df = df.copy().sort_values("time")

    asia = df.tail(50)

    asia_high = asia["high"].max()
    asia_low = asia["low"].min()
    asia_mid = (asia_high + asia_low) / 2
    asia_range = max(asia_high - asia_low, 0.0001)

    root = np.sqrt(asia_mid)
    step = asia_range / root

    sell_low = asia_high + step
    sell_high = asia_high + step * 2

    buy_low = asia_low - step * 2
    buy_high = asia_low - step

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

    invalid_up = asia_high + (step * 3)
    invalid_down = asia_low - (step * 3)

    macro = "Expansion structure → distribution"
    probability = "LFH 60%"
    session = "Asia drift → London expansion → NY resolution"

    trse = {
        "regime": "RES",
        "delay": np.random.randint(1,6),
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

# ============================================
# 🔴 FAILURE FILTER (UNCHANGED)
# ============================================
def titan_failure_filter(df):
    reasons = []
    score = 0

    recent = df.tail(20)
    range_val = recent["high"].max() - recent["low"].min()

    if range_val < 0.001:
        score += 30
        reasons.append("Low volatility → no expansion capacity")

    trend = recent["close"].iloc[-1] - recent["close"].iloc[0]
    if abs(trend) < 0.0005:
        score += 20
        reasons.append("No structural trend")

    return score, reasons

# ============================================
# 🧠 REGIME DETECTOR (NEW)
# ============================================
def detect_regime(df):
    recent = df.tail(20)

    move = abs(recent["close"].iloc[-1] - recent["open"].iloc[0])
    range_ = recent["high"].max() - recent["low"].min()
    directional = sum(np.sign(recent["close"].diff().fillna(0)))

    if move > range_ * 0.8 and abs(directional) > 10:
        return "STRONG_TREND"

    if range_ < 0.001:
        return "DRIFT"

    if range_ > 0.004:
        return "EXPANSION"

    return "RANGE"

# ============================================
# 🧠 NED FILTER (NEW)
# ============================================
def ned_filter(df):
    recent = df.tail(10)

    volatility = recent["high"].max() - recent["low"].min()
    directional = sum(np.sign(recent["close"].diff().fillna(0)))

    return volatility > 0.004 or abs(directional) > 7

# ============================================
# 🔴 KILL SWITCH (NEW)
# ============================================
def kill_switch(regime):
    return regime in ["STRONG_TREND", "DRIFT"]

# ============================================
# 🧠 FINAL DECISION ENGINE (NEW)
# ============================================
def titan_decision(regime, ned_block, kill):

    if kill:
        return "🔴 DO NOT TRADE — KILL SWITCH"

    if ned_block:
        return "🔴 DO NOT TRADE — NED BLOCK"

    if regime == "EXPANSION":
        return "🟡 CAUTION — VOLATILITY"

    return "🟢 TRADE ALLOWED"

# ============================================
# 🚀 UI
# ============================================
st.set_page_config(layout="wide")
st.title("🚀 TITAN ENGINE V5")

st.write("Spain Time:", datetime.now())

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:

    df = load_data(pair)

    if df.empty:
        continue

    result = titan_engine(df)

    time_pdf = titan_time_pdf(df)
    harmonic = calculate_time_windows(df)
    jenkins = get_active_jenkins(pair)

    st.header(pair)

    st.write("🟡 Macro Bias:", result["macro"])
    st.write("🟡 Regime Expectation:", result["probability"])
    st.write("🟡 Session Model:", result["session"])

    sz = result["sell_zone"]
    bz = result["buy_zone"]

    st.write(f"🔴 SELL: {sz[0]:.5f} – {sz[1]:.5f}")
    st.write(f"🟢 BUY: {bz[0]:.5f} – {bz[1]:.5f}")

    st.write("🟡 Invalidation Up:", f"{result['invalid_up']:.5f}")
    st.write("🟡 Invalidation Down:", f"{result['invalid_down']:.5f}")

    st.write("🟡 Targets HIGH:", [f"{x:.5f}" for x in result["high_targets"]])
    st.write("🟡 Targets LOW:", [f"{x:.5f}" for x in result["low_targets"]])

    st.write("🟡 Score:", result["score"])
    st.write("🧠 Action:", titan_action_guide(result["score"]))

    # ============================================
    # 🔥 NEW LAYER (SAFE ADD)
    # ============================================
    regime = detect_regime(df)
    ned_block = ned_filter(df)
    kill = kill_switch(regime)
    decision = titan_decision(regime, ned_block, kill)

    st.write("🧠 Regime:", regime)

    if kill:
        st.error("🔴 KILL SWITCH ACTIVE")
    elif ned_block:
        st.warning("🧠 NED BLOCK ACTIVE")

    st.write("🧠 Final Decision:", decision)
    st.write(f"🛡 Hedge Level: {HEDGE_PIPS} pips")

    # 🔥 ORIGINAL ENGINE
    f_score, f_reasons = titan_failure_filter(df)
    e_weight, e_reasons = titan_event_engine()

    total_score = f_score + (e_weight * 10)

    if total_score >= 60:
        st.session_state.red_streak += 1
        st.error(f"🔴 RED DAY {st.session_state.red_streak} — DO NOT TRADE")
    elif total_score >= 40:
        st.session_state.red_streak = 0
        st.warning("🟡 YELLOW DAY — Caution")
    else:
        st.session_state.red_streak = 0
        st.success("🟢 GREEN DAY — Trade allowed")

    st.write("⏱ Event Timing:", titan_event_timing())

    st.write("🟡 TRSE:", result["trse"])

    st.write("⏱ GANN TIME:")
    for t in time_pdf:
        st.write(t["time"].strftime("%H:%M"))

    st.write("⏱ LOW WINDOWS:")
    for t in harmonic["low_windows"]:
        st.write(t.strftime("%H:%M"))

    st.write("⏱ HIGH WINDOWS:")
    for t in harmonic["high_windows"]:
        st.write(t.strftime("%H:%M"))

    st.write("📅 JENKINS:")
    if jenkins:
        for d, s in jenkins:
            st.write(f"{d} → {s}")
    else:
        st.write("No active Jenkins date")

    st.markdown("---")

# ============================================
# 📜 EXECUTION RULES (UNCHANGED)
# ============================================
st.markdown("### 🧠 Execution Rules")
st.markdown("""
• Trade only inside window  
• First confirmed extreme defines direction  
• Respect structural invalidation  
• No confirmation → No trade  
• NY trade only if London expansion confirmed
""")

st.session_state.titan_locked_date = today_spain
