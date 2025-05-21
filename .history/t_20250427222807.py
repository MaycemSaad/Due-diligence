import streamlit as st
from streamlit_lottie import st_lottie
import requests
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# Streamlit Config
st.set_page_config(page_title="Chainvestor Hub", layout="wide", initial_sidebar_state="collapsed")

# ==== Custom Professional CSS ====
st.markdown("""
    <style>
    /* Global Styles */
    html, body, .stApp {
        background-color: #0d0d0d;
        color: #e0e0e0;
        font-family: 'Poppins', sans-serif;
    }

    /* Header */
    .header-container {
        text-align: center;
        padding: 30px 10px;
        margin-bottom: 50px;
    }

    .header-container img {
        width: 120px;
        margin-bottom: 20px;
    }

    .header-container h1 {
        font-size: 42px;
        font-weight: 700;
        color: #F4C430;
        margin-bottom: 5px;
    }

    .header-container p {
        font-size: 18px;
        color: #b0b0b0;
    }

    /* Cards */
    .card {
        background-color: #1a1a1a;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 30px 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    .card h3 {
        color: #F4C430;
        font-size: 22px;
        margin-bottom: 10px;
    }

    .card p {
        font-size: 16px;
        color: #d0d0d0;
    }

    /* CTA Button */
    .cta-btn {
        display: inline-block;
        padding: 12px 28px;
        margin-top: 20px;
        background-color: #F4C430;
        color: #0d0d0d;
        font-weight: bold;
        border-radius: 30px;
        text-decoration: none;
        transition: background-color 0.3s ease;
    }

    .cta-btn:hover {
        background-color: #d4aa00;
        color: black;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    </style>
""", unsafe_allow_html=True)

# ==== Session Initialization ====
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# ==== Page Routing ====
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
    # ==== Landing Page ====
    st.markdown("""
    <div class="header-container">
        <img src="data:image/png;base64,INSERT_YOUR_LOGO_BASE64_HERE" alt="Chainvestor Logo">
        <h1>Chainvestor Hub</h1>
        <p>Smarter, Safer Investments Powered by AI and Blockchain</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs(["🏠 Home", "ℹ️ About", "🛠️ Services", "✉️ Contact"])

    # ==== Home Tab ====
    with tabs[0]:
        # Optional Lottie Animation
        def load_lottie_url(url: str):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()

        lottie_animation = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_tno6cg2w.json")
        st_lottie(lottie_animation, height=250, speed=1, quality="high")

        # Main Card
        st.markdown("""
        <div class="card">
            <h3>Empower Your Portfolio</h3>
            <p>Gain faster insights, anticipate risks, and optimize your decisions with Chainvestor Hub's intelligent solutions.</p>
            <a href="#services" class="cta-btn">Explore Services</a>
        </div>
        """, unsafe_allow_html=True)

        # Features
        st.markdown("<br>", unsafe_allow_html=True)
        cols = st.columns(3)

        features = [
            ("AI Risk Detection", "Identify hidden threats in real-time."),
            ("Smart Compliance", "Automate compliance with changing regulations."),
            ("Investment Insights", "Deep data-driven investment analysis."),
        ]

        for col, (title, desc) in zip(cols, features):
            with col:
                st.markdown(f"""
                <div class="card">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

        # Call to Action
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h3>Ready to Transform Your Investments?</h3>
            <p>Discover how Chainvestor Hub can help you lead the future of finance with confidence and clarity.</p>
            <a href="#contact" class="cta-btn">Get Started</a>
        </div>
        """, unsafe_allow_html=True)
