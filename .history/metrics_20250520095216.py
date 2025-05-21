import pandas as pd
import numpy as np

def compute_metrics(price_df, social_df, timeframe_minutes):
    time_threshold = price_df['timestamp'].max() - pd.Timedelta(minutes=timeframe_minutes)
    
    price_df = price_df[price_df['timestamp'] >= time_threshold]
    social_df = social_df[social_df['timestamp'] >= time_threshold]

    price_change = ((price_df['price'].iloc[-1] - price_df['price'].iloc[0]) / price_df['price'].iloc[0]) * 100
    sentiment_score = social_df['sentiment'].mean() if not social_df.empty else 0
    correlation = price_df['price'].corr(social_df['sentiment']) if not price_df.empty and not social_df.empty else 0
    social_vol = social_df['volume'].sum() if not social_df.empty else 0

    alert_level = "Normal"
    if abs(sentiment_score) > 0.5:
        alert_level = "ALERT"

    return price_change, sentiment_score, correlation, social_vol, alert_level
