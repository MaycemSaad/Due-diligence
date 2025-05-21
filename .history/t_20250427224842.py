import streamlit as st
from streamlit_lottie import st_lottie
import requests
import time
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app

# ==== Streamlit Config ====
st.set_page_config(page_title="Chainvestor Hub", layout="wide", initial_sidebar_state="collapsed")

# ==== Custom CSS Animated Professional ====
st.markdown("""
<style>
html, body, .stApp {
    background-color: #0d0d0d;
    color: #e0e0e0;
    font-family: 'Poppins', sans-serif;
    scroll-behavior: smooth;
}
/* Tabs Centered & Bigger */
.stTabs [data-baseweb="tab-list"] {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 50px; /* Plus grand espace entre les tabs */
    font-size: 22px; /* Texte plus grand */
    padding: 15px 0;
}

.stTabs [data-baseweb="tab"] {
    flex: none !important;
    font-weight: 600;
}

.stTabs [data-baseweb="tab"] > div {
    font-size: 22px; /* Texte dans chaque tab */
}

/* Active tab underline color */
.stTabs [aria-selected="true"] {
    color: #F4C430; /* Couleur du tab actif */
    border-bottom: 3px solid #F4C430;
}          

/* Header */
.header-container {
    text-align: center;
    padding: 40px 10px;
    margin-bottom: 50px;
    animation: fadeIn 2s ease-in-out;
}

@keyframes fadeIn {
    0% { opacity: 0; transform: translateY(-20px);}
    100% { opacity: 1; transform: translateY(0);}
}

.header-container img {
    width: 120px;
    margin-bottom: 20px;
}

.header-container h1 {
    font-size: 45px;
    font-weight: 700;
    color: #F4C430;
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
    margin-bottom: 30px;
    transition: all 0.3s ease;
}

.card:hover {
    border-color: #F4C430;
    transform: translateY(-5px);
}

/* CTA Button */
.cta-btn {
    display: inline-block;
    padding: 12px 28px;
    background-color: #F4C430;
    color: #0d0d0d;
    font-weight: bold;
    border-radius: 30px;
    text-decoration: none;
    transition: all 0.3s ease;
    margin-top: 20px;
}

.cta-btn:hover {
    background-color: #d4aa00;
}
            /* Hover Light Effect for Cards */
.card-hover {
    background-color: #1a1a1a;
    border: 1px solid #333;
    border-radius: 12px;
    padding: 25px;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(255,215,0,0.1);
}

.card-hover:hover {
    transform: translateY(-8px);
    box-shadow: 0 8px 20px rgba(255,215,0,0.25);
    border: 1px solid #F4C430;
}

/* Floating Button */
.floating-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: #F4C430;
    color: #0d0d0d;
    padding: 15px;
    border-radius: 50%;
    font-size: 24px;
    text-align: center;
    text-decoration: none;
    z-index: 100;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { transform: scale(1);}
    50% { transform: scale(1.1);}
    100% { transform: scale(1);}
}

</style>
""", unsafe_allow_html=True)

