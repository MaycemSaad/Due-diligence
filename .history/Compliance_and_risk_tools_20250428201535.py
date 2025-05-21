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
    # ==== Sidebar Menu ====
    st.sidebar.title("🔙 Menu")
    if st.sidebar.button("🏠 Back to App"):
        st.session_state.page = "main"
        st.rerun()

    # ==== Tabs for Each Tool ====
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Document Authenticity", 
        "🚨 Scam Detector", 
        "🛡️ Smart Compliance", 
        "📱 Social Media Analysis", 
        "💹 Crypto Market", 
        "🏛️ Crypto Companies"
    ])

    with tab1:
        st.markdown("### 📝 Document Authenticity Checker")
        show_document_authenticity_pro_ultimate()

    with tab2:
        st.markdown("### 🚨 Scam Detector")
        show_scam_detector()

    with tab3:
        st.markdown("### 🛡️ Smart Compliance Analyzer")
        show_smart_compliance_analyzer()

    with tab4:
        st.markdown("### 📱 Social Media Analysis")
        show_social_media_analysis()

    with tab5:
        st.markdown("### 💹 Crypto Market Overview")
        show_crypto_market()

    with tab6:
        st.markdown("### 🏛️ Crypto Companies Database")
        show_crypto_companies()
