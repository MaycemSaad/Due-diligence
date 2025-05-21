import streamlit as st
import pandas as pd
import requests
import time
import os
import json
import plotly.graph_objs as go

# Configuration
CACHE_FILE = "crypto_data_cache.json"
THEME_COLOR = "#00eaff"

# Chargement cache
def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if time.time() - cache["timestamp"] < 300:  # 5 minutes
                return cache["data"]
    return None

# Sauvegarde cache
def save_cache(data):
    cache = {"timestamp": time.time(), "data": data}
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

# Fetch données crypto
def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 10,
        "page": 1,
        "sparkline": True,
        "price_change_percentage": "24h"
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        if df.empty:
            return pd.DataFrame()
        df = df.rename(columns={
            "id": "Id",
            "image": "Logo",
            "name": "Name",
            "symbol": "Symbol",
            "current_price": "Price",
            "market_cap": "Market Cap",
            "total_volume": "24h Volume",
            "price_change_percentage_24h": "24h Change",
            "sparkline_in_7d": "Sparkline"
        })
        return df[["Id", "Logo", "Name", "Symbol", "Price", "Market Cap", "24h Volume", "24h Change", "Sparkline"]]
    except Exception as e:
        print(f"Erreur fetch_crypto_data: {e}")
        return pd.DataFrame()

# Sparkline Graph
def create_sparkline(prices):
    if not prices or not isinstance(prices, list):
        return st.empty()
    trend = (prices[-1] - prices[0]) / prices[0] if prices[0] else 0
    line_color = "#00cc00" if trend >= 0 else "#ff4d4d"
    fig = go.Figure(go.Scatter(
        x=list(range(len(prices))),
        y=prices,
        mode="lines",
        line=dict(color=line_color, width=2),
    ))
    fig.update_layout(
        height=40,
        width=100,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_visible=False,
        yaxis_visible=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(fig, use_container_width=False)

# Fonction principale
def show_crypto_market():
    st.header("📈 Crypto Market Live")
    st.subheader("Real-time top 10 cryptocurrency market data")

    refresh = st.button("🔄 Refresh Crypto Data")

    if refresh:
        df = fetch_crypto_data()
        if not df.empty:
            save_cache(df.to_dict(orient="records"))
    else:
        cached_data = load_cache()
        if cached_data:
            df = pd.DataFrame(cached_data)
        else:
            df = fetch_crypto_data()
            if not df.empty:
                save_cache(df.to_dict(orient="records"))

    if df.empty:
        st.error("Erreur : Impossible de récupérer les données du marché. Réessaye plus tard.")
    else:
        for idx, row in df.iterrows():
            st.markdown(f"### {row['Name']} ({row['Symbol'].upper()})")
            cols = st.columns([1, 2, 2, 2, 2, 2, 2])

            # Logo
            with cols[0]:
                if isinstance(row["Logo"], str) and row["Logo"].startswith("http"):
                    st.image(row["Logo"], width=40)

            # Prix
            with cols[1]:
                st.metric(label="Price", value=f"${row['Price']:,}")

            # Market Cap
            with cols[2]:
                st.metric(label="Market Cap", value=f"${int(row['Market Cap']):,}")

            # Volume
            with cols[3]:
                st.metric(label="24h Volume", value=f"${int(row['24h Volume']):,}")

            # 24h Change
            with cols[4]:
                change = row['24h Change']
                change_str = f"{change:.2f}%" if pd.notnull(change) else "N/A"
                st.metric(label="24h Change", value=change_str)

            # Sparkline
            with cols[5]:
                if isinstance(row["Sparkline"], dict) and "price" in row["Sparkline"]:
                    create_sparkline(row["Sparkline"]["price"])
                elif isinstance(row["Sparkline"], list):
                    create_sparkline(row["Sparkline"])

            st.markdown("---")
