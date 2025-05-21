import streamlit as st
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app
from socialMedia import show_social_media_analysis
from portfolio import show_crypto_market
from crypto_companies import show_crypto_companies
from compliance_check import show_smart_compliance_analyzer
from Scam_detector import show_scam_detector
from Document_Authenticity_Checker import show_document_authenticity_pro_ultimate
import time
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.app_logo import add_logo
from streamlit_extras.toggle_switch import st_toggle_switch
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.add_vertical_space import add_vertical_space
import pandas as pd
import plotly.express as px

# ==== Config ====
st.set_page_config(
    page_title="🔍 Due Diligence AI Pro", 
    layout="wide",
    page_icon="🔍",
    initial_sidebar_state="expanded"
)

# ==== CSS ====
st.markdown("""
<style>
    :root {
        --primary: #2563eb;
        --secondary: #1e40af;
        --accent: #3b82f6;
        --background: #f8fafc;
        --card: #ffffff;
        --text: #1e293b;
        --text-secondary: #64748b;
    }
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
        background-color: var(--background);
        color: var(--text);
    }
    
    .main-title {
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        margin-top: 2rem;
        color: var(--text);
        line-height: 1.2;
        background: linear-gradient(to right, #2563eb, #1e40af);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: var(--text-secondary);
        margin-bottom: 3rem;
        line-height: 1.6;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .feature-card {
        background-color: var(--card);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        height: 100%;
        border-left: 4px solid var(--primary);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 1rem;
        color: var(--primary);
    }
    
    .stButton > button {
        font-size: 1rem;
        font-weight: 600;
        padding: 0.7rem 1.5rem;
        border-radius: 8px;
        background-color: var(--primary);
        color: white;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary);
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [role="tablist"] {
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .stTabs [role="tab"] {
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border-radius: 8px 8px 0 0;
        margin: 0 0.25rem;
        transition: all 0.3s ease;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        background-color: var(--primary);
        color: white;
    }
    
    .stTabs [role="tab"]:not([aria-selected="true"]):hover {
        background-color: rgba(37, 99, 235, 0.1);
    }
    
    .tool-card {
        background-color: var(--card);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 2rem;
    }
    
    .tool-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    .tool-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
        color: var(--primary);
    }
    
    .tool-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
        color: var(--text);
    }
    
    .tool-description {
        color: var(--text-secondary);
        margin-bottom: 1.5rem;
    }
    
    .stats-card {
        background-color: var(--card);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        text-align: center;
    }
    
    .stats-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary);
        margin: 0.5rem 0;
    }
    
    .stats-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: 0;
    }
    
    .testimonial-card {
        background-color: var(--card);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1rem;
    }
    
    .testimonial-text {
        font-style: italic;
        color: var(--text);
        margin-bottom: 1rem;
    }
    
    .testimonial-author {
        font-weight: 600;
        color: var(--primary);
        margin: 0;
    }
    
    .testimonial-role {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin: 0;
    }
    
    .pricing-card {
        background-color: var(--card);
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        transition: all 0.3s ease;
        text-align: center;
        border: 2px solid transparent;
    }
    
    .pricing-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: var(--primary);
    }
    
    .pricing-card.popular {
        border-color: var(--primary);
        position: relative;
    }
    
    .popular-badge {
        position: absolute;
        top: -12px;
        right: 20px;
        background-color: var(--primary);
        color: white;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .pricing-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: var(--text);
    }
    
    .pricing-price {
        font-size: 2.5rem;
        font-weight: 800;
        color: var(--primary);
        margin: 1rem 0;
    }
    
    .pricing-period {
        font-size: 1rem;
        color: var(--text-secondary);
    }
    
    .pricing-feature {
        margin: 0.75rem 0;
        color: var(--text);
    }
    
    .pricing-button {
        margin-top: 1.5rem;
    }
    
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.5rem;
        }
        
        .subtitle {
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
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ==== Dark Mode Toggle ====
dark_mode = st.checkbox("Dark Mode", value=st.session_state.dark_mode)
st.session_state.dark_mode = dark_mode

# Apply dark mode if enabled
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        :root {
            --primary: #3b82f6;
            --secondary: #1e40af;
            --accent: #60a5fa;
            --background: #1e293b;
            --card: #334155;
            --text: #f8fafc;
            --text-secondary: #94a3b8;
        }
    </style>
    """, unsafe_allow_html=True)


