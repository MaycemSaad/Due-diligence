import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# ==== Streamlit Config ====
st.set_page_config(page_title="Chainvestor Hub", layout="wide", initial_sidebar_state="collapsed")

# ==== Advanced CSS ====
st.markdown("""
<style>
html, body, .stApp {
    background: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Poppins', sans-serif;
    scroll-behavior: smooth;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, #0d0d0d, #1a1a1a);
    text-align: center;
    padding: 80px 20px 60px 20px;
}
.hero h1 {
    font-size: 64px;
    font-weight: 800;
    color: #ffcc00;
    margin-bottom: 20px;
}
.hero p {
    font-size: 22px;
    color: #ccc;
}

/* Sections */
.section {
    padding: 80px 20px;
    max-width: 1200px;
    margin: auto;
}
.section h2 {
    text-align: center;
    font-size: 36px;
    color: #ffcc00;
    margin-bottom: 50px;
}
.section p {
    text-align: center;
    color: #aaa;
    margin-bottom: 50px;
    font-size: 18px;
}

/* Cards */
.card {
    background: #1a1a1a;
    border-radius: 16px;
    padding: 30px;
    text-align: center;
    transition: 0.3s;
    border: 1px solid #222;
}
.card:hover {
    transform: translateY(-8px);
    box-shadow: 0 10px 20px rgba(255,204,0,0.2);
    border: 1px solid #ffcc00;
}
.card h3 {
    color: #ffcc00;
    font-size: 24px;
    margin-bottom: 15px;
}

/* Timeline */
.timeline {
    position: relative;
    max-width: 900px;
    margin: auto;
}
.timeline::after {
    content: '';
    position: absolute;
    width: 4px;
    background-color: #ffcc00;
    top: 0;
    bottom: 0;
    left: 50%;
    margin-left: -2px;
}
.container-tl {
    padding: 20px 40px;
    position: relative;
    background-color: inherit;
    width: 50%;
}
.container-tl.left {
    left: 0;
}
.container-tl.right {
    left: 50%;
}
.container-tl::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    right: -10px;
    background-color: #ffcc00;
    border: 3px solid #1a1a1a;
    top: 15px;
    border-radius: 50%;
    z-index: 1;
}
.right::after {
    left: -10px;
}
.text-box {
    padding: 20px;
    background: #1a1a1a;
    position: relative;
    border-radius: 6px;
}

/* CTA Button */
.cta-btn {
    margin-top: 30px;
    padding: 14px 36px;
    background: #ffcc00;
    color: #0d0d0d;
    border-radius: 50px;
    font-weight: 700;
    text-decoration: none;
    display: inline-block;
    transition: 0.3s;
}
.cta-btn:hover {
    background: #e6b800;
}

/* Footer */
.footer {
    background: #111;
    padding: 40px 20px;
    text-align: center;
    font-size: 15px;
    color: #777;
    margin-top: 80px;
}
.hero-image:hover {
    transform: scale(1.05);
    transition: all 0.4s ease-in-out;
}
.footer a {
    color: #ffcc00;
    margin: 0 10px;
    text-decoration: none;
    font-size: 20px;
}
footer {visibility: hidden;}
.css-cio0dv {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==== Helper ====
def load_lottie_url(url):
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

    # Hero Section
# ==== Landing Page Hero (with image) ====

    hero_col1, hero_col2 = st.columns(2)

    with hero_col1:
        st.markdown("""
        <div class="hero-text">
            <h1 style="font-size: 60px; font-weight: 800; color: #ffcc00;">Chainvestor Hub</h1>
            <p style="font-size: 22px; color: #ccc; margin-top: 20px;">
                Smarter, Safer Investments Powered by AI and Blockchain.
            </p>
            <div style="margin-top: 30px;">
                <a href="#services" class="cta-btn">Get Started</a>
                <a href="#about" class="cta-btn" style="background-color:#1a1a1a; color:#ffcc00; margin-left: 20px; border: 2px solid #ffcc00;">Learn More</a>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with hero_col2:
        st.image("", use_column_width=True)


    # Features Section
    st.markdown("""
    <div class="section" id="features">
        <h2>🚀 Features</h2>
        <p>Cutting-edge tools to transform your portfolio management.</p>
        """, unsafe_allow_html=True)

    cols = st.columns(3)
    features = [
        ("⚡ AI Risk Detection", "Real-time risk scanning."),
        ("🛡️ Compliance Engine", "Always regulation-ready."),
        ("📊 Predictive Analytics", "Forecast future movements.")
    ]
    for col, (title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # About Section
    st.markdown("""
    <div class="section" id="about">
        <h2>ℹ️ About Us</h2>
        <div class="timeline">
            <div class="container-tl left">
                <div class="text-box">
                    <h3>2019</h3>
                    <p>Chainvestor founded to revolutionize crypto investments.</p>
                </div>
            </div>
            <div class="container-tl right">
                <div class="text-box">
                    <h3>2021</h3>
                    <p>Launched our proprietary AI Risk Engine.</p>
                </div>
            </div>
            <div class="container-tl left">
                <div class="text-box">
                    <h3>2024</h3>
                    <p>Global expansion to 20+ countries and 3500+ investors.</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Services Section
    st.markdown("""
    <div class="section" id="services">
        <h2>🛠️ Our Services</h2>
        <p>Everything you need for smarter, safer investing.</p>
        """, unsafe_allow_html=True)

    cols2 = st.columns(2)
    services = [
        ("🔍 Due Diligence Automation", "Automated AI due diligence reports."),
        ("📈 Portfolio Stress Testing", "Simulate extreme market conditions."),
    ]
    for col, (title, desc) in zip(cols2, services):
        with col:
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Contact Section
    st.markdown("""
    <div class="section" id="contact">
        <h2>✉️ Contact Us</h2>
        <p>Ready to transform your investment strategy? Let's talk.</p>
        <form action="https://formsubmit.co/YOUR_EMAIL" method="POST">
            <input type="text" name="name" required placeholder="Your name" style="width:100%;padding:12px;margin:10px 0;">
            <input type="email" name="email" required placeholder="Your email" style="width:100%;padding:12px;margin:10px 0;">
            <textarea name="message" required placeholder="Your message" style="width:100%;padding:12px;height:120px;margin:10px 0;"></textarea>
            <button type="submit" class="cta-btn">Send Message</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

# ==== Footer ====
st.markdown("""
<div class="footer">
    <p>© 2025 Chainvestor Hub | <a href="#features">Features</a> | <a href="#about">About</a> | <a href="#services">Services</a> | <a href="#contact">Contact</a></p>
</div>
""", unsafe_allow_html=True)
