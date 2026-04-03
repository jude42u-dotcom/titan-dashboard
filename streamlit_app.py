import streamlit as st
from datetime import datetime

st.set_page_config(page_title="TITAN Dashboard", layout="wide")

# HEADER
st.title("TITAN Trading Dashboard")
st.subheader(f"UTC Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

# SESSION STATUS
st.markdown("## Session Status")

now = datetime.utcnow().hour

london_active = 7 <= now <= 16
ny_active = 12 <= now <= 21

col1, col2 = st.columns(2)

with col1:
    st.write("London Session:", "ACTIVE" if london_active else "CLOSED")

with col2:
    st.write("New York Session:", "ACTIVE" if ny_active else "CLOSED")

# MARKET CONTEXT
st.markdown("## Market Context")
st.write("DXY Bias: Neutral")
st.write("Risk Sentiment: Mixed")
st.write("Week Bias: TBD")

# TABS
tab1, tab2, tab3 = st.tabs(["EURUSD", "GBPUSD", "Comparison"])

with tab1:
    st.markdown("### EURUSD")
    st.write("Macro Bias: BUY")
    st.write("Buy Zone: 1.0800 - 1.0820")
    st.write("Sell Zone: 1.0950 - 1.0970")
    st.write("Invalidation: 1.0750")
    st.write("Targets: 1.1000")

with tab2:
    st.markdown("### GBPUSD")
    st.write("Macro Bias: SELL")
    st.write("Buy Zone: 1.2600 - 1.2620")
    st.write("Sell Zone: 1.2750 - 1.2770")
    st.write("Invalidation: 1.2800")
    st.write("Targets: 1.2500")

with tab3:
    st.markdown("### Comparison")
    st.write("EURUSD vs GBPUSD overview")
