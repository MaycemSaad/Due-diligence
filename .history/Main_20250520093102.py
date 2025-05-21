import streamlit as st
from auth import show_login_page, show_signup_page,show_verification_page
from test import show_due_diligence_app

# ==== Config ====
st.set_page_config(page_title="💬 Due Diligence AI", layout="wide")

# ==== CSS ====
st.markdown("""
<style>
    html, body {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        font-family: 'Arial', sans-serif;
        color: white !important;
    }
    .main-title {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        margin-top: 3rem;
        color: white !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #f0f0f0 !important;
        margin-bottom: 3rem;
        line-height: 1.6;
    }
    .stButton > button {
        font-size: 1.1rem;
        padding: 0.7rem 2rem;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white !important;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    p, div, span, li {
        color: white !important;
    }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        color: white !important;
        background-color: rgba(255,255,255,0.1) !important;
    }
    .stChatMessage {
        background-color: rgba(255,255,255,0.1) !important;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stAlert {
        background-color: rgba(255,255,255,0.15) !important;
        border-left: 4px solid #4CAF50;
    }
    @media (max-width: 600px) {
        .main-title {
            font-size: 2.5rem;
        }
        .subtitle {
            font-size: 1rem;
        }
        .stButton > button {
            padding: 0.5rem 1.5rem;
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

# ==== Page Control ====
if st.session_state.page == "login":
    show_login_page()
elif st.session_state.page == "signup":
    show_signup_page()
elif st.session_state.page == "verify_identity":
    show_verification_page()    
elif st.session_state.user:
    if st.session_state.user["role"] == "admin":
        from admin_dashboard import show_admin_dashboard
        show_admin_dashboard()
    else:
        show_due_diligence_app()
else:
    # ========================
    # ======== TABS ===========
    # ========================
    tabs = st.tabs(["🏠 Home", "ℹ️ About", "💼 Services", "📞 Contact"])

    # === Home Tab ===
    import streamlit as st
    import time

    with tabs[0]:
        st.markdown("<h1 class='main-title'>Smart Insights.<br>For Your Trusted Decisions</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Streamlined due diligence to empower investors, startups, and enterprises to make faster, smarter, and more informed decisions.</p>", unsafe_allow_html=True)

        # Adding an image
        st.image("images.jpg", use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Why We Do This")
            st.write("""
                In today's fast-paced business environment, reliable due diligence is more essential than ever. 
                Our platform simplifies the process of evaluating businesses, investments, or partnerships 
                by automating document review, background checks, and financial validation.
            """)

            # Key benefits with animations
            st.markdown("### Key Benefits:")
            benefits = [
                "🚀 **Efficiency**: Reduce time spent on manual checks.",
                "✅ **Accuracy**: Leverage AI to minimize human error.",
                "📈 **Scalability**: Easily handle multiple evaluations simultaneously."
            ]
            for benefit in benefits:
                st.write(benefit)
                time.sleep(0.5)  # Animation delay

            if st.button("Learn More", key="why_we_do_this"):
                st.markdown("<p>Discover how our tools can help you!</p>", unsafe_allow_html=True)

        with col2:
            st.subheader("Helping You Grow In Every Stage")
            st.write("""
                Whether you're a venture capitalist, M&A advisor, or a startup founder, 
                we provide the tools to conduct thorough due diligence at every step — 
                from early-stage screening to final deal closing.
            """)

            # Animated statistics
            st.markdown("### Key Statistics:")
            stats = {
                "Projects Evaluated": 1500,
                "Users Served": 5000,
                "Average Time Saved Per Evaluation": "3 hours",
            }
            for key, value in stats.items():
                st.write(f"**{key}:** {value}")
                time.sleep(0.5)  # Animation delay

            if st.button("Explore Services", key="helping_you_grow"):
                st.markdown("<p>Check out our comprehensive services!</p>", unsafe_allow_html=True)

        # Pro Features Section
        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>Pro Features</h2>", unsafe_allow_html=True)
        st.write("""
            Upgrade to Pro to unlock advanced features that enhance your due diligence process:
        """)
        pro_features = [
            "🔍 **Advanced Analytics**: Gain deeper insights into your data.",
            "⚙️ **Customizable Dashboards**: Tailor your workspace to fit your needs.",
            "📊 **Real-time Collaboration**: Work seamlessly with your team.",
            "🛡️ **Enhanced Security**: Keep your data safe with top-notch security measures."
        ]
        for feature in pro_features:
            st.write(feature)
            time.sleep(0.5)  # Animation delay

        # Call to action
        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>Get Started Today!</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Join us to enhance your decision-making process with our innovative tools.</p>", unsafe_allow_html=True)
        if st.button("Get Started"):
            st.markdown("<p>Sign up to access our platform!</p>", unsafe_allow_html=True)
    # === About Tab ===
    with tabs[1]:
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>About Us</h2>", unsafe_allow_html=True)
        st.write("""
            We are a team of passionate professionals dedicated to transforming the due diligence process.
            Our platform combines cutting-edge technology, AI, and decades of experience to help investors,
            startups, and enterprises make more informed decisions, faster.
        """)
        st.write("""
            ### 🏆 Our Mission
            To simplify and accelerate due diligence, empowering smarter decision making.
        """)

    # === Services Tab ===
    with tabs[2]:
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>Our Services</h2>", unsafe_allow_html=True)
        st.write("""
        - AI-powered Document Review
        - Real-time Risk Analysis
        - Background Checks & Financial Validation
        - Customizable Workflows
        - Secure Data Rooms
        """)

    # === Contact Tab ===
    with tabs[3]:
        st.markdown("<h2 style='text-align: center; color: #2E3B4E;'>Contact Us</h2>", unsafe_allow_html=True)
        st.write("""
            📧 Email: info@duediligenceplatform.com  
            📞 Phone: +1 (800) 123-4567  
            📍 Address: 123 Business Avenue, Suite 456, New York, NY 10001
        """)

        # ===== Login/Signup Buttons =====
        spacer1, col_connexion, spacer2, col_signup, spacer3 = st.columns([1, 2, 0.5, 2, 1])
        with col_connexion:
            if st.button("🔐 Login"):
                st.session_state.page = "login"
                st.rerun()
        with col_signup:
            if st.button("📝 Signup"):
                st.session_state.page = "signup"
                st.rerun()