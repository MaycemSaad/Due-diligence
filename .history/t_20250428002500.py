import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# ==== Streamlit Config ====
st.set_page_config(page_title="Chainvestor Hub", layout="wide", initial_sidebar_state="collapsed")

# ==== Modern Professional CSS ====
st.markdown("""
<style>
/* General */
html, body, .stApp {
    background: linear-gradient(145deg, #0d0d0d, #1a1a1a);
    color: #e0e0e0;
    font-family: 'Poppins', sans-serif;
    scroll-behavior: smooth;
}

/* Navigation Tabs */
.stTabs [data-baseweb="tab-list"] {
    display: flex;
    justify-content: center;
    gap: 40px;
    font-size: 20px;
    padding: 20px 0;
}
.stTabs [data-baseweb="tab"] {
    flex: none !important;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: #ffcc00;
    border-bottom: 3px solid #ffcc00;
}

/* Header */
.header-container {
    text-align: center;
    padding: 50px 15px;
    animation: fadeIn 2s ease;
}
@keyframes fadeIn {
    0% {opacity:0; transform:translateY(-30px);}
    100% {opacity:1; transform:translateY(0);}
}
.header-container img {
    width: 130px;
}
.header-container h1 {
    font-size: 50px;
    font-weight: 800;
    color: #ffcc00;
    margin-top: 15px;
}
.header-container p {
    font-size: 20px;
    color: #c0c0c0;
}

/* Card Styling */
.card, .card-hover {
    background: #1f1f1f;
    border: 1px solid #333;
    border-radius: 16px;
    padding: 30px 20px;
    transition: all 0.3s ease;
    margin-bottom: 30px;
}
.card-hover:hover {
    transform: translateY(-10px);
    border-color: #ffcc00;
    box-shadow: 0 8px 20px rgba(255, 204, 0, 0.25);
}

/* CTA Buttons */
.cta-btn {
    background: #ffcc00;
    color: #0d0d0d;
    font-weight: 700;
    padding: 12px 30px;
    border-radius: 50px;
    text-decoration: none;
    display: inline-block;
    margin-top: 20px;
    transition: background 0.3s;
}
.cta-btn:hover {
    background: #e6b800;
}

/* Floating Contact Button */
.floating-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background: #ffcc00;
    color: #0d0d0d;
    font-size: 26px;
    padding: 16px;
    border-radius: 50%;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0% {transform: scale(1);}
    50% {transform: scale(1.1);}
    100% {transform: scale(1);}
}

/* Footer */
.footer {
    background: #111;
    padding: 50px 20px 20px 20px;
    margin-top: 50px;
    font-family: 'Poppins', sans-serif;
}
.footer-content {
    max-width: 1200px;
    margin: auto;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
}
.footer-section {
    flex: 1;
    min-width: 220px;
    margin: 20px 0;
}
.footer-section h4 {
    color: #ffcc00;
    font-size: 22px;
    margin-bottom: 10px;
}
.footer-section p, .footer-section a {
    color: #b0b0b0;
    font-size: 16px;
    text-decoration: none;
}
.footer-section a:hover {
    color: #ffcc00;
}
.footer-bottom {
    text-align: center;
    margin-top: 30px;
    font-size: 14px;
    color: #777;
}
.footer-socials a {
    font-size: 24px;
    margin-right: 15px;
    color: #b0b0b0;
}
.footer-socials a:hover {
    color: #ffcc00;
}

/* Hide Default Streamlit Footer */
footer {visibility: hidden;}
.css-cio0dv {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==== Helper Functions ====
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ==== Session State ====
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# ==== Routing ====
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

    with tabs[0]:
        lottie_home = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_2glqweqs.json")
        if lottie_home:
            st_lottie(lottie_home, height=300)
        
        st.markdown("""
        <div class="card">
            <h2>Empower Your Portfolio</h2>
            <p>AI-based tools to optimize investments and minimize risk.</p>
            <a href="#Services" class="cta-btn">Explore Now</a>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        features = [
            ("⚡ AI Risk Detection", "Real-time risk insights."),
            ("🛡️ Smart Compliance", "Auto regulatory alignment."),
            ("📊 Market Forecast", "Data-driven investment decisions."),
        ]
        for col, (title, desc) in zip(cols, features):
            with col:
                st.markdown(f"""
                <div class="card-hover">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
        <a href="#Contact" class="floating-btn">✉️</a>
        """, unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("""
        <div class="card">
            <h2>🚀 About Chainvestor</h2>
            <p>We bridge AI and blockchain to shape a smarter financial future.</p>
        </div>
        """, unsafe_allow_html=True)

    with tabs[2]:
        st.markdown("""
        <div class="card">
            <h2>🛠️ Our Services</h2>
            <p>From risk detection to portfolio forecasting — a full suite for investors.</p>
        </div>
        """, unsafe_allow_html=True)

    with tabs[3]:
        st.markdown("""
        <div class="card">
            <h2>✉️ Contact Us</h2>
            <p>Let's build a smarter investment journey together.</p>
        </div>
        """, unsafe_allow_html=True)

        contact_form = """
        <form action="https://formsubmit.co/YOUR_EMAIL" method="POST">
            <input type="text" name="name" required placeholder="Name" style="width:100%; padding:10px; margin:10px 0;">
            <input type="email" name="email" required placeholder="Email" style="width:100%; padding:10px; margin:10px 0;">
            <textarea name="message" required placeholder="Message" style="width:100%; padding:10px; height:120px;"></textarea>
            <button type="submit" style="background:#ffcc00; color:#0d0d0d; border:none; border-radius:30px; padding:10px 30px; margin-top:15px;">Send</button>
        </form>
        """
        st.markdown(contact_form, unsafe_allow_html=True)

# ==== Footer ====
st.markdown("""
<div class="footer">
  <div class="footer-content">
    <div class="footer-section">
      <h4>About</h4>
      <p>Leading the era of AI and blockchain investments with confidence and clarity.</p>
    </div>
    <div class="footer-section">
      <h4>Links</h4>
      <a href="#Home">🏠 Home</a><br>
      <a href="#About">ℹ️ About</a><br>
      <a href="#Services">🛠️ Services</a><br>
      <a href="#Contact">✉️ Contact</a>
    </div>
    <div class="footer-section">
      <h4>Contact</h4>
      <p>Email: contact@chainvestorhub.com</p>
      <p>Phone: +1 800 123 4567</p>
      <div class="footer-socials">
        <a href="https://twitter.com/" target="_blank">🐦</a>
        <a href="https://linkedin.com/" target="_blank">💼</a>
        <a href="https://github.com/" target="_blank">🐙</a>
      </div>
    </div>
  </div>
  <div class="footer-bottom">
    © 2025 Chainvestor Hub | All rights reserved.
  </div>
</div>
""", unsafe_allow_html=True)
