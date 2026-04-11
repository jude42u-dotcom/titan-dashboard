import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
import pytz
import json

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
    targets_high = [asia_low + step, asia_low, asia_low - step]
    targets_low = [asia_high - step, asia_high, asia_high + step]
    invalid_up = asia_high + (step * 3)
    invalid_down = asia_low - (step * 3)
    macro = "Expansion structure → distribution"
    probability = "LFH 60%"
    session = "Asia drift → London expansion → NY resolution"
    trse = {"regime": "RES", "delay": np.random.randint(1,6), "expectation": "Expansion Expected"}
    return {
        "macro": macro, "probability": probability, "session": session,
        "sell_zone": (float(sell_low), float(sell_high)),
        "buy_zone": (float(buy_low), float(buy_high)),
        "invalid_up": float(invalid_up), "invalid_down": float(invalid_down),
        "high_targets": [float(x) for x in targets_high],
        "low_targets": [float(x) for x in targets_low],
        "score": 80, "trse": trse
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
    return True if (volatility > 0.004 or abs(directional) > 7) else False

# ============================================
# 🔴 KILL SWITCH
# ============================================

def kill_switch(regime):
    return True if regime in ["STRONG_TREND", "DRIFT"] else False

# ============================================
# 🧠 LEGACY DECISION (kept for compatibility)
# ============================================

def titan_decision(regime, ned_block, kill):
    if kill: return "🔴 DO NOT TRADE — KILL SWITCH"
    if ned_block: return "🔴 DO NOT TRADE — NED BLOCK"
    if regime == "EXPANSION": return "🟡 CAUTION — VOLATILITY"
    return "🟢 TRADE ALLOWED"

# ============================================
# ⚙️ HEDGE CONFIG & JENKINS HELPERS
# ============================================

HEDGE_PIPS = 200

def interpret_jenkins(signal, strength):
    base = "LOW formation window" if signal == "BUY" else "HIGH formation window"
    suffix = "(Primary timing day)" if strength == "🔥 STRONG" else "(Near timing window)"
    return f"{base} → wait for confirmation before {'buying' if signal=='BUY' else 'selling'} {suffix}"

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
# 📅 EVENT & TIMING ENGINES
# ============================================

def titan_event_engine():
    today = str(datetime.now().date())
    weight = 2 if today in MAJOR_EVENTS else 0
    reasons = [MAJOR_EVENTS[today]] if today in MAJOR_EVENTS else []
    return weight, reasons

def titan_event_timing():
    now = datetime.now().hour
    if now < 8: return "PRE-LONDON", "Wait — no trade"
    elif 8 <= now < 14: return "LONDON", "Primary execution window"
    elif 14 <= now < 17: return "NY", "Secondary execution"
    else: return "POST-NY", "Avoid new trades"

# ============================================
# 🔥 TIME ENGINES (GANN & HARMONIC)
# ============================================

def titan_time_pdf(df):
    if df is None or df.empty: return []
    last_price = float(df["close"].iloc[-1])
    root = np.sqrt(last_price)
    angles = [0.25, 0.5, 1.0, 2.0]
    base_time = df["time"].iloc[-1]
    windows = []
    for a in angles:
        minutes = root * a * 60
        future_time = base_time + pd.Timedelta(minutes=minutes)
        windows.append({"angle": a, "time": future_time})
    return windows

def calculate_time_windows(df):
    recent = df.tail(100)
    low_anchor = recent.loc[recent["low"].idxmin()]
    high_anchor = recent.loc[recent["high"].idxmax()]
    low_time, high_time = low_anchor["time"], high_anchor["time"]
    now = df["time"].iloc[-1]
    low_diff = (now - low_time).total_seconds() / 60
    high_diff = (now - high_time).total_seconds() / 60
    harmonics = [0.125, 0.167, 0.25, 0.333]
    low_windows = [low_time + pd.Timedelta(minutes=low_diff * h) for h in harmonics]
    high_windows = [high_time + pd.Timedelta(minutes=high_diff * h) for h in harmonics]
    return {"low_windows": low_windows, "high_windows": high_windows}

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

def titan_action_guide(score):
    if score < 40: return "🟢 Normal TITAN Trading Day → Execute zones inside time windows"
    elif 40 <= score < 60: return "🟡 Caution → Conflicting signals → Wait for London confirmation"
    else: return "🔴 Do Not Trade → Market conditions invalid"

# ============================================
# 🧠 RSD & MARKET CONDITION DETECTORS
# ============================================

def titan_rsd(df_eur, df_gbp):
    score, reasons = 0, []
    eur_range = df_eur.tail(96)["high"].max() - df_eur.tail(96)["low"].min()
    gbp_range = df_gbp.tail(96)["high"].max() - df_gbp.tail(96)["low"].min()
    if eur_range > 0.008 or gbp_range > 0.010:
        score += 1; reasons.append("Volatility Expansion")
    eur_trend = df_eur["close"].iloc[-1] - df_eur["close"].iloc[-20]
    gbp_trend = df_gbp["close"].iloc[-1] - df_gbp["close"].iloc[-20] 
    if np.sign(eur_trend) == np.sign(gbp_trend):
        score += 1; reasons.append("Session Alignment")
    eur_moves = np.sign(df_eur["close"].diff().tail(20))
    if abs(eur_moves.sum()) > 10:
        score += 1; reasons.append("Momentum Stack")
    if abs(eur_trend) > 0.004 and abs(gbp_trend) > 0.004:
        score += 1; reasons.append("Correlation Spike")
    eur_fast = abs(df_eur["close"].iloc[-1] - df_eur["close"].iloc[-12])
    if eur_fast > 0.003:
        score += 1; reasons.append("Velocity Spike")
    return score, reasons

def rsd_interpretation(score):
    if score <= 1: return "🟢 Stable regime"
    elif score == 2: return "🟡 Early shift"
    elif score == 3: return "🟠 Transition"
    elif score == 4: return "🔴 High risk"
    else: return "🚨 Systemic event"

def detect_market_condition(df_eur, df_gbp):
    conditions = []
    eur_range = df_eur.tail(96)["high"].max() - df_eur.tail(96)["low"].min()
    if eur_range < 0.004: conditions.append("Low Volatility Compression")
    if eur_range > 0.008: conditions.append("High Volatility Expansion")
    eur_trend = df_eur["close"].iloc[-1] - df_eur["close"].iloc[-20]
    if abs(eur_trend) > 0.004: conditions.append("Strong Trend")
    if abs(eur_trend) < 0.001: conditions.append("Range Market")
    gbp_trend = df_gbp["close"].iloc[-1] - df_gbp["close"].iloc[-20]
    if np.sign(eur_trend) == np.sign(gbp_trend): conditions.append("Correlation Spike")
    eur_moves = np.sign(df_eur["close"].diff().tail(30))
    if abs(eur_moves.sum()) > 15: conditions.append("Session Alignment")
    return conditions

def score_conditions(conditions):
    score = 0
    for c in conditions:
        if c == "Range Market": score -= 1
        if c == "Low Volatility Compression": score += 1
        if c in ["High Volatility Expansion", "Strong Trend"]: score += 2
        if c in ["Correlation Spike", "Session Alignment"]: score += 3
    return max(score, 0)

def heatmap_output(score):
    if score <= 1: return "🟢", "Stable market", "GREEN"
    elif score <= 3: return "🟡", "Early instability", "YELLOW"
    elif score == 4: return "🔴", "High-risk regime", "RED"
    else: return "🚨", "Systemic danger", "RED"

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
# 🧬 TITAN FIRST EXTREME PROBABILITY ENGINE
# ============================================

def titan_fe_probability_engine(df):
    df = df.copy().sort_values("time")
    now = df["time"].iloc[-1]
    start = df["time"].iloc[0]
    hour = now.hour
    hours_since_open = (now - start).total_seconds() / 3600
    hourly_prob = {0: 19.4, 1: 8, 2: 6, 3: 5, 4: 4, 5: 6, 6: 9, 7: 10, 8: 11, 9: 9, 10: 7, 11: 5, 12: 6, 13: 7, 14: 5, 15: 3, 16: 2, 17: 2, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1, 23: 1}
    base_prob = hourly_prob.get(hour, 5)
    if hour < 6: session, weight = "Asia", 1.2
    elif 6 <= hour < 12: session, weight = "London", 1.0
    else: session, weight = "New York", 0.8
    prob = base_prob * weight
    hold_4h = False
    if hours_since_open >= 4:
        prob += 20; hold_4h = True
        persistence_text = "Extreme survived 4H → near guaranteed hold"
    else:
        persistence_text = "Not yet confirmed (below 4H)"
    if 12 <= hour <= 14:
        prob += 10
        transition_text = "NY transition window → trend probability elevated"
    else:
        transition_text = "Normal session behavior"
    prob = min(prob, 95)
    if prob >= 80: interpretation = "Very high probability extreme → strong structural day"
    elif prob >= 60: interpretation = "High probability extreme → tradable condition"
    elif prob >= 40: interpretation = "Moderate probability → wait for confirmation"
    else: interpretation = "Low probability → high risk / possible trap"
    return {
        "probability": round(prob, 1), "session": session, "hour": hour,
        "interpretation": interpretation, "persistence_text": persistence_text,
        "transition_text": transition_text, "hold_4h": hold_4h
    }

# ============================================
# 🧠 CORE HIERARCHY ENGINE (THE FIX)
# ============================================

def titan_hierarchical_decision(data):
    """
    1. HARD INVALIDATION
    2. STRUCTURAL DOMINANCE (4H HOLD) -> IF TRUE, IGNORE FE PROB
    3. REGIME FILTER
    4. PROBABILITY FILTER
    """
    if data["post_ny"]: return "DO NOT TRADE", "Post-NY session. No new trades allowed."
    if data["invalid_market"]: return "DO NOT TRADE", "Market conditions invalid (Instability block)."
    if data["correlation_spike"]: return "DO NOT TRADE", "Correlation spike detected → Systemic risk."

    # FIX: 4H Hold Priority
    if data["fe_4h_valid"]:
        return "TRADE ALLOWED", "Extreme confirmed (4H hold) → Structural edge active. FE probability bypassed."

    if data["regime"] == "RANGE": return "TRADE ALLOWED", "Range environment → Mean reversion active."
    if data["fe_prob"] < 40: return "CAUTION", f"Weak extreme ({data['fe_prob']}%) → High trap probability."

    return "TRADE ALLOWED", "Conditions favorable. Execute normally."

def interpret_decision_panel(decision, reason):
    if decision == "DO NOT TRADE": return f"🚫 DO NOT TRADE\n\n{reason}"
    if decision == "CAUTION": return f"⚠️ CAUTION — REDUCE RISK\n\n{reason}"
    return f"✅ TRADE ALLOWED\n\n{reason}"

def compute_confidence_score(data):
    score = 0
    if data["session"] == "London": score += 25
    score += min(data["fe_prob"], 25)
    if data["fe_4h_valid"]: score += 20
    if data["heatmap"] == "GREEN": score += 15
    elif data["heatmap"] == "YELLOW": score += 5
    if data["rsd_stable"]: score += 10
    return score

# ============================================
# 🚀 UI MAIN EXECUTION
# ============================================

st.set_page_config(layout="wide")
st.title("🚀 TITAN ENGINE V5")
st.write("Spain Time:", datetime.now())

pairs = ["EUR/USD", "GBP/USD"]
pair_data = {}
for p in pairs:
    df_temp = load_data(p)
    if not df_temp.empty: pair_data[p] = df_temp

if len(pair_data) == 2:
    rsd_score, rsd_reasons = titan_rsd(pair_data["EUR/USD"], pair_data["GBP/USD"])
    market_conditions = detect_market_condition(pair_data["EUR/USD"], pair_data["GBP/USD"])
    condition_score = score_conditions(market_conditions)
    heat_icon, heat_text, heat_label = heatmap_output(condition_score)
else:
    rsd_score, rsd_reasons, heat_label, heat_icon, heat_text = 0, [], "GREY", "⚪", "Waiting..."

for pair in pairs:
    if pair not in pair_data: continue
    df = pair_data[pair]
    result = titan_engine(df)
    fe_prob_data = titan_fe_probability_engine(df)
    regime = detect_regime(df)

    # Hierarchical Input
    h_input = {
        "session": fe_prob_data["session"],
        "fe_prob": fe_prob_data["probability"],
        "fe_4h_valid": fe_prob_data["hold_4h"],
        "regime": regime,
        "invalid_market": rsd_score >= 4 or heat_label == "RED",
        "correlation_spike": "Correlation Spike" in market_conditions,
        "post_ny": datetime.now().hour >= 17,
        "rsd_stable": rsd_score <= 1,
        "heatmap": heat_label
    }

    decision_status, decision_reason = titan_hierarchical_decision(h_input)
    final_msg = interpret_decision_panel(decision_status, decision_reason)
    conf_score = compute_confidence_score(h_input)

    st.header(pair)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("🧠 TITAN DECISION PANEL")
        if decision_status == "DO NOT TRADE": st.error(final_msg)
        elif decision_status == "CAUTION": st.warning(final_msg)
        else: st.success(final_msg)
        st.info(f"📊 First Extreme: {'Extreme confirmed (4H hold)' if h_input['fe_4h_valid'] else 'Needs confirmation'}")
    with col2:
        st.metric("TITAN Confidence Score", f"{conf_score}/100")

    st.markdown("---")
    st.write("🟡 Macro Bias:", result["macro"])
    st.write("🟡 Regime Expectation:", result["probability"])
    st.write("🟡 Session Model:", result["session"])

    sz, bz = result["sell_zone"], result["buy_zone"]
    st.write(f"🔴 SELL: {sz[0]:.5f} – {sz[1]:.5f} | 🟢 BUY: {bz[0]:.5f} – {bz[1]:.5f}")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.write("🟡 Targets HIGH:")
        for x in result["high_targets"]: st.write(f"  → {x:.5f}")
    with col_t2:
        st.write("🟡 Targets LOW:")
        for x in result["low_targets"]: st.write(f"  → {x:.5f}")

    # Probability & RSD Output
    st.write("📊 FE Probability:", f"{fe_prob_data['probability']}%")
    st.caption(f"{fe_prob_data['session']} | {fe_prob_data['persistence_text']} | {fe_prob_data['transition_text']}")
    st.write("🧠 RSD State:", rsd_interpretation(rsd_score))
    
    # Heatmap
    if heat_label == "GREEN": st.success(f"{heat_icon} {heat_text}")
    elif heat_label == "YELLOW": st.warning(f"{heat_icon} {heat_text}")
    else: st.error(f"{heat_icon} {heat_text}")

    # Legacy Checks
    ned_block = ned_filter(df)
    kill = kill_switch(regime)
    st.write("🧠 Regime:", regime)
    if kill: st.error("🔴 KILL SWITCH ACTIVE")
    elif ned_block: st.warning("🧠 NED BLOCK ACTIVE")
    
    # Streaks & Failure Filter
    f_score, f_reasons = titan_failure_filter(df)
    e_weight, e_reasons = titan_event_engine()
    total_f_score = f_score + (e_weight * 10)
    if total_f_score >= 60:
        st.session_state.red_streak += 1
        st.error(f"🔴 RED DAY {st.session_state.red_streak} — STOP")
    else:
        st.session_state.red_streak = 0
        st.success("🟢 TRADE DAY")

    # Time Displays
    st.write("⏱ GANN TIME:")
    st.write(", ".join([t["time"].strftime("%H:%M") for t in titan_time_pdf(df)]))
    
    st.write("⏱ HARMONIC WINDOWS:")
    hw = calculate_time_windows(df)
    st.write("LOWS:", ", ".join([t.strftime("%H:%M") for t in hw["low_windows"]]))
    st.write("HIGHS:", ", ".join([t.strftime("%H:%M") for t in hw["high_windows"]]))

    # Jenkins Display
    st.write("📅 JENKINS:")
    jenkins_hits = get_active_jenkins(pair)
    if jenkins_hits:
        for d, s, strength in jenkins_hits:
            st.write(f"{strength} → {d} → {s}")
            st.caption(interpret_jenkins(s, strength))
    else:
        st.write("No active Jenkins date")

    st.markdown("---")

# Execution Rules
st.markdown("### 🧠 Execution Rules")
st.markdown("• Trade only inside window\n• First confirmed extreme defines direction\n• Respect structural invalidation\n• No confirmation → No trade\n• NY trade only if London expansion confirmed")

st.session_state.titan_locked_date = today_spain
