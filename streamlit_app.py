import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# =========================
# TIME (SPAIN)
# =========================
def get_spain_time():
    tz = pytz.timezone("Europe/Madrid")
    return datetime.now(tz)

# =========================
# DATA (STOOQ - RELIABLE)
# =========================
def get_data(symbol):
    try:
        mapping = {
            "EURUSD": "eurusd",
            "GBPUSD": "gbpusd"
        }

        url = f"https://stooq.com/q/d/l/?s={mapping[symbol]}&i=d"
        df = pd.read_csv(url)

        df.columns = [c.capitalize() for c in df.columns]
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values("Date")

        return df

    except:
        return pd.DataFrame()

# =========================
# TITAN ENGINE (SIMPLIFIED CORE)
# =========================
def run_pair(symbol):
    df = get_data(symbol)

    if df.empty or len(df) < 10:
        return {
            "structure": "NO DATA",
            "bias": "N/A",
            "regime": "N/A",
            "first_extreme": "N/A",
            "score": 0,
            "buy": 0,
            "sell": 0,
            "t1": 0,
            "t2": 0,
            "t3": 0
        }

    last = float(df["Close"].iloc[-1])
    prev = float(df["Close"].iloc[-2])

    # Simple structure logic (placeholder until full TITAN engine)
    if last > prev:
        structure = "UPTREND"
        bias = "BUY"
    elif last < prev:
        structure = "DOWNTREND"
        bias = "SELL"
    else:
        structure = "RANGE"
        bias = "NEUTRAL"

    # Basic zones & targets (temporary stable logic)
    buy = round(last * 0.995, 5)
    sell = round(last * 1.005, 5)

    t1 = round(last * 1.002, 5)
    t2 = round(last * 1.004, 5)
    t3 = round(last * 1.006, 5)

    score = 60 if bias != "NEUTRAL" else 30

    return {
        "structure": structure,
        "bias": bias,
        "regime": "ACTIVE",
        "first_extreme": "Computed",
        "score": score,
        "buy": buy,
        "sell": sell,
        "t1": t1,
        "t2": t2,
        "t3": t3
    }

# =========================
# UI
# =========================
st.set_page_config(page_title="TITAN PRO ENGINE", layout="centered")

st.title("🚀 TITAN PRO ENGINE")

spain_time = get_spain_time()
st.write(f"Spain Time: {spain_time}")

# =========================
# EURUSD
# =========================
st.header("EURUSD")
eur = run_pair("EURUSD")

st.write(f"Structure: {eur['structure']}")
st.write(f"Bias: {eur['bias']}")
st.write(f"Regime: {eur['regime']}")
st.write(f"First Extreme: {eur['first_extreme']}")
st.write(f"Score: {eur['score']}")

st.subheader("Zones")
st.write(f"Buy: {eur['buy']}")
st.write(f"Sell: {eur['sell']}")

st.subheader("Targets")
st.write(f"T1: {eur['t1']}")
st.write(f"T2: {eur['t2']}")
st.write(f"T3: {eur['t3']}")

st.subheader("TRSE")
st.write("Rotation Day")
st.write("Delay: 1")

st.subheader("Time Windows")
st.write("London 1: 08:30–10:00")
st.write("London 2: 11:30–13:00")
st.write("NY: 14:30–16:30")

# =========================
# GBPUSD
# =========================
st.header("GBPUSD")
gbp = run_pair("GBPUSD")

st.write(f"Structure: {gbp['structure']}")
st.write(f"Bias: {gbp['bias']}")
st.write(f"Regime: {gbp['regime']}")
st.write(f"First Extreme: {gbp['first_extreme']}")
st.write(f"Score: {gbp['score']}")

st.subheader("Zones")
st.write(f"Buy: {gbp['buy']}")
st.write(f"Sell: {gbp['sell']}")

st.subheader("Targets")
st.write(f"T1: {gbp['t1']}")
st.write(f"T2: {gbp['t2']}")
st.write(f"T3: {gbp['t3']}")

st.subheader("TRSE")
st.write("Rotation Day")
st.write("Delay: 1")

st.subheader("Time Windows")
st.write("London 1: 08:30–10:00")
st.write("London 2: 11:30–13:00")
st.write("NY: 14:30–16:30")
