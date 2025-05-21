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
        st.markdown("""
            <div style="padding: 3rem 2rem; background: linear-gradient(to right, #0f2027, #203a43, #2c5364); border-radius: 15px; text-align: center;">
                <h1 style="color: white; font-size: 3.5rem; font-weight: bold;">Empower Your Decisions with Smart Due Diligence</h1>
                <p style="color: #ccc; font-size: 1.3rem; max-width: 800px; margin: 2rem auto;">
                    Unlock the power of AI-driven insights, automate risk assessments, and make faster, smarter investment decisions. 
                    Welcome to the future of due diligence.
                </p>
                <div style="margin-top: 2rem;">
                    <a href="#services" style="background-color: #4CAF50; color: white; padding: 15px 30px; border-radius: 30px; text-decoration: none; font-size: 1.2rem;">Explore Services</a>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 🚀 Why Choose Us?")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div style="background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #2E3B4E;">AI Automation</h3>
                    <p style="color: #555;">Leverage cutting-edge AI to automate document analysis, background verification, and risk flagging.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div style="background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #2E3B4E;">Real-Time Insights</h3>
                    <p style="color: #555;">Get dynamic risk scoring and sentiment analysis powered by live financial and social media data.</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div style="background-color: white; border-radius: 10px; padding: 1.5rem; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
                    <h3 style="color: #2E3B4E;">Secure & Compliant</h3>
                    <p style="color: #555;">Work with enterprise-grade security, GDPR compliance, and encrypted data rooms.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📈 Our Impact")
        components.html("""
            <div style="display: flex; justify-content: center; gap: 50px; margin: 4rem 0;">
                <div style="text-align: center;">
                    <h1 style="color: #4CAF50;">+1,500</h1>
                    <p>Entities Analyzed</p>
                </div>
                <div style="text-align: center;">
                    <h1 style="color: #4CAF50;">+500</h1>
                    <p>Deals Verified</p>
                </div>
                <div style="text-align: center;">
                    <h1 style="color: #4CAF50;">$1.2B+</h1>
                    <p>Assets Screened</p>
                </div>
            </div>
        """, height=250)

        st.markdown("### 🌟 What We Offer")
        st.markdown("""
            - 📄 **Automated Document Review**  
            - 🛡️ **Background and Compliance Checks**  
            - 🔎 **Crypto Market Risk Analysis**  
            - 🤖 **Social Media Threat Detection**  
            - 🧠 **Real-Time Fraud Detection and Smart Alerts**  
            - 🔒 **Encrypted Data Rooms and Secure Sharing**  
        """)

        st.markdown("---")

        st.markdown("""
            <div style="padding: 2rem; background: #4CAF50; color: white; border-radius: 15px; text-align: center; margin-top: 2rem;">
                <h2 style="font-size: 2rem;">Start Smarter Due Diligence Today!</h2>
                <p style="font-size: 1.2rem;">Join hundreds of businesses who trust us to make informed decisions. </p>
                <a href="#contact" style="background-color: white; color: #4CAF50; padding: 15px 30px; border-radius: 30px; text-decoration: none; font-size: 1.1rem; margin-top: 1rem;">Get in Touch</a>
            </div>
        """, unsafe_allow_html=True)



