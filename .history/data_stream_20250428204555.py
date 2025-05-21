import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_live_data(pair):
    now = datetime.now()
    timestamps = pd.date_range(now - timedelta(minutes=100), periods=100, freq='1min')

    price_df = pd.DataFrame({
        "timestamp": timestamps,
        "price": np.random.normal(50000, 3000, 100) if pair == "BTC-USD" else
                 np.random.normal(3000, 300, 100) if pair == "ETH-USD" else
                 np.random.normal(100, 10, 100),
        "volume": np.random.lognormal(10, 1, 100)
    })

    social_df = pd.DataFrame({
        "timestamp": timestamps,
        "source": np.random.choice(["Twitter", "Reddit", "Telegram", "4chan", "Discord"], 100),
        "content": ["Crypto is great 🚀"] * 100,
        "sentiment": np.random.uniform(-1, 1, 100),
        "volume": np.random.poisson(50, 100)
    })

    return price_df, social_df
