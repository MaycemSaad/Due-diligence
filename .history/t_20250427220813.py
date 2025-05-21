import streamlit as st
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app
from socialMedia import show_social_media_analysis
from portfolio import show_crypto_market
from crypto_companies import show_crypto_companies
from compliance_check import show_smart_compliance_analyzer
from Scam_detector import show_scam_detector
from Document_Authenticity_Checker import show_document_authenticity_pro_ultimate
import streamlit.components.v1 as components 
from streamlit_lottie import st_lottie
import requests


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



        # ==== Display Lottie animated illustration ====
        def load_lottie_url(url: str):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()

        lottie_animation = load_lottie_url("https://assets7.lottiefiles.com/packages/lf20_tno6cg2w.json")  # You can change to another animation link

        st_lottie(lottie_animation, speed=1, reverse=False, loop=True, quality="high", height=300)

        st.markdown("""<br><br>""", unsafe_allow_html=True)

        # ==== Hero section ====
        st.markdown("""
            <div style="background: linear-gradient(to right, #0f0c29, #302b63, #24243e); padding: 6rem 2rem; border-radius: 20px; text-align: center;">
                <h1 style="color: white; font-size: 3.8rem; font-weight: 900; animation: fadeIn 2s ease-in;">Empower Smarter Decisions with AI-Driven Due Diligence</h1>
                <p style="color: #c0c0c0; font-size: 1.5rem; margin-top: 2rem; animation: fadeIn 3s ease-in;">Instant risk insights, real-time fraud detection, automated analysis for investors, enterprises, and innovators.</p>
                <a href="#services" style="margin-top: 2rem; display: inline-block; background-color: #10b981; color: white; padding: 14px 35px; border-radius: 30px; font-size: 1.2rem; text-decoration: none;">Discover Platform</a>
            </div>
            <style>
                @keyframes fadeIn {
                    from {opacity: 0;}
                    to {opacity: 1;}
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""<br><br>""", unsafe_allow_html=True)

        # ==== Why Choose Us ====
        st.markdown("## 🚀 Why Choose Us?")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div style="background: #1e1e1e; border-radius: 12px; padding: 2rem; height: 100%; text-align: center; box-shadow: 0px 0px 10px rgba(0,0,0,0.2);">
                    <h3 style="color: #10b981;">AI Automation</h3>
                    <p style="color: #aaa;">Automate document analysis, verification, risk flagging and more using powerful AI pipelines.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div style="background: #1e1e1e; border-radius: 12px; padding: 2rem; height: 100%; text-align: center; box-shadow: 0px 0px 10px rgba(0,0,0,0.2);">
                    <h3 style="color: #10b981;">Real-Time Insights</h3>
                    <p style="color: #aaa;">Monitor social media, financials, and regulatory news in real-time with smart sentiment models.</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div style="background: #1e1e1e; border-radius: 12px; padding: 2rem; height: 100%; text-align: center; box-shadow: 0px 0px 10px rgba(0,0,0,0.2);">
                    <h3 style="color: #10b981;">Security & Compliance</h3>
                    <p style="color: #aaa;">GDPR-compliant, encryption-first platform securing your data and processes end-to-end.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""<br><br>""", unsafe_allow_html=True)

        # ==== Wavy separator ====
        st.markdown("""
            <div style="height: 50px; background: url('https://cdn.pixabay.com/photo/2017/01/31/17/44/wave-2021930_1280.png') center no-repeat; background-size: cover;"></div>
        """, unsafe_allow_html=True)

        # ==== Impact Section ====
        st.markdown("## 📊 Our Impact")
        st.markdown("""<br>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("""
                <div style="background: #1f2937; border-radius: 12px; padding: 2rem; text-align: center; box-shadow: 0px 0px 20px rgba(0,0,0,0.3);">
                    <h2 style="color: #10b981; font-size: 2.5rem;">+1,500</h2>
                    <p style="color: white;">Entities Analyzed</p>
                    <p style="color: #9ca3af; font-size: 0.9rem;">Reviewed businesses, assets, and documents through smart parsing and AI.</p>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
                <div style="background: #1f2937; border-radius: 12px; padding: 2rem; text-align: center; box-shadow: 0px 0px 20px rgba(0,0,0,0.3);">
                    <h2 style="color: #10b981; font-size: 2.5rem;">+500</h2>
                    <p style="color: white;">Deals Verified</p>
                    <p style="color: #9ca3af; font-size: 0.9rem;">Validated M&A, partnerships, investments and mitigated transactional risks.</p>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown("""
                <div style="background: #1f2937; border-radius: 12px; padding: 2rem; text-align: center; box-shadow: 0px 0px 20px rgba(0,0,0,0.3);">
                    <h2 style="color: #10b981; font-size: 2.5rem;">$1.2B+</h2>
                    <p style="color: white;">Assets Screened</p>
                    <p style="color: #9ca3af; font-size: 0.9rem;">Screened assets across industries, blockchain projects, startups and enterprises.</p>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""<br><br>""", unsafe_allow_html=True)

        # ==== What We Offer ====
        st.markdown("## 🌟 What We Offer")
        st.markdown("""<br>""", unsafe_allow_html=True)
        offer_col1, offer_col2 = st.columns(2)
        with offer_col1:
            st.markdown("""
                <ul style="list-style-type: none; padding: 0; font-size: 1.1rem;">
                    <li style="margin-bottom: 1rem;">📄 <b>Automated Document Review</b><br><span style="color: #9ca3af;">AI-powered extraction, classification, and anomaly detection in documents.</span></li>
                    <li style="margin-bottom: 1rem;">🛡️ <b>Risk & Compliance Verification</b><br><span style="color: #9ca3af;">Evaluate financials, founders, and companies against regulatory standards.</span></li>
                    <li style="margin-bottom: 1rem;">📊 <b>Crypto & Financial Monitoring</b><br><span style="color: #9ca3af;">Track token projects, crypto investments, and market sentiment.</span></li>
                </ul>
            """, unsafe_allow_html=True)
        with offer_col2:
            st.markdown("""
                <ul style="list-style-type: none; padding: 0; font-size: 1.1rem;">
                    <li style="margin-bottom: 1rem;">📢 <b>Real-Time Threat Detection</b><br><span style="color: #9ca3af;">Detect fraud attempts, scams, fake documents, and pump & dump signals.</span></li>
                    <li style="margin-bottom: 1rem;">🔒 <b>End-to-End Secure Data Rooms</b><br><span style="color: #9ca3af;">Encrypted data storage and sharing during due diligence phases.</span></li>
                    <li style="margin-bottom: 1rem;">🚀 <b>Smart Alerts & Reporting</b><br><span style="color: #9ca3af;">Stay ahead with custom alerts, dashboards and predictive analytics.</span></li>
                </ul>
            """, unsafe_allow_html=True)

        st.markdown("""<br><br>""", unsafe_allow_html=True)

        # ==== Final Call to Action ====
        st.markdown("""
            <div style="padding: 3rem; background: linear-gradient(to right, #11998e, #38ef7d); border-radius: 20px; text-align: center;">
                <h2 style="color: white; font-size: 2.5rem; font-weight: bold;">Join the Future of Due Diligence</h2>
                <p style="color: #f0f0f0; font-size: 1.3rem;">Hundreds of businesses already trust our smart platform to make critical decisions faster, safer, smarter.</p>
                <a href="#contact" style="margin-top: 1.5rem; display: inline-block; background-color: white; color: #11998e; padding: 15px 30px; border-radius: 30px; font-size: 1.2rem; text-decoration: none;">Start Now</a>
            </div>
        """, unsafe_allow_html=True)

