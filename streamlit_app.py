import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# =========================================
# TRSE ENGINE (ROTATIONAL STATE)
# =========================================
def trse_engine(df):

    df["time"] = pd.to_datetime(df["time"])
    df["date"] = df["time"].dt.date

    daily = df.groupby("date").agg({
        "high": "max",
        "low": "min",
        "close": "last"
    }).reset_index()

    if len(daily) < 5:
        return {"regime": "UNKNOWN", "delay": 0, "expectation": "None"}

    # Detect compression / expansion
    ranges = daily["high"] - daily["low"]
    recent = ranges.tail(3)

    compression = recent.max() < ranges.mean()
    expansion = recent.iloc[-1] > recent.mean()

    # Delay day logic (PDF style)
    delay = 0
    for i in range(len(ranges)-1, 0, -1):
        if ranges.iloc[i] < ranges.iloc[i-1]:
            delay += 1
        else:
            break

    # Regime classification
    if compression:
        regime = f"RDS Day {min(delay,5)}"
        expectation = "Rotation"
    elif expansion:
        regime = "EXPANSION"
        expectation = "Trend continuation"
    else:
        regime = "TRANSITION"
        expectation = "Mixed"

    return {
        "regime": regime,
        "delay": delay,
        "expectation": expectation
    }


# =========================================
# WEEKLY COMPRESSION (MACRO BIAS)
# =========================================
def weekly_bias(df):

    df["time"] = pd.to_datetime(df["time"])
    df["week"] = df["time"].dt.isocalendar().week

    weekly = df.groupby("week").agg({
        "high": "max",
        "low": "min",
        "close": "last"
    }).reset_index()

    if len(weekly) < 3:
        return "Structural environment"

    last = weekly.iloc[-1]
    prev = weekly.iloc[-2]

    lower_high = last["high"] < prev["high"]
    higher_low = last["low"] > prev["low"]

    if lower_high:
        return "Weekly compression → lower highs (bearish pressure)"
    elif higher_low:
        return "Weekly compression → higher lows (bullish pressure)"
    else:
        return "Expansion structure"


# =========================================
# SESSION IDENTITY (PDF FLOW)
# =========================================
def session_model(df):

    df["time"] = pd.to_datetime(df["time"])
    today = df["time"].dt.date.iloc[-1]

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


# =========================================
# TITAN CORE (FIXED GEOMETRY)
# =========================================
def titan_core(df):

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    now = df["time"].iloc[-1]
    today = now.date()

    asia_df = df[(df["time"].dt.hour >= 0) & (df["time"].dt.hour < 7)]

    if len(asia_df) < 10:
        return None

    asia_high = asia_df["high"].max()
    asia_low = asia_df["low"].min()
    asia_mid = (asia_high + asia_low) / 2

    anchor = asia_mid
    asia_range = asia_high - asia_low

    if asia_range < 0.0005:
        asia_range = 0.0005

    root = np.sqrt(anchor)
    step = asia_range / root

    # GANN LEVELS
    g1 = (root + step) ** 2
    g2 = (root + 2*step) ** 2
    g3 = (root + 3*step) ** 2

    g_1 = (root - step) ** 2
    g_2 = (root - 2*step) ** 2
    g_3 = (root - 3*step) ** 2

    # CAP (DEM)
    max_ext = asia_range * 2.2

    def cap(x):
        return max(min(x, anchor + max_ext), anchor - max_ext)

    g1, g2, g3 = cap(g1), cap(g2), cap(g3)
    g_1, g_2, g_3 = cap(g_1), cap(g_2), cap(g_3)

    # REGIME
    last = df.iloc[-1]

    if abs(last["high"] - asia_high) > abs(last["low"] - asia_low):
        regime = "HFL"
    else:
        regime = "LFL"

    # ZONES
    sell_zone = (g1, g2)
    buy_zone = (g_2, g_1)

    # TARGETS
    if regime == "HFL":
        targets = [g_1, g_2, g_3]
    else:
        targets = [g1, g2, g3]

    return {
        "regime": regime,
        "sell_zone": sell_zone,
        "buy_zone": buy_zone,
        "targets": targets,
        "asia_high": asia_high,
        "asia_low": asia_low,
        "range": asia_range
    }


# =========================================
# FINAL TITAN ENGINE (FULL STACK)
# =========================================
def titan_engine(df):

    core = titan_core(df)
    if core is None:
        return None

    trse = trse_engine(df)
    macro = weekly_bias(df)
    session = session_model(df)

    # INVALIDATION
    invalid_up = core["asia_high"] + core["range"] * 0.3
    invalid_down = core["asia_low"] - core["range"] * 0.3

    # WINDOWS
    london_windows = "08:30–09:30 / 11:00–12:30"
    ny_window = "14:30–16:00"

    # SCORE (FULL CONFLUENCE)
    score = 50

    if "compression" in macro:
        score += 10
    if core["regime"] == "HFL":
        score += 10
    if trse["delay"] >= 2:
        score += 10

    score = min(score, 100)

    return {
        "macro": macro,
        "session": session,
        "regime": core["regime"],
        "sell_zone": core["sell_zone"],
        "buy_zone": core["buy_zone"],
        "targets": core["targets"],
        "invalid_up": invalid_up,
        "invalid_down": invalid_down,
        "london_windows": london_windows,
        "ny_window": ny_window,
        "score": score,
        "trse": trse
        }
