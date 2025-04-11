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

# 🎨 Configuration de la page
st.set_page_config(page_title="📊 Admin Dashboard - AI Chatbot Analytics", page_icon="🤖", layout="wide")

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
page = st.sidebar.radio("Select a Page", ["Overview", "Q&A Data", "Engagement Analysis", "Sentiment Analysis", "NER & Topics"])

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
if page == "Overview":
    st.header("📊 AI Chatbot Overview")
    st.write("Welcome to the AI Chatbot Analytics Dashboard! Use the sidebar to explore different insights.")

elif page == "Q&A Data":
    st.header("📊 Chatbot Q&A Data")
    if not df.empty:
        st.dataframe(df[['_id', 'question', 'answer', 'timestamp', 'response_length']], use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected filters.")

elif page == "Engagement Analysis":
    st.header("📈 Engagement Over Time")
    if not df.empty:
        fig = px.line(df, x="timestamp", y="response_length", title="Engagement Over Time", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

elif page == "Sentiment Analysis":
    st.header("📈 Sentiment Analysis")
    sentiment_counts = df["sentiment_label"].value_counts()
    fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, 
                 title="Sentiment Distribution", color_discrete_sequence=["#2ECC71", "#E74C3C", "#F1C40F"])
    st.plotly_chart(fig, use_container_width=True)

elif page == "NER & Topics":
    st.header("🔍 Named Entity Recognition (NER) & Topics")
    nlp = spacy.load("en_core_web_sm")
    all_text = " ".join(df["answer"].dropna())
    doc = nlp(all_text)
    entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
    wordcloud = WordCloud(width=800, height=400, background_color="#0F172A", colormap="viridis").generate(" ".join(entities))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# 📌 Footer
st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #64748B; font-size: 0.9rem;">
        AI Chatbot Admin Dashboard v2.0 • Powered by Streamlit • Updated: {datetime.now().strftime("%Y-%m-%d")}
    </div>
""", unsafe_allow_html=True)