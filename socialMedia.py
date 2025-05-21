import streamlit as st
import pandas as pd
import time
import os
import json
from newsapi import NewsApiClient  # ✅ Corrected
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer  # ✅ Correct
from portfolio import fetch_crypto_data

# === Configuration ===
CACHE_FILE = "social_media_cache.json"
NEWSAPI_KEY = "b1e73214686448c6828be8f624bce390"
TOP_10_COINS = ["bitcoin", "ethereum", "tether", "xrp", "bnb", "solana", "usd-coin", "dogecoin", "cardano", "tron"]

newsapi = NewsApiClient(api_key=NEWSAPI_KEY)
sentiment_analyzer = SentimentIntensityAnalyzer()

def fetch_new_social_media_posts(coins=TOP_10_COINS):
    posts = []
    df = fetch_crypto_data()
    coin_map = {row["Name"].lower(): row for row in df.to_dict("records")}

    try:
        for coin in coins:
            articles = newsapi.get_everything(q=coin, language="en", sort_by="publishedAt", page_size=1)
            if articles["status"] == "ok" and articles["articles"]:
                for article in articles["articles"]:
                    posts.append({
                        "id": article.get("url", str(int(time.time()))),
                        "text": article.get("title", "") + " - " + (article.get("description", "") or "")[:280],
                        "created_at": article.get("publishedAt", time.strftime("%Y-%m-%d %H:%M:%S")),
                        "user": article.get("source", {}).get("name", "Unknown"),
                        "platform": "News",
                        "coin": coin,
                        "logo": coin_map.get(coin.lower(), {}).get("Logo", "")
                    })
    except Exception as e:
        print(f"Error fetching NewsAPI data: {e}")

    for post in posts:
        sentiment_scores = sentiment_analyzer.polarity_scores(post["text"])
        post["sentiment"] = "positive" if sentiment_scores["compound"] > 0.05 else "negative" if sentiment_scores["compound"] < -0.05 else "neutral"
        post["sentiment_score"] = sentiment_scores["compound"]
        coin = post["coin"].lower()
        if coin in coin_map:
            try:
                price_change = float(coin_map[coin]["24h Change"].replace("%", ""))
                post["price_change_24h"] = price_change
            except:
                post["price_change_24h"] = 0.0
        else:
            post["price_change_24h"] = 0.0
    return posts

def save_cache(data):
    cache = {"timestamp": time.time(), "data": data}
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)
            if time.time() - cache["timestamp"] < 600:
                return cache["data"]
    return []

def predict_investment(posts):
    df = pd.DataFrame(posts)
    results = []

    for coin in df["coin"].unique():
        coin_posts = df[df["coin"] == coin]
        avg_sentiment = coin_posts["sentiment_score"].mean()
        price_change = coin_posts["price_change_24h"].iloc[-1]
        score = avg_sentiment * 50 + price_change * 2

        if score > 20:
            recommendation = "Investir 🚀"
            color = "green"
        elif score < -20:
            recommendation = "Ne pas investir ❌"
            color = "red"
        else:
            recommendation = "Attendre 🤔"
            color = "gray"

        results.append({
            "coin": coin.capitalize(),
            "recommendation": recommendation,
            "color": color,
            "avg_sentiment": avg_sentiment,
            "price_change": price_change
        })
    return results

def show_social_media_analysis():
    st.header("📢 Crypto Social Media Analysis")

    if st.button("🔄 Refresh Social Data"):
        posts = fetch_new_social_media_posts()
        save_cache(posts)
    else:
        posts = load_cache()

    if posts:
        df_posts = pd.DataFrame(posts)[["coin", "text", "user", "platform", "created_at", "sentiment", "price_change_24h"]]
        st.subheader("📰 Latest Articles")
        st.dataframe(df_posts, use_container_width=True)

        st.subheader("📈 Investment Predictions")
        predictions = predict_investment(posts)

        for pred in predictions:
            with st.expander(f"{pred['coin']} - {pred['recommendation']}", expanded=True):
                st.markdown(f"**Sentiment Moyen :** {pred['avg_sentiment']:.2f}")
                st.markdown(f"**Variation 24h :** {pred['price_change']:.2f}%")
                st.markdown(f"**Décision :** :{pred['color']}[{pred['recommendation']}]")
    else:
        st.warning("No posts available. Click Refresh to fetch new data.")
