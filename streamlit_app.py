import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz
import numpy as np

# ==============================
# 🔐 HARD KEY CHECK (FAILSAFE)
# ==============================
if "TWELVE_API_KEY" not in st.secrets:
    st.error("🚫 API KEY MISSING — ADD IN STREAMLIT SECRETS")
    st.stop()

API_KEY = st.secrets["TWELVE_API_KEY"]

# ==============================
# 🌍 TIME
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
    lows = df["low"].tail(8).values
    
    trend = np.sign(highs[-1] - highs[0])

    if abs(highs[-1] - highs[0]) < 0.0005:
        return "RES", 0, "Rotation Expected"
    elif trend != 0:
        return "PCS", 0, "Continuation Likely"
    else:
        return "RDS", 3, "Rotation Pressure"

# ==============================
# 🧠 TITAN ENGINE
# ==============================
def titan(df):

    last = df.iloc[-1]
    high = df["high"].max()
    low = df["low"].min()
    mid = (high + low)/2
    rng = high - low

    if last["close"] > mid:
        regime = "LFHL"
        prob = "62%"
        first = "LOW"
    else:
        regime = "HFL"
        prob = "58%"
        first = "HIGH"

    sell_zone = (high - rng*0.2, high)
    buy_zone = (low, low + rng*0.2)

    t1d = mid - rng*0.25
    t2d = mid - rng*0.5
    t3d = low

    t1u = mid + rng*0.25
    t2u = mid + rng*0.5
    t3u = high

    inv_up = high + rng*0.02
    inv_dn = low - rng*0.02

    london1 = "08:10–09:40"
    london2 = "10:30–11:50"
    ny = "14:30–15:45"

    score = int((abs(last["close"] - mid)/rng)*100)

    trse_regime, trse_day, trse_exp = trse(df)

    return {
        "sell":sell_zone,
        "buy":buy_zone,
        "inv_up":inv_up,
        "inv_dn":inv_dn,
        "t1d":t1d,"t2d":t2d,"t3d":t3d,
        "t1u":t1u,"t2u":t2u,"t3u":t3u,
        "regime":regime,"prob":prob,"first":first,
        "l1":london1,"l2":london2,"ny":ny,
        "score":score,
        "trse":trse_regime,
        "day":trse_day,
        "exp":trse_exp
    }

# ==============================
# 🎯 OUTPUT
# ==============================
def display(pair, d):

    st.markdown(f"## 🔵 {pair}")

    st.markdown(f"🟡 Macro Bias: Structural rotation environment")
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

    st.markdown(f"🟡 TRSE OUTPUT:")
    st.markdown(f"Regime: {d['trse']}")
    st.markdown(f"Delay Day: {d['day']}")
    st.markdown(f"Expectation: {d['exp']}")

    st.markdown("---")

# ==============================
# 🚀 APP
# ==============================
st.title("🚀 TITAN FULL ENGINE")

st.write(f"Spain Time: {spain_time()}")

for pair in ["EUR/USD","GBP/USD"]:
    df, raw = get_data(pair)

    if df is None:
        st.error("DATA ERROR")
        st.json(raw)
    else:
        d = titan(df)
        display(pair.replace("/",""), d)
