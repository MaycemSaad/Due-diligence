
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
