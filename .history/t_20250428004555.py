import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# ==== Streamlit Config ====
st.set_page_config(page_title="Chainvestor Hub", layout="wide", initial_sidebar_state="collapsed")

# ==== Advanced Global CSS ====
st.markdown("""
<style>
/* Global settings */
html, body, .stApp {
    background: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Poppins', sans-serif;
    scroll-behavior: smooth;
}

/* Navbar */
.navbar {
    background-color: #0d0d0d;
    padding: 20px 50px;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 8px rgba(255, 204, 0, 0.2);
}
.navbar-logo {
    font-size: 28px;
    font-weight: bold;
    color: #ffcc00;
    text-decoration: none;
}
.navbar-links {
    display: flex;
    gap: 30px;
}
.navbar-links a {
    font-size: 18px;
    color: #e0e0e0;
    text-decoration: none;
    transition: 0.3s;
}
.navbar-links a:hover {
    color: #ffcc00;
}

/* Hero Section */
.hero {
    padding: 100px 20px 60px 20px;
    background: linear-gradient(135deg, #0d0d0d, #1a1a1a);
}
.hero h1 {
    font-size: 64px;
    font-weight: 800;
    color: #ffcc00;
}
.hero p {
    font-size: 22px;
    color: #ccc;
    margin-top: 20px;
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
    margin-bottom: 30px;
}
.section p {
    text-align: center;
    font-size: 18px;
    color: #aaa;
    margin-bottom: 40px;
}

/* Cards */
.card {
    background: #1a1a1a;
    border-radius: 16px;
    padding: 30px;
    text-align: center;
    border: 1px solid #222;
    transition: 0.3s;
}
.card:hover {
    transform: translateY(-8px);
    box-shadow: 0 10px 20px rgba(255, 204, 0, 0.2);
    border-color: #ffcc00;
}
.card h3 {
    color: #ffcc00;
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
    width: 50%;
}
.container-tl.left { left: 0; }
.container-tl.right { left: 50%; }
.container-tl::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    background-color: #ffcc00;
    border: 3px solid #1a1a1a;
    border-radius: 50%;
    top: 15px;
    z-index: 1;
}
.right::after { left: -10px; }
.text-box {
    background: #1a1a1a;
    padding: 20px;
    border-radius: 6px;
}

/* CTA Buttons */
.cta-btn {
    background: #ffcc00;
    color: #0d0d0d;
    font-weight: 700;
    padding: 12px 30px;
    border-radius: 50px;
    text-decoration: none;
    margin-top: 30px;
    display: inline-block;
    transition: background 0.3s;
}
.cta-btn:hover {
    background: #e6b800;
}

/* Footer */
.footer {
    background: #111;
    padding: 40px 20px;
    text-align: center;
    margin-top: 80px;
    font-size: 15px;
    color: #777;
}
.footer a {
    color: #ffcc00;
    text-decoration: none;
    margin: 0 10px;
}
footer {visibility: hidden;}
.css-cio0dv {visibility: hidden;}

/* Adjust padding because of fixed navbar */
.stApp { padding-top: 100px; }
</style>
""", unsafe_allow_html=True)

# ==== Session State ====
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# ==== Navbar HTML ====
st.markdown("""
<div class="navbar">
    <div class="navbar-logo">Chainvestor</div>
    <div class="navbar-links">
        <a href="#home">Home</a>
        <a href="#features">Features</a>
        <a href="#about">About</a>
        <a href="#services">Services</a>
        <a href="#contact">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

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
    # ==== Hero Section ====
    st.markdown('<div id="home"></div>', unsafe_allow_html=True)
    hero_col1, hero_col2 = st.columns(2)
    with hero_col1:
        st.markdown("""
        <div class="hero">
            <h1>Chainvestor Hub</h1>
            <p>Smarter, Safer Investments Powered by AI and Blockchain.</p>
            <a href="#services" class="cta-btn">Get Started</a>
            <a href="#about" class="cta-btn" style="background:#1a1a1a; color:#ffcc00; margin-left:20px; border:2px solid #ffcc00;">Learn More</a>
        </div>
        """, unsafe_allow_html=True)
    with hero_col2:
        st.image("crypto.png", use_container_width=True)

    # ==== Features Section ====
    st.markdown('<div id="features"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section">
        <h2>🚀 Features</h2>
        <p>Cutting-edge tools to transform your portfolio management.</p>
    """, unsafe_allow_html=True)

    cols = st.columns(3)
    features = [("⚡ AI Risk Detection", "Real-time risk scanning."),
                ("🛡️ Compliance Engine", "Always regulation-ready."),
                ("📊 Predictive Analytics", "Forecast future movements.")]
    for col, (title, desc) in zip(cols, features):
        with col:
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ==== About Section ====
    st.markdown('<div id="about"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section">
        <h2>ℹ️ About Us</h2>
        <div class="timeline">
            <div class="container-tl left"><div class="text-box"><h3>2019</h3><p>Chainvestor founded to revolutionize crypto investments.</p></div></div>
            <div class="container-tl right"><div class="text-box"><h3>2021</h3><p>Launched our proprietary AI Risk Engine.</p></div></div>
            <div class="container-tl left"><div class="text-box"><h3>2024</h3><p>Expanded to 20+ countries and 3500+ investors.</p></div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==== Services Section ====
    st.markdown('<div id="services"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section">
        <h2>🛠️ Our Services</h2>
        <p>Everything you need for smarter, safer investing.</p>
    """, unsafe_allow_html=True)

    cols2 = st.columns(2)
    services = [("🔍 Due Diligence Automation", "Automated AI due diligence reports."),
                ("📈 Portfolio Stress Testing", "Simulate extreme market conditions.")]
    for col, (title, desc) in zip(cols2, services):
        with col:
            st.markdown(f"""
            <div class="card">
                <h3>{title}</h3>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ==== Contact Section ====
    st.markdown('<div id="contact"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section">
        <h2>✉️ Contact Us</h2>
        <p>Ready to transform your investment strategy? Let's talk.</p>
        <form action="https://formsubmit.co/YOUR_EMAIL" method="POST">
            <input type="text" name="name" required placeholder="Your Name" style="width:100%;padding:12px;margin:10px 0;">
            <input type="email" name="email" required placeholder="Your Email" style="width:100%;padding:12px;margin:10px 0;">
            <textarea name="message" required placeholder="Your Message" style="width:100%;padding:12px;height:120px;margin:10px 0;"></textarea>
            <button type="submit" class="cta-btn">Send Message</button>
        </form>
    </div>
    """, unsafe_allow_html=True)

    # ==== Footer ====
    st.markdown("""
    <div class="footer">
        © 2025 Chainvestor Hub | 
        <a href="#features">Features</a> | 
        <a href="#about">About</a> | 
        <a href="#services">Services</a> | 
        <a href="#contact">Contact</a>
    </div>
    """, unsafe_allow_html=True)
