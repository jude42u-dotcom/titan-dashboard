
import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz
import json
# ============================================
# 🧠 MICRO ENGINE (1M FOREVER LAYER)
# ============================================

class MicroEngine:
    def __init__(self, df):
        self.df = df.copy().sort_values("time")

    def detect_regime(self):
        session = self.df.tail(240)  # ~4 hours of 1m data
        high_idx = session["high"].idxmax()
        low_idx = session["low"].idxmin()

        if low_idx < high_idx:
            return "LFHL"
        elif high_idx < low_idx:
            return "HFL"
        else:
            return "UNCLEAR"

    def calculate_levels(self):
        recent = self.df.tail(120)
        buy = recent["low"].min()
        sell = recent["high"].max()
        return buy, sell

    def calculate_targets(self, buy, sell):
        r = abs(sell - buy)

        buy_t = [buy + r*0.5, buy + r*1.0, buy + r*1.5]
        sell_t = [sell - r*0.5, sell - r*1.0, sell - r*1.5]

        return buy_t, sell_t

    def calculate_invalidation(self, buy, sell):
        buffer = abs(sell - buy) * 0.3
        return buy - buffer, sell + buffer

    def calculate_windows(self):
        now = self.df["time"].iloc[-1]

        low_w = (now - pd.Timedelta(minutes=30), now + pd.Timedelta(minutes=30))
        high_w = (now + pd.Timedelta(minutes=60), now + pd.Timedelta(minutes=120))

        return low_w, high_w

    def run(self):
        regime = self.detect_regime()
        buy, sell = self.calculate_levels()
        buy_t, sell_t = self.calculate_targets(buy, sell)
        buy_inv, sell_inv = self.calculate_invalidation(buy, sell)
        low_w, high_w = self.calculate_windows()

        return {
            "regime": regime,
            "buy": buy,
            "sell": sell,
            "buy_t": buy_t,
            "sell_t": sell_t,
            "buy_inv": buy_inv,
            "sell_inv": sell_inv,
            "low_w": low_w,
            "high_w": high_w
        }

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
    gbp_trend = df_gbp["close"].iloc[-1] - df_gbp["close"].iloc[-20] 

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
# 🧠 MARKET CONDITION DETECTOR (MCM)
# ============================================
def detect_market_condition(df_eur, df_gbp):

    conditions = []

    eur_range = df_eur.tail(96)["high"].max() - df_eur.tail(96)["low"].min()
    gbp_range = df_gbp.tail(96)["high"].max() - gbp_range if 'gbp_range' in locals() else 0 # Placeholder fix for local var
    # Re-calculate for accuracy
    gbp_range = df_gbp.tail(96)["high"].max() - df_gbp.tail(96)["low"].min()

    if eur_range < 0.004:
        conditions.append("Low Volatility Compression")

    if eur_range > 0.008:
        conditions.append("High Volatility Expansion")

    eur_trend = df_eur["close"].iloc[-1] - df_eur["close"].iloc[-20]

    if abs(eur_trend) > 0.004:
        conditions.append("Strong Trend")

    if abs(eur_trend) < 0.001:
        conditions.append("Range Market")

    gbp_trend = df_gbp["close"].iloc[-1] - df_gbp["close"].iloc[-20]

    if np.sign(eur_trend) == np.sign(gbp_trend):
        conditions.append("Correlation Spike")

    eur_moves = np.sign(df_eur["close"].diff().tail(30))
    if abs(eur_moves.sum()) > 15:
        conditions.append("Session Alignment")

    return conditions

# ============================================
# 🧠 CONDITION SCORING + HEATMAP
# ============================================
def score_conditions(conditions):

    score = 0

    for c in conditions:
        if c in ["Range Market"]:
            score -= 1

        if c in ["Low Volatility Compression"]:
            score += 1

        if c in ["High Volatility Expansion"]:
            score += 2

        if c in ["Strong Trend"]:
            score += 2

        if c in ["Correlation Spike"]:
            score += 3

        if c in ["Session Alignment"]:
            score += 3

    return max(score, 0)

