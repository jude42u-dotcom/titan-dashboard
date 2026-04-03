import streamlit as st
import json
import os
from datetime import datetime
import pytz

# IMPORT TITAN ENGINE (CORRECT)
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
# LOAD / SAVE OUTPUT
# ============================
def load_saved_output():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return None

def save_output(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ============================
# MAIN LOGIC
# ============================
st.set_page_config(page_title="TITAN Dashboard", layout="wide")

st.title("🚀 TITAN Trading Dashboard")

now = datetime.now(SPAIN_TZ)
st.write(f"🕒 Spain Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

data = load_saved_output()

# RUN ENGINE ONLY ONCE AFTER 10:50
if is_after_update_time():
    if data is None:
        st.warning("⚙️ Running TITAN engine (daily update)...")
        data = run_engine()
        save_output(data)
else:
    st.info("⏳ Waiting for 10:50 Spain time update...")

# ============================
# DISPLAY OUTPUT
# ============================
if data:
    for pair in data:
        st.header(pair)

        d = data[pair]

        st.write(f"**Macro Bias:** {d.get('macro_bias', '-')}")
        st.write(f"**Regime:** {d.get('regime', '-')}")
        st.write(f"**Confluence Score:** {d.get('score', '-')}")

        st.write("### Zones")
        st.write(f"Buy Zone: {d.get('buy_zone', '-')}")
        st.write(f"Sell Zone: {d.get('sell_zone', '-')}")

        st.write("### Targets")
        st.write(f"T1: {d.get('t1', '-')}")
        st.write(f"T2: {d.get('t2', '-')}")
        st.write(f"T3: {d.get('t3', '-')}")

        st.write("### Invalidation")
        st.write(f"Up: {d.get('invalid_up', '-')}")
        st.write(f"Down: {d.get('invalid_down', '-')}")

        st.markdown("---")

else:
    st.warning("No data yet. Waiting for first run.")
