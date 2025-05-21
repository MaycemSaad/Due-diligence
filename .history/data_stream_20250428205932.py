import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_random_post():
    crypto_assets = ['Bitcoin', 'Ethereum', 'Solana', 'Cardano', 'Dogecoin', 'Polkadot', 'Avalanche']
    actions = [
        "is pumping ", 
        "is crashing ", 
        "hit a new ATH ", 
        "is facing huge sell pressure ",
        "is recovering fast ",
        "experiences whale activity ",
        "launches a new upgrade 🔧",
        "gets listed on new exchange 🏦",
        "suffers a hack! 🔓",
        "surpasses market expectations 🎯"
    ]
    
    asset = random.choice(crypto_assets)
    action = random.choice(actions)
    return f"{asset} {action}"

def get_live_data(pair):
    now = datetime.now()
    timestamps = pd.date_range(end=now, periods=100, freq='1min')

    # Base price logic
    if pair == "BTC-USD":
        base_price = 50000
    elif pair == "ETH-USD":
        base_price = 3000
    else:
        base_price = 100

    price_changes = np.random.normal(0, 50, 100)  # random walk
    price_series = base_price + np.cumsum(price_changes)

    price_df = pd.DataFrame({
        "timestamp": timestamps,
        "price": price_series,
        "volume": np.random.lognormal(10, 1, 100)
    })

    social_df = pd.DataFrame({
        "timestamp": timestamps,
        "source": np.random.choice(["Twitter", "Reddit", "Telegram", "4chan", "Discord"], 100),
        "content": [generate_random_post() for _ in range(100)],
        "sentiment": np.random.uniform(-1, 1, 100),
        "volume": np.random.poisson(50, 100)
    })

    return price_df, social_df