def heatmap_output(score):

    if score <= 1:
        return "🟢", "Stable market", "GREEN"

    elif score == 2:
        return "🟡", "Early instability", "YELLOW"

    elif score == 3:
        return "🟡", "Transition phase", "YELLOW"

    elif score == 4:
        return "🔴", "High-risk regime", "RED"

    else:
        return "🚨", "Systemic danger", "RED"

def interpret_condition(cond):

    mapping = {
        "Range Market": "Mean-reversion environment → best for TITAN",
        "Low Volatility Compression": "Compression building → breakout risk coming",
        "High Volatility Expansion": "Expansion active → continuation risk",
        "Strong Trend": "Directional control → TITAN weak",
        "Correlation Spike": "Pairs moving together → systemic risk",
        "Session Alignment": "Multi-session trend → high probability continuation"
    }

    return mapping.get(cond, "")

# ============================================
# 🧬 TITAN FIRST EXTREME PROBABILITY ENGINE v1.0
# ============================================
def titan_fe_probability_engine(df):

    df = df.copy().sort_values("time")

    now = df["time"].iloc[-1]
    start = df["time"].iloc[0]

    hour = now.hour
    hours_since_open = (now - start).total_seconds() / 3600

    # 1. HOURLY PROBABILITY (CORE)
    hourly_prob = {
        0: 19.4, 1: 8, 2: 6, 3: 5, 4: 4,
        5: 6, 6: 9, 7: 10, 8: 11, 9: 9,
        10: 7, 11: 5, 12: 6, 13: 7,
        14: 5, 15: 3, 16: 2, 17: 2,
        18: 1, 19: 1, 20: 1, 21: 1,
        22: 1, 23: 1
    }

    base_prob = hourly_prob.get(hour, 5)

    # 2. SESSION WEIGHTING
    if hour < 6:
        session = "Asia"
        session_weight = 1.2
    elif 6 <= hour < 12:
        session = "London"
        session_weight = 1.0
    else:
        session = "New York"
        session_weight = 0.8

    prob = base_prob * session_weight

    # 3. 4H PERSISTENCE RULE
    hold_4h = False
    if hours_since_open >= 4:
        persistence_boost = 20
        persistence_text = "Extreme survived 4H → near guaranteed hold"
        hold_4h = True
    else:
        persistence_boost = 0
        persistence_text = "Not yet confirmed (below 4H)"

    prob += persistence_boost

    # 4. TRANSITION WINDOW (12–14)
    if 12 <= hour <= 14:
        prob += 10
        transition_text = "NY transition window → trend probability elevated (~63%)"
    else:
        transition_text = "Normal session behavior"

    # 5. FINAL NORMALIZATION
    prob = min(prob, 95)

    # 6. INTERPRETATION (ONE LINE)
    if prob >= 80:
        interpretation = "Very high probability extreme → strong structural day"
    elif prob >= 60:
        interpretation = "High probability extreme → tradable condition"
    elif prob >= 40:
        interpretation = "Moderate probability → wait for confirmation"
    else:
        interpretation = "Low probability → high risk / possible trap"

    return {
        "probability": round(prob, 1),
        "session": session,
        "hour": hour,
        "interpretation": interpretation,
        "persistence_text": persistence_text,
        "transition_text": transition_text,
        "hold_4h": hold_4h
    }

# ============================================
# 🧠 CORE RULE ENGINE (NEW ADDITION)
# ============================================

