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
st.sidebar.header("📌 Dashboard Navigation")
st.sidebar.markdown("---")

# 🔹 Main Navigation Buttons
selected_page = st.sidebar.selectbox("📍 Select a Page", [
    "🏠 Overview", 
    "📄 Q&A Data", 
    "📊 Engagement Analysis", 
    "📈 Sentiment Analysis", 
    "🔍 NER & Topics", 
    "📥 Data Export", 
    "📌 Statistics", 
    "🖥️ Live Chat Monitoring", 
    "📊 User Interaction Trends"
])

st.sidebar.markdown("---")

# 🔍 Advanced Filters
st.sidebar.header("🎯 Data Filters")
if not df.empty:
    # 📅 Date Range Selection
    st.sidebar.subheader("📅 Date Range")
    date_range = st.sidebar.date_input("Select Date Range", [df["timestamp"].min().date(), df["timestamp"].max().date()])
    
    # 😊 Sentiment Selection
    st.sidebar.subheader("😊 Sentiment Filter")
    sentiment_options = ["All", "Positive", "Neutral", "Negative"]
    sentiment_filter = st.sidebar.selectbox("Filter by Sentiment", sentiment_options)
    
    # 🔎 Keyword Search
    st.sidebar.subheader("🔎 Search Keyword")
    keyword = st.sidebar.text_input("Enter a keyword to search")

    # Applying Filters
    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0]).tz_localize('UTC')
        end_date = (pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)).tz_localize('UTC')
        df = df[(df["timestamp"] >= start_date) & (df["timestamp"] < end_date)]
    
    if sentiment_filter != "All":
        df = df[df["sentiment_label"] == sentiment_filter]
    
    if keyword:
        df = df[df["question"].str.contains(keyword, case=False, na=False)]

st.sidebar.markdown("---")
st.sidebar.info("📊 Use these filters to refine your chatbot analytics.")

# 📊 Page Navigation
if page == "Overview":
    st.header("📊 AI Chatbot Overview")
    
    # 🔹 Introduction Section
    st.subheader("💡 Dashboard Insights")
    st.write(
        "Welcome to the AI Chatbot Analytics Dashboard! This platform provides an in-depth analysis of chatbot interactions, user engagement, sentiment trends, and topic recognition. Use the sidebar filters to refine your analysis and gain valuable insights."
    )
    
    # 🔹 Key Metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="💬 Total Interactions", value=len(df))
    
    with col2:
        avg_response_length = round(df["response_length"].mean(), 2)
        st.metric(label="📝 Avg. Response Length", value=f"{avg_response_length} words")
    
    with col3:
        unique_users = df["question"].nunique()
        st.metric(label="👥 Unique Questions", value=unique_users)
    
    # 🔹 Sentiment Analysis Overview
    st.subheader("😊 Sentiment Distribution")
    sentiment_counts = df["sentiment_label"].value_counts()
    fig_sentiment = px.pie(
        values=sentiment_counts.values, 
        names=sentiment_counts.index, 
        title="Overall Sentiment Distribution", 
        color_discrete_sequence=["#2ECC71", "#E74C3C", "#F1C40F"]
    )
    st.plotly_chart(fig_sentiment, use_container_width=True)
    
    # 🔹 Engagement Over Time
    st.subheader("📈 Engagement Trends")
    fig_engagement = px.line(
        df, x="timestamp", y="response_length", 
        title="Chatbot Engagement Over Time", markers=True, 
        line_shape='spline', template='plotly_white'
    )
    st.plotly_chart(fig_engagement, use_container_width=True)
    
    # 🔹 Most Asked Questions
    st.subheader("📌 Most Frequent Questions")
    most_asked_questions = df["question"].value_counts().head(5).reset_index()
    most_asked_questions.columns = ["Question", "Count"]
    st.dataframe(most_asked_questions, use_container_width=True)
    
    # 🔹 Active Users Trend
    st.subheader("🚀 User Activity Over Time")
    df["date"] = df["timestamp"].dt.date
    daily_activity = df.groupby("date").size().reset_index(name="Interactions")
    fig_activity = px.bar(
        daily_activity, x="date", y="Interactions", 
        title="User Activity Over Time", color_discrete_sequence=["#1F77B4"]
    )
    st.plotly_chart(fig_activity, use_container_width=True)
    
    # 🔹 Word Cloud for Most Common Words
    st.subheader("🌍 Commonly Used Words")
    all_text = " ".join(df["question"].dropna())
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(all_text)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
    
    st.success("📢 Stay updated with your chatbot’s analytics and optimize interactions for better engagement!")


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
    if not df.empty:
        sentiment_counts = df["sentiment_label"].value_counts()
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, 
                     title="Sentiment Distribution", color_discrete_sequence=["#2ECC71", "#E74C3C", "#F1C40F"])
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No sentiment data available.")

elif page == "NER & Topics":
    st.header("🔍 Named Entity Recognition (NER) & Topics")
    if not df.empty:
        nlp = spacy.load("en_core_web_sm")
        all_text = " ".join(df["answer"].dropna())
        doc = nlp(all_text)
        entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
        if entities:
            wordcloud = WordCloud(width=800, height=400, background_color="white" if theme_mode == "Light" else "#0F172A", colormap="viridis").generate(" ".join(entities))
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.warning("⚠️ No named entities found in the selected dataset.")
    else:
        st.warning("⚠️ No data available for the selected filters.")

elif page == "Data Export":
    st.header("📥 Export Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Data as CSV", data=csv, file_name="chatbot_data.csv", mime="text/csv")

elif page == "Statistics":
    st.header("📊 Data Statistics")
    st.write(df.describe())

elif page == "Live Chat Monitoring":
    st.header("📡 Live Chat Monitoring")
    if not df.empty:
        latest_messages = df[["question", "answer", "timestamp"]].head(10)
        st.dataframe(latest_messages, use_container_width=True)
    else:
        st.warning("⚠️ No chat data available.")

elif page == "User Interaction Trends":
    st.header("📊 User Interaction Trends")
    if not df.empty:
        interaction_counts = df["question"].value_counts().reset_index()
        interaction_counts.columns = ["Question", "Count"]
        fig = px.bar(interaction_counts.head(10), x="Count", y="Question", orientation='h', title="Top User Questions", text_auto=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No user interaction data available.")

# 📌 Footer
st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #64748B; font-size: 0.9rem;">
        AI Chatbot Admin Dashboard v2.0 • Powered by Streamlit • Updated: {datetime.now().strftime("%Y-%m-%d")}
    </div>
""", unsafe_allow_html=True)
