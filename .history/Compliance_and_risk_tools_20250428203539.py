import streamlit as st
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app
from socialMedia import show_social_media_analysis
from portfolio import show_crypto_market
from crypto_companies import show_crypto_companies
from compliance_check import show_smart_compliance_analyzer
from Scam_detector import show_scam_detector
from Document_Authenticity_Checker import show_document_authenticity_pro_ultimate

def show_Tools():
    # ==== Sidebar ====
    st.sidebar.markdown("""
    <style>
    /* Sidebar Custom */
    .sidebar-content {
        background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
        padding: 30px 10px;
        border-radius: 20px;
        margin-top: 20px;
        box-shadow: 0 8px 20px rgba(255, 204, 0, 0.15);
    }
    .sidebar-title {
        font-size: 26px;
        font-weight: 700;
        color: #ffcc00;
        text-align: center;
        margin-bottom: 25px;
        text-transform: uppercase;
    }
    .sidebar-button button {
        width: 100%;
        padding: 12px 0;
        font-weight: 600;
        font-size: 18px;
        border-radius: 12px;
        background: linear-gradient(90deg, #ffcc00, #e6b800);
        border: none;
        color: black;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(255,204,0,0.3);
    }
    .sidebar-button button:hover {
        background: linear-gradient(90deg, #e6b800, #ffcc00);
        color: white;
        transform: translateY(-2px);
    }
    </style>
    <div class="sidebar-content">
        <div class="sidebar-title">🔙 Menu</div>
    </div>
    """, unsafe_allow_html=True)

    if st.sidebar.button("🏠 Back to App", key="back_to_app", help="Go back to Main Page"):
        st.session_state.page = "main"
        st.rerun()

    # ==== Tabs Layout ====
    st.markdown("""
    <style>
    /* Tabs Custom */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 24px;
        margin-bottom: 30px;
        margin-top: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1f1f1f;
        padding: 14px 28px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 18px;
        color: #ccc;
        transition: all 0.3s ease;
        border: 1px solid #333;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #292929;
        color: #fff;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #ffcc00, #e6b800);
        color: black;
        font-weight: bold;
        box-shadow: 0 4px 14px rgba(255, 204, 0, 0.3);
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Document Authenticity", 
        "🚨 Scam Detector", 
        "🛡️ Smart Compliance", 
        "📱 Social Media Analysis", 
        "💹 Crypto Market", 
        "🏛️ Crypto Companies"
    ])

    # ==== Content per Tab ====
    with tab1:
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>📝 Document Authenticity Checker</h2>", unsafe_allow_html=True)
        show_document_authenticity_pro_ultimate()

    with tab2:
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🚨 Scam Detector</h2>", unsafe_allow_html=True)
        show_scam_detector()

    with tab3:
        st.markdown("<h2 style='text-align:center; color:#ffcc00;'>🛡️ Smart Compliance Analyzer</h2>", unsafe_allow_html=True)
        show_smart_compliance_analyzer()

    with tab4:
        show_social_media_analysis()

    with tab5:
        show_crypto_market()

    with tab6:
        show_crypto_companies()
