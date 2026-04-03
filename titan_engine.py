import pandas as pd
import numpy as np
from datetime import datetime

def run_engine(eurusd, gbpusd):

    def calculate(pair_price):
        if pair_price is None:
            return {"status": "NO DATA"}

        buy_45 = pair_price - 0.0020
        buy_90 = pair_price - 0.0040

        sell_45 = pair_price + 0.0020
        sell_90 = pair_price + 0.0040

        return {
            "price": pair_price,
            "buy_zone": [round(buy_45, 5), round(buy_90, 5)],
            "sell_zone": [round(sell_45, 5), round(sell_90, 5)],
            "bias": "BUY" if pair_price > 1 else "SELL",
            "hfl": "HIGH FIRST",
            "lfhl": "LOW FIRST",
            "score": np.random.randint(60, 90),
            "delay_days": np.random.randint(1, 4),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    return {
        "EURUSD": calculate(eurusd),
        "GBPUSD": calculate(gbpusd)
    }
