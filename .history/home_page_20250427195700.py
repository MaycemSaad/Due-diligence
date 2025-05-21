import streamlit as st
import streamlit.components.v1 as components

# ✅ Configuration
st.set_page_config(
    page_title="💬 Due Diligence AI", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ Modern CSS + Animations + Hero Video Background
st.markdown("""
    <head>
    <link href="https://unpkg.com/aos@2.3.1/dist/aos.css" rel="stylesheet">
    <style>
        /* General Reset */
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body, html, [data-testid="stAppViewContainer"] {
            background-color: #f8fafc;
            font-family: 'Inter', sans-serif;
            scroll-behavior: smooth;
        }

        /* Navbar */
        .navbar {
            position: fixed;
            top: 0; left: 0; right: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 1000;
        }
        .navbar a {
            color: #1e293b;
            margin: 0 1rem;
            font-weight: 500;
            text-decoration: none;
            position: relative;
        }
        .navbar a:hover::after {
            content: "";
            position: absolute;
            left: 0; bottom: -5px;
            width: 100%;
            height: 2px;
            background: #2563eb;
        }
        .navbar .actions button {
            background-color: #2563eb;
            color: white;
            padding: 0.5rem 1rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        .navbar .actions button:hover {
            background-color: #1d4ed8;
        }

        /* Hero Section with Video Background */
        .hero {
            position: relative;
            height: 95vh;
            width: 100%;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: white;
        }
        #heroVideo {
            position: absolute;
            top: 0; left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: -1;
            filter: brightness(0.6);
        }
        .hero-content {
            z-index: 2;
            padding: 2rem;
            animation: fadeIn 2s ease-in;
        }
        .hero h1 {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        .hero .cta-btns button {
            margin: 0 0.5rem;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
        }
        .cta-primary {
            background: #2563eb;
            color: white;
        }
        .cta-secondary {
            background: transparent;
            color: white;
            border: 2px solid white;
        }
        .cta-primary:hover, .cta-secondary:hover {
            background: #1d4ed8;
            border-color: #1d4ed8;
        }

        /* Features Section */
        .features {
            padding: 5rem 2rem;
            background: #f8fafc;
            text-align: center;
        }
        .features h2 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
            color: #0f172a;
        }
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }
        .feature-card {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
        }
        .feature-card:hover {
            transform: translateY(-10px);
        }

        /* Footer */
        .footer {
            background: #0f172a;
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }

        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    </head>
""", unsafe_allow_html=True)

# ✅ Navbar HTML
components.html("""
<div class="navbar">
    <div>
        <a href="/">Due<span style="color:#2563eb;">Diligence</span></a>
    </div>
    <div>
        <a href="#features">Features</a>
        <a href="#about">About</a>
        <a href="#contact">Contact</a>
    </div>
    <div class="actions">
        <button onclick="window.location.href='?page=login'">Login</button>
    </div>
</div>
""", height=70)

# ✅ Hero Section avec Vidéo
components.html("""
<div class="hero">
    <video autoplay muted loop id="heroVideo">
        <source src="https://cdn.coverr.co/videos/coverr-working-on-a-computer-1643/1080p.mp4" type="video/mp4">
    </video>
    <div class="hero-content" data-aos="fade-up">
        <h1>Empower Your Decisions</h1>
        <p>Smart, fast, AI-powered due diligence insights at your fingertips.</p>
        <div class="cta-btns">
            <button class="cta-primary" onclick="window.location.href='?page=signup'">Get Started</button>
            <button class="cta-secondary" onclick="window.location.href='#features'">Learn More</button>
        </div>
    </div>
</div>
""", height=800)

# ✅ Features Section
st.markdown("""
<section id="features" class="features">
    <h2 data-aos="fade-up">Our Core Features</h2>
    <div class="features-grid">
        <div class="feature-card" data-aos="fade-up" data-aos-delay="100">
            <h3>AI Risk Detection</h3>
            <p>Identify hidden risks instantly with advanced ML models.</p>
        </div>
        <div class="feature-card" data-aos="fade-up" data-aos-delay="200">
            <h3>Real-Time Monitoring</h3>
            <p>Continuous alerts on company changes, market moves, and red flags.</p>
        </div>
        <div class="feature-card" data-aos="fade-up" data-aos-delay="300">
            <h3>Data Privacy</h3>
            <p>Bank-grade encryption and GDPR-compliant security standards.</p>
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

# ✅ Activate AOS Animations
components.html("""
<script src="https://unpkg.com/aos@2.3.1/dist/aos.js"></script>
<script>
  AOS.init({
    duration: 1000,
    once: true
  });
</script>
""", height=0)
