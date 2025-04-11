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
page = st.sidebar.radio("Select a Page", ["Overview", "Q&A Data", "Engagement Analysis", "Sentiment Analysis", "NER & Topics", "Data Export", "Statistics"])

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

# 📊 Page Navigation
if page == "NER & Topics":
    st.header("🔍 Named Entity Recognition (NER) & Topics")
    if not df.empty:
        nlp = spacy.load("en_core_web_sm")
        all_text = " ".join(df["answer"].dropna())
        doc = nlp(all_text)
        entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
        entity_counts = Counter(entities)

        if entities:
            # 🎭 Animated Bar Chart
            entity_df = pd.DataFrame(entity_counts.most_common(10), columns=["Entity", "Count"])
            fig = px.bar(entity_df, x="Count", y="Entity", orientation='h', text_auto=True, animation_frame=entity_df.index, 
                         title="Top Named Entities", template="plotly_dark" if theme_mode == "Dark" else "plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # 🎨 Animated Word Cloud
            st.subheader("📌 Dynamic Word Cloud")
            for _ in range(3):
                wordcloud = WordCloud(width=800, height=400, background_color="white" if theme_mode == "Light" else "#0F172A", colormap="viridis").generate(" ".join(entities))
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                st.pyplot(fig)
                time.sleep(2)
        else:
            st.warning("⚠️ No named entities found in the selected dataset.")
    else:
        st.warning("⚠️ No data available for the selected filters.")

# 📌 Footer
st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #64748B; font-size: 0.9rem;">
        AI Chatbot Admin Dashboard v2.0 • Powered by Streamlit • Updated: {datetime.now().strftime("%Y-%m-%d")}
    </div>
""", unsafe_allow_html=True)