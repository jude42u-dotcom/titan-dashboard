import streamlit as st
from datetime import datetime
import pytz

from titan_engine import calculate_titan

st.set_page_config(page_title="TITAN PRO ENGINE", layout="wide")

# -------------------------
# HEADER
# -------------------------
st.title("🚀 TITAN PRO ENGINE")

spain = pytz.timezone("Europe/Madrid")
now = datetime.now(spain)

st.write(f"Spain Time: {now}")

# -------------------------
# SNAPSHOT LOGIC (22:50)
# -------------------------
if now.hour < 22 or (now.hour == 22 and now.minute < 50):
    st.error("No snapshot yet. Wait for 22:50 Spain time.")
    st.stop()

# -------------------------
# PAIRS
# -------------------------
pairs = ["EURUSD", "GBPUSD"]

for pair in pairs:
    st.header(pair)

    result = calculate_titan(pair)

    st.write(f"Structure: {result['structure']}")
    st.write(f"Bias: {result['bias']}")
    st.write(f"Regime: {result['regime']}")
    st.write(f"First Extreme: {result['first_extreme']}")
    st.write(f"Score: {result['score']}")

    st.subheader("Zones")
    st.write(f"Buy: {result['buy_zone']}")
    st.write(f"Sell: {result['sell_zone']}")

    st.subheader("Targets")
    st.write(f"T1: {result['t1']}")
    st.write(f"T2: {result['t2']}")
    st.write(f"T3: {result['t3']}")

    st.subheader("TRSE")
    st.write("Rotation Day")
    st.write("Delay: 1")

    st.subheader("Time Windows")
    st.write("London 1: 08:30–10:00")
    st.write("London 2: 11:30–13:00")
    st.write("NY: 14:30–16:30")
