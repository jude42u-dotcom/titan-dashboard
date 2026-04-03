import streamlit as st
from datetime import datetime
import pytz
from titan_engine import calculate_titan

# --- PAGE CONFIG ---
st.set_page_config(page_title="TITAN PRO ENGINE", layout="wide")

# --- HEADER ---
st.title("🚀 TITAN PRO ENGINE")

# --- TIME ---
spain = pytz.timezone("Europe/Madrid")
now = datetime.now(spain)

st.write(f"Spain Time: {now}")

# =========================
# 🔥 TEST MODE (ALWAYS RUN)
# =========================
RUN_ENGINE = True

# =========================
# ENGINE EXECUTION
# =========================
if RUN_ENGINE:

    pairs = ["EURUSD", "GBPUSD"]

    for pair in pairs:
        result = calculate_titan(pair)

        st.header(pair)

        if result is None:
            st.write("Structure: NO DATA")
            st.write("Bias: N/A")
            st.write("Regime: N/A")
            st.write("First Extreme: N/A")
            st.write("Score: 0")
            continue

        # --- STRUCTURE ---
        st.write(f"Structure: {result['structure']}")
        st.write(f"Bias: {result['bias']}")
        st.write(f"Regime: {result['regime']}")
        st.write(f"First Extreme: Computed")
        st.write(f"Score: {result['score']}")

        # --- ZONES ---
        st.subheader("Zones")
        st.write(f"Buy: {result['buy_zone']}")
        st.write(f"Sell: {result['sell_zone']}")

        # --- TARGETS ---
        st.subheader("Targets")
        st.write(f"T1: {result['t1']}")
        st.write(f"T2: {result['t2']}")
        st.write(f"T3: {result['t3']}")

        # --- TRSE ---
        st.subheader("TRSE")
        st.write("Rotation Day")
        st.write("Delay: 1")

        # --- TIME WINDOWS ---
        st.subheader("Time Windows")
        st.write("London 1: 08:30–10:00")
        st.write("London 2: 11:30–13:00")
        st.write("NY: 14:30–16:30")

else:
    st.error("No snapshot yet. Wait for 22:50 Spain time.")
