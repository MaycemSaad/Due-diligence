import os
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from pymongo import MongoClient

# 🎨 Streamlit Page Config
st.set_page_config(page_title="📊 AI Chatbot Analytics", page_icon="🤖", layout="wide")

# 🛠️ Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

# 🔹 Load Data from MongoDB
data = list(collection.find().sort("timestamp", -1))
df = pd.DataFrame(data)

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["response_length"] = df["answer"].apply(lambda x: len(x.split()))

# 📊 Sidebar Filters
st.sidebar.header("🔍 Filters")

# Date Range Filter
default_start = df["timestamp"].min() if not df.empty else datetime.now()
default_end = df["timestamp"].max() if not df.empty else datetime.now()
date_range = st.sidebar.date_input("Select Date Range", [default_start, default_end])

# Sentiment Filter
sentiment_options = ["All", "Positive", "Neutral", "Negative"]
sentiment_filter = st.sidebar.selectbox("Filter by Sentiment", sentiment_options)

# Keyword Search
keyword = st.sidebar.text_input("Search Keyword")

# Apply Filters
if not df.empty:
    if len(date_range) == 2:
        df = df[(df["timestamp"] >= pd.to_datetime(date_range[0])) & (df["timestamp"] <= pd.to_datetime(date_range[1]))]
    if sentiment_filter != "All":
        df = df[df["sentiment_label"] == sentiment_filter]
    if keyword:
        df = df[df["question"].str.contains(keyword, case=False, na=False)]

# 📝 Display Chatbot Q&A Data
st.header("📊 Chatbot Q&A Data")

st.dataframe(df[["_id", "question", "answer", "timestamp", "response_length"]], use_container_width=True)

# 📈 Engagement Over Time Chart
st.header("📈 Engagement Over Time")
if not df.empty:
    fig = px.line(df, x="timestamp", y="response_length", title="Engagement Over Time", markers=True)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for the selected filters.")
