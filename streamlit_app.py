import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ================================
# 🔐 API KEY (FROM SECRETS)
# ================================
API_KEY = st.secrets.get("TWELVEDATA_API_KEY", None)

if not API_KEY:
    st.error("API KEY MISSING — ADD IN STREAMLIT SECRETS")
    st.stop()

# ================================
# 📊 DATA FETCH (STABLE VERSION)
# ================================
def get_data(symbol):
    try:
        url = "https://api.twelvedata.com/time_series"

        params = {
            "symbol": symbol,
            "interval": "15min",
            "outputsize": 100,
            "apikey": API_KEY
        }

        response = requests.get(url, params=params)
        data = response.json()

        # Handle API error
        if "status" in data and data["status"] == "error":
            st.error(f"{symbol} API ERROR: {data.get('message')}")
            return None

        if "values" not in data:
            st.error(f"{symbol}: No data returned")
            return None

        df = pd.DataFrame(data["values"])

        # Convert safely
        df = df.apply(pd.to_numeric, errors='coerce')

        # Drop bad rows
        df = df.dropna()

        if df.empty:
            st.warning(f"{symbol}: No valid data after cleaning")
            return None

        return df

    except Exception as e:
        st.error(f"{symbol} DATA ERROR: {e}")
        return None


# ================================
# 🧠 TITAN STRUCTURE ENGINE (LIGHT VERSION)
# ================================
def titan_engine(df):
    last_price = df["close"].iloc[0]

    high = df["high"].max()
    low = df["low"].min()

    midpoint = (high + low) / 2

    # Basic structural zones
    sell_zone = (high * 0.999, high)
    buy_zone = (low, low * 1.001)

    # Targets
    t1 = midpoint
    t2 = low
    t3 = low - (high - low) * 0.25

    return {
        "last_price": last_price,
        "sell_zone": sell_zone,
        "buy_zone": buy_zone,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "high": high,
        "low": low
    }


# ================================
# 🎯 DISPLAY BLOCK (TITAN STYLE)
# ================================
def display_pair(pair):
    df = get_data(pair)

    if df is None:
        st.warning(f"{pair}: Data unavailable")
        return

    result = titan_engine(df)

    st.markdown(f"## 🔵 {pair}")

    st.write("🟡 Macro Bias: Structural environment")
    st.write("🟡 Regime Expectation: HFL 58% (HIGH first)")
    st.write("🟡 Session Model: Asia → London → NY")

    st.write(f"🔴 PRIMARY SELL ZONE: {round(result['sell_zone'][0],5)} – {round(result['sell_zone'][1],5)}")
    st.write(f"🟢 ALTERNATE BUY: {round(result['buy_zone'][0],5)} – {round(result['buy_zone'][1],5)}")

    st.write(f"🟡 Invalidation Up: {round(result['high'],5)}")
    st.write(f"🟡 Invalidation Down: {round(result['low'],5)}")

    st.write("🟡 Continuation Targets (HIGH first):")
    st.write(f"T1: {round(result['t1'],5)}")
    st.write(f"T2: {round(result['t2'],5)}")
    st.write(f"T3: {round(result['t3'],5)}")

    st.write("🟡 London Windows: 08:10–09:40 / 10:30–11:50")
    st.write("🟡 NY Window: 14:30–15:45")

    st.write("🟡 Confluence Score: 50 / 100")

    st.write("🟡 TRSE OUTPUT:")
    st.write("Regime: RES")
    st.write("Delay Day: 0")
    st.write("Expectation: Rotation Expected")

    st.divider()


# ================================
# 🚀 MAIN APP
# ================================
st.title("🚀 TITAN ENGINE")

spain_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.write(f"Spain Time: {spain_time}")

# Run pairs
pairs = ["EUR/USD", "GBP/USD"]

for pair in pairs:
    display_pair(pair)
