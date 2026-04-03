import streamlit as st
import json
import os
from datetime import datetime
import pytz

from titan_engine import run_engine

# ============================
# CONFIG
# ============================
SPAIN_TZ = pytz.timezone("Europe/Madrid")
SAVE_FILE = "titan_output.json"

# ============================
# TIME CHECK
# ============================
def is_after_update_time():
    now = datetime.now(SPAIN_TZ)
    return now.hour > 10 or (now.hour == 10 and now.minute >= 50)

# ============================
# LOAD / SAVE
# ============================
def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return None

def save_data(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ============================
# UI
# ============================
st.set_page_config(page_title="TITAN Dashboard")
st.title("🚀 TITAN Trading Dashboard")

now = datetime.now(SPAIN_TZ)
st.write(f"🕒 Spain Time: {now}")

data = load_data()

# ============================
# ENGINE EXECUTION
# ============================
if is_after_update_time():

    if data is None:
        st.warning("⚙️ Running TITAN engine...")

        data = run_engine()

        if "ERROR" in data:
            st.error(data["ERROR"])
        else:
            save_data(data)
            st.success("✅ TITAN updated")

else:
    st.info("⏳ Waiting for 10:50 Spain time")

# ============================
# DISPLAY
# ============================
if data and "ERROR" not in data:

    for pair in data:
        st.header(pair)

        d = data[pair]

        st.write(f"**Bias:** {d['macro_bias']}")
        st.write(f"**Regime:** {d['regime']}")
        st.write(f"**Score:** {d['score']}")

        st.write("### Zones")
        st.write(f"Buy: {d['buy_zone']}")
        st.write(f"Sell: {d['sell_zone']}")

        st.write("### Targets")
        st.write(f"T1: {d['t1']}")
        st.write(f"T2: {d['t2']}")
        st.write(f"T3: {d['t3']}")

        st.write("### Invalidation")
        st.write(f"Up: {d['invalid_up']}")
        st.write(f"Down: {d['invalid_down']}")

        st.markdown("---")

elif data and "ERROR" in data:
    st.error(data["ERROR"])

else:
    st.warning("No data yet.")