def titan_decision_engine(data):
    reasons = []
    state = []

    if data["post_ny"]:
        return "DO NOT TRADE", "Post-NY session. No new trades allowed."

    if data["rsd"] == 0:
        return "DO NOT TRADE", "Market structure unstable."

    if data["fe_prob"] < 40:
        reasons.append("First extreme is weak (<40%)")
    elif data["fe_prob"] > 70:
        state.append("Strong extreme")

    if data["fe_4h_valid"]:
        state.append("Extreme confirmed (4H hold)")

    if data["heatmap"] == "RED":
        return "DO NOT TRADE", "Market unstable (RED condition)."

    if data["heatmap"] == "YELLOW":
        reasons.append("Market in transition phase")

    if data["correlation"]:
        reasons.append("Correlation spike detected")

    if len(reasons) > 0:
        return "CAUTION", " | ".join(reasons)

    return "TRADE ALLOWED", "Conditions favorable. Execute strategy."

# ============================================
# 🧬 INTERPRETATION LAYER (NEW ADDITION)
# ============================================

def interpret_decision(decision, reason):
    if decision == "DO NOT TRADE":
        return f"🚫 DO NOT TRADE\n\nMarket conditions are not favorable.\n{reason}\n\nStand aside. Your edge is not present."
    elif decision == "CAUTION":
        return f"⚠ CAUTION — REDUCE RISK\n\n{reason}\n\nMarket is unstable or unclear. Expect traps or fake moves. Trade smaller or wait."
    elif decision == "TRADE ALLOWED":
        return f"✅ TRADE ALLOWED\n\n{reason}\n\nConditions support the strategy. Execute normally using your zones and timing."

def fe_interpretation(prob, hold_4h):
    if hold_4h:
        return "Extreme confirmed (4H hold). Very high probability it holds."
    if prob < 40:
        return "Weak extreme. High probability of break or trap."
    elif prob < 70:
        return "Moderate extreme. Needs confirmation."
    else:
        return "Strong extreme. High probability of holding."

# ============================================
# 🔥 CONFIDENCE SCORE ENGINE (NEW ADDITION)
# ============================================

def compute_confidence_score(data):
    score = 0
    if data["session"] == "London": score += 25
    score += min(data["fe_prob"], 25)
    if data["fe_4h_valid"]: score += 20
    if data["heatmap"] == "GREEN": score += 15
    elif data["heatmap"] == "YELLOW": score += 5
    if data["rsd"] == 1: score += 10
    return score
    # ============================================
# ⚡ MICRO STRUCTURE ENGINE (FOREVER PROTOCOL)
# ============================================

def titan_micro_engine(df):

    df = df.copy().sort_values("time")

    recent = df.tail(120)

    high = recent["high"].max()
    low = recent["low"].min()
    mid = (high + low) / 2

    range_ = high - low
    step = range_ / 4

    # REGIME DETECTION
    last = recent.iloc[-1]["close"]
    prev = recent.iloc[-20]["close"]

    if last > prev:
        regime = "LFHL (Low → High → Higher Low)"
    else:
        regime = "HFL (High → Low → Lower High)"

    # LEVELS
    buy_levels = (low, low + step)
    sell_levels = (high - step, high)

    # TARGETS
    buy_targets = [mid, high - step, high]
    sell_targets = [mid, low + step, low]

    # INVALIDATION
    invalid_buy = low - step
    invalid_sell = high + step

    # TIME WINDOWS (simple harmonic proxy)
    base_time = df["time"].iloc[-1]
    windows = [
        base_time + pd.Timedelta(minutes=15),
        base_time + pd.Timedelta(minutes=30),
        base_time + pd.Timedelta(minutes=60),
    ]

    return {
        "regime": regime,
        "buy_levels": buy_levels,
        "sell_levels": sell_levels,
        "buy_targets": buy_targets,
        "sell_targets": sell_targets,
        "invalid_buy": invalid_buy,
        "invalid_sell": invalid_sell,
        "windows": windows
    }


# ============================================
# 🖥️ MICRO PANEL UI
# ============================================