# Apply dark mode if enabled
if st.session_state.dark_mode:
    st.markdown("""
    <style>
        :root {
            --primary: #3b82f6;
            --secondary: #1e40af;
            --accent: #60a5fa;
            --background: #1e293b;
            --card: #334155;
            --text: #f8fafc;
            --text-secondary: #94a3b8;
        }
    </style>
    """, unsafe_allow_html=True)

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
    # ======== TABS ==========
    # ========================
    tabs = st.tabs(["🏠 Home", "📊 Features", "💎 Premium", "📞 Contact"])

    # === Home Tab ===
    # === Home Tab ===
    with tabs[0]:
        st.markdown("<h1 class='main-title'>Advanced Due Diligence<br>Intelligence Platform</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Harness the power of AI-driven analytics to uncover risks, verify authenticity, and make confident investment decisions with our comprehensive due diligence suite.</p>", unsafe_allow_html=True)
        
        # Hero Image
        st.image("due_diligence.avif", use_column_width=True)  # Replace with your image path

        # Hero CTA Buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("🚀 Get Started", key="hero_get_started"):
                st.session_state.page = "signup"
                st.rerun()
        with col2:
            if st.button("🛠️ Explore Tools", key="hero_explore_tools"):
                # Navigate to tools page
                st.session_state.page = "tools"
                st.rerun()
        with col3:
            if st.button("📞 Contact Sales", key="hero_contact_sales"):
                # Navigate to contact page
                st.session_state.page = "contact"
                st.rerun()
        
        # Stats Section
        st.markdown("---")
        st.subheader("Trusted by leading organizations worldwide")
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        for i, (value, label) in enumerate([
            ("250K+", "Documents Analyzed"),
            ("98%", "Accuracy Rate"),
            ("10K+", "Active Users"),
            ("24/7", "Support"),
        ]):
            with stats_col1 if i == 0 else (stats_col2 if i == 1 else (stats_col3 if i == 2 else stats_col4)):
                st.markdown(f'<div class="stats-value">{value}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="stats-label">{label}</div>', unsafe_allow_html=True)

        # Features Grid
        st.markdown("---")
        st.subheader("Key Features")
        features = [
            ("🔍", "Deep Document Analysis", "AI-powered examination of contracts, financial statements, and legal documents to uncover hidden risks and anomalies."),
            ("📈", "Financial Health Scoring", "Comprehensive evaluation of financial stability with predictive analytics for future performance."),
            ("🕵️", "Background Verification", "Automated checks on company leadership, litigation history, and regulatory compliance."),
            ("🌐", "Global Compliance", "Multi-jurisdictional compliance checks across 150+ countries with local regulation expertise."),
            ("🤖", "AI Risk Prediction", "Machine learning models that predict potential risks based on historical patterns and market trends."),
            ("🔗", "Blockchain Verification", "Immutable record-keeping and smart contract validation for transparent due diligence processes."),
        ]
        
        for i in range(0, len(features), 3):
            cols = st.columns(3)
            for j, (icon, title, description) in enumerate(features[i:i+3]):
                with cols[j]:
                    st.markdown(f'<div class="feature-icon">{icon}</div>', unsafe_allow_html=True)
                    st.subheader(title)
                    st.write(description)

        # Testimonials
        st.markdown("---")
        st.subheader("What Our Clients Say")
        testimonials = [
            ("This platform reduced our due diligence time by 70% while improving accuracy. The AI risk flags have saved us from two potentially disastrous investments.", "Sarah Johnson", "Investment Director, Venture Capital"),
            ("The compliance automation features alone are worth the subscription. We've streamlined our KYC process across 12 jurisdictions with one platform.", "Michael Chen", "Head of Compliance, Global Bank"),
            ("As a startup, the investor-ready reports helped us secure funding faster by pre-answering 90% of due diligence questions upfront.", "David Martinez", "CEO, FinTech Startup"),
        ]
        
        for i, (text, author, role) in enumerate(testimonials):
            col = st.columns(3)[i]
            with col:
                st.markdown(f'<div class="testimonial-text">"{text}"</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="testimonial-author">{author}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="testimonial-role">{role}</div>', unsafe_allow_html=True)
    
    
    # === Features Tab ===
    with tabs[1]:
        st.subheader("Advanced Features for Professional Due Diligence")
        st.write("Our platform offers a comprehensive set of features designed to meet the needs of professionals across industries.")
        
        # Feature Categories
        feature_category = st.radio(
            "Explore Features by Category:",
            ["🔍 Document Analysis", "📊 Financial Intelligence", "🕵️ Background Checks", "🌐 Global Compliance", "🤖 AI & Automation"],
            horizontal=True,
            label_visibility="hidden"
        )
        
        st.markdown("---")
        
        if feature_category == "🔍 Document Analysis":
            col1, col2 = st.columns(2)
            with col1:
                with stylable_container(
                    key="doc_feature1",
                    css_styles="""
                    {
                        background-color: var(--card);
                        border-radius: 12px;
                        padding: 1.5rem;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        margin-bottom: 1rem;
                    }
                    """
                ):
                    st.markdown("### Forensic Document Examination")
                    st.write("- AI-powered detection of document tampering")
                    st.write("- Metadata analysis and timestamp verification")
                    st.write("- Signature and seal authenticity checks")
                    st.write("- Cross-document consistency analysis")
            
            with col2:
                with stylable_container(
                    key="doc_feature2",
                    css_styles="""
                    {
                        background-color: var(--card);
                        border-radius: 12px;
                        padding: 1.5rem;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        margin-bottom: 1rem;
                    }
                    """
                ):
                    st.markdown("### Contract Intelligence")
                    st.write("- Automated red flag detection in contracts")
                    st.write("- Clause comparison across document versions")
                    st.write("- Unfair term identification")
                    st.write("- Obligation extraction and tracking")
        
        elif feature_category == "📊 Financial Intelligence":
            col1, col2 = st.columns(2)
            with col1:
                with stylable_container(
                    key="fin_feature1",
                    css_styles="""
                    {
                        background-color: var(--card);
                        border-radius: 12px;
                        padding: 1.5rem;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        margin-bottom: 1rem;
                    }
                    """
                ):
                    st.markdown("### Financial Statement Analysis")
                    st.write("- Automated ratio and trend analysis")
                    st.write("- Anomaly detection in financial data")
                    st.write("- Benchmarking against industry standards")
                    st.write("- Cash flow sustainability scoring")
            
            with col2:
                with stylable_container(
                    key="fin_feature2",
                    css_styles="""
                    {
                        background-color: var(--card);
                        border-radius: 12px;
                        padding: 1.5rem;
                        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                        margin-bottom: 1rem;
                    }
                    """
                ):
                    st.markdown("### Transaction Monitoring")
                    st.write("- Pattern recognition in payment flows")
                    st.write("- Related-party transaction identification")
                    st.write("- Money laundering risk scoring")
                    st.write("- Blockchain transaction tracing")
        
        # ... (similar sections for other feature categories)
        
        # Feature Demo Section
        st.markdown("---")
        st.subheader("See It In Action")
        
        # Create a sample dataframe for demonstration
        demo_data = pd.DataFrame({
            "Document Type": ["Annual Report", "Contract", "Financial Statement", "Compliance Filing"],
            "Risk Score": [15, 42, 28, 65],
            "Authenticity": [98, 76, 95, 62],
            "Key Issues": ["None", "Unusual clauses", "Revenue recognition", "Late filing"]
        })
        
        # Interactive dataframe explorer
        filtered_df = dataframe_explorer(demo_data, case=False)
        st.dataframe(filtered_df, use_container_width=True)
        
        # Visualization
        fig = px.bar(
            filtered_df,
            x="Document Type",
            y="Risk Score",
            color="Key Issues",
            title="Document Risk Analysis",
            template="plotly_white"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # === Premium Tab ===
# === Premium Tab ===
    with tabs[2]:
        st.subheader("Premium Plans for Every Need")
        st.write("Choose the plan that fits your due diligence requirements and scale as you grow.")
        
        # Pricing Cards
        pricing_col1, pricing_col2, pricing_col3 = st.columns(3)

        with pricing_col1:
            with stylable_container(
                key="pricing1",
                css_styles="""
                {
                    background-color: var(--card);
                    border-radius: 12px;
                    padding: 2rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    text-align: center;
                    height: 100%;
                }
                """
            ):
                st.markdown('<div class="pricing-title">Starter</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-price">$99</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-period">per month</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ 50 document analyses</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ Basic compliance checks</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ 5 social media scans</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✗ No API access</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✗ Limited support</div>', unsafe_allow_html=True)

        with pricing_col2:
            with stylable_container(
                key="pricing2",
                css_styles="""
                {
                    background-color: var(--card);
                    border-radius: 12px;
                    padding: 2rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    text-align: center;
                    height: 100%;
                }
                """
            ):
                st.markdown('<div class="pricing-title">Professional</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-price">$199</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-period">per month</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ 200 document analyses</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ Advanced compliance checks</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ 20 social media scans</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ API access</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✗ Priority support</div>', unsafe_allow_html=True)

        with pricing_col3:
            with stylable_container(
                key="pricing3",
                css_styles="""
                {
                    background-color: var(--card);
                    border-radius: 12px;
                    padding: 2rem;
                    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                    text-align: center;
                    height: 100%;
                }
                """
            ):
                st.markdown('<div class="pricing-title">Enterprise</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-price">$499</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-period">per month</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ Unlimited document analyses</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ Comprehensive compliance checks</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ Unlimited social media scans</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ Dedicated API access</div>', unsafe_allow_html=True)
                st.markdown('<div class="pricing-feature">✓ 24/7 priority support</div>', unsafe_allow_html=True)

        # Call to Action
        st.markdown("---")
        st.subheader("Start Your Journey Today!")
        if st.button("🚀 Choose Your Plan"):
            st.session_state.page = "signup"
            st.rerun()

    # === Contact Tab ===
    with tabs[3]:
        st.subheader("Contact Us")
        st.write("For inquiries, support, or feedback, please reach out to us.")
        st.write("📧 Email: support@duediligenceai.com")
        st.write("📞 Phone: +1 (800) 123-4567")
        st.write("📍 Address: 123 Business St, Suite 456, City, State, 12345")

        # Contact Form (optional)
        with st.form(key='contact_form'):
            name = st.text_input("Your Name")
            email = st.text_input("Your Email")
            message = st.text_area("Message")
            submit_button = st.form_submit_button("Send Message")
            if submit_button:
                st.success("Message sent successfully!")

# End of the Streamlit app