import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud
import spacy
import nltk
from nltk.corpus import stopwords
from collections import Counter
import string
from datetime import datetime
from pymongo import MongoClient
from textblob import TextBlob
import plotly.graph_objects as go
import time

# 🎨 Configuration de la page
st.set_page_config(page_title="📊 Admin Dashboard - AI Chatbot Analytics", page_icon="🤖", layout="wide")

# 🌗 Light/Dark Mode Toggle
theme_mode = st.sidebar.radio("Choose Theme", ["Light", "Dark"], index=1)

def apply_theme(theme):
    if theme == "Dark":
        return """
            <style>
                body { background-color: #0F172A; color: white; }
                .stApp { background-color: #0F172A; }
                h1, h2, h3, h4, h5, h6, p, label { color: white !important; }
            </style>
        """
    else:
        return """
            <style>
                body { background-color: white; color: black; }
                .stApp { background-color: white; }
                h1, h2, h3, h4, h5, h6, p, label { color: black !important; }
            </style>
        """
st.markdown(apply_theme(theme_mode), unsafe_allow_html=True)

# 🛠️ Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

# 🔹 Chargement des données MongoDB
data = list(collection.find().sort("timestamp", -1))
df = pd.DataFrame(data)

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce', utc=True)
    df.dropna(subset=["timestamp"], inplace=True)
    df["response_length"] = df["answer"].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)

    # Ensure sentiment analysis columns exist
    if "sentiment_label" not in df.columns:
        df["sentiment"] = df["answer"].apply(lambda x: TextBlob(x).sentiment.polarity if isinstance(x, str) else 0)
        df["sentiment_label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))

# 📊 Sidebar Navigation
st.sidebar.header("🔍 Dashboard Navigation")
page = st.sidebar.radio("Select a Page", ["Overview", "Q&A Data", "Engagement Analysis", "Sentiment Analysis", "NER & Topics", "Data Export", "Statistics", "Live Chat Monitoring", "User Interaction Trends"])

# 📊 Sidebar Filters
st.sidebar.header("🔍 Filters")
if not df.empty:
    date_range = st.sidebar.date_input("Select Date Range", [df["timestamp"].min().date(), df["timestamp"].max().date()])
    sentiment_options = ["All", "Positive", "Neutral", "Negative"]
    sentiment_filter = st.sidebar.selectbox("Filter by Sentiment", sentiment_options)
    keyword = st.sidebar.text_input("Search Keyword")

    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0]).tz_localize('UTC')
        end_date = (pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)).tz_localize('UTC')
        df = df[(df["timestamp"] >= start_date) & (df["timestamp"] < end_date)]
    if sentiment_filter != "All":
        df = df[df["sentiment_label"] == sentiment_filter]
    if keyword:
        df = df[df["question"].str.contains(keyword, case=False, na=False)]

# 📊 New Functionalities
if page == "Live Chat Monitoring":
    st.header("📡 Live Chat Monitoring")
    if not df.empty:
        latest_messages = df.head(10)[["question", "answer", "timestamp"]]
        st.dataframe(latest_messages, use_container_width=True)
    else:
        st.warning("⚠️ No chat data available.")

elif page == "User Interaction Trends":
    st.header("📊 User Interaction Trends")
    if not df.empty:
        interaction_counts = df["question"].value_counts().head(10).reset_index()
        interaction_counts.columns = ["Question", "Count"]
        fig = px.bar(interaction_counts, x="Count", y="Question", orientation='h', title="Top User Questions", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No user interaction data available.")

# 📌 Footer
st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #64748B; font-size: 0.9rem;">
        AI Chatbot Admin Dashboard v2.0 • Powered by Streamlit • Updated: {datetime.now().strftime("%Y-%m-%d")}
    </div>
""", unsafe_allow_html=True)
