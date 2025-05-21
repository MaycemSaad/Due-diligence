from auth import show_login_page, show_signup_page
from test import show_due_diligence_app
from socialMedia import show_social_media_analysis
from portfolio import show_crypto_market
from crypto_companies import show_crypto_companies
from compliance_check import show_smart_compliance_analyzer
from Scam_detector import show_scam_detector
from Document_Authenticity_Checker import show_document_authenticity_pro_ultimate
def show_Tools():
        # Create the tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📝 Document Authenticity", 
        "🚨 Scam Detector", 
        "🛡️ Smart Compliance", 
        "📱 Social Media Analysis", 
        "💹 Crypto Market", 
        "🏛️ Crypto Companies"
    ])

    # Now put each function inside the right tab
    with tab1:
        show_document_authenticity_pro_ultimate()

    with tab2:
        show_scam_detector()

    with tab3:
        show_smart_compliance_analyzer()

    with tab4:
        show_social_media_analysis()

    with tab5:
        show_crypto_market()

    with tab6:
        show_crypto_companies()
