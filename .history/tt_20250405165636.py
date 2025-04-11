import streamlit as st
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Due Diligence Platform", layout="wide")

# Hero section
st.markdown("""
    <div style="padding: 4rem 2rem 2rem; background: linear-gradient(to right, #1a1a1a, #0f0f0f); text-align: center;">
        <h1 style="color: white; font-size: 3rem;">Smart Insights.<br>For Your Trusted Decisions</h1>
        <p style="color: #ccc; font-size: 1.2rem;">Streamlined due diligence to empower investors, startups, and enterprises.</p>
    </div>
""", unsafe_allow_html=True)

# Create the columns BEFORE using them
col1, col2 = st.columns(2)

with col1:
    st.subheader("Why We Do This")
    st.markdown("""
        In today's fast-paced business environment, reliable due diligence is more essential than ever. 
        Our platform simplifies the process of evaluating businesses, investments, or partnerships 
        by automating document review, background checks, and financial validation.
    """)

with col2:
    st.subheader("Helping You Grow In Every Stage")
    st.markdown("""
        Whether you're a venture capitalist, M&A advisor, or a startup founder, 
        we provide the tools to conduct thorough due diligence at every step — 
        from early-stage screening to final deal closing. Make faster, smarter decisions with confidence.
    """)

# Value proposition
st.markdown("""
    <div style="padding: 2rem 4rem;">
        <h2>Analyze, Verify & Decide Confidently With Our Due Diligence Platform</h2>
        <p>
            We've supported hundreds of companies in navigating risk and opportunity. 
            With customizable workflows, smart alerts, and a secure data room, 
            our platform is designed to streamline even the most complex due diligence processes.
        </p>
    </div>
""", unsafe_allow_html=True)

# Animated stats
components.html("""
    <div style="display: flex; justify-content: center; gap: 50px;">
        <div style="background-color:#111; padding:20px; border-radius:15px; text-align:center;">
            <h1 id="count1" style="color:#06f;">0</h1>
            <p style="color:white;">Entities Analyzed</p>
        </div>
        <div style="background-color:#111; padding:20px; border-radius:15px; text-align:center;">
            <h1 id="count2" style="color:#06f;">0</h1>
            <p style="color:white;">Deals Verified</p>
        </div>
        <div style="background-color:#111; padding:20px; border-radius:15px; text-align:center;">
            <h1 id="count3" style="color:#06f;">0</h1>
            <p style="color:white;">Total Value Screened ($)</p>
        </div>
    </div>

    <script>
        function animate(id, target, duration) {
            const element = document.getElementById(id);
            let count = 0;
            const increment = target / (duration / 10);
            const interval = setInterval(() => {
                count += increment;
                if (count >= target) {
                    count = target;
                    clearInterval(interval);
                }
                element.innerText = Math.floor(count).toLocaleString();
            }, 10);
        }

        animate('count1', 1280, 2000);
        animate('count2', 347, 2000);
        animate('count3', 1500000000, 2000);
    </script>
""", height=250)