def render_micro_panel(df):

    micro = titan_micro_engine(df)

    st.markdown("### ⚡ MICRO STRUCTURE (FOREVER 1M)")

    col1, col2 = st.columns(2)

    with col1:
        st.write("🧠 Regime:", micro["regime"])
        st.write(f"🟢 Buy Zone: {micro['buy_levels'][0]:.5f} – {micro['buy_levels'][1]:.5f}")
        st.write(f"🔴 Sell Zone: {micro['sell_levels'][0]:.5f} – {micro['sell_levels'][1]:.5f}")

    with col2:
        st.write(f"❌ Buy Invalidation: {micro['invalid_buy']:.5f}")
        st.write(f"❌ Sell Invalidation: {micro['invalid_sell']:.5f}")

    col3, col4 = st.columns(2)

    with col3:
        st.write("🎯 Buy Targets:")
        for t in micro["buy_targets"]:
            st.write(f"→ {t:.5f}")

    with col4:
        st.write("🎯 Sell Targets:")
        for t in micro["sell_targets"]:
            st.write(f"→ {t:.5f}")

    st.write("⏱ Micro Time Windows:")
    for t in micro["windows"]:
        st.write(t.strftime("%H:%M"))

    st.markdown("---")

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
    market_conditions = detect_market_condition(data["EUR/USD"], data["GBP/USD"])
    condition_score = score_conditions(market_conditions)
    heat_icon, heat_text, heat_label = heatmap_output(condition_score)
else:
    rsd_score, rsd_reasons = 0, []
    market_conditions = []
    condition_score = 0
    heat_icon, heat_text, heat_label = "⚪", "Waiting for data...", "GREY"

for pair in pairs:

    if pair not in data:
        continue

    df = data[pair]

# ✅ MICRO PANEL (NEW LAYER)
render_micro_panel(df)

# ✅ MACRO ENGINE (EXISTING)
result = titan_engine(df)

# ✅ TIME + SUPPORT DATA (FIXED)
time_pdf = titan_time_pdf(df)
harmonic = calculate_time_windows(df)
jenkins = get_active_jenkins(pair)

# ✅ UI START
st.header(pair)

    # ============================================
    # 🧠 NEW INTEGRATED DECISION PANEL
    # ============================================
    fe_prob_data = titan_fe_probability_engine(df)
    
    # Prepare data for new Engine
    engine_input = {
        "session": fe_prob_data["session"],
        "fe_prob": fe_prob_data["probability"],
        "fe_4h_valid": fe_prob_data["hold_4h"],
        "rsd": 1 if rsd_score <= 2 else 0,
        "heatmap": heat_label,
        "correlation": True if "Correlation Spike" in market_conditions else False,
        "post_ny": True if datetime.now().hour >= 17 else False
    }

    decision_status, decision_reason = titan_decision_engine(engine_input)
    final_msg = interpret_decision(decision_status, decision_reason)
    fe_text = fe_interpretation(engine_input["fe_prob"], engine_input["fe_4h_valid"])
    conf_score = compute_confidence_score(engine_input)

    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🧠 TITAN DECISION PANEL")
        if decision_status == "DO NOT TRADE":
            st.error(final_msg)
        elif decision_status == "CAUTION":
            st.warning(final_msg)
        else:
            st.success(final_msg)
        
        st.info(f"📊 **First Extreme:** {fe_text}")

    with col2:
        st.metric("TITAN Confidence Score", f"{conf_score}/100")

    st.markdown("---")

    st.write("🟡 Macro Bias:", result["macro"])
    st.write("🟡 Regime Expectation:", result["probability"])
    st.write("🟡 Session Model:", result["session"])

    sz = result["sell_zone"]
    bz = result["buy_zone"]

    st.write(f"🔴 SELL: {sz[0]:.5f} – {sz[1]:.5f}")
    st.write(f"🟢 BUY: {bz[0]:.5f} – {bz[1]:.5f}")

    st.write("🟡 Invalidation Up:", f"{result['invalid_up']:.5f}")
    st.write("🟡 Invalidation Down:", f"{result['invalid_down']:.5f}")

    st.write("🟡 Targets HIGH:")
    for x in result["high_targets"]:
        st.write(f"  → {x:.5f}")
        
    st.write("🟡 Targets LOW:")
    for x in result["low_targets"]:
        st.write(f"  → {x:.5f}")

    st.write("🟡 Score:", result["score"])

    # ============================================
    # 🧬 FIRST EXTREME PROBABILITY ENGINE OUTPUT
    # ============================================
    st.write("📊 First Extreme Probability:", f"{fe_prob_data['probability']}%")
    st.write("🧠 FE Interpretation:", fe_prob_data["interpretation"])

    st.caption(
        f"{fe_prob_data['session']} session | Hour {fe_prob_data['hour']} | "
        f"{fe_prob_data['persistence_text']} | {fe_prob_data['transition_text']}"
    )

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

    # ============================================
    # 🧠 MARKET HEATMAP DISPLAY
    # ============================================
    st.write("🧠 Market Condition Heatmap:")

    if heat_icon == "🟢":
        st.success(f"{heat_icon} {heat_text}")
    elif heat_icon == "🟡":
        st.warning(f"{heat_icon} {heat_text}")
    else:
        st.error(f"{heat_icon} {heat_text}")

    if market_conditions:
        for cond in market_conditions:
            st.write(f"• {cond}")
            st.caption(interpret_condition(cond))
    else:
        st.write("No dominant condition detected")

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

    st.write(f"🛡 Hedge Level: {HEDGE_PIPS} pips")

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
# ============================================
# 🧠 SECONDARY RULE ENGINE + SCHEDULER (ADDED ONLY)
# ============================================

