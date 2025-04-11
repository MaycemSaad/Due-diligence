import streamlit as st
import streamlit.components.v1 as components

# Set page config
st.set_page_config(page_title="Due Diligence Platform", layout="wide")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "About", "Statistics"])

# --- HOME PAGE ---
if page == "Home":
    st.markdown("""
        <div style="padding: 4rem 2rem 2rem; background: linear-gradient(to right, #1a1a1a, #0f0f0f); text-align: center; border-radius: 20px;">
            <h1 style="color: white; font-size: 3rem;">Smart Insights.<br>For Your Trusted Decisions</h1>
            <p style="color: #ccc; font-size: 1.2rem;">Streamlined due diligence to empower investors, startups, and enterprises.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 15px;">
                <h3>Why We Do This</h3>
                <p>
                    In today's fast-paced business environment, reliable due diligence is more essential than ever. 
                    Our platform simplifies the process of evaluating businesses, investments, or partnerships 
                    by automating document review, background checks, and financial validation.
                </p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 15px;">
                <h3>Helping You Grow In Every Stage</h3>
                <p>
                    Whether you're a venture capitalist, M&A advisor, or a startup founder, 
                    we provide the tools to conduct thorough due diligence at every step — 
                    from early-stage screening to final deal closing. Make faster, smarter decisions with confidence.
                </p>
            </div>
        """, unsafe_allow_html=True)

# --- ABOUT PAGE ---
elif page == "About":
    st.markdown("""
        <div style="background-color: #e8f0fe; padding: 30px; border-radius: 15px;">
            <h2>About Our Platform</h2>
            <p>
                Our Due Diligence platform was created to modernize and accelerate the evaluation of businesses, partnerships,
                and investments. With a user-centric design, smart document scanning, and AI-driven alerts, we help you
                reduce risk, improve decision quality, and close deals faster.
            </p>
        </div>
    """, unsafe_allow_html=True)

# --- STATISTICS PAGE ---
elif page == "Statistics":
    st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h2>Platform Impact</h2>
            <p>Explore how we've helped organizations make smarter decisions.</p>
        </div>
    """, unsafe_allow_html=True)

    components.html("""
        <div style="display: flex; justify-content: center; gap: 50px;">
            <div style="background-color:#111; padding:20px; border-radius:15px; text-align:center; min-width: 200px;">
                <h1 id="count1" style="color:#06f; font-size: 2.5rem;">0</h1>
                <p style="color:white; font-size: 1rem;">Entities Analyzed</p>
            </div>
            <div style="background-color:#111; padding:20px; border-radius:15px; text-align:center; min-width: 200px;">
                <h1 id="count2" style="color:#06f; font-size: 2.5rem;">0</h1>
                <p style="color:white; font-size: 1rem;">Deals Verified</p>
            </div>
            <div style="background-color:#111; padding:20px; border-radius:15px; text-align:center; min-width: 200px;">
                <h1 id="count3" style="color:#06f; font-size: 2.5rem;">0</h1>
                <p style="color:white; font-size: 1rem;">Total Value Screened ($)</p>
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
    """, height=300)