# ==== Load Lottie ====
def load_lottie_url(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

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
        # Hero Section with Lottie
        # Load a working Lottie animation (example: finance growth animation)
        lottie_hero = load_lottie_url("https://assets9.lottiefiles.com/packages/lf20_2glqweqs.json")

        if lottie_hero:
            st_lottie(lottie_hero, height=300, speed=1, quality="high")
        else:
            st.error("Failed to load animation.")


        # Main Hero Card
        st.markdown("""
        <div class="card">
            <h3>Empower Your Portfolio</h3>
            <p>Gain faster insights, anticipate risks, and optimize your decisions with Chainvestor Hub's intelligent solutions.</p>
            <a href="#services" class="cta-btn">Explore Features</a>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Features
        cols = st.columns(3)
        features = [
            ("⚡ AI Risk Detection", "Identify hidden threats in real-time."),
            ("🛡️ Smart Compliance", "Automate compliance with changing regulations."),
            ("📊 Investment Insights", "Deep data-driven investment analysis."),
        ]

        for col, (title, desc) in zip(cols, features):
            with col:
                st.markdown(f"""
                <div class="card">
                    <h3>{title}</h3>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

        # Statistics (Animated Counter)
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(label="Projects Completed", value="1,200+")
        with col2:
            st.metric(label="Active Investors", value="3,500+")
        with col3:
            st.metric(label="Compliance Success", value="98.7%")

        # Final Call to Action
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="card">
            <h3>Ready to Transform Your Investments?</h3>
            <p>Discover how Chainvestor Hub can help you lead the future of finance with confidence and clarity.</p>
            <a href="#contact" class="cta-btn">Get Started</a>
        </div>
        """, unsafe_allow_html=True)

        # Floating Contact Button
        st.markdown("""
        <a href="#contact" class="floating-btn">✉️</a>
        """, unsafe_allow_html=True)
           
    # ==== About Tab (Version Pro) ====
    with tabs[1]:
        st.markdown("""
        <div class="card">
            <h2 style="color: #F4C430;">🚀 About Chainvestor Hub</h2>
            <p style="font-size: 18px;">We are revolutionizing the investment world by blending <span style="color:#F4C430;">AI</span> and <span style="color:#F4C430;">Blockchain</span> technologies to drive smarter, safer financial decisions worldwide.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # 2 Columns: Left (Timeline) + Right (Animation)
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("""
            <h3 style="color: #F4C430;">📈 Our Growth Story</h3>
            <ul style="list-style-type:none; font-size:17px; padding-left:0;">
                <li style="margin-bottom:20px;">
                    <span style="color:#F4C430;">➔ 2019: Foundation</span><br>Chainvestor Hub was born to simplify crypto investments.
                </li>
                <li style="margin-bottom:20px;">
                    <span style="color:#F4C430;">➔ 2021: AI Engine Launch</span><br>We integrated real-time risk analysis powered by AI.
                </li>
                <li style="margin-bottom:20px;">
                    <span style="color:#F4C430;">➔ 2024: Global Expansion</span><br>Serving 3500+ investors across 20+ countries.
                </li>
            </ul>
            """, unsafe_allow_html=True)

        with col_right:
            lottie_about_new = load_lottie_url("https://assets4.lottiefiles.com/packages/lf20_0yfsb3a1.json")  # 👈 New nice animation
            if lottie_about_new:
                st_lottie(lottie_about_new, height=350, speed=1, quality="high")
            else:
                st.error("Failed to load About animation.")


    # ==== Services Tab (Version Luxe) ====
    with tabs[2]:
        st.markdown("""
        <div class="card">
            <h2 style="color: #F4C430;">🛠️ Our Services</h2>
            <p style="font-size: 18px;">Empowering investors with cutting-edge solutions tailored to today's fast-paced markets.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Section Standard Services
        st.markdown("""
        <h3 style="color: #F4C430;">🔹 Standard Services</h3>
        <hr style="border-top: 2px solid #F4C430;">
        """, unsafe_allow_html=True)

        cols1 = st.columns(3)

        standard_services = [
            ("🔍 Due Diligence Automation", "Accelerate your financial analysis with AI-driven insights."),
            ("📈 Predictive Analytics", "Forecast market movements with machine learning models."),
            ("🛡️ Smart Compliance", "Ensure end-to-end compliance with evolving global regulations."),
        ]

        for col, (title, desc) in zip(cols1, standard_services):
            with col:
                st.markdown(f"""
                <div style="background-color:#1a1a1a; border:1px solid #333; border-radius:12px; padding:25px; text-align:center; transition:0.3s; box-shadow: 0 4px 12px rgba(255,215,0,0.1);">
                    <h4 style="color: #F4C430;">{title}</h4>
                    <p style="color: #d0d0d0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Section Premium Services
        st.markdown("""
        <h3 style="color: #F4C430;">💎 Premium Services</h3>
        <hr style="border-top: 2px solid #F4C430;">
        """, unsafe_allow_html=True)

        cols2 = st.columns(2)

        premium_services = [
            ("📊 Portfolio Stress Testing", "Simulate and prepare for market shocks before they happen."),
            ("🧠 Deep Behavioral Analytics", "Decode investor sentiment to stay ahead of trends."),
        ]

for col, (title, desc) in zip(cols1, standard_services):
    with col:
        st.markdown(f"""
        <div class="card-hover">
            <h4 style="color: #F4C430;">{title}</h4>
            <p style="color: #d0d0d0;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)


        st.markdown("<br>", unsafe_allow_html=True)

        lottie_services = load_lottie_url("https://lottie.host/8ed679eb-6c8f-41b1-88db-3c4c67bc9b17/8OEKV0ePQT.json")

        if lottie_services:
            st_lottie(lottie_services, height=350, speed=1, quality="high")
        else:
            st.error("Failed to load Services animation.")



    # ==== Contact Tab ====
    with tabs[3]:
        st.markdown("""
        <div class="card">
            <h3>Contact Us</h3>
            <p>We're here to help you transform your investment journey. Reach out to us!</p>
        </div>
        """, unsafe_allow_html=True)

        contact_form = """
        <form action="https://formsubmit.co/your-email@example.com" method="POST">
            <input type="text" name="name" placeholder="Your name" required style="width: 100%; padding: 10px; margin-bottom: 10px;">
            <input type="email" name="email" placeholder="Your email" required style="width: 100%; padding: 10px; margin-bottom: 10px;">
            <textarea name="message" placeholder="Your message" required style="width: 100%; padding: 10px; height: 150px;"></textarea>
            <button type="submit" style="background-color:#F4C430; color:#0d0d0d; padding: 10px 20px; border: none; border-radius: 30px; font-weight: bold; margin-top:10px;">Send</button>
        </form>
        """

        st.markdown(contact_form, unsafe_allow_html=True)

        lottie_contact = load_lottie_url("https://assets3.lottiefiles.com/packages/lf20_dyci6j8u.json")
        if lottie_contact:
            st_lottie(lottie_contact, height=250, speed=1, quality="high")
        else:
            st.error("Failed to load Contact animation.")

