import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# ==============================
# API KEY
# ==============================
API_KEY = st.secrets.get("TWELVEDATA_API_KEY")

if not API_KEY:
    st.error("API KEY MISSING — add TWELVEDATA_API_KEY in Streamlit secrets")
    st.stop()

# ==============================
# DATA FETCH
# ==============================
def get_data(symbol):
    try:
        url = "https://api.twelvedata.com/time_series"

        params = {
            "symbol": symbol,
            "interval": "15min",
            "outputsize": 500,
            "apikey": API_KEY
        }

        r = requests.get(url, params=params)
        data = r.json()

        if "values" not in data:
            st.error(f"{symbol} API ERROR: {data}")
            return None

        df = pd.DataFrame(data["values"])

        df = df.rename(columns={
            "datetime": "time",
            "open": "open",
            "high": "high",
            "low": "low",
            "close": "close"
        })

        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df = df.dropna(subset=["time"])

        df = df.sort_values("time")

        df[["open","high","low","close"]] = df[["open","high","low","close"]].astype(float)

        return df

    except Exception as e:
        st.error(f"DATA ERROR: {e}")
        return None

# ==============================
# TITAN ENGINE (STABLE BASE)
# ==============================
def titan_engine(df):
    if df is None or len(df) < 50:
        return None

    df = df.copy()

    # ==============================
    # TIME SAFE FIX (CRITICAL)
    # ==============================
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    df = df.dropna(subset=["time"])

    df["hour"] = df["time"].dt.hour

    # ==============================
    # SESSION SPLIT
    # ==============================
    asia = df[(df["hour"] >= 0) & (df["hour"] < 8)]
    london = df[(df["hour"] >= 8) & (df["hour"] < 13)]

    if asia.empty or london.empty:
        return None

    asia_high = asia["high"].max()
    asia_low = asia["low"].min()

    london_high = london["high"].max()
    london_low = london["low"].min()

    # ==============================
    # FIRST EXTREME
    # ==============================
    if london_high > asia_high:
        first = "HIGH"
    elif london_low < asia_low:
        first = "LOW"
    else:
        first = "RANGE"

    # ==============================
    # REGIME
    # ==============================
    if first == "HIGH":
        regime = "HFL"
    elif first == "LOW":
        regime = "LFHL"
    else:
        regime = "RANGE"

    # ==============================
    # GANN BASE (SAFE VERSION)
    # ==============================
    last_close = df.iloc[-1]["close"]

    root = last_close ** 0.5

    gann_up = (root + 0.125) ** 2
    gann_down = (root - 0.125) ** 2

    # ==============================
    # ZONES
    # ==============================
    sell_low = round(gann_up, 5)
    sell_high = round(gann_up + 0.0003, 5)

    buy_low = round(gann_down, 5)
    buy_high = round(gann_down + 0.0003, 5)

    inv_up = round(gann_up + 0.0006, 5)
    inv_down = round(gann_down - 0.0006, 5)

    # ==============================
    # TARGETS
    # ==============================
    t1 = round(last_close, 5)

    if regime == "LFHL":
        t2 = round(gann_down, 5)
        t3 = round(gann_up, 5)
    else:
        t2 = round(gann_up, 5)
        t3 = round(gann_down, 5)

    # ==============================
    # CONFLUENCE SCORE
    # ==============================
    score = 0

    if first != "RANGE":
        score += 30

    if abs(london_high - asia_high) > 0.0005 or abs(london_low - asia_low) > 0.0005:
        score += 20

    if regime != "RANGE":
        score += 20

    if abs(last_close - gann_up) < 0.001 or abs(last_close - gann_down) < 0.001:
        score += 30

    score = min(score, 100)

    return {
        "regime": regime,
        "sell": (sell_low, sell_high),
        "buy": (buy_low, buy_high),
        "inv_up": inv_up,
        "inv_down": inv_down,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "score": score
    }

# ==============================
# DISPLAY
# ==============================
def display_pair(symbol):

    df = get_data(symbol)

    if df is None:
        st.warning(f"{symbol}: Data unavailable")
        return

    result = titan_engine(df)

    if result is None:
        st.warning(f"{symbol}: Engine failed")
        return

    st.subheader(symbol)

    st.write(f"Regime: {result['regime']}")

    st.write(f"SELL: {result['sell'][0]} – {result['sell'][1]}")
    st.write(f"BUY: {result['buy'][0]} – {result['buy'][1]}")

    st.write(f"Invalidation Up: {result['inv_up']}")
    st.write(f"Invalidation Down: {result['inv_down']}")

    st.write("Targets:")
    st.write(f"T1: {result['t1']}")
    st.write(f"T2: {result['t2']}")
    st.write(f"T3: {result['t3']}")

    st.write(f"Confluence Score: {result['score']} / 100")

    st.write("---")

# ==============================
# MAIN
# ==============================
st.title("TITAN ENGINE V3")

spain_time = datetime.utcnow() + timedelta(hours=2)
st.write(f"Spain Time: {spain_time.strftime('%Y-%m-%d %H:%M:%S')}")

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    display_pair(pair)
