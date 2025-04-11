import streamlit as st
import streamlit.components.v1 as components
import time

# ----- Page Config -----
st.set_page_config(page_title="About || NFTun Marketplace", layout="wide")

# ----- Custom CSS for dark navbar -----
st.markdown("""
    <style>
        body {
            background-color: #0D0D0D;
            color: white;
        }
        .navbar {
            background-color: #141414;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #333;
        }
        .navbar a {
            color: white;
            text-decoration: none;
            margin-left: 1.5rem;
            font-weight: bold;
        }
        .navbar a:hover {
            color: #06f;
        }
        .hero {
            padding: 4rem 2rem 2rem;
            background: linear-gradient(to right, #1a1a1a, #0f0f0f);
            text-align: center;
        }
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 0.5rem;
        }
        .hero p {
            font-size: 1.3rem;
            color: #ccc;
        }
        .section {
            padding: 2rem 4rem;
        }
        .stat-card {
            background-color: #1A1A1A;
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.05);
            margin: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ----- Navbar -----
st.markdown("""
    <div class="navbar">
        <div style="font-size: 1.5rem;"><b style="color:#06f;">n</b>uron</div>
        <div>
            <a href="#">Home</a>
            <a href="#">About</a>
            <a href="#">Explore</a>
            <a href="#">Pages</a>
            <a href="#">Blog</a>
            <a href="#">Contact</a>
        </div>
    </div>
""", unsafe_allow_html=True)

# ----- Hero Section -----
st.markdown("""
    <div class="hero">
        <h1>Direct Teams.<br>For Your Dadicated Dreams</h1>
    </div>
""", unsafe_allow_html=True)

# ----- "Why We Do This" Section -----
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Why We Do This")
    st.markdown("""
        NFTs are virtual tokens that represent ownership of something inherently distinct and scarce, 
        whether it be a physical or digital item, such as artwork, a soundtrack, a collectible, 
        an in-game item or real estate. Unlike regular cryptocurrencies like bitcoin or fiat money like the U.S.
    """)
    st.button("See Our Blog")

with col2:
    st.markdown("### Helping You Grow In Every Stage")
    st.markdown("""
        NFTs are virtual tokens that represent ownership of something inherently distinct and scarce, 
        whether it be a physical or digital item, such as artwork, a soundtrack, a collectible, 
        an in-game item or real estate. Unlike regular cryptocurrencies like bitcoin or fiat money like the U.S.
    """)

# ----- "Create and Collect NFTs" -----
st.markdown("""
    <div class="section">
        <h2>Create, Sell well & Collect your Wonderful NFTs at Nuron Very Fast</h2>
        <p>
            The NFTs is a one-trick pony that climbed the ladders of success in recent years. 
            The growth of NFTs is tremendous, and according to Pymnts.com, 
            the total sales volume of NFTs has nearly crossed $2.5 billion in the last six months. 
            Surprisingly, the total sales volume of NFTs was $13.7 million in 2020. 
            On comparing both the values,
        </p>
    </div>
""", unsafe_allow_html=True)

# ----- Animated Statistics with JavaScript -----
components.html("""
    <div style="display: flex; justify-content: center; gap: 50px;">
        <div class="stat-card">
            <h1 id="nft_count">0</h1>
            <p>Nuron All NFT's</p>
        </div>
        <div class="stat-card">
            <h1 id="creator_count">0</h1>
            <p>All Creators</p>
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
                element.innerText = Math.floor(start);
            }, 10);
        }

        countUp("nft_count", 309, 2000);
        countUp("creator_count", 508, 2000);
    </script>
""", height=200)

