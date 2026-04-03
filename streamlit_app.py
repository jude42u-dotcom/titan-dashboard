import requests

API_KEY = "e7636f5efb884afc9f706a6834e716f6"
BASE_URL = "https://api.twelvedata.com/time_series"

# ============================
# FETCH DATA
# ============================
def fetch_data(symbol, interval, outputsize=100):
    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    response = requests.get(url).json()

    if "values" not in response:
        raise Exception(f"API error for {symbol}")

    return response["values"]

# ============================
# CORE ENGINE
# ============================
def run_engine():
    
    # FETCH DATA (AUTO)
    eurusd_m1 = fetch_data("EUR/USD", "1min", 100)
    gbpusd_m1 = fetch_data("GBP/USD", "1min", 100)

    # SIMPLE PLACEHOLDER LOGIC (we upgrade later)
    eur_price = float(eurusd_m1[0]["close"])
    gbp_price = float(gbpusd_m1[0]["close"])

    return {
        "EURUSD": {
            "macro_bias": "BUY" if eur_price > 1.05 else "SELL",
            "regime": "Expansion",
            "score": 75,
            "buy_zone": eur_price - 0.002,
            "sell_zone": eur_price + 0.002,
            "t1": eur_price + 0.003,
            "t2": eur_price + 0.006,
            "t3": eur_price + 0.010,
            "invalid_up": eur_price + 0.015,
            "invalid_down": eur_price - 0.015
        },
        "GBPUSD": {
            "macro_bias": "BUY" if gbp_price > 1.20 else "SELL",
            "regime": "Expansion",
            "score": 78,
            "buy_zone": gbp_price - 0.002,
            "sell_zone": gbp_price + 0.002,
            "t1": gbp_price + 0.003,
            "t2": gbp_price + 0.006,
            "t3": gbp_price + 0.010,
            "invalid_up": gbp_price + 0.015,
            "invalid_down": gbp_price - 0.015
        }
    }
