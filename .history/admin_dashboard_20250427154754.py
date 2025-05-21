import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import time
from Questions_Bank import Questions_bank


def show_admin_dashboard():
    # === Database Connections ===
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]
    qa_col = db["qa"]

    # === Load Q&A Data ===
    df = pd.DataFrame(list(qa_col.find()))
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        df["response_length"] = df["answer"].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)
        if "sentiment_label" not in df.columns:
            df["sentiment"] = df["answer"].apply(lambda x: TextBlob(x).sentiment.polarity if isinstance(x, str) else 0)
            df["sentiment_label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))

    # === Global CSS Professional Mode ===
    st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #0f172a;
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a, #1e293b);
        padding: 2rem 1rem;
        border-right: 2px solid #1e293b;
        height: 100vh;
    }
    h1, h2, h3, .sidebar-title {
        color: #38bdf8;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # === Sidebar ===
    with st.sidebar:
        st.image("logo.png", width=150)
        st.markdown('<div class="sidebar-title">Due Diligence AI</div>', unsafe_allow_html=True)

        page = st.radio("Navigation", [
            "👥 Manage Users", 
            "🤖 Questions Bank", 
            "📊 Overview", 
            "📚 Q&A Data", 
            "📈 Engagement Analysis", 
            "💬 Sentiment Analysis", 
            "📈 Statistics", 
            "🔥 Trending Topics", 
            "✨ Advanced Sentiment Analysis"
        ], index=0)

    st.markdown('<hr style="border: 1px solid #334155;">', unsafe_allow_html=True)

    # === Pages ===
    if page == "👥 Manage Users":
        manage_users(users_col)

    elif page == "🤖 Questions Bank":
        Questions_bank()

    elif page == "📊 Overview":
        show_overview(df)

    elif page == "📚 Q&A Data":
        st.title("📚 Q&A Data")
        st.info("This section displays all Q&A exchanges from the chatbot.")
        st.dataframe(df[['question', 'answer', 'timestamp', 'response_length']], use_container_width=True)
        st.download_button("📥 Download Q&A CSV", df.to_csv(index=False).encode('utf-8'), "qa_data.csv")

    elif page == "📈 Engagement Analysis":
        st.title("📈 Engagement Over Time")
        st.info("Shows the daily number of user interactions.")
        df["date"] = df["timestamp"].dt.date
        engagement = df.groupby("date").size().reset_index(name="Interactions")
        fig = px.line(engagement, x="date", y="Interactions", title="User Engagement", markers=True, color_discrete_sequence=["#38bdf8"])
        st.plotly_chart(fig, use_container_width=True)

    elif page == "💬 Sentiment Analysis":
        st.title("💬 Sentiment Analysis")
        st.info("Pie chart of Positive, Neutral, Negative responses.")
        sentiment_counts = df["sentiment_label"].value_counts()
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Sentiment Distribution", color_discrete_sequence=["#38bdf8", "#0ea5e9", "#0f172a"])
        st.plotly_chart(fig, use_container_width=True)

    elif page == "📈 Statistics":
        st.title("📈 Data Statistics")
        st.info("Summary statistics of chatbot responses.")
        st.dataframe(df.describe(), use_container_width=True)
        st.download_button("📥 Download Statistics CSV", df.describe().to_csv().encode('utf-8'), "statistics.csv")

    elif page == "🔥 Trending Topics":
        st.title("🔥 Trending Topics")
        st.info("Top keywords extracted from user questions.")
        vectorizer = TfidfVectorizer(stop_words='english', max_features=20)
        tfidf_matrix = vectorizer.fit_transform(df["question"].dropna())
        keywords = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
        top_keywords = keywords.mean().sort_values(ascending=False).reset_index()
        top_keywords.columns = ["Keyword", "Importance"]
        fig = px.bar(top_keywords, x="Importance", y="Keyword", orientation="h", title="Top Keywords", color_discrete_sequence=["#38bdf8"])
        st.plotly_chart(fig, use_container_width=True)

    elif page == "✨ Advanced Sentiment Analysis":
        st.title("✨ Sentiment Analysis Over Time")
        st.info("Tracks how sentiment evolves over time.")
        df["date"] = df["timestamp"].dt.date
        sentiment_trend = df.groupby(["date", "sentiment_label"]).size().unstack().fillna(0)
        fig = px.line(sentiment_trend, title="Sentiment Trend Over Time")
        st.plotly_chart(fig, use_container_width=True)


# === Function for Manage Users ===
def manage_users(users_col):
    st.title("👥 User Management Panel")
    with st.expander("➕ Add New User", expanded=False):
        with st.form(key="create_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name")
                email = st.text_input("Email")
            with col2:
                last_name = st.text_input("Last Name")
                password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            submit_create = st.form_submit_button("Create User 🚀")

        if submit_create:
            if not all([first_name, last_name, email, password]):
                st.error("❌ Please fill all fields.")
            elif users_col.find_one({"email": email}):
                st.error("❌ Email already exists.")
            else:
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                users_col.insert_one({
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": hashed_pw,
                    "role": role,
                    "created_at": datetime.now(timezone.utc)
                })
                st.success(f"✅ {first_name} created successfully!")
                st.rerun()

    st.divider()
    st.subheader("🔎 Search Users")
    search_query = st.text_input("Search by Name or Email").lower()
    users = list(users_col.find({}, {"password": 0}))

    if search_query:
        users = [u for u in users if search_query in u.get('first_name', '').lower() or search_query in u.get('last_name', '').lower() or search_query in u.get('email', '').lower()]

    st.dataframe(pd.DataFrame(users))


# === Simple Overview Page ===
def show_overview(df):
    st.title("📊 Dashboard Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Interactions", value=len(df))
    col2.metric(label="Avg Response Length", value=f"{round(df['response_length'].mean(), 2)} words")
    col3.metric(label="Unique Questions", value=df["question"].nunique())

    st.markdown("## 🚀 Engagement Over Time")
    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date").size().reset_index(name="Interactions")
    fig = px.area(daily, x="date", y="Interactions", title="Interactions per Day", color_discrete_sequence=["#0ea5e9"])
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("## 📈 Sentiment Distribution")
    sentiment_counts = df["sentiment_label"].value_counts()
    fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Sentiment Pie Chart", color_discrete_sequence=["#38bdf8", "#0ea5e9", "#64748B"])
    st.plotly_chart(fig, use_container_width=True)

    st.download_button("📥 Download Full Dataset CSV", df.to_csv(index=False).encode('utf-8'), "full_dataset.csv")