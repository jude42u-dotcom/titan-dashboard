import requests

API_KEY = "e7636f5efb884afc9f706a6834e716f6"
BASE_URL = "https://api.twelvedata.com/time_series"

# ============================
# FETCH DATA
# ============================
def fetch_data(symbol, interval="1min", outputsize=100):
    url = f"{BASE_URL}?symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={API_KEY}"
    response = requests.get(url).json()

    if "values" not in response:
        raise Exception(f"API ERROR: {response}")

    return response["values"]

# ============================
# CORE ENGINE (SAFE VERSION)
# ============================
def run_engine():
    try:
        eurusd = fetch_data("EUR/USD")
        gbpusd = fetch_data("GBP/USD")

        eur_price = float(eurusd[0]["close"])
        gbp_price = float(gbpusd[0]["close"])

        return {
            "EURUSD": {
                "macro_bias": "BUY" if eur_price > 1.05 else "SELL",
                "regime": "Expansion",
                "score": 75,
                "buy_zone": round(eur_price - 0.002, 5),
                "sell_zone": round(eur_price + 0.002, 5),
                "t1": round(eur_price + 0.003, 5),
                "t2": round(eur_price + 0.006, 5),
                "t3": round(eur_price + 0.010, 5),
                "invalid_up": round(eur_price + 0.015, 5),
                "invalid_down": round(eur_price - 0.015, 5)
            },
            "GBPUSD": {
                "macro_bias": "BUY" if gbp_price > 1.20 else "SELL",
                "regime": "Expansion",
                "score": 78,
                "buy_zone": round(gbp_price - 0.002, 5),
                "sell_zone": round(gbp_price + 0.002, 5),
                "t1": round(gbp_price + 0.003, 5),
                "t2": round(gbp_price + 0.006, 5),
                "t3": round(gbp_price + 0.010, 5),
                "invalid_up": round(gbp_price + 0.015, 5),
                "invalid_down": round(gbp_price - 0.015, 5)
            }
        }

    except Exception as e:
        return {"ERROR": str(e)}