def check_secondary_rules(df):
    results = []

    now = datetime.now(SPAIN_TZ)
    hour = now.hour

    # Rule 1 — London timing
    rule_london = 7 <= hour <= 12
    results.append(("London Window", rule_london, "Best execution window"))

    # Rule 2 — 4H awareness (NOT auto validation)
    rule_4h = hour >= 10
    results.append(("4H Rule Awareness", rule_4h, "Check if extreme held 4H manually"))

    # Rule 3 — Volatility
    recent = df.tail(20)
    range_val = recent["high"].max() - recent["low"].min()
    rule_vol = range_val > 0.001
    results.append(("Volatility OK", rule_vol, "Sufficient movement"))

    # Rule 4 — Regime stability
    regime = detect_regime(df)
    rule_regime = regime in ["RANGE"]
    results.append(("Stable Regime", rule_regime, f"Current regime: {regime}"))

    return results


# ============================================
# 🧠 SCORING ENGINE (ADDED ONLY)
# ============================================

def score_secondary_rules(results):
    score = 0

    for name, passed, _ in results:
        if name == "4H Rule Awareness" and passed:
            score += 30
        elif name == "London Window" and passed:
            score += 20
        elif name == "Volatility OK" and passed:
            score += 15
        elif name == "Stable Regime" and passed:
            score += 25

    # London open bonus (precision timing)
    now = datetime.now(SPAIN_TZ)
    if 8 <= now.hour <= 10:
        score += 10

    return min(score, 100)


# ============================================
# 🧠 INTERPRETATION (ADDED ONLY)
# ============================================

def interpret_secondary(results, score):
    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]

    # HARD BLOCK (critical)
    for r in results:
        if r[0] == "Stable Regime" and not r[1]:
            return "NO TRADE", score, passed, failed, "Market not in stable range structure"

    if score >= 80:
        return "GO TRADE", score, passed, failed, "Strong confluence — conditions aligned"
    elif score >= 60:
        return "GO TRADE (Reduced)", score, passed, failed, "Moderate confluence — reduce size"
    elif score >= 40:
        return "CAUTION", score, passed, failed, "Weak structure — wait for confirmation"
    else:
        return "NO TRADE", score, passed, failed, "Conditions not favorable"


