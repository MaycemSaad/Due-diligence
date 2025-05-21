import streamlit as st
from streamlit_lottie import st_lottie
import requests
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# Streamlit configuration
st.set_page_config(page_title="💬 Due Diligence AI", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS inspired by the provided image
st.markdown("""
<style>
body, .stApp {
    background-color: #121212;
    color: #ffffff;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.header-container {
    padding: 40px;
    text-align: center;
    border-radius: 10px;
    background-color: transparent;
    margin-bottom: 50px;
}
.header-container h1 {
    color: #ffffff;
    font-size: 56px;
    font-weight: bold;
}
.header-container p {
    color: #b0b3b8;
    font-size: 18px;
}
.tabs {
    justify-content: center;
    margin-bottom: 50px;
}
.card {
    background-color: #181818;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.3);
    text-align: center;
}
.card h3 {
    color: #00b0ff;
    margin-bottom: 15px;
}
.card p {
    color: #b0b3b8;
}
.cta-btn {
    display: inline-block;
    padding: 12px 30px;
    background-color: #00b0ff;
    color: white;
    text-decoration: none;
    border-radius: 25px;
    font-weight: bold;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# Session Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# Page management based on session state
if st.session_state.page == "login":
    show_login_page()

elif st.session_state.page == "signup":
    show_signup_page()

elif st.session_state.user:
    if st.session_state.user["role"] == "admin":
        from admin_dashboard import show_admin_dashboard
        show_admin_dashboard()
    else:
        show_due_diligence_app()

else:
    # Header
    st.markdown("""
    <div class="header-container">
        <img src="logo.png" width="100"/>
        <h1>Empower Smarter Decisions with AI-Driven Due Diligence</h1>
        <p>Advanced analytics, real-time insights, and automated verification.</p>
        <a href="#services" class="cta-btn">Get Started</a>
    </div>
    """, unsafe_allow_html=True)

    # Tabs
    tabs = st.tabs(["🏠 Home", "ℹ️ About", "🛠️ Services", "✉️ Contact"])

    # Home Tab
    with tabs[0]:
        # Lottie Animation
        def load_lottie_url(url: str):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()

        lottie_animation = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_tno6cg2w.json")
        st_lottie(lottie_animation, height=300, speed=1, quality="high")

        # Features Cards
        cols = st.columns(3)
        features = [
            ("AI Automation", "Automated document analysis, verification, and reporting."),
            ("Real-Time Monitoring", "Instant insights into financial and social trends."),
            ("Security & Compliance", "Encrypted and fully compliant data handling.")
        ]

        for col, feature in zip(cols, features):
            col.markdown(f"""
            <div class="card">
                <h3>{feature[0]}</h3>
                <p>{feature[1]}</p>
            </div>
            """, unsafe_allow_html=True)

        # Call to Action
        st.markdown("""
        <div class="card">
            <h3>Join the Future of Due Diligence</h3>
            <p>Start automating your processes and enhancing your decision-making today.</p>
            <a href="#contact" class="cta-btn">Sign Up Now</a>
        </div>
        """, unsafe_allow_html=True)