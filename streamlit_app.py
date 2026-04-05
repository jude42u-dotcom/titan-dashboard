import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz

# ============================================
# 🔒 LOCK MODE (UNCHANGED)
# ============================================
SPAIN_TZ = pytz.timezone("Europe/Madrid")

def get_spain_date():
    return datetime.now(SPAIN_TZ).date()

if "titan_locked_date" not in st.session_state:
    st.session_state.titan_locked_date = None

today_spain = get_spain_date()

if st.session_state.titan_locked_date == today_spain:
    st.warning("🔒 TITAN LOCKED FOR TODAY — Refresh disabled")
    st.stop()

# 🔁 RED CLUSTER TRACKING (NEW)
if "red_streak" not in st.session_state:
    st.session_state.red_streak = 0

# ============================================
# 🔐 YOUR API KEY (UNCHANGED)
# ============================================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"

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
# 🔥 FAILURE + CLUSTER ENGINE (NEW)
# ============================================
def titan_failure_cluster(df):

    recent = df.tail(100)

    high = recent["high"].max()
    low = recent["low"].min()
    adr = max(high - low, 0.0001)

    price = df["close"].iloc[-1]
    mid = (high + low) / 2

    distance = abs(price - mid)

    score = 0
    reasons = []

    if distance > adr * 0.65:
        score += 30
        reasons.append("Distance exceeds session capacity")

    move = abs(recent["close"].iloc[-1] - recent["close"].iloc[-8])
    if move > adr * 0.4:
        score += 25
        reasons.append("Excess displacement")

    slope = recent["close"].diff().mean()
    if (price > mid and slope > 0) or (price < mid and slope < 0):
        score += 20
        reasons.append("No pull toward equilibrium")

    if distance > adr * 0.35:
        score += 10
        reasons.append("High distance vs ADR")

    return score, reasons

# ============================================
# 🌍 EVENT CALENDAR ENGINE (NEW)
# ============================================
def titan_event_calendar():

    now = datetime.now()
    weekday = now.weekday()
    day = now.day
    month = now.month

    weight = 0
    reasons = []

    if month == 12 and day in [24,25]:
        weight += 2
        reasons.append("Christmas liquidity")

    if month == 7 and day == 4:
        weight += 2
        reasons.append("US Holiday")

    if weekday == 4 and day <= 7:
        weight += 1
        reasons.append("NFP window")

    if 10 <= day <= 15:
        weight += 1
        reasons.append("CPI window")

    return weight, reasons

# ============================================
# ⏱ EVENT TIMING ENGINE (NEW)
# ============================================
def titan_event_timing():

    hour = datetime.now().hour

    if (7 <= hour < 9) or (13 <= hour < 14):
        return "PRE-EVENT", "Avoid early trades"

    elif (9 <= hour < 10) or (14 <= hour < 16):
        return "EVENT", "DO NOT TRADE"

    elif (10 <= hour < 12) or (16 <= hour < 18):
        return "POST-EVENT", "Best execution window"

    return "NORMAL", "Standard conditions"

# ============================================
# 🚀 UI
# ============================================
st.set_page_config(layout="wide")
st.title("🚀 TITAN ENGINE V6")

st.write("Spain Time:", datetime.now())

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:

    df = load_data(pair)

    if df.empty:
        continue

    result = titan_engine(df)

    st.header(pair)

    st.write("🟡 Macro Bias:", result["macro"])
    st.write("🟡 Regime Expectation:", result["probability"])

    sz = result["sell_zone"]
    bz = result["buy_zone"]

    st.write(f"🔴 SELL: {sz[0]:.5f} – {sz[1]:.5f}")
    st.write(f"🟢 BUY: {bz[0]:.5f} – {bz[1]:.5f}")

    # 🔥 FAILURE + EVENT
    score, reasons = titan_failure_cluster(df)
    event_w, event_r = titan_event_calendar()
    score += event_w * 10
    reasons.extend(event_r)

    # 🔴 CLASSIFICATION
    if score >= 60:
        st.session_state.red_streak += 1
        rd = st.session_state.red_streak

        st.write(f"🔴 RED DAY {min(rd,4)}")
        st.write("🚫 DO NOT TRADE")

    elif score >= 40:
        st.session_state.red_streak = 0
        st.write("🟡 YELLOW DAY")
        st.write("⚠️ Wait for confirmation")

    else:
        st.session_state.red_streak = 0
        st.write("🟢 GREEN DAY")
        st.write("✅ Normal TITAN execution")

    st.write("🔎 Reasons:", reasons)

    # ⏱ TIMING
    phase, action = titan_event_timing()
    st.write("⏱ Phase:", phase)
    st.write("🧠 Timing Action:", action)

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
