import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import time

from data_stream import get_live_data
from metrics import compute_metrics
from plots import (
    create_price_sentiment_chart, 
    create_sentiment_heatmap, 
    create_volume_correlation_chart, 
    create_source_impact_chart, 
    create_technical_indicators
)
from export import export_csv, export_pdf
from styles import set_custom_styles

# === Streamlit Settings ===
st.set_page_config(page_title="Crypto Sentiment Pro", layout="wide", initial_sidebar_state="expanded")
set_custom_styles()

# === Sidebar ===
st.sidebar.image("", width=200)
st.sidebar.title("Crypto Sentiment Pro 🚀")

selected_pair = st.sidebar.selectbox("Select Crypto Pair", ['BTC-USD', 'ETH-USD', 'SOL-USD', 'ADA-USD', 'DOT-USD'])
timeframe_minutes = st.sidebar.selectbox("Select Timeframe", [5, 15, 60, 240, 1440], index=2)
refresh_rate = st.sidebar.slider("Auto-Refresh every (seconds)", 5, 60, 10)

# === Main Tabs ===
tabs = st.tabs(["🏠 Home", "📈 Charts", "💬 Social Feed", "📊 Technical Analysis", "🚨 Alerts", "📂 Export"])

# Simulate live incoming data
price_df, social_df = get_live_data(selected_pair)

# Metrics
price_change, sentiment_score, correlation, social_vol, alert_level = compute_metrics(price_df, social_df, timeframe_minutes)

# === HOME ===
with tabs[0]:
    st.header(f"Overview: {selected_pair}")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Price Change", f"{price_change:+.2f}%")
    col2.metric("Sentiment Score", f"{sentiment_score:.2f}")
    col3.metric("Correlation", f"{correlation:.2f}")
    col4.metric("Social Volume", f"{social_vol}")
    col5.metric("Market Alert", alert_level)

    st.plotly_chart(create_price_sentiment_chart(price_df, social_df), use_container_width=True)

# === CHARTS ===
with tabs[1]:
    st.header("Advanced Charts")
    st.plotly_chart(create_sentiment_heatmap(social_df), use_container_width=True)
    st.plotly_chart(create_volume_correlation_chart(price_df, social_df), use_container_width=True)
    st.plotly_chart(create_source_impact_chart(social_df), use_container_width=True)

# === SOCIAL FEED ===
with tabs[2]:
    st.header("Latest Social Mentions")
    st.dataframe(social_df[['timestamp', 'source', 'sentiment', 'content']].sort_values('timestamp', ascending=False).head(10))

# === TECHNICAL ANALYSIS ===
with tabs[3]:
    st.header("Technical Indicators")
    st.plotly_chart(create_technical_indicators(price_df), use_container_width=True)

# === ALERTS ===
with tabs[4]:
    st.header("Market Alerts")
    if abs(sentiment_score) > 0.5:
        st.error(f"🚨 Strong market sentiment detected! ({sentiment_score:.2f})")
    else:
        st.success("✅ Market is stable.")

# === EXPORT ===
with tabs[5]:
    st.header("Export Your Analysis")
    export_csv(price_df, social_df)
    export_pdf(price_df, social_df)

# Auto-refresh
time.sleep(refresh_rate)
st.experimental_rerun()
