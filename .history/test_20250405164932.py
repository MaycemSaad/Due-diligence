import streamlit as st
import streamlit.components.v1 as components

# Page configuration
st.set_page_config(page_title="About || NFTfun Marketplace", layout="wide")

# --- Navigation Bar ---
st.markdown("""
    <style>
        .nav-bar {
            background-color: #111;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }
        .nav-left {
            display: flex;
            align-items: center;
        }
        .nav-left h2 {
            margin-right: 2rem;
            color: #00bfff;
        }
        .nav-links a {
            margin: 0 1rem;
            text-decoration: none;
            color: white;
            font-weight: 500;
        }
        .nav-links a:hover {
            color: #00bfff;
        }
    </style>
    <div class="nav-bar">
        <div class="nav-left">
            <h2>Nuron</h2>
            <div class="nav-links">
                <a href="#home">Home</a>
                <a href="#about">About</a>
                <a href="#explore">Explore</a>
                <a href="#pages">Pages</a>
                <a href="#blog">Blog</a>
                <a href="#contact">Contact</a>
            </div>
        </div>
        <div>
            <input type="text" placeholder="Search here" style="padding:5px; border-radius:5px;">
            <button style="margin-left:10px; padding:6px 12px; background:#00bfff; color:white; border:none; border-radius:5px;">Wallet Connect</button>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- Hero Section ---
st.markdown("""
    <div style="padding: 60px 0; text-align: center; background: linear-gradient(to right, #000428, #004e92); color: white;">
        <h1>Direct Teams.<br>For Your <span style='color:#00bfff;'>Dedicated Dreams</span></h1>
    </div>
""", unsafe_allow_html=True)

# --- Why We Do This ---
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
        ### Why We Do This
        NFTs are virtual tokens that represent ownership of something inherently distinct and scarce, whether it be a physical or digital item, such as artwork, a soundtrack, a collectible, an in-game item or real estate.

        Unlike regular cryptocurrencies like bitcoin or fiat money like the U.S.
        
        [See Our Blog](#)
    ""
    )
with col2:
    st.markdown("""
        ### Helping You Grow In Every Stage
        NFTs represent ownership of unique digital or physical assets. Whether it's artwork, collectibles or real estate, NFTs offer a new era of value. Unlike currencies, they are non-fungible and unique.
    ""
    )

# --- Create, Sell & Collect ---
st.markdown("""
    ## Create, Sell well & Collect your Wonderful NFTs at Nuron Very Fast
    <div style="display: flex; gap: 20px;">
        <p style="flex: 1;">
            The NFTs is a one-trick pony that climbed the ladders of success in recent years. The growth of NFTs is tremendous, and according to Pymnts.com, the total sales volume of NFTs has nearly crossed $2.5 billion in the last six months.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- Animated Statistics ---
st.markdown("<h2 style='text-align: center;'>Nuron Statistics</h2>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

def animated_stat(label, target_value, delay=10):
    components.html(f"""
        <div style="text-align: center; padding: 30px; background-color: #111;
                    border-radius: 15px; margin: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.5);">
            <h1 id="{label}" style="color: #00bfff; font-size: 40px;">0</h1>
            <p style="color: #ccc; font-size: 18px;">{label}</p>
            <script>
                let count = 0;
                let target = {target_value};
                let speed = {delay};
                let el = document.getElementById("{label}");
                let increment = Math.ceil(target / 100);

                let counter = setInterval(function() {{
                    count += increment;
                    if (count >= target) {{
                        count = target;
                        clearInterval(counter);
                    }}
                    el.innerText = count.toLocaleString();
                }}, speed);
            </script>
        </div>
    """, height=150)

with col1:
    animated_stat("Nuron All NFTs", 309)
with col2:
    animated_stat("All Creators", 508)
with col3:
    animated_stat("Total NFT Volume ($)", 2500000000, delay=1)

# Footer or Additional Content Here if needed
