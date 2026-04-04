import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# =====================================
# 🔐 API KEY (STREAMLIT SECRETS)
# =====================================
API_KEY = st.secrets.get("TWELVEDATA_API_KEY")

if not API_KEY:
    st.error("API KEY MISSING — add in Streamlit Secrets")
    st.stop()

# =====================================
# 📡 FETCH DATA
# =====================================
def get_data(symbol):
    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": "15min",
        "outputsize": 200,
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

    df["time"] = pd.to_datetime(df["time"])
    df = df.sort_values("time")

    for col in ["open", "high", "low", "close"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    if df.empty:
        return None

    return df

# =====================================
# 🧠 TITAN ENGINE
# =====================================
def titan_engine(df):

    # --- Previous day structure ---
    yesterday = df[df["time"] < datetime.utcnow().date()]
    prev_high = yesterday["high"].max()
    prev_low = yesterday["low"].min()

    # --- Asia session (00:00–06:00 UTC) ---
    asia = df[(df["time"].dt.hour >= 0) & (df["time"].dt.hour < 6)]
    asia_high = asia["high"].max()
    asia_low = asia["low"].min()
    asia_mid = (asia_high + asia_low) / 2

    # --- Current price ---
    price = df.iloc[-1]["close"]

    # --- London breakout detection ---
    london = df[(df["time"].dt.hour >= 7) & (df["time"].dt.hour < 12)]
    london_high = london["high"].max()
    london_low = london["low"].min()

    broke_high = london_high > asia_high
    broke_low = london_low < asia_low

    # --- Regime detection ---
    if broke_high and not broke_low:
        regime = "HFL"  # high first
    elif broke_low and not broke_high:
        regime = "LFHL"  # low first
    else:
        regime = "RANGE"

    # --- Spain midpoint logic ---
    midpoint = (prev_high + prev_low) / 2

    # --- Zones ---
    sell_zone = (asia_high, asia_high + 0.0003)
    buy_zone = (asia_low - 0.0003, asia_low)

    # --- Targets (REAL directional asymmetry) ---
    range_size = asia_high - asia_low

    if regime == "HFL":
        t1 = asia_mid
        t2 = asia_low
        t3 = asia_low - range_size * 0.5
    elif regime == "LFHL":
        t1 = asia_mid
        t2 = asia_high
        t3 = asia_high + range_size * 0.5
    else:
        t1 = midpoint
        t2 = prev_high
        t3 = prev_low

    # --- Invalidation ---
    invalid_up = asia_high + range_size * 0.2
    invalid_down = asia_low - range_size * 0.2

    # --- Confluence score ---
    score = 0

    if regime != "RANGE":
        score += 30

    if abs(price - midpoint) < range_size:
        score += 20

    if broke_high or broke_low:
        score += 20

    if range_size > 0.002:
        score += 30

    return {
        "regime": regime,
        "sell_zone": sell_zone,
        "buy_zone": buy_zone,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "invalid_up": invalid_up,
        "invalid_down": invalid_down,
        "score": score
    }

# =====================================
# 🎯 DISPLAY
# =====================================
def display_pair(symbol):

    df = get_data(symbol)

    if df is None:
        st.warning(f"{symbol}: Data unavailable")
        return

    result = titan_engine(df)

    st.subheader(f"🔵 {symbol}")

    st.write("🟡 Macro Bias: Structural environment")

    if result["regime"] == "HFL":
        st.write("🟡 Regime Expectation: HIGH first")
    elif result["regime"] == "LFHL":
        st.write("🟡 Regime Expectation: LOW first")
    else:
        st.write("🟡 Regime Expectation: RANGE")

    st.write("🟡 Session Model: Asia → London → NY")

    st.write(f"🔴 PRIMARY SELL ZONE: {round(result['sell_zone'][0],5)} – {round(result['sell_zone'][1],5)}")
    st.write(f"🟢 ALTERNATE BUY: {round(result['buy_zone'][0],5)} – {round(result['buy_zone'][1],5)}")

    st.write(f"🟡 Invalidation Up: {round(result['invalid_up'],5)}")
    st.write(f"🟡 Invalidation Down: {round(result['invalid_down'],5)}")

    st.write("🟡 Continuation Targets:")
    st.write(f"T1: {round(result['t1'],5)}")
    st.write(f"T2: {round(result['t2'],5)}")
    st.write(f"T3: {round(result['t3'],5)}")

    st.write("🟠 London Windows: 08:10–09:40 / 10:30–11:50")
    st.write("🟠 NY Window: 14:30–15:45")

    st.write(f"🟡 Confluence Score: {result['score']} / 100")

    st.write("🟡 TRSE OUTPUT:")
    st.write(f"Regime: {result['regime']}")
    st.write("Delay Day: 0")

    if result["regime"] == "RANGE":
        st.write("Expectation: Rotation Expected")
    else:
        st.write("Expectation: Expansion Expected")

    st.divider()

# =====================================
# 🚀 MAIN APP
# =====================================
st.title("🚀 TITAN ENGINE v2")

spain_time = datetime.utcnow() + timedelta(hours=2)
st.write(f"Spain Time: {spain_time.strftime('%Y-%m-%d %H:%M:%S')}")

pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    display_pair(pair)
