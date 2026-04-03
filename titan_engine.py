import pandas as pd
import random

def get_mock_data():
    # Generate stable fake market data (no API dependency)
    data = []
    price = 1.0800

    for i in range(10):
        change = random.uniform(-0.002, 0.002)
        open_price = price
        close_price = price + change
        high = max(open_price, close_price) + random.uniform(0, 0.001)
        low = min(open_price, close_price) - random.uniform(0, 0.001)

        data.append({
            "open": open_price,
            "high": high,
            "low": low,
            "close": close_price
        })

        price = close_price

    return pd.DataFrame(data)


def calculate_structure(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if last["high"] > prev["high"] and last["low"] > prev["low"]:
        return "UPTREND"
    elif last["high"] < prev["high"] and last["low"] < prev["low"]:
        return "DOWNTREND"
    else:
        return "RANGE"


def calculate_momentum(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return "BUY" if last["close"] > prev["close"] else "SELL"


def calculate_volatility(df):
    last = df.iloc[-1]
    return last["high"] - last["low"]


def calculate_score(structure, momentum, volatility):
    score = 0

    if structure == "UPTREND" and momentum == "BUY":
        score += 40
    elif structure == "DOWNTREND" and momentum == "SELL":
        score += 40

    if volatility > 0.001:
        score += 30
    else:
        score += 10

    if structure != "RANGE":
        score += 30

    return min(score, 100)


def calculate_titan(pair):
    df = get_mock_data()

    structure = calculate_structure(df)
    momentum = calculate_momentum(df)
    volatility = calculate_volatility(df)
    score = calculate_score(structure, momentum, volatility)

    last = df.iloc[-1]

    return {
        "structure": structure,
        "bias": momentum,
        "regime": "ACTIVE" if score >= 60 else "WEAK",
        "score": score,
        "buy_zone": round(last["low"], 5),
        "sell_zone": round(last["high"], 5),
        "t1": round(last["close"] * 0.999, 5),
        "t2": round(last["close"] * 1.001, 5),
        "t3": round(last["close"] * 1.002, 5),
    }