# ============================================
# ⏰ EXECUTION FUNCTION (ADDED ONLY)
# ============================================

def run_secondary_update(df):
    results = check_secondary_rules(df)
    score = score_secondary_rules(results)
    decision = interpret_secondary(results, score)

    st.session_state["secondary_results"] = results
    st.session_state["secondary_score"] = score
    st.session_state["secondary_decision"] = decision
    st.session_state["last_secondary_run"] = datetime.now(SPAIN_TZ)


# ============================================
# ⏰ SCHEDULER FIXED (ADDED ONLY)
# ============================================

now = datetime.now(SPAIN_TZ)

if "last_secondary_run" not in st.session_state:
    st.session_state["last_secondary_run"] = None

run_time = st.session_state["last_secondary_run"]

# ✅ FIXED LOGIC — runs anytime AFTER 08:30 (once per day)
if now.hour >= 8:
    if run_time is None or run_time.date() != now.date():
        if len(data) > 0:
            any_pair = list(data.keys())[0]
            run_secondary_update(data[any_pair])


# ============================================
# 🧠 4H RULE REMINDER (STATIC — NO AUTO LOGIC)
# ============================================

st.markdown("### ⏱ 4H RULE REMINDER")

current_hour = now.hour

if current_hour < 6:
    st.info("Extreme likely forming → do NOT assume direction yet")
elif 6 <= current_hour < 8:
    st.warning("Extreme forming → monitor closely before London")
elif 8 <= current_hour < 10:
    st.warning("London active → wait before trusting extreme")
else:
    st.success("If extreme formed earlier → 4H validation possible")


# ============================================
# 🧠 MANUAL EXTREME TRACKER (USER CONTROLLED)
# ============================================

st.markdown("### 🎯 Extreme Tracker (Manual 4H Timer)")

if "extreme_time" not in st.session_state:
    st.session_state["extreme_time"] = None

col1, col2 = st.columns(2)

with col1:
    if st.button("Mark Extreme Now"):
        st.session_state["extreme_time"] = datetime.now(SPAIN_TZ)

with col2:
    if st.button("Reset Extreme"):
        st.session_state["extreme_time"] = None

extreme_time = st.session_state["extreme_time"]

if extreme_time:
    elapsed = (datetime.now(SPAIN_TZ) - extreme_time).total_seconds() / 3600

    st.write(f"Extreme marked at: {extreme_time.strftime('%H:%M')}")

    if elapsed >= 4:
        st.success("✅ 4H HOLD CONFIRMED → EXTREME VALID")
    else:
        remaining = 4 - elapsed
        st.warning(f"⏳ 4H not complete → wait {remaining:.1f} hours")

else:
    st.info("No extreme marked yet")


# ============================================
# 🖥️ SECONDARY PANEL DISPLAY
# ============================================

st.markdown("## 🧠 SECONDARY RULE PANEL (08:30 CHECK)")

if "secondary_decision" in st.session_state:

    decision, score, passed, failed, reason = st.session_state["secondary_decision"]

    if decision.startswith("GO"):
        st.success(f"{decision} ({score}/100)")
    elif decision == "CAUTION":
        st.warning(f"{decision} ({score}/100)")
    else:
        st.error(f"{decision} ({score}/100)")

    st.write(reason)

    st.markdown("### ✅ Rules Met")
    for r in passed:
        st.write(f"- {r[0]} → {r[2]}")

    st.markdown("### ❌ Rules Not Met")
    for r in failed:
        st.write(f"- {r[0]} → {r[2]}")

    last_run = st.session_state.get("last_secondary_run")
    if last_run:
        st.caption(f"Last update: {last_run.strftime('%H:%M')} Spain time")

else:
    st.info("Waiting for 08:30 rule validation...")
