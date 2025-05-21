import streamlit as st
from pymongo import MongoClient
import bcrypt
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import spacy
import numpy as np
from wordcloud import WordCloud
from collections import Counter
from datetime import datetime, timezone
from textblob import TextBlob
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
    st.markdown(""" YOUR CSS STYLE SAME AS BEFORE """, unsafe_allow_html=True)

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
            "🔍 NER & Topics", 
            "📈 Statistics", 
            "🔥 Trending Topics", 
            "✨ Advanced Sentiment Analysis"
        ], index=0, key="page_radio")
    
    st.markdown('<hr style="border: 1px solid #334155;">', unsafe_allow_html=True)

    # === Pages ===
    if page == "👥 Manage Users":
        manage_users(users_col)

    elif page == "🤖 Questions Bank":
        Questions_bank()

    elif page == "📊 Overview":
        show_overview(df)

    elif page == "📚 Q&A Data":
        st.header("📚 Q&A Data")
        st.dataframe(df[['question', 'answer', 'timestamp', 'response_length']], use_container_width=True)

    elif page == "📈 Engagement Analysis":
        st.header("📈 Engagement Over Time")
        df["date"] = df["timestamp"].dt.date
        engagement = df.groupby("date").size().reset_index(name="Interactions")
        fig = px.line(engagement, x="date", y="Interactions", title="User Engagement", markers=True, color_discrete_sequence=["#38bdf8"])
        st.plotly_chart(fig, use_container_width=True)

    elif page == "💬 Sentiment Analysis":
        st.header("💬 Sentiment Analysis")
        sentiment_counts = df["sentiment_label"].value_counts()
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Sentiment Distribution", color_discrete_sequence=["#38bdf8", "#0ea5e9", "#0f172a"])
        st.plotly_chart(fig, use_container_width=True)

    elif page == "🔍 NER & Topics":
        st.header("🔍 Named Entity Recognition")
        nlp = spacy.load("en_core_web_sm")
        text = " ".join(df["answer"].dropna())
        doc = nlp(text)
        entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
        if entities:
            wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(entities))
            fig, ax = plt.subplots(figsize=(10,5))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.warning("⚠️ No entities found.")

    elif page == "📈 Statistics":
        st.header("📈 Data Statistics")
        st.dataframe(df.describe(), use_container_width=True)

    elif page == "🔥 Trending Topics":
        st.header("🔥 Trending Topics")
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer = TfidfVectorizer(stop_words='english', max_features=20)
        tfidf_matrix = vectorizer.fit_transform(df["question"].dropna())
        keywords = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
        top_keywords = keywords.mean().sort_values(ascending=False).reset_index()
        top_keywords.columns = ["Keyword", "Importance"]
        fig = px.bar(top_keywords, x="Importance", y="Keyword", orientation="h", title="Top Keywords", color_discrete_sequence=["#38bdf8"])
        st.plotly_chart(fig, use_container_width=True)

    elif page == "✨ Advanced Sentiment Analysis":
        st.header("✨ Sentiment Analysis Over Time")
        df["date"] = df["timestamp"].dt.date
        sentiment_trend = df.groupby(["date", "sentiment_label"]).size().unstack().fillna(0)
        fig = px.line(sentiment_trend, title="Sentiment Over Time")
        st.plotly_chart(fig, use_container_width=True)

# === Function for Manage Users (keeps your original logic) ===
def manage_users(users_col):
    # ➕ Add User
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

    # 🔎 Search and List Users
    st.subheader("🔎 Search Users")
    search_query = st.text_input("Search by Name or Email").lower()
    users = list(users_col.find({}, {"password": 0}))

    if search_query:
        users = [u for u in users if search_query in u.get('first_name', '').lower() or search_query in u.get('last_name', '').lower() or search_query in u.get('email', '').lower()]

    users_per_page = 6
    total_pages = (len(users) - 1) // users_per_page + 1
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = 1

    start_idx = (st.session_state.admin_page - 1) * users_per_page
    end_idx = start_idx + users_per_page

    for user in users[start_idx:end_idx]:
        initials = (user.get('first_name', '')[:1] + user.get('last_name', '')[:1]).upper()
        with st.container():
            st.markdown(f"""<div style="background:#1e293b;padding:20px;border-radius:14px;margin-bottom:20px;"><div style="display: flex; align-items: center; margin-bottom: 10px;"><div class="avatar">{initials}</div><div><div class="user-name">{user.get('first_name', '')} {user.get('last_name', '')}</div><div class="user-email">{user['email']}</div><div class="badge">{user.get('role', 'user').capitalize()}</div></div></div>""", unsafe_allow_html=True)
            with st.form(key=f"user_edit_form_{str(user['_id'])}"):
                col1, col2 = st.columns([2, 1])
                with col1:
                    new_role = st.selectbox("Change Role", options=["user", "admin"], index=0 if user.get("role") == "user" else 1, key=f"role_select_{str(user['_id'])}")
                with col2:
                    update_role = st.form_submit_button("💾 Update Role")
                    delete_user = st.form_submit_button("🗑️ Delete User")
                if update_role:
                    users_col.update_one({"_id": user["_id"]}, {"$set": {"role": new_role}})
                    st.success(f"✅ {user['email']}'s role updated.")
                    st.rerun()
                if delete_user:
                    users_col.delete_one({"_id": user["_id"]})
                    st.error(f"🗑️ {user['email']} deleted.")
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Previous"):
            if st.session_state.admin_page > 1:
                st.session_state.admin_page -= 1
                st.rerun()
    with col2:
        st.markdown(f"<p style='text-align:center;'>Page {st.session_state.admin_page} / {total_pages}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("➡️ Next"):
            if st.session_state.admin_page < total_pages:
                st.session_state.admin_page += 1
                st.rerun()

# === Simple Overview Page ===
def show_overview(df):
    st.header("📊 Overview")
    st.metric(label="💬 Total Interactions", value=len(df))
    st.metric(label="📝 Avg Response Length", value=f"{round(df['response_length'].mean(), 2)} words")
    st.metric(label="👥 Unique Questions", value=df["question"].nunique())

# --- END ---

