import streamlit as st

# ----- Page Config -----
st.set_page_config(
    page_title="Nuron | About",
    page_icon="🌀",
    layout="wide"
)

# ----- Custom Styling -----
st.markdown("""
    <style>
        html, body {
            background-color: #0d0d0d;
            color: #f0f0f0;
            font-family: 'Segoe UI', sans-serif;
        }
        .title {
            font-size: 42px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 10px;
        }
        .subtitle {
            font-size: 24px;
            color: #bbbbbb;
        }
        .section {
            background-color: #1c1c1c;
            padding: 40px;
            border-radius: 20px;
            margin-top: 40px;
        }
        .stat-card {
            text-align: center;
            background-color: #111;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
            margin: 10px;
        }
        .stat-card h1 {
            color: #00bfff;
            font-size: 40px;
            margin: 0;
        }
        .stat-card p {
            color: #ccc;
            margin: 0;
            font-size: 18px;
        }
        .nav {
            color: #999;
            font-size: 16px;
        }
    </style>
""", unsafe_allow_html=True)

# ----- Navbar -----
st.markdown("### 🌀 Nuron")
st.markdown('<div class="nav">Home | About | Explore | Pages | Blog | Contact</div>', unsafe_allow_html=True)
st.divider()

# ----- Hero Section -----
st.markdown('<div class="title">Direct Teams.<br>For Your Dedicated Dreams</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A powerful NFT platform built for artists, collectors, and creators.</div>', unsafe_allow_html=True)

# ----- Why Section -----
st.markdown('<div class="section">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    st.subheader("Why We Do This")
    st.write("NFTs are virtual tokens that represent ownership of something inherently distinct and scarce, "
             "whether it be a physical or digital item such as artwork, a soundtrack, or real estate. "
             "Unlike regular cryptocurrencies like Bitcoin or fiat money, NFTs are unique.")

    st.button("🔗 Visit Our Blog")

with col2:
    st.subheader("Helping You Grow In Every Stage")
    st.write("Whether you're an artist just starting out or a seasoned creator, Nuron helps you launch, "
             "promote, and monetize your NFTs effortlessly with industry-leading tools and community support.")
st.markdown('</div>', unsafe_allow_html=True)

# ----- Create / Sell Section -----
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("Create, Sell & Collect NFTs Fast")

st.write("NFTs have exploded in popularity. According to Pymnts.com, the total sales volume of NFTs has "
         "nearly crossed $2.5 billion in just six months. Back in 2020, that number was only $13.7 million. "
         "This rapid growth shows the world’s appetite for digital ownership is just beginning.")

st.markdown('</div>', unsafe_allow_html=True)

# ----- Statistics -----
st.markdown('<div class="section">', unsafe_allow_html=True)
st.subheader("📊 Nuron Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="stat-card">
            <h1>309</h1>
            <p>Nuron All NFTs</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="stat-card">
            <h1>508</h1>
            <p>All Creators</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="stat-card">
            <h1>$2.5B</h1>
            <p>Total NFT Volume</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
