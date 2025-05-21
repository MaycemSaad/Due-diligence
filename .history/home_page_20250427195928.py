import streamlit as st
import streamlit.components.v1 as components

# ✅ Page Config
st.set_page_config(
    page_title="Due Diligence AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ Modern CSS + AOS Animations
st.markdown("""
    <head>
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <style>

        /* Reset */
        * {margin: 0; padding: 0; box-sizing: border-box;}

        html, body, [data-testid="stAppViewContainer"] {
            background: linear-gradient(to bottom right, #f8fafc, #e2e8f0);
            font-family: 'Inter', sans-serif;
            scroll-behavior: smooth;
        }

        /* Navbar */
        .navbar {
            position: fixed;
            top: 0; left: 0; right: 0;
            padding: 1rem 2rem;
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        }
        .navbar-logo {
            font-weight: 700;
            font-size: 1.4rem;
            color: #2563eb;
            text-decoration: none;
        }
        .navbar-links {
            display: flex;
            gap: 1.5rem;
        }
        .navbar-links a {
            color: #0f172a;
            font-weight: 500;
            text-decoration: none;
            font-size: 1rem;
            position: relative;
        }
        .navbar-links a:hover::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 2px;
            background: #2563eb;
            left: 0;
            bottom: -4px;
        }
        .navbar-actions button {
            background: #2563eb;
            color: white;
            border: none;
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .navbar-actions button:hover {
            background: #1d4ed8;
        }

        /* Hero Section */
        .hero {
            padding: 8rem 2rem 6rem;
            text-align: center;
        }
        .hero h1 {
            font-size: 3rem;
            color: #0f172a;
            font-weight: 800;
            margin-bottom: 1rem;
        }
        .hero h1 span {
            color: #2563eb;
        }
        .hero p {
            font-size: 1.2rem;
            color: #475569;
            margin-bottom: 2.5rem;
        }
        .hero-buttons button {
            margin: 0 0.5rem;
            padding: 0.8rem 1.8rem;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: 0.3s;
        }
        .btn-primary {
            background: #2563eb;
            color: white;
        }
        .btn-primary:hover {
            background: #1d4ed8;
        }
        .btn-outline {
            background: transparent;
            border: 2px solid #2563eb;
            color: #2563eb;
        }
        .btn-outline:hover {
            background: #2563eb;
            color: white;
        }

        /* Features Section */
        .features {
            padding: 5rem 2rem;
            background: white;
        }
        .features h2 {
            text-align: center;
            font-size: 2.5rem;
            color: #0f172a;
            margin-bottom: 2rem;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        .feature-card {
            background: #f1f5f9;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 6px 10px rgba(0,0,0,0.05);
            transition: 0.3s;
        }
        .feature-card:hover {
            transform: translateY(-8px);
            background: #e0f2fe;
        }
        .feature-card h3 {
            color: #0f172a;
            margin-bottom: 1rem;
        }
        .feature-card p {
            color: #475569;
        }

        /* Footer */
        .footer {
            background: #0f172a;
            color: white;
            padding: 3rem 2rem;
            text-align: center;
            font-size: 0.9rem;
        }

        /* AOS */
        @keyframes fadeIn {
            from {opacity: 0; transform: translateY(20px);}
            to {opacity: 1; transform: translateY(0);}
        }
    </style>
    </head>
""", unsafe_allow_html=True)

# ✅ Navbar
components.html("""
<div class="navbar">
    <a class="navbar-logo" href="/">DueDiligence</a>
    <div class="navbar-links">
        <a href="#features">Features</a>
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
    </div>
    <div class="navbar-actions">
        <button onclick="window.location.href='?page=login'">Login</button>
    </div>
</div>
""", height=70)

# ✅ Hero
components.html("""
<section class="hero" data-aos="fade-up">
    <h1>For Your <span>Trusted Decisions</span></h1>
    <p>Streamlined due diligence to empower smarter, faster, and more informed investment decisions with our AI platform.</p>
    <div class="hero-buttons">
        <button class="btn-primary" onclick="window.location.href='?page=signup'">Get Started</button>
        <button class="btn-outline" onclick="window.location.href='#features'">Learn More</button>
    </div>
</section>
""", height=600)

# ✅ Features
st.markdown("""
<section id="features" class="features">
    <h2 data-aos="fade-up">Our Core Features</h2>
    <div class="features-grid">
        <div class="feature-card" data-aos="fade-up" data-aos-delay="100">
            <h3>AI Risk Analysis</h3>
            <p>Analyze thousands of data points to spot potential issues instantly.</p>
        </div>
        <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
            <h3>Real-Time Monitoring</h3>
            <p>Get alerts on company changes, regulatory issues, and market news in real-time.</p>
        </div>
        <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <h3>Data Security</h3>
            <p>Enterprise-grade encryption and GDPR-compliant protocols to protect your data.</p>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# ✅ Footer
st.markdown("""
<footer class="footer">
    © 2025 Due Diligence AI — All rights reserved.
</footer>
""", unsafe_allow_html=True)

# ✅ AOS Activation
components.html("""
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script>
  AOS.init({
    duration: 1000,
    once: true
  });
</script>
""", height=0)
