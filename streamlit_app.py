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

today_spain = get_spain_date()

if st.session_state.titan_locked_date == today_spain:
    st.warning("🔒 TITAN LOCKED FOR TODAY — Refresh disabled")
    st.stop()

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
# 🔥 GANN TIME (UNCHANGED)
# ============================================
def titan_time_pdf(df):
    if df is None or df.empty:
        return []

    last_price = float(df["close"].iloc[-1])
    root = np.sqrt(last_price)

    angles = [0.25, 0.5, 1.0, 2.0]

    base_time = df["time"].iloc[-1]

    windows = []

    for a in angles:
        minutes = root * a * 60
        future_time = base_time + pd.Timedelta(minutes=minutes)

        windows.append({
            "angle": a,
            "time": future_time
        })

    return windows

# ============================================
# 🔥 HARMONIC TIME WINDOWS (UNCHANGED)
# ============================================
def calculate_time_windows(df):

    recent = df.tail(100)

    low_anchor = recent.loc[recent["low"].idxmin()]
    high_anchor = recent.loc[recent["high"].idxmax()]

    low_time = low_anchor["time"]
    high_time = high_anchor["time"]

    now = df["time"].iloc[-1]

    low_diff = (now - low_time).total_seconds() / 60
    high_diff = (now - high_time).total_seconds() / 60

    harmonics = [0.125, 0.167, 0.25, 0.333]

    low_windows = []
    high_windows = []

    for h in harmonics:
        low_proj = low_time + pd.Timedelta(minutes=low_diff * h)
        high_proj = high_time + pd.Timedelta(minutes=high_diff * h)

        low_windows.append(low_proj)
        high_windows.append(high_proj)

    return {
        "low_windows": low_windows,
        "high_windows": high_windows
    }

# ============================================
# 🔥 JENKINS DETECTOR (UNCHANGED)
# ============================================
def get_active_jenkins(pair):
    today = datetime.now().date()

    active = []

    for date_str, signal in JENKINS_DATES.get(pair, []):
        d = datetime.strptime(date_str, "%Y-%m-%d").date()

        if abs((today - d).days) <= 1:
            active.append((date_str, signal))

    return active

# ============================================
# 🧠 TITAN ACTION INTERPRETATION (NEW)
# ============================================
def titan_action_guide(score):
    if score < 40:
        return "🟢 Normal TITAN Trading Day → Execute zones inside time windows"
    elif 40 <= score < 60:
        return "🟡 Caution → Conflicting signals → Wait for London confirmation before trading"
    else:
        return "🔴 Do Not Trade → Market conditions invalid for TITAN execution"

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

    # 🧠 ACTION GUIDE (NEW)
    st.write("🧠 Action:", titan_action_guide(result["score"]))

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

# 🔒 LOCK DAY AFTER RUN
st.session_state.titan_locked_date = today_spain
