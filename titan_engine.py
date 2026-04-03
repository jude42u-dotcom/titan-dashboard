import requests
import math
from datetime import datetime

API_KEY = "e7636f5efb884afc9f706a6834e716f6"
BASE_URL = "https://api.twelvedata.com/time_series"

# ============================
# FETCH DATA
# ============================
def fetch(symbol, interval, outputsize):
    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    data = requests.get(url).json()

    if "values" not in data:
        raise Exception(f"API ERROR: {data}")

    return list(reversed(data["values"]))  # oldest → newest

# ============================
# STRUCTURE ENGINE (M1)
# ============================
def detect_structure(m1):
    highs = [float(c["high"]) for c in m1]
    lows = [float(c["low"]) for c in m1]

    recent_high = max(highs[-30:])
    recent_low = min(lows[-30:])

    last = float(m1[-1]["close"])

    if last > recent_high:
        return "BREAK_HIGH"
    elif last < recent_low:
        return "BREAK_LOW"
    else:
        return "RANGE"

# ============================
# TRSE CYCLE (DAY TYPE)
# ============================
def trse_cycle(daily):
    ranges = [float(d["high"]) - float(d["low"]) for d in daily[-5:]]
    avg_range = sum(ranges) / len(ranges)

    today_range = float(daily[-1]["high"]) - float(daily[-1]["low"])

    if today_range > avg_range * 1.2:
        return "EXPANSION"
    elif today_range < avg_range * 0.8:
        return "COMPRESSION"
    else:
        return "NORMAL"

# ============================
# GANN SQRT LEVELS
# ============================
def gann_levels(price):
    root = math.sqrt(price * 10000)

    up_45 = ((root + 1) ** 2) / 10000
    down_45 = ((root - 1) ** 2) / 10000

    up_90 = ((root + 2) ** 2) / 10000
    down_90 = ((root - 2) ** 2) / 10000

    return up_45, down_45, up_90, down_90

# ============================
# CONFLUENCE SCORE
# ============================
def confluence(structure, cycle):
    score = 50

    if structure == "BREAK_HIGH":
        score += 15
    elif structure == "BREAK_LOW":
        score += 15

    if cycle == "EXPANSION":
        score += 20
    elif cycle == "COMPRESSION":
        score -= 10

    return max(0, min(100, score))

# ============================
# ENGINE
# ============================
def run_engine():
    try:
        pairs = ["EUR/USD", "GBP/USD"]
        results = {}

        for pair in pairs:

            m1 = fetch(pair, "1min", 200)
            h1 = fetch(pair, "1h", 24)
            daily = fetch(pair, "1day", 10)
            weekly = fetch(pair, "1week", 5)

            last_price = float(m1[-1]["close"])

            structure = detect_structure(m1)
            cycle = trse_cycle(daily)

            g45_up, g45_down, g90_up, g90_down = gann_levels(last_price)

            score = confluence(structure, cycle)

            bias = "BUY" if structure == "BREAK_HIGH" else "SELL" if structure == "BREAK_LOW" else "NEUTRAL"

            results[pair.replace("/", "")] = {
                "macro_bias": bias,
                "regime": cycle,
                "score": score,
                "buy_zone": round(g45_down, 5),
                "sell_zone": round(g45_up, 5),
                "t1": round(g45_up, 5),
                "t2": round(g90_up, 5),
                "t3": round(g90_up + (g90_up - g45_up), 5),
                "invalid_up": round(g90_up + 0.005, 5),
                "invalid_down": round(g90_down - 0.005, 5)
            }

        return results

    except Exception as e:
        return {"ERROR": str(e)}
