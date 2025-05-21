import streamlit as st
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app
from socialMedia import show_social_media_analysis
from portfolio import show_crypto_market
from crypto_companies import show_crypto_companies
from compliance_check import show_smart_compliance_analyzer
from Scam_detector import show_scam_detector
from Document_Authenticity_Checker import show_document_authenticity_pro_ultimate

# ==== Config ====
st.set_page_config(page_title="💬 Due Diligence AI", layout="wide")

# ==== CSS ====
st.markdown("""
<style>
    html, body {
        background: linear-gradient(to right, #e0eafc, #cfdef3);
        font-family: 'Arial', sans-serif;
    }
    .main-title {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        margin-top: 3rem;
        color: #2E3B4E;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #555;
        margin-bottom: 3rem;
        line-height: 1.6;
    }
    .center-buttons {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 2rem;
    }
    .stButton > button {
        font-size: 1.1rem;
        padding: 0.7rem 2rem;
        border-radius: 8px;
        background-color: #007BFF;
        color: white;
        border: none;
        transition: background-color 0.3s, transform 0.3s;
    }
    .stButton > button:hover {
        background-color: #0056b3;
        transform: scale(1.05);
    }
    h2 {
        color: #2E3B4E;
        border-bottom: 2px solid #007BFF;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    p {
        text-align: justify;
        color: #333;
    }
    @media (max-width: 600px) {
        .main-title {
            font-size: 2.5rem;
        }
        .subtitle {
            font-size: 1rem;
        }
        .stButton > button {
            padding: 0.5rem 1.5rem;
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ==== Session Init ====
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# ==== Page Control ====
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
    # ========================
    # ======== TABS ===========
    # ========================
    tabs = st.tabs(["🏠 Home", "ℹ️ About", "💼 Services", "📞 Contact"])

    # === Home Tab ===
# === Home Tab ===
    with tabs[0]:
        st.markdown("<h1 class='main-title'>Smart Insights.<br>For Your Trusted Decisions</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Streamlined due diligence to empower investors, startups, and enterprises to make faster, smarter, and more informed decisions.</p>", unsafe_allow_html=True)

        # Adding an image
        st.image("path/to/your/image.jpg", use_column_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Why We Do This")
            st.write("""
                In today's fast-paced business environment, reliable due diligence is more essential than ever. 
                Our platform simplifies the process of evaluating businesses, investments, or partnerships 
                by automating document review, background checks, and financial validation.
            """)
            # Adding an animated button
            if st.button("Learn More", key="why_we_do_this"):
                st.markdown("<p>Discover how our tools can help you!</p>", unsafe_allow_html=True)

        with col2:
            st.subheader("Helping You Grow In Every Stage")
            st.write("""
                Whether you're a venture capitalist, M&A advisor, or a startup founder, 
                we provide the tools to conduct thorough due diligence at every step — 
                from early-stage screening to final deal closing.
            """)
            # Adding an animated button
            if st.button("Explore Services", key="helping_you_grow"):
                st.markdown("<p>Check out our comprehensive services!</p>", unsafe_allow_html=True)

    # Additional CSS for animations
    st.markdown("""
    <style>
        .stButton > button {
            transition: transform 0.3s, background-color 0.3s;
        }
        .stButton > button:hover {
            transform: scale(1.1);
            background-color: #0056b3;
        }
    </style>
    """, unsafe_allow_html=True)
    # === About Tab ===
    with tabs[1]:
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>About Us</h2>", unsafe_allow_html=True)
        st.write("""
            We are a team of passionate professionals dedicated to transforming the due diligence process.
            Our platform combines cutting-edge technology, AI, and decades of experience to help investors,
            startups, and enterprises make more informed decisions, faster.
        """)
        st.write("""
            ### 🏆 Our Mission
            To simplify and accelerate due diligence, empowering smarter decision making.
        """)

    # === Services Tab ===
    with tabs[2]:
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>Our Services</h2>", unsafe_allow_html=True)
        st.write("""
        - AI-powered Document Review
        - Real-time Risk Analysis
        - Background Checks & Financial Validation
        - Customizable Workflows
        - Secure Data Rooms
        """)

    # === Contact Tab ===
    with tabs[3]:
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>Contact Us</h2>", unsafe_allow_html=True)
        st.write("""
            📧 Email: info@duediligenceplatform.com  
            📞 Phone: +1 (800) 123-4567  
            📍 Address: 123 Business Avenue, Suite 456, New York, NY 10001
        """)

        # ===== Login/Signup Buttons =====
        spacer1, col_connexion, spacer2, col_signup, spacer3 = st.columns([1, 2, 0.5, 2, 1])
        with col_connexion:
            if st.button("🔐 Login"):
                st.session_state.page = "login"
                st.rerun()
        with col_signup:
            if st.button("📝 Signup"):
                st.session_state.page = "signup"
                st.rerun()

