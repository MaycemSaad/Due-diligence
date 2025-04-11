import streamlit as st

# Custom CSS for styling (optional)
st.markdown("""
    <style>
    body {
        background-color: #0e0e0e;
        color: white;
    }
    .navbar {
        background-color: #181818;
        padding: 10px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .logo {
        font-weight: bold;
        font-size: 24px;
        color: #00aaff;
    }
    .nav-links {
        margin-top: 10px;
    }
    .nav-links a {
        margin-right: 15px;
        text-decoration: none;
        color: white;
        font-weight: 500;
    }
    .section {
        padding: 30px;
        border-radius: 12px;
        background-color: #1e1e1e;
        margin-bottom: 20px;
    }
    .stat-box {
        display: flex;
        justify-content: space-around;
        margin-top: 20px;
    }
    .card {
        background-color: #111111;
        padding: 20px;
        border-radius: 12px;
        width: 200px;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Navbar
st.markdown("""
<div class="navbar">
    <div class="logo">n <span style="color:white;">nuron</span></div>
    <div class="nav-links">
        <a href="#">Home</a>
        <a href="#">About</a>
        <a href="#">Explore</a>
        <a href="#">Pages</a>
        <a href="#">Blog</a>
        <a href="#">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("## 🎯 Direct Teams. For Your Dedicated Dreams")

# Why Section
st.markdown("""
<div class="section">
    <h3>Why We Do This</h3>
    <p>NFTs are virtual tokens that represent ownership of something inherently distinct and scarce...</p>
    <a href="#">👉 See Our Blog</a>
</div>

<div class="section">
    <h3>Helping You Grow In Every Stage</h3>
    <p>Whether you're new to NFTs or an experienced collector, we provide tools to make your journey smooth.</p>
</div>
""", unsafe_allow_html=True)

# Create & Sell Section
st.markdown("""
<div class="section">
    <h3>Create, Sell Well & Collect Your Wonderful NFTs at Nuron Very Fast</h3>
    <p>The NFT market is booming. With our platform, you can enter the space easily and start monetizing your creativity.</p>
</div>
""", unsafe_allow_html=True)

# Statistics
st.markdown("""
<div class="section">
    <h3>Nuron Statistics</h3>
    <div class="stat-box">
        <div class="card">
            <h2>309</h2>
            <p>Nuron All NFT's</p>
        </div>
        <div class="card">
            <h2>508</h2>
            <p>All Creators</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
