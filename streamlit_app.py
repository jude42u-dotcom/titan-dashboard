import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import pytz

# =========================
# CONFIG
# =========================
API_KEY = "YOUR_TWELVEDATA_API_KEY"  # 🔴 PUT YOUR KEY HERE
MIN_ROWS = 50

# =========================
# FORMAT
# =========================
def fmt(x):
    return f"{float(x):.5f}"

# =========================
# TIME
# =========================
def spain_time():
    return datetime.now(pytz.timezone("Europe/Madrid"))

# =========================
# DATA (TWELVEDATA)
# =========================
def get_data(symbol="EUR/USD", interval="15min"):

    url = "https://api.twelvedata.com/time_series"

    params = {
        "symbol": symbol,
        "interval": interval,
        "outputsize": 100,
        "apikey": API_KEY
    }

    try:
        r = requests.get(url, params=params)
        data = r.json()

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])

        df.rename(columns={
            "datetime": "time",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close"
        }, inplace=True)

        df["time"] = pd.to_datetime(df["time"])
        df.set_index("time", inplace=True)

        df = df.astype(float)
        df = df.sort_index()

        return df

    except:
        return None

# =========================
# VALIDATION LAYER
# =========================
def validate(df):

    if df is None or df.empty:
        return False, "NO DATA"

    if len(df) < MIN_ROWS:
        return False, "INSUFFICIENT DATA"

    if df.isnull().any().any():
        return False, "NaN FOUND"

    if (df["High"] < df["Low"]).any():
        return False, "INVALID HIGH/LOW"

    if df.index.duplicated().any():
        return False, "DUPLICATES"

    # time continuity check
    expected = pd.Timedelta(minutes=15)
    diffs = df.index.to_series().diff().dropna()

    if not (diffs == expected).all():
        return False, "TIME GAPS"

    return True, "OK"

# =========================
# TITAN CORE (UNCHANGED LOGIC)
# =========================
def titan(df):

    highs = df["High"]
    lows = df["Low"]
    close = df["Close"].iloc[-1]

    recent_high = highs.iloc[-20:].max()
    recent_low = lows.iloc[-20:].min()
    R = recent_high - recent_low

    current_range = highs.iloc[-1] - lows.iloc[-1]
    avg_range = (highs - lows).iloc[-20:].mean()

    if current_range < avg_range:
        regime = "HFL (HIGH first)"
        bias = "SELL"
    else:
        regime = "LFHL (LOW first)"
        bias = "BUY"

    sell_zone = (recent_high - 0.2 * R, recent_high)
    buy_zone = (recent_low, recent_low + 0.2 * R)

    inv_up = recent_high
    inv_down = recent_low

    if bias == "SELL":
        t1 = close - 0.5 * R
        t2 = close - 1.0 * R
        t3 = close - 1.5 * R

        alt_t1 = close + 0.5 * R
        alt_t2 = close + 1.0 * R
        alt_t3 = close + 1.5 * R
    else:
        t1 = close + 0.5 * R
        t2 = close + 1.0 * R
        t3 = close + 1.5 * R

        alt_t1 = close - 0.5 * R
        alt_t2 = close - 1.0 * R
        alt_t3 = close - 1.5 * R

    return {
        "regime": regime,
        "sell_zone": sell_zone,
        "buy_zone": buy_zone,
        "inv_up": inv_up,
        "inv_down": inv_down,
        "t1": t1,
        "t2": t2,
        "t3": t3,
        "alt_t1": alt_t1,
        "alt_t2": alt_t2,
        "alt_t3": alt_t3
    }

# =========================
# DISPLAY WRAPPER (CRITICAL)
# =========================
def run(symbol):

    st.header(symbol)

    df = get_data(symbol)

    valid, reason = validate(df)

    if not valid:
        st.error(f"DATA REJECTED: {reason}")
        return

    r = titan(df)

    st.write(f"🟡 Regime: {r['regime']}")

    st.write(f"🔴 SELL ZONE: {fmt(r['sell_zone'][0])} – {fmt(r['sell_zone'][1])}")
    st.write(f"🟢 BUY ZONE: {fmt(r['buy_zone'][0])} – {fmt(r['buy_zone'][1])}")

    st.write(f"Invalidation Up: {fmt(r['inv_up'])}")
    st.write(f"Invalidation Down: {fmt(r['inv_down'])}")

    st.write("Targets (Primary):")
    st.write(f"T1: {fmt(r['t1'])}")
    st.write(f"T2: {fmt(r['t2'])}")
    st.write(f"T3: {fmt(r['t3'])}")

    st.write("Targets (Alternate):")
    st.write(f"T1: {fmt(r['alt_t1'])}")
    st.write(f"T2: {fmt(r['alt_t2'])}")
    st.write(f"T3: {fmt(r['alt_t3'])}")

# =========================
# APP
# =========================
st.title("🚀 TITAN PRO ENGINE (STABLE BUILD)")

st.write(f"Spain Time: {spain_time()}")

run("EUR/USD")
run("GBP/USD")
