import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import numpy as np

# ==============================
# 🔐 YOUR API KEY (EMBEDDED)
# ==============================
API_KEY = "eb11f97c310f407da9961dc7c67a697e"

# ==============================
# ⏰ TIME
# ==============================
def spain_time():
    return datetime.now(pytz.timezone("Europe/Madrid"))

# ==============================
# 📡 DATA FETCH
# ==============================
def get_data(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=15min&outputsize=100&apikey={API_KEY}"
    r = requests.get(url).json()

    if "values" not in r:
        return None, r

    df = pd.DataFrame(r["values"])
    df = df.astype({"open":float,"high":float,"low":float,"close":float})
    df = df.iloc[::-1].reset_index(drop=True)

    return df, r

# ==============================
# 🧠 TRSE
# ==============================
def trse(df):
    highs = df["high"].tail(8).values
    move = highs[-1] - highs[0]

    if abs(move) < 0.0005:
        return "RES", 0, "Rotation Expected"
    elif move > 0:
        return "PCS", 0, "Continuation Likely"
    else:
        return "RDS", 3, "Rotation Pressure"

# ==============================
# 🧠 TITAN STRUCTURE ENGINE
# ==============================
def titan(df):

    last = df.iloc[-1]

    high = df["high"].max()
    low = df["low"].min()
    mid = (high + low) / 2
    rng = high - low

    if last["close"] > mid:
        regime = "LFHL"
        first = "LOW"
        prob = "62%"
    else:
        regime = "HFL"
        first = "HIGH"
        prob = "58%"

    sell_zone = (high - rng*0.2, high)
    buy_zone = (low, low + rng*0.2)

    t1_down = mid - rng*0.25
    t2_down = mid - rng*0.5
    t3_down = low

    t1_up = mid + rng*0.25
    t2_up = mid + rng*0.5
    t3_up = high

    inv_up = high + rng*0.02
    inv_dn = low - rng*0.02

    london_1 = "08:10–09:40"
    london_2 = "10:30–11:50"
    ny_window = "14:30–15:45"

    score = int((abs(last["close"] - mid) / rng) * 100)

    regime_trse, day, exp = trse(df)

    return {
        "sell": sell_zone,
        "buy": buy_zone,
        "inv_up": inv_up,
        "inv_dn": inv_dn,
        "t1d": t1_down,
        "t2d": t2_down,
        "t3d": t3_down,
        "t1u": t1_up,
        "t2u": t2_up,
        "t3u": t3_up,
        "regime": regime,
        "first": first,
        "prob": prob,
        "l1": london_1,
        "l2": london_2,
        "ny": ny_window,
        "score": score,
        "trse": regime_trse,
        "day": day,
        "exp": exp
    }

# ==============================
# 🎯 DISPLAY
# ==============================
def display(pair, d):

    st.markdown(f"## 🔵 {pair}")

    st.markdown(f"🟡 Macro Bias: Structural environment")
    st.markdown(f"🟡 Regime Expectation: {d['regime']} {d['prob']} ({d['first']} first)")
    st.markdown(f"🟡 Session Model: Asia → London → NY")

    st.markdown(f"🔴 PRIMARY SELL ZONE: 🟣 {round(d['sell'][0],5)} – {round(d['sell'][1],5)}")
    st.markdown(f"🟢 ALTERNATE BUY: 🟣 {round(d['buy'][0],5)} – {round(d['buy'][1],5)}")

    st.markdown(f"🟡 Invalidation Up: 🟣 {round(d['inv_up'],5)}")
    st.markdown(f"🟡 Invalidation Down: 🟣 {round(d['inv_dn'],5)}")

    st.markdown("🟡 Continuation Targets (HIGH first):")
    st.markdown(f"T1: 🟣 {round(d['t1d'],5)}")
    st.markdown(f"T2: 🟣 {round(d['t2d'],5)}")
    st.markdown(f"T3: 🟣 {round(d['t3d'],5)}")

    st.markdown("🟡 Continuation Targets (LOW first):")
    st.markdown(f"T1: 🟣 {round(d['t1u'],5)}")
    st.markdown(f"T2: 🟣 {round(d['t2u'],5)}")
    st.markdown(f"T3: 🟣 {round(d['t3u'],5)}")

    st.markdown(f"🟠 London Windows: 🟣 {d['l1']} 🟣 {d['l2']}")
    st.markdown(f"🟠 NY Window: 🟣 {d['ny']}")

    st.markdown(f"🟡 Confluence Score: 🟣 {d['score']} / 100")

    st.markdown("🟡 TRSE OUTPUT:")
    st.markdown(f"Regime: {d['trse']}")
    st.markdown(f"Delay Day: {d['day']}")
    st.markdown(f"Expectation: {d['exp']}")

    st.markdown("---")

# ==============================
# 🚀 APP
# ==============================
st.title("🚀 TITAN ENGINE")

st.write(f"Spain Time: {spain_time()}")

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    df, raw = get_data(pair)

    if df is None:
        st.error("DATA ERROR")
        st.json(raw)
    else:
        result = titan(df)
        display(pair.replace("/", ""), result)
