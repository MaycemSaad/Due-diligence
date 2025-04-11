
# Replace hero section
st.markdown("""
    <div class="hero">
        <h1>Smart Insights.<br>For Your Trusted Decisions</h1>
        <p>Streamlined due diligence to empower investors, startups, and enterprises.</p>
    </div>
""", unsafe_allow_html=True)

# Why We Do This - LEFT COLUMN
with col1:
    st.markdown("### Why We Do This")
    st.markdown("""
        In today's fast-paced business environment, reliable due diligence is more essential than ever. 
        Our platform simplifies the process of evaluating businesses, investments, or partnerships 
        by automating document review, background checks, and financial validation.
    """)
    st.button("Explore Our Insights")

# Helping You Grow - RIGHT COLUMN
with col2:
    st.markdown("### Helping You Grow In Every Stage")
    st.markdown("""
        Whether you're a venture capitalist, M&A advisor, or a startup founder, 
        we provide the tools to conduct thorough due diligence at every step — 
        from early-stage screening to final deal closing. Make faster, smarter decisions with confidence.
    """)

# Create/Sell section → Analyze & Verify
st.markdown("""
    <div class="section">
        <h2>Analyze, Verify & Decide Confidently With Our Due Diligence Platform</h2>
        <p>
            We've supported hundreds of companies in navigating risk and opportunity. 
            With customizable workflows, smart alerts, and a secure data room, 
            our platform is designed to streamline even the most complex due diligence processes.
        </p>
    </div>
""", unsafe_allow_html=True)

# Stats: animated
components.html("""
    <div style="display: flex; justify-content: center; gap: 50px;">
        <div class="stat-card">
            <h1 id="nft_count">0</h1>
            <p>Entities Analyzed</p>
        </div>
        <div class="stat-card">
            <h1 id="creator_count">0</h1>
            <p>Deals Verified</p>
        </div>
        <div class="stat-card">
            <h1 id="value_count">0</h1>
            <p>Total Value Screened ($)</p>
        </div>
    </div>

    <script>
        function countUp(id, target, duration) {
            let element = document.getElementById(id);
            let start = 0;
            let increment = target / (duration / 10);

            let interval = setInterval(() => {
                start += increment;
                if (start >= target) {
                    start = target;
                    clearInterval(interval);
                }
                element.innerText = Math.floor(start).toLocaleString();
            }, 10);
        }

        countUp("nft_count", 1280, 2000);
        countUp("creator_count", 347, 2000);
        countUp("value_count", 1500000000, 2000);
    </script>
""", height=250)
