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
    .sidebar-content {
        background: rgba(20, 20, 30, 0.85);
        padding: 30px 10px;
        border-radius: 20px;
        margin-top: 20px;
    }
    .sidebar-title {
        font-size: 28px;
        font-weight: bold;
        color: #ffcc00;
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar-button button {
        width: 100%;
        height: 50px;
        font-weight: bold;
        background: linear-gradient(90deg, #ffcc00, #e6b800);
        border: none;
        border-radius: 10px;
        color: black;
        transition: 0.3s;
    }
    .sidebar-button button:hover {
        background: linear-gradient(90deg, #e6b800, #ffcc00);
        color: white;
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
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        gap: 30px;
        margin-bottom: 30px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1a1a1a;
        padding: 12px 24px;
        border-radius: 12px;
        font-weight: bold;
        transition: 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #ffcc00, #e6b800);
        color: black;
        font-weight: bold;
    }
    .content-container {
        background: #161616;
        padding: 40px;
        border-radius: 20px;
        margin: 30px auto;
        max-width: 1200px;
        box-shadow: 0 8px 24px rgba(255, 204, 0, 0.1);
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

    # ==== Content in Tabs ====
    with tab1:
        with st.container():
            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            st.markdown("## 📝 Document Authenticity Checker PRO+")
            show_document_authenticity_pro_ultimate()
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        with st.container():
            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            
            show_scam_detector()
            st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        with st.container():
            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            
            show_smart_compliance_analyzer()
            st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        with st.container():
            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            
            show_social_media_analysis()
            st.markdown('</div>', unsafe_allow_html=True)

    with tab5:
        with st.container():
            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            
            show_crypto_market()
            st.markdown('</div>', unsafe_allow_html=True)

    with tab6:
        with st.container():
            st.markdown('<div class="content-container">', unsafe_allow_html=True)
            
            show_crypto_companies()
            st.markdown('</div>', unsafe_allow_html=True)
