import streamlit as st
from streamlit_lottie import st_lottie
import requests
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# Streamlit configuration
st.set_page_config(page_title="💬 Due Diligence AI", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(135deg, #2c3e50, #4ca1af);
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header-container {
    padding: 20px;
    text-align: center;
    border-radius: 10px;
    background-color: rgba(0, 0, 0, 0.4);
    margin-bottom: 30px;
}

.header-container h1 {
    color: #f5f7fa;
    font-size: 48px;
}

.tabs {
    justify-content: center;
    margin-bottom: 50px;
}

.card {
    background-color: rgba(255, 255, 255, 0.1);
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    text-align: center;
}

.card h3 {
    color: #1dd1a1;
    margin-bottom: 15px;
}

.card p {
    color: #c8d6e5;
}

.cta-btn {
    display: inline-block;
    padding: 12px 25px;
    background-color: #1dd1a1;
    color: white;
    text-decoration: none;
    border-radius: 25px;
    font-weight: bold;
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
        <img src="" width="100"/>
        <h1>Due Diligence AI</h1>
        <p>Your smart partner for informed decision-making.</p>
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

        # Hero Section
        st.markdown("""
        <div class="card">
            <h3>Empower Smarter Decisions with AI-Driven Due Diligence</h3>
            <p>Automate insights, detect risks instantly, and optimize decisions for businesses and investors.</p>
            <a href="#services" class="cta-btn">Explore Features</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Why Choose Us
        cols = st.columns(3)
        features = [
            ("AI Automation", "Automate verification and document analysis."),
            ("Real-Time Insights", "Instant market and risk insights."),
            ("Security & Compliance", "End-to-end encrypted and compliant processes.")
        ]

        for col, feature in zip(cols, features):
            col.markdown(f"""
            <div class="card">
                <h3>{feature[0]}</h3>
                <p>{feature[1]}</p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Call to Action
        st.markdown("""
        <div class="card">
            <h3>Join Our Community</h3>
            <p>Make your decisions smarter, safer, and quicker.</p>
            <a href="#contact" class="cta-btn">Get Started</a>
        </div>
        """, unsafe_allow_html=True)