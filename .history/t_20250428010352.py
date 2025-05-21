import streamlit as st

# ==== Streamlit Config ====
st.set_page_config(page_title="Chainvestor Hub", layout="wide", initial_sidebar_state="collapsed")

# ==== Global Styles ====
st.markdown("""
    <style>
        html, body, .stApp {
            background: #0d0d0d;
            color: #e0e0e0;
            font-family: 'Poppins', sans-serif;
        }
        h1, h2, h3 {
            color: #ffcc00;
        }
        .section {
            padding: 40px 20px;
        }
        .card {
            background: #1a1a1a;
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            border: 1px solid #222;
            transition: 0.3s;
        }
        .card:hover {
            transform: translateY(-8px);
            box-shadow: 0 10px 20px rgba(255, 204, 0, 0.2);
            border-color: #ffcc00;
        }
        .footer {
            background: #111;
            padding: 40px 20px;
            text-align: center;
            margin-top: 80px;
            font-size: 15px;
            color: #777;
        }
    </style>
""", unsafe_allow_html=True)

# ==== Tabs Navigation ====
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Home", "🚀 Features", "ℹ️ About", "🛠️ Services", "✉️ Contact"])

# ==== Home Section ====
with tab1:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
            <h1>Chainvestor Hub</h1>
            <p>Smarter, Safer Investments Powered by AI and Blockchain.</p>
            <a href="#services" style="background-color: #ffcc00; color: black; padding: 12px 20px; border-radius: 25px; text-decoration: none;">🚀 Get Started</a>
            <a href="#about" style="background-color: transparent; color: #ffcc00; padding: 12px 20px; border: 2px solid #ffcc00; border-radius: 25px; text-decoration: none; margin-left: 20px;">ℹ️ Learn More</a>
        """, unsafe_allow_html=True)
    with col2:
        st.image("crypto.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==== Features Section ====
with tab2:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.header("🚀 Features")
    st.write("Cutting-edge tools to transform your portfolio management.")
    features = [("⚡ AI Risk Detection", "Real-time risk scanning."),
                ("🛡️ Compliance Engine", "Always regulation-ready."),
                ("📊 Predictive Analytics", "Forecast future movements.")]
    cols = st.columns(3)
    for col, (title, desc) in zip(cols, features):
        with col:
            st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==== About Section ====
with tab3:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.header("ℹ️ About Us")
    st.write("Our journey to revolutionize crypto investment.")
    st.markdown("""
        <div style="margin-top: 40px;">
            <h3>2019</h3>
            <p>Chainvestor founded to revolutionize crypto investments.</p>
            <h3>2021</h3>
            <p>Launched our proprietary AI Risk Engine.</p>
            <h3>2024</h3>
            <p>Expanded to 20+ countries and 3500+ investors.</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==== Services Section ====
with tab4:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.header("🛠️ Our Services")
    st.write("Everything you need for smarter, safer investing.")
    services = [("🔍 Due Diligence Automation", "Automated AI due diligence reports."),
                ("📈 Portfolio Stress Testing", "Simulate extreme market conditions.")]
    cols2 = st.columns(2)
    for col, (title, desc) in zip(cols2, services):
        with col:
            st.markdown(f"<div class='card'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==== Contact Section ====
with tab5:
    st.markdown('<div class="section">', unsafe_allow_html=True)
    st.header("✉️ Contact Us")
    st.write("Ready to transform your investment strategy? Let's talk.")
    contact_form = """
        <form action="https://formsubmit.co/YOUR_EMAIL" method="POST">
             <input type="text" name="name" placeholder="Your Name" required style="width:100%;padding:10px;margin:5px 0;">
             <input type="email" name="email" placeholder="Your Email" required style="width:100%;padding:10px;margin:5px 0;">
             <textarea name="message" placeholder="Your Message" required style="width:100%;padding:10px;height:100px;margin:5px 0;"></textarea>
             <button type="submit" style="background-color:#ffcc00;color:black;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Send</button>
        </form>
    """
    st.markdown(contact_form, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ==== Footer (Always Visible) ====
st.markdown("""
    <div class="footer">
        © 2025 Chainvestor Hub | 
        <a href="#features">Features</a> | 
        <a href="#about">About</a> | 
        <a href="#services">Services</a> | 
        <a href="#contact">Contact</a>
    </div>
""", unsafe_allow_html=True)
