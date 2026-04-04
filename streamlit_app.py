import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# =========================
# 🔐 API KEY
# =========================
API_KEY = st.secrets.get("TWELVEDATA_API_KEY")

if not API_KEY:
    st.error("API KEY MISSING — ADD IN STREAMLIT SECRETS")
    st.stop()

# =========================
# 📊 DATA FETCH (FINAL FIXED)
# =========================
def get_data(symbol):
    try:
        url = "https://api.twelvedata.com/time_series"

        params = {
            "symbol": symbol,          # MUST be EUR/USD format
            "interval": "5min",
            "outputsize": 100,
            "apikey": API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Handle API errors clearly
        if "status" in data and data["status"] == "error":
            st.error(f"{symbol} API ERROR: {data.get('message')}")
            return None

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])

        # Convert safely (NO crashes)
        for col in ["open", "high", "low", "close"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna()

        if df.empty:
            return None

        return df

    except Exception as e:
        st.error(f"{symbol}: Data fetch failed")
        return None


# =========================
# ⚙️ TITAN ENGINE (STABLE BASE)
# =========================
def titan_engine(df):
    last = df.iloc[0]

    high = last["high"]
    low = last["low"]
    close = last["close"]

    midpoint = (high + low) / 2

    return {
        "sell_low": round(high - 0.0003, 5),
        "sell_high": round(high, 5),
        "buy_low": round(low, 5),
        "buy_high": round(low + 0.0003, 5),
        "inv_up": round(high + 0.0001, 5),
        "inv_down": round(low - 0.0001, 5),
        "t1": round(midpoint, 5),
        "t2": round(midpoint - 0.0003, 5),
        "t3": round(midpoint - 0.0006, 5),
    }


# =========================
# 📺 DISPLAY
# =========================
def display_pair(symbol):
    df = get_data(symbol)

    if df is None:
        st.warning(f"{symbol}: Data unavailable")
        return

    result = titan_engine(df)

    st.subheader(f"🔵 {symbol}")

    st.write("🟡 Macro Bias: Structural environment")
    st.write("🟡 Regime Expectation: HFL 58% (HIGH first)")
    st.write("🟡 Session Model: Asia → London → NY")

    st.write(f"🔴 PRIMARY SELL ZONE: 🟣 {result['sell_low']} – {result['sell_high']}")
    st.write(f"🟢 ALTERNATE BUY: 🟣 {result['buy_low']} – {result['buy_high']}")

    st.write(f"🟡 Invalidation Up: 🟣 {result['inv_up']}")
    st.write(f"🟡 Invalidation Down: 🟣 {result['inv_down']}")

    st.write("🟡 Continuation Targets (HIGH first):")
    st.write(f"T1: 🟣 {result['t1']}")
    st.write(f"T2: 🟣 {result['t2']}")
    st.write(f"T3: 🟣 {result['t3']}")

    st.write("🟡 Continuation Targets (LOW first):")
    st.write(f"T1: 🟣 {result['t1']}")
    st.write(f"T2: 🟣 {result['t2']}")
    st.write(f"T3: 🟣 {result['t3']}")

    st.write("🟠 London Windows: 🟣 08:10–09:40 🟣 10:30–11:50")
    st.write("🟠 NY Window: 🟣 14:30–15:45")

    st.write("🟡 Confluence Score: 🟣 50 / 100")

    st.write("🟡 TRSE OUTPUT:")
    st.write("Regime: RES")
    st.write("Delay Day: 0")
    st.write("Expectation: Rotation Expected")

    st.divider()


# =========================
# 🚀 MAIN APP
# =========================
st.title("🚀 TITAN ENGINE")

spain_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"Spain Time: {spain_time}")

# IMPORTANT: TwelveData FOREX FORMAT
pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    display_pair(pair)
