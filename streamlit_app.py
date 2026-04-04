import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import pytz

# =========================
# TIME (SPAIN)
# =========================
spain = pytz.timezone("Europe/Madrid")
now = datetime.now(spain)

st.set_page_config(layout="wide")
st.title("🚀 TITAN PRO ENGINE")
st.write(f"Spain Time: {now}")

# =========================
# DATA
# =========================
def get_data(pair):
    symbol_map = {
        "EURUSD": "EURUSD=X",
        "GBPUSD": "GBPUSD=X"
    }
    df = yf.download(symbol_map[pair], period="5d", interval="15m")
    df.dropna(inplace=True)
    return df

# =========================
# MACRO STRUCTURE
# =========================
def macro_bias(df):
    highs = df["High"].rolling(20).max()
    lows = df["Low"].rolling(20).min()

    if highs.iloc[-1] < highs.iloc[-5]:
        return "Weekly compression → lower highs (distribution)"
    elif lows.iloc[-1] > lows.iloc[-5]:
        return "Weekly compression → higher lows (accumulation)"
    else:
        return "Expansion / neutral structure"

# =========================
# REGIME (FIRST EXTREME)
# =========================
def regime_expectation(df):
    range_now = df["High"].iloc[-1] - df["Low"].iloc[-1]
    avg_range = (df["High"] - df["Low"]).mean()

    if range_now < avg_range:
        return "HFL (HIGH first)"
    else:
        return "LFHL (LOW first)"

# =========================
# SESSION MODEL
# =========================
def session_model():
    return "Asia drift → London expansion → NY resolution"

# =========================
# LIQUIDITY ZONES
# =========================
def liquidity_zones(df):
    high_cluster = df["High"].rolling(10).max().iloc[-1]
    low_cluster = df["Low"].rolling(10).min().iloc[-1]

    return {
        "sell_low": round(high_cluster - 0.0005, 5),
        "sell_high": round(high_cluster, 5),
        "buy_low": round(low_cluster, 5),
        "buy_high": round(low_cluster + 0.0005, 5)
    }

# =========================
# TARGET ENGINE
# =========================
def targets(df, direction="HIGH"):
    last = df["Close"].iloc[-1]
    rng = (df["High"] - df["Low"]).mean()

    if direction == "HIGH":
        return [
            round(last + rng * 0.5, 5),
            round(last + rng * 1.0, 5),
            round(last + rng * 1.5, 5)
        ]
    else:
        return [
            round(last - rng * 0.5, 5),
            round(last - rng * 1.0, 5),
            round(last - rng * 1.5, 5)
        ]

# =========================
# TIME WINDOWS (DYNAMIC)
# =========================
def time_windows():
    base = now.replace(hour=0, minute=0, second=0, microsecond=0)

    return [
        (base + timedelta(hours=8, minutes=30), base + timedelta(hours=10)),
        (base + timedelta(hours=11, minutes=30), base + timedelta(hours=13)),
        (base + timedelta(hours=14, minutes=30), base + timedelta(hours=16, minutes=30))
    ]

# =========================
# TRSE ENGINE
# =========================
def trse():
    day = now.day % 5 + 1
    return {
        "regime": f"RDS Day {day}",
        "delay": day,
        "next": "Rotation Expected" if day >= 3 else "Expansion"
    }

# =========================
# CONFLUENCE SCORE
# =========================
def score(df):
    vol = (df["High"] - df["Low"]).std()
    return int(min(100, 50 + vol * 10000))

# =========================
# MAIN ENGINE
# =========================
def titan(pair):
    df = get_data(pair)

    macro = macro_bias(df)
    regime = regime_expectation(df)
    session = session_model()
    zones = liquidity_zones(df)

    if "HIGH first" in regime:
        t_main = targets(df, "LOW")
        t_alt = targets(df, "HIGH")
    else:
        t_main = targets(df, "HIGH")
        t_alt = targets(df, "LOW")

    times = time_windows()
    tr = trse()
    sc = score(df)

    return {
        "macro": macro,
        "regime": regime,
        "session": session,
        "zones": zones,
        "targets_main": t_main,
        "targets_alt": t_alt,
        "times": times,
        "trse": tr,
        "score": sc
    }

# =========================
# DISPLAY
# =========================
def show(pair):
    r = titan(pair)

    st.header(pair)

    st.write(f"🟡 Macro Bias: ⚪ {r['macro']}")
    st.write(f"🟡 Regime Expectation: 🔴 {r['regime']}")
    st.write(f"🟡 Session Model: ⚪ {r['session']}")

    st.write(f"🔴 PRIMARY SELL ZONE: 🟣 {r['zones']['sell_low']} – {r['zones']['sell_high']}")
    st.write(f"🟢 ALTERNATE BUY: 🟣 {r['zones']['buy_low']} – {r['zones']['buy_high']}")

    st.write(f"🟡 Invalidation Up: 🟣 {r['zones']['sell_high'] + 0.002}")
    st.write(f"🟡 Invalidation Down: 🟣 {r['zones']['buy_low'] - 0.002}")

    st.write("🟡 Continuation Targets (PRIMARY):")
    for i, t in enumerate(r["targets_main"], 1):
        st.write(f"T{i}: 🟣 {t}")

    st.write("🟡 Continuation Targets (ALTERNATE):")
    for i, t in enumerate(r["targets_alt"], 1):
        st.write(f"T{i}: 🟣 {t}")

    st.write("🟠 London Time Windows (Spain):")
    for t in r["times"][:2]:
        st.write(f"🟣 {t[0].strftime('%H:%M')} – {t[1].strftime('%H:%M')}")

    st.write(f"🟠 NY Conditional Window: 🟣 {r['times'][2][0].strftime('%H:%M')} – {r['times'][2][1].strftime('%H:%M')}")

    st.write(f"🟡 Confluence Score: 🟣 {r['score']} / 100")

    st.write("🟡 TRSE OUTPUT:")
    st.write(f"Regime: {r['trse']['regime']}")
    st.write(f"Delay Day Count: {r['trse']['delay']}")
    st.write(f"Next-Day Expectation: {r['trse']['next']}")

    st.write("🟡 Execution Rules:")
    st.write("• Trade only inside window")
    st.write("• First confirmed extreme defines direction")
    st.write("• Respect structural invalidation")
    st.write("• No confirmation → No trade")
    st.write("• NY trade only if London expansion confirmed")

# =========================
# RUN
# =========================
show("EURUSD")
show("GBPUSD")
