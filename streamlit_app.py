import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="TITAN Dashboard", layout="wide")

# -------------------------
# AUTO REFRESH (30 sec)
# -------------------------
st_autorefresh = st.empty()
time.sleep(0.1)

# -------------------------
# LIVE PRICE FUNCTION
# -------------------------
def get_price(pair):
    try:
        url = f"https://api.exchangerate.host/latest?base={pair[:3]}&symbols={pair[3:]}"
        res = requests.get(url).json()
        return res["rates"][pair[3:]]
    except:
        return None

# -------------------------
# TITAN LOGIC (basic v1)
# -------------------------
def titan_bias(price, pivot=1.0850):
    if price is None:
        return "NO DATA"
    return "BUY" if price > pivot else "SELL"

# -------------------------
# HEADER
# -------------------------
st.title("TITAN Trading Dashboard")

# -------------------------
# MARKET CONTEXT
# -------------------------
st.subheader("Market Context")

eurusd_price = get_price("EURUSD")
gbpusd_price = get_price("GBPUSD")

st.write(f"EURUSD Price: {eurusd_price}")
st.write(f"GBPUSD Price: {gbpusd_price}")

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3 = st.tabs(["EURUSD", "GBPUSD", "Comparison"])

# -------------------------
# EURUSD PANEL
# -------------------------
with tab1:
    st.header("EURUSD")

    bias = titan_bias(eurusd_price)

    st.write(f"Macro Bias: {bias}")

    if eurusd_price:
        st.write(f"Live Price: {round(eurusd_price,5)}")

        buy_zone = eurusd_price - 0.002
        sell_zone = eurusd_price + 0.002

        st.write(f"Buy Zone: {round(buy_zone,5)} - {round(eurusd_price,5)}")
        st.write(f"Sell Zone: {round(eurusd_price,5)} - {round(sell_zone,5)}")

        st.write(f"Invalidation: {round(eurusd_price - 0.005,5)}")
        st.write(f"Target: {round(eurusd_price + 0.01,5)}")

# -------------------------
# GBPUSD PANEL
# -------------------------
with tab2:
    st.header("GBPUSD")

    bias = titan_bias(gbpusd_price, pivot=1.2700)

    st.write(f"Macro Bias: {bias}")

    if gbpusd_price:
        st.write(f"Live Price: {round(gbpusd_price,5)}")

        buy_zone = gbpusd_price - 0.002
        sell_zone = gbpusd_price + 0.002

        st.write(f"Buy Zone: {round(buy_zone,5)} - {round(gbpusd_price,5)}")
        st.write(f"Sell Zone: {round(gbpusd_price,5)} - {round(sell_zone,5)}")

        st.write(f"Invalidation: {round(gbpusd_price - 0.005,5)}")
        st.write(f"Target: {round(gbpusd_price + 0.01,5)}")

# -------------------------
# COMPARISON
# -------------------------
with tab3:
    st.header("Comparison")

    data = {
        "Pair": ["EURUSD", "GBPUSD"],
        "Price": [eurusd_price, gbpusd_price],
        "Bias": [
            titan_bias(eurusd_price),
            titan_bias(gbpusd_price, pivot=1.2700)
        ]
    }

    df = pd.DataFrame(data)
    st.dataframe(df)
