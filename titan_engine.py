import pandas as pd
import random

# -------------------------
# MOCK DATA (STABLE — NO ERRORS)
# -------------------------
def get_mock_data():
    data = []
    price = 1.0800

    for i in range(20):
        open_price = price
        high = open_price + random.uniform(0.0005, 0.0020)
        low = open_price - random.uniform(0.0005, 0.0020)
        close = random.uniform(low, high)

        data.append({
            "open": open_price,
            "high": high,
            "low": low,
            "close": close
        })

        price = close

    return pd.DataFrame(data)

# -------------------------
# TITAN ENGINE V2
# -------------------------
def calculate_titan(pair):
    df = get_mock_data()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    # STRUCTURE
    if last["high"] > prev["high"] and last["low"] > prev["low"]:
        structure = "UPTREND"
    elif last["high"] < prev["high"] and last["low"] < prev["low"]:
        structure = "DOWNTREND"
    else:
        structure = "RANGE"

    # ASIA RANGE (first 5 candles)
    asia_high = df["high"].iloc[:5].max()
    asia_low = df["low"].iloc[:5].min()

    # FIRST EXTREME
    if last["close"] > asia_high:
        first_extreme = "HIGH TAKEN"
        bias = "BUY"
    elif last["close"] < asia_low:
        first_extreme = "LOW TAKEN"
        bias = "SELL"
    else:
        first_extreme = "INSIDE RANGE"
        bias = "NEUTRAL"

    # REGIME
    regime = "ACTIVE" if bias != "NEUTRAL" else "WAIT"

    # VOLATILITY
    range_size = last["high"] - last["low"]

    # SCORE
    score = 0
    if structure != "RANGE":
        score += 30
    if bias != "NEUTRAL":
        score += 40
    if range_size > 0.001:
        score += 30

    score = min(score, 100)

    # ZONES
    buy_zone = round(asia_low, 5)
    sell_zone = round(asia_high, 5)

    # TARGETS (EXPANSION)
    expansion = asia_high - asia_low

    if bias == "BUY":
        t1 = asia_high + expansion * 0.5
        t2 = asia_high + expansion * 1.0
        t3 = asia_high + expansion * 1.5
    elif bias == "SELL":
        t1 = asia_low - expansion * 0.5
        t2 = asia_low - expansion * 1.0
        t3 = asia_low - expansion * 1.5
    else:
        t1 = t2 = t3 = last["close"]

    return {
        "structure": structure,
        "bias": bias,
        "regime": regime,
        "first_extreme": first_extreme,
        "score": score,
        "buy_zone": round(buy_zone, 5),
        "sell_zone": round(sell_zone, 5),
        "t1": round(t1, 5),
        "t2": round(t2, 5),
        "t3": round(t3, 5),
    }
