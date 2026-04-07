import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz

# ============================================
# 🔒 LOCK MODE
# ============================================

SPAIN_TZ = pytz.timezone("Europe/Madrid")

def get_spain_date():
    return datetime.now(SPAIN_TZ).date()

if "titan_locked_date" not in st.session_state:
    st.session_state.titan_locked_date = None

if "red_streak" not in st.session_state:
    st.session_state.red_streak = 0

today_spain = get_spain_date()

if st.session_state.titan_locked_date == today_spain:
    st.warning("🔒 TITAN LOCKED FOR TODAY — Refresh disabled")
    st.stop()

# ============================================
# 🔐 YOUR API KEY
# ============================================

API_KEY = "eb11f97c310f407da9961dc7c67a697e"

# ============================================
# 📅 STATIC EVENT CALENDAR
# ============================================

MAJOR_EVENTS = {
    "2026-04-10": "US CPI",
    "2026-04-15": "FOMC",
    "2026-05-01": "NFP",
    "2026-12-25": "Christmas",
}

# ============================================
# 📅 FULL JENKINS ENGINE
# ============================================

JENKINS_ALL = {
    "EUR/USD": [
        ("2026-01-20", "SELL"),
        ("2026-02-06", "SELL"),
        ("2026-03-08", "BUY"),
        ("2026-04-07", "SELL"),
        ("2026-04-20", "BUY"),
        ("2026-05-07", "BUY"),
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
# 📡 LOAD DATA
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
# 🧠 TITAN ENGINE
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
# 🧠 REGIME DETECTOR
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
# 🧠 NED FILTER
# ============================================

def ned_filter(df):
    recent = df.tail(10)

    volatility = recent["high"].max() - recent["low"].min()
    directional = sum(np.sign(recent["close"].diff().fillna(0)))

    if volatility > 0.004:
        return True

    if abs(directional) > 7:
        return True

    return False

# ============================================
# 🔴 KILL SWITCH
# ============================================

def kill_switch(regime):
    if regime in ["STRONG_TREND", "DRIFT"]:
        return True
    return False

# ============================================
# 🧠 FINAL DECISION ENGINE
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
# ⚙️ HEDGE CONFIG
# ============================================

HEDGE_PIPS = 200

# ============================================
# 🧠 JENKINS INTERPRETATION OVERLAY
# ============================================

def interpret_jenkins(signal, strength):

    if signal == "BUY":
        base = "LOW formation window → wait for confirmation before buying"
    else:
        base = "HIGH formation window → wait for confirmation before selling"

    if strength == "🔥 STRONG":
        return f"{base} (Primary timing day)"
    else:
        return f"{base} (Near timing window)"

# ============================================
# 🔴 FAILURE FILTER
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
# 📅 EVENT ENGINE
# ============================================

def titan_event_engine():
    today = str(datetime.now().date())
    weight = 0
    reasons = []

    if today in MAJOR_EVENTS:
        weight += 2
        reasons.append(MAJOR_EVENTS[today])

    return weight, reasons

# ============================================
# ⏱ EVENT TIMING ENGINE
# ============================================

def titan_event_timing():
    now = datetime.now().hour

    if now < 8:
        return "PRE-LONDON", "Wait — no trade"
    elif 8 <= now < 14:
        return "LONDON", "Primary execution window"
    elif 14 <= now < 17:
        return "NY", "Secondary execution"
    else:
        return "POST-NY", "Avoid new trades"

# ============================================
# 🔥 GANN TIME
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
# 🔥 HARMONIC TIME WINDOWS
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
# 🔥 JENKINS DETECTOR
# ============================================

def get_active_jenkins(pair):
    today = datetime.now().date()
    active = []

    for date_str, signal in JENKINS_ALL.get(pair, []):
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        diff = (today - d).days

        if abs(diff) <= 2:
            strength = "🔥 STRONG" if diff == 0 else "⚠️ NEAR"
            active.append((date_str, signal, strength))

    return active

# ============================================
# 🧠 TITAN ACTION INTERPRETATION
# ============================================

def titan_action_guide(score):
    if score < 40:
        return "🟢 Normal TITAN Trading Day → Execute zones inside time windows"
    elif 40 <= score < 60:
        return "🟡 Caution → Conflicting signals → Wait for London confirmation before trading"
    else:
        return "🔴 Do Not Trade → Market conditions invalid for TITAN execution"

# ============================================
# 🧠 REGIME SHIFT DETECTOR (RSD v1.0)
# ============================================
def titan_rsd(df_eur, df_gbp):

    score = 0
    reasons = []

    # MODULE 1 — VOLATILITY EXPANSION
    eur_range = df_eur.tail(96)["high"].max() - df_eur.tail(96)["low"].min()
    gbp_range = df_gbp.tail(96)["high"].max() - df_gbp.tail(96)["low"].min()

    if eur_range > 0.008 or gbp_range > 0.010:
        score += 1
        reasons.append("Volatility Expansion")

    # MODULE 2 — SESSION ALIGNMENT
    eur_trend = df_eur["close"].iloc[-1] - df_eur["close"].iloc[-20]
    gbp_trend = df_gbp["close"].iloc[-1] - df_gbp["close"].iloc[-20] # FIXED SYNTAX ERROR HERE

    if np.sign(eur_trend) == np.sign(gbp_trend):
        score += 1
        reasons.append("Session Alignment")

    # MODULE 3 — MOMENTUM STACK
    eur_moves = np.sign(df_eur["close"].diff().tail(20))
    if abs(eur_moves.sum()) > 10:
        score += 1
        reasons.append("Momentum Stack")

    # MODULE 4 — CORRELATION SPIKE
    if abs(eur_trend) > 0.004 and abs(gbp_trend) > 0.004:
        score += 1
        reasons.append("Correlation Spike")

    # MODULE 5 — VELOCITY
    eur_fast = abs(df_eur["close"].iloc[-1] - df_eur["close"].iloc[-12])
    if eur_fast > 0.003:
        score += 1
        reasons.append("Velocity Spike")

    return score, reasons


# ============================================
# 🧠 RSD INTERPRETATION
# ============================================
def rsd_interpretation(score):

    if score <= 1:
        return "🟢 Stable regime → Trade normally"
    elif score == 2:
        return "🟡 Early shift → Reduce exposure"
    elif score == 3:
        return "🟠 Transition → No new trades"
    elif score == 4:
        return "🔴 High risk → Block trading"
    else:
        return "🚨 Systemic event → Full shutdown"

# ============================================
# 🚀 UI
# ============================================

st.set_page_config(layout="wide")
st.title("🚀 TITAN ENGINE V5")

st.write("Spain Time:", datetime.now())

pairs = ["EUR/USD", "GBP/USD"]

# ============================================
# 🧠 LOAD DATA FOR RSD
# ============================================
data = {}
for p in pairs:
    df_temp = load_data(p)
    if not df_temp.empty:
        data[p] = df_temp

if len(data) == 2:
    rsd_score, rsd_reasons = titan_rsd(data["EUR/USD"], data["GBP/USD"])
else:
    rsd_score, rsd_reasons = 0, []

for pair in pairs:

    if pair not in data:
        continue
    
    df = data[pair]

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

    # EXPANDED TARGET DISPLAY
    st.write("🟡 Targets HIGH:")
    for x in result["high_targets"]:
        st.write(f"  → {x:.5f}")
        
    st.write("🟡 Targets LOW:")
    for x in result["low_targets"]:
        st.write(f"  → {x:.5f}")

    st.write("🟡 Score:", result["score"])

    # ============================================
    # 🧠 RSD OUTPUT
    # ============================================
    st.write("🧠 RSD Score:", rsd_score)
    st.write("🧠 RSD State:", rsd_interpretation(rsd_score))

    if rsd_score >= 5:
        st.error("🚨 SYSTEMIC EVENT — STOP ALL TRADING")
    elif rsd_score >= 4:
        st.error("🔴 HIGH RISK REGIME")
    elif rsd_score >= 3:
        st.warning("🟡 TRANSITION DETECTED")
    elif rsd_score >= 2:
        st.info("⚠️ EARLY SHIFT")
    else:
        st.success("🟢 NORMAL CONDITIONS")

    if rsd_reasons:
        st.write("🧠 RSD Drivers:", rsd_reasons)

    st.write("🧠 Action:", titan_action_guide(result["score"]))

    # ============================================
    # 🧠 NEW RISK ENGINE
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

    # Hedge display
    st.write(f"🛡 Hedge Level: {HEDGE_PIPS} pips")

    # 🔥 FAILURE FILTER LOGIC
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

    # ============================================
    # 📅 JENKINS DISPLAY
    # ============================================
    st.write("📅 JENKINS:")

    if jenkins:
        for d, s, strength in jenkins:
            st.write(f"{strength} → {d} → {s}")
            st.caption(interpret_jenkins(s, strength))
    else:
        st.write("No active Jenkins date")

    st.markdown("---")

# ============================================
# 📜 EXECUTION RULES
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
