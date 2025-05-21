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
    # Hero section
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

    # Why Choose Us Section
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

    # Wavy separator
    st.markdown("""
        <div style="height: 50px; background: url('https://cdn.pixabay.com/photo/2017/01/31/17/44/wave-2021930_1280.png') center no-repeat; background-size: cover;"></div>
    """, unsafe_allow_html=True)

    # Impact Section
    st.markdown("## 📈 Our Impact")
    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown("<h2 style='text-align:center; color: #10b981;'>+1,500</h2><p style='text-align:center;'>Entities Analyzed</p>", unsafe_allow_html=True)
    with col5:
        st.markdown("<h2 style='text-align:center; color: #10b981;'>+500</h2><p style='text-align:center;'>Deals Verified</p>", unsafe_allow_html=True)
    with col6:
        st.markdown("<h2 style='text-align:center; color: #10b981;'>$1.2B+</h2><p style='text-align:center;'>Assets Screened</p>", unsafe_allow_html=True)

    st.markdown("""<br><br>""", unsafe_allow_html=True)

    # What We Offer
    st.markdown("## 🌟 What We Offer")
    st.markdown("""
        - 📄 **Automated Document Review**  
        - 🛡️ **Risk & Compliance Verification**  
        - 📊 **Crypto & Financial Market Monitoring**  
        - 📢 **Real-Time Threat Detection**  
        - 🔒 **End-to-End Secure Data Rooms**  
    """)

    st.markdown("""<br><br>""", unsafe_allow_html=True)

    # Final Call to Action
    st.markdown("""
        <div style="padding: 3rem; background: linear-gradient(to right, #11998e, #38ef7d); border-radius: 20px; text-align: center;">
            <h2 style="color: white; font-size: 2.5rem; font-weight: bold;">Join the Future of Due Diligence</h2>
            <p style="color: #f0f0f0; font-size: 1.3rem;">Hundreds of businesses already trust our smart platform to make critical decisions faster, safer, smarter.</p>
            <a href="#contact" style="margin-top: 1.5rem; display: inline-block; background-color: white; color: #11998e; padding: 15px 30px; border-radius: 30px; font-size: 1.2rem; text-decoration: none;">Start Now</a>
        </div>
    """, unsafe_allow_html=True)

