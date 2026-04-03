import pandas as pd
import requests

def get_data(pair):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}=X?interval=1d&range=10d"
    r = requests.get(url).json()
    
    try:
        result = r['chart']['result'][0]
        timestamps = result['timestamp']
        ohlc = result['indicators']['quote'][0]

        df = pd.DataFrame({
            "time": timestamps,
            "open": ohlc["open"],
            "high": ohlc["high"],
            "low": ohlc["low"],
            "close": ohlc["close"],
        })

        return df.dropna()

    except:
        return None


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

    if volatility > 0.005:
        score += 30
    else:
        score += 10

    if structure != "RANGE":
        score += 30

    return min(score, 100)


def calculate_titan(pair):
    df = get_data(pair)

    if df is None or len(df) < 3:
        return None

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
