import streamlit as st
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app
from socialMedia import show_social_media_analysis
from portfolio import show_crypto_market
from crypto_companies import show_crypto_companies
from compliance_check import show_smart_compliance_analyzer
from Scam_detector import show_scam_detector
from Document_Authenticity_Checker import show_document_authenticity_pro_ultimate

# ====== Streamlit Config ======
st.set_page_config(page_title="💬 Due Diligence AI", layout="wide")

# ====== Stylish CSS for the page ======
st.markdown("""
    <style>
        html, body {
            background: linear-gradient(to right, #f5f7fa, #c3cfe2);
        }
        .main-title {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            margin-top: 2rem;
            color: #2E3B4E;
        }
        .subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #555;
            margin-bottom: 2rem;
        }
        .stTabs [role="tablist"] {
            justify-content: center;
        }
    </style>
""", unsafe_allow_html=True)

# ====== Session Initialization ======
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# ====== Manage Pages depending on session ======
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
    # ====== Actual Tabs ======
    tabs = st.tabs(["🏠 Home", "ℹ️ About", "🛠️ Services", "✉️ Contact"
                    ])

    # === Tab 1: Home ===
    with tabs[0]:
        st.header("🏠 Home")
        st.markdown("""
            <div style="padding: 2rem; text-align:center;">
                <h1 class="main-title">Smart Insights.<br>For Your Trusted Decisions</h1>
                <p class="subtitle">Streamlined due diligence to empower investors, startups, and enterprises to make faster, smarter, and more informed decisions.</p>
            </div>
        """, unsafe_allow_html=True)

    # === Tab 2: About ===
    with tabs[1]:
        st.header("ℹ️ About Us")
        st.write("""
            We are a team of passionate professionals transforming the due diligence process.
            Our platform uses AI, technology and experience to deliver fast and reliable analysis.
        """)

    # === Tab 3: Services ===
    with tabs[2]:
        st.header("🛠️ Our Services")
        st.write("""
            - AI-powered Document Review
            - Risk Analysis & Background Checks
            - Smart Compliance Checks
            - Secure Data Rooms
            - Crypto Investment Monitoring
        """)

    # === Tab 4: Contact ===
    with tabs[3]:
        st.header("✉️ Contact Us")
        st.write("""
            📧 Email: info@duediligenceplatform.com  
            📞 Phone: +1 (800) 123-4567  
            📍 Address: 123 Business Avenue, New York, NY
        """)

    # === Tab 5: Document Authenticity Checker ===
    with tabs[4]:
        st.header("📄 Document Authenticity Check")
        show_document_authenticity_pro_ultimate()

    # === Tab 6: Scam Detector ===
    with tabs[5]:
        st.header("🚨 Scam Detector")
        show_scam_detector()

    # === Tab 7: Smart Compliance Analyzer ===
    with tabs[6]:
        st.header("⚖️ Smart Compliance Analyzer")
        show_smart_compliance_analyzer()

    # === Tab 8: Social Media Analysis ===
    with tabs[7]:
        st.header("📊 Social Media Analysis")
        show_social_media_analysis()

    # === Tab 9: Crypto Market ===
    with tabs[8]:
        st.header("💹 Crypto Market Tracker")
        show_crypto_market()

    # === Tab 10: Crypto Companies ===
    with tabs[9]:
        st.header("🏢 Crypto Companies Overview")
        show_crypto_companies()
