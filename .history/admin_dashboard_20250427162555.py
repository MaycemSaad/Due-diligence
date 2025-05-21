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
    .sidebar-title {
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        color: #38bdf8;
        margin-bottom: 2rem;
    }
    [role="radiogroup"] > label {
        background-color: #1e293b;
        color: #cbd5e1;
        margin-bottom: 12px;
        border-radius: 10px;
        padding: 12px;
        font-size: 18px;
        transition: all 0.3s ease;
        width: 100%; /* ✅ Force largeur uniforme */
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 50px; /* ✅ Fixe aussi la hauteur pour plus d'élégance */
    }
    [role="radiogroup"] > label:hover {
        background-color: #0ea5e9;
        color: white;
        transform: scale(1.05);
    }
    [role="radiogroup"] > label[data-selected="true"] {
        background-color: #38bdf8;
        color: white;
        font-weight: bold;
    }
    h1, h2, h3 {
        color: #38bdf8;
        font-weight: bold;
    }
    .user-card {
        background: #1e293b;
        padding: 1.2rem;
        border-radius: 14px;
        margin-bottom: 1rem;
        box-shadow: 0px 8px 24px rgba(0,0,0,0.15);
        transition: all 0.3s ease;
    }
    .user-card:hover {
        background: #334155;
        transform: translateY(-3px);
    }
    .avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: #0ea5e9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 20px;
        color: white;
        margin-right: 12px;
    }
    button {
        border-radius: 12px !important;
        font-weight: bold !important;
        background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
        color: white !important;
        border: none !important;
        transition: all 0.3s ease;
    }
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0px 10px 20px rgba(56,189,248,0.4);
    }
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #38bdf8;
        padding: 12px 24px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.2);
        z-index: 9999;
    }
    hr {
        border: 1px solid #334155;
    }
    input, select, textarea {
        border-radius: 8px;
        padding: 10px;
        background-color: #1e293b;
        color: white;
        border: none;
        outline: none;
    }
    input:focus, select:focus, textarea:focus {
        background-color: #273549;
        border: 1px solid #38bdf8;
    }
    .stForm {
        background-color: #1e293b;
        border-radius: 10px;
        padding: 20px;
    }
                .stButton>button {
    background: linear-gradient(135deg, #38bdf8, #0ea5e9);
    border: none;
    color: white;
    font-weight: bold;
    height: 45px;
    border-radius: 10px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(135deg, #0ea5e9, #38bdf8);
    transform: scale(1.02);
}
    </style>
    """, unsafe_allow_html=True)

    # === Sidebar ===
    with st.sidebar:
        st.image("logo.png", width=150)
        st.markdown('<div class="sidebar-title">Due Diligence AI</div>', unsafe_allow_html=True)

        page = st.radio("Navigation", [
            "📊 Overview", 
            "👥 Manage Users", 
            "🤖 Questions Bank", 
            "📚 Q&A Data", 
            "📈 Engagement Analysis", 
            "💬 Sentiment Analysis", 
            "📈 Statistics", 
            "🔥 Trending Topics", 
            "✨ Advanced Sentiment Analysis"
        ], index=0)
        # === Logout Button ===
    st.markdown("---")  # Petite séparation visuelle
    if st.button("🚪 Logout"):
        st.session_state.user = None  # On vide la session utilisateur
        st.success("✅ Logged out successfully!")
        time.sleep(1)
        st.rerun()

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


# === Function for Manage Users (Restored old version) ===
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

    users_per_page = 6
    total_pages = (len(users) - 1) // users_per_page + 1

    if "admin_page" not in st.session_state:
        st.session_state.admin_page = 1

    start_idx = (st.session_state.admin_page - 1) * users_per_page
    end_idx = start_idx + users_per_page

    for user in users[start_idx:end_idx]:
        initials = (user.get('first_name', '')[:1] + user.get('last_name', '')[:1]).upper()
        with st.container():
            st.markdown(f"""
            <div style='background:#1e293b;padding:20px;border-radius:14px;margin-bottom:20px;display:flex;align-items:center;justify-content:space-between;'>
                <div style='display:flex;align-items:center;'>
                    <div class='avatar' style='width:50px;height:50px;border-radius:50%;background-color:#0ea5e9;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:20px;color:white;margin-right:12px;'>{initials}</div>
                    <div>
                        <div style='font-size:18px;font-weight:bold;'>{user.get('first_name', '')} {user.get('last_name', '')}</div>
                        <div style='font-size:14px;color:#cbd5e1;'>{user['email']}</div>
                        <div style='font-size:14px;margin-top:4px;color:#38bdf8;'>{user.get('role', 'user').capitalize()}</div>
                    </div>
                </div>
                <div style='display:flex;flex-direction:column;align-items:flex-end;'>
            """, unsafe_allow_html=True)

            with st.form(key=f"user_edit_form_{str(user['_id'])}", clear_on_submit=True):
                new_role = st.selectbox("Change Role", options=["user", "admin"], index=0 if user.get("role") == "user" else 1, key=f"role_select_{str(user['_id'])}")
                update_col, delete_col = st.columns(2)
                with update_col:
                    update_role = st.form_submit_button("💾 Update Role")
                with delete_col:
                    delete_user = st.form_submit_button("🗑️ Delete User")

                if update_role:
                    users_col.update_one({"_id": user["_id"]}, {"$set": {"role": new_role}})
                    st.success(f"✅ {user['email']}'s role updated.")
                    st.rerun()

                if delete_user:
                    users_col.delete_one({"_id": user["_id"]})
                    st.error(f"🗑️ {user['email']} deleted.")
                    st.rerun()

            st.markdown("</div></div>", unsafe_allow_html=True)

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