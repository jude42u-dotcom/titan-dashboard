import pandas as pd
import requests

def get_data(pair):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{pair}=X?interval=1d&range=5d"
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


def calculate_titan(pair):
    df = get_data(pair)

    if df is None or len(df) < 2:
        return None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    direction = "BUY" if last["close"] > prev["close"] else "SELL"

    return {
        "structure": "UPTREND" if direction == "BUY" else "DOWNTREND",
        "bias": direction,
        "regime": "ACTIVE",
        "score": 70,
        "buy_zone": round(last["low"], 5),
        "sell_zone": round(last["high"], 5),
        "t1": round(last["close"] * 0.999, 5),
        "t2": round(last["close"] * 1.001, 5),
        "t3": round(last["close"] * 1.002, 5),
    }
