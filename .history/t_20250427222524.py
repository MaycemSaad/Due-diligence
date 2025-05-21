import streamlit as st
from streamlit_lottie import st_lottie
import requests
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# Streamlit configuration
st.set_page_config(page_title="💬 Due Diligence AI", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS (luxury style)
st.markdown("""
<style>
body, .stApp {
    background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
    color: #f5f5f5;
    font-family: 'Poppins', sans-serif;
}

.header-container {
    padding: 20px;
    text-align: center;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 215, 0, 0.05));
    margin-bottom: 30px;
    box-shadow: 0 4px 15px rgba(255, 215, 0, 0.2);
}

.header-container h1 {
    color: #FFD700;
    font-size: 48px;
    font-weight: bold;
}

.tabs {
    justify-content: center;
    margin-bottom: 50px;
}

.card {
    background: rgba(255, 255, 255, 0.05);
    padding: 25px;
    border-radius: 15px;
    border: 1px solid #FFD700;
    box-shadow: 0 6px 12px rgba(255, 215, 0, 0.2);
    text-align: center;
}

.card h3 {
    color: #FFD700;
    margin-bottom: 15px;
}

.card p {
    color: #cccccc;
    font-size: 16px;
}

.cta-btn {
    display: inline-block;
    padding: 12px 30px;
    background: #FFD700;
    color: black;
    text-decoration: none;
    border-radius: 30px;
    font-weight: bold;
    font-size: 16px;
    margin-top: 15px;
}

.cta-btn:hover {
    background: #e6c200;
    color: black;
}

</style>
""", unsafe_allow_html=True)

# Session Initialization
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# Page management
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
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/45/Golden_Circle.png" width="100"/>
        <h1>Chainvestor Hub</h1>
        <p>Your Smart Partner for Financial Intelligence</p>
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
            <h3>Empower Smarter Investments with AI</h3>
            <p>Automate insights, detect financial risks, and make bold, informed decisions with Chainvestor Hub.</p>
            <a href="#services" class="cta-btn">Explore Features</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Why Choose Us
        cols = st.columns(3)
        features = [
            ("AI Automation", "Automate verification and document analysis."),
            ("Real-Time Insights", "Get instant market and compliance insights."),
            ("Security & Compliance", "Secure, encrypted, and regulation-ready.")
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
            <h3>Join the Elite Investors Network</h3>
            <p>Smarter decisions, bigger successes. Chainvestor Hub empowers you to lead the future of finance.</p>
            <a href="#contact" class="cta-btn">Join Now</a>
        </div>
        """, unsafe_allow_html=True)
