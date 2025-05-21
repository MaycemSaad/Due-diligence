import streamlit as st
from auth import show_login_page, show_signup_page
from test import show_due_diligence_app
import streamlit.components.v1 as components

# ✅ Page configuration at the top
st.set_page_config(
    page_title="💬 Due Diligence AI", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ✅ Professional CSS with animations and modern design
st.markdown("""
    <style>
        :root {
            --primary: #2563eb;
            --primary-dark: #1d4ed8;
            --secondary: #1e293b;
            --accent: #f59e0b;
            --light: #f8fafc;
            --dark: #0f172a;
            --success: #10b981;
            --card-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #f8fafc;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            scroll-behavior: smooth;
        }
        
        /* Modern navbar */
        .navbar {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            z-index: 1000;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .navbar-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .navbar-logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--dark);
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .navbar-logo span {
            color: var(--primary);
        }
        
        .navbar-links {
            display: flex;
            gap: 2rem;
        }
        
        .navbar-link {
            color: var(--secondary);
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95rem;
            transition: var(--transition);
            position: relative;
            padding: 0.5rem 0;
        }
        
        .navbar-link:hover {
            color: var(--primary);
        }
        
        .navbar-link::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--primary);
            transition: var(--transition);
        }
        
        .navbar-link:hover::after {
            width: 100%;
        }
        
        .navbar-link.active {
            color: var(--primary);
        }
        
        .navbar-link.active::after {
            width: 100%;
        }
        
        .navbar-actions {
            display: flex;
            gap: 1rem;
        }
        
        .btn {
            padding: 0.6rem 1.25rem;
            border-radius: 8px;
            font-weight: 500;
            font-size: 0.9rem;
            cursor: pointer;
            transition: var(--transition);
            border: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
        }
        
        .btn-outline {
            background: transparent;
            color: var(--primary);
            border: 1px solid var(--primary);
        }
        
        .btn-outline:hover {
            background: rgba(37, 99, 235, 0.05);
            transform: translateY(-2px);
        }
        
        /* Hero section */
        .hero {
            min-height: 90vh;
            display: flex;
            align-items: center;
            padding: 8rem 2rem 4rem;
            position: relative;
            overflow: hidden;
        }
        
        .hero::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 80%;
            height: 200%;
            background: radial-gradient(circle, rgba(37, 99, 235, 0.1) 0%, rgba(255, 255, 255, 0) 70%);
            z-index: -1;
        }
        
        .hero-container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
        }
        
        .hero-content {
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }
        
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1.2;
            color: var(--dark);
        }
        
        .hero-title span {
            color: var(--primary);
        }
        
        .hero-subtitle {
            font-size: 1.25rem;
            color: var(--secondary);
            line-height: 1.6;
            max-width: 90%;
        }
        
        .hero-actions {
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }
        
        .hero-image {
            position: relative;
            border-radius: 1rem;
            overflow: hidden;
            box-shadow: var(--card-shadow);
            transform: perspective(1000px) rotateY(-5deg);
            transition: var(--transition);
        }
        
        .hero-image:hover {
            transform: perspective(1000px) rotateY(0deg);
        }
        
        /* Features section */
        .section {
            padding: 6rem 2rem;
        }
        
        .section-title {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--dark);
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .section-subtitle {
            font-size: 1.1rem;
            color: var(--secondary);
            text-align: center;
            max-width: 700px;
            margin: 0 auto 3rem;
            line-height: 1.6;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .feature-card {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: var(--card-shadow);
            transition: var(--transition);
            border: 1px solid rgba(0, 0, 0, 0.05);
        }
        
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        
        .feature-icon {
            width: 60px;
            height: 60px;
            background: rgba(37, 99, 235, 0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 1.5rem;
        }
        
        .feature-icon svg {
            width: 30px;
            height: 30px;
            color: var(--primary);
        }
        
        .feature-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--dark);
            margin-bottom: 1rem;
        }
        
        .feature-description {
            color: var(--secondary);
            line-height: 1.6;
            font-size: 0.95rem;
        }
        
        /* Stats section */
        .stats {
            background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
            padding: 5rem 2rem;
            color: white;
            position: relative;
            overflow: hidden;
        }
        
        .stats::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd' opacity='0.1'%3E%3Cg fill='%23ffffff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }
        
        .stats-container {
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 2rem;
            text-align: center;
        }
        
        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        /* Testimonials */
        .testimonials {
            background: white;
            padding: 6rem 2rem;
        }
        
        .testimonials-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .testimonial-card {
            background: white;
            border-radius: 1rem;
            padding: 2rem;
            box-shadow: var(--card-shadow);
            border: 1px solid rgba(0, 0, 0, 0.05);
            position: relative;
        }
        
        .testimonial-card::before {
            content: '"';
            position: absolute;
            top: 1rem;
            left: 1.5rem;
            font-size: 4rem;
            color: rgba(37, 99, 235, 0.1);
            font-family: serif;
            line-height: 1;
        }
        
        .testimonial-content {
            font-style: italic;
            color: var(--secondary);
            line-height: 1.6;
            margin-bottom: 1.5rem;
            position: relative;
            z-index: 1;
        }
        
        .testimonial-author {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .testimonial-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            object-fit: cover;
        }
        
        .testimonial-author-info {
            display: flex;
            flex-direction: column;
        }
        
        .testimonial-name {
            font-weight: 600;
            color: var(--dark);
        }
        
        .testimonial-role {
            font-size: 0.85rem;
            color: var(--secondary);
            opacity: 0.8;
        }
        
        /* CTA section */
        .cta {
            background: linear-gradient(135deg, var(--dark) 0%, #1e293b 100%);
            padding: 6rem 2rem;
            color: white;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .cta::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -20%;
            width: 80%;
            height: 200%;
            background: radial-gradient(circle, rgba(37, 99, 235, 0.1) 0%, rgba(255, 255, 255, 0) 70%);
            z-index: 0;
        }
        
        .cta-container {
            max-width: 700px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }
        
        .cta-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
        }
        
        .cta-description {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        .cta-actions {
            display: flex;
            justify-content: center;
            gap: 1rem;
        }
        
        /* Footer */
        .footer {
            background: var(--dark);
            color: white;
            padding: 4rem 2rem 2rem;
        }
        
        .footer-container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 3rem;
        }
        
        .footer-logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: white;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .footer-logo span {
            color: var(--primary);
        }
        
        .footer-description {
            font-size: 0.9rem;
            opacity: 0.7;
            line-height: 1.6;
            margin-bottom: 1.5rem;
        }
        
        .footer-social {
            display: flex;
            gap: 1rem;
        }
        
        .social-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.1);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: var(--transition);
        }
        
        .social-icon:hover {
            background: var(--primary);
            transform: translateY(-3px);
        }
        
        .footer-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
        }
        
        .footer-links {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .footer-link {
            color: rgba(255, 255, 255, 0.7);
            text-decoration: none;
            transition: var(--transition);
            font-size: 0.9rem;
        }
        
        .footer-link:hover {
            color: white;
            transform: translateX(5px);
        }
        
        .footer-bottom {
            max-width: 1200px;
            margin: 3rem auto 0;
            padding-top: 2rem;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            opacity: 0.7;
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in {
            animation: fadeIn 0.8s ease-out forwards;
        }
        
        .delay-100 {
            animation-delay: 0.1s;
        }
        
        .delay-200 {
            animation-delay: 0.2s;
        }
        
        .delay-300 {
            animation-delay: 0.3s;
        }
        
        /* Responsive adjustments */
        @media (max-width: 1024px) {
            .hero-container {
                grid-template-columns: 1fr;
                gap: 3rem;
            }
            
            .hero-image {
                order: -1;
                max-width: 600px;
                margin: 0 auto;
            }
            
            .hero-content {
                text-align: center;
                align-items: center;
            }
            
            .hero-actions {
                justify-content: center;
            }
            
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .section-title {
                font-size: 2rem;
            }
            
            .navbar-links {
                display: none;
            }
            
            .cta-actions {
                flex-direction: column;
            }
        }
        
        /* Custom scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--primary);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-dark);
        }
    </style>
""", unsafe_allow_html=True)

# Session state management
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "home"

# Page routing
if st.session_state.user:
    show_due_diligence_app()
elif st.session_state.page == "login":
    show_login_page()
elif st.session_state.page == "signup":
    show_signup_page()
else:
    # Modern navbar
    components.html("""
    <div class="navbar">
        <div class="navbar-container">
            <a href="/" class="navbar-logo">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 7L12 12L21 7L12 2Z" fill="#2563eb"/>
                    <path d="M3 12L12 17L21 12" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
                    <path d="M3 17L12 22L21 17" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
                </svg>
                Due<span>Diligence</span>
            </a>
            <div class="navbar-links">
                <a href="?page=home" class="navbar-link active">Home</a>
                <a href="?page=about" class="navbar-link">About</a>
                <a href="?page=services" class="navbar-link">Services</a>
                <a href="?page=contact" class="navbar-link">Contact</a>
            </div>
            <div class="navbar-actions">
                <button class="btn btn-outline" onclick="window.location.href='?page=login'">Login</button>
                <button class="btn btn-primary" onclick="window.location.href='?page=signup'">Get Started</button>
            </div>
        </div>
    </div>
    """, height=70)

    # Hero section
    st.markdown("""
    <div class="hero">
        <div class="hero-container">
            <div class="hero-content animate-fade-in">
                <h1 class="hero-title">Smart Insights <span>For Your Trusted Decisions</span></h1>
                <p class="hero-subtitle">
                    Streamlined due diligence to empower investors, startups, and enterprises to make faster, 
                    smarter, and more informed decisions with our AI-powered platform.
                </p>
                <div class="hero-actions">
                    <button class="btn btn-primary" onclick="window.location.href='?page=signup'">
                        Get Started
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M5 12H19M19 12L12 5M19 12L12 19" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                    <button class="btn btn-outline" onclick="window.location.href='?page=about'">
                        Learn More
                    </button>
                </div>
            </div>
            <div class="hero-image animate-fade-in delay-100">
                <img src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?ixlib=rb-1.2.1&auto=format&fit=crop&w=1000&q=80" alt="Due Diligence Dashboard" style="width:100%; height:auto; display:block;">
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Features section
    st.markdown("""
    <div class="section">
        <h2 class="section-title">Why Choose Our Platform</h2>
        <p class="section-subtitle">
            We combine cutting-edge technology with financial expertise to deliver unparalleled due diligence services
        </p>
        <div class="features-grid">
            <div class="feature-card animate-fade-in delay-100">
                <div class="feature-icon">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3 class="feature-title">AI-Powered Analysis</h3>
                <p class="feature-description">
                    Our proprietary algorithms analyze documents, financials, and market data to identify risks and opportunities with 95% accuracy.
                </p>
            </div>
            <div class="feature-card animate-fade-in delay-200">
                <div class="feature-icon">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M19.4 15C19.2669 15.3016 19.227 15.6363 19.2847 15.9606C19.3425 16.2849 19.4954 16.5836 19.7226 16.8149C19.9498 17.0462 20.2396 17.1979 20.5493 17.2486C20.859 17.2993 21.1726 17.2466 21.448 17.098L21.55 17.05C21.8266 16.939 22.0524 16.7331 22.188 16.471C22.3236 16.2089 22.3596 15.9084 22.2893 15.6249C22.219 15.3414 22.0476 15.0939 21.807 14.9277C21.5664 14.7615 21.2733 14.6884 20.982 14.722H20.55C20.086 13.377 19.173 12.229 17.964 11.475C16.755 10.721 15.321 10.408 13.903 10.587C12.485 10.766 11.168 11.426 10.178 12.457C9.187 13.488 8.583 14.825 8.467 16.25C8.351 17.675 8.731 19.096 9.543 20.281C10.355 21.466 11.549 22.339 12.925 22.754C14.301 23.169 15.773 23.1 17.1 22.558" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        <path d="M4.60002 15C4.7331 15.3016 4.77302 15.6363 4.71526 15.9606C4.6575 16.2849 4.5046 16.5836 4.27741 16.8149C4.05022 17.0462 3.7604 17.1979 3.45069 17.2486C3.14098 17.2993 2.82744 17.2466 2.552 17.098L2.45002 17.05C2.17337 16.939 1.94762 16.7331 1.81202 16.471C1.67642 16.2089 1.64042 15.9084 1.71071 15.6249C1.781 15.3414 1.9524 15.0939 2.193 14.9277C2.4336 14.7615 2.72672 14.6884 3.01802 14.722H3.45002C3.91402 13.377 4.82702 12.229 6.03602 11.475C7.24502 10.721 8.67902 10.408 10.097 10.587C11.515 10.766 12.832 11.426 13.822 12.457C14.813 13.488 15.417 14.825 15.533 16.25C15.649 17.675 15.269 19.096 14.457 20.281C13.645 21.466 12.451 22.339 11.075 22.754C9.69902 23.169 8.22702 23.1 6.90002 22.558" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3 class="feature-title">Real-Time Monitoring</h3>
                <p class="feature-description">
                    Track changes and updates in real-time with our continuous monitoring system that alerts you to critical developments.
                </p>
            </div>
            <div class="feature-card animate-fade-in delay-300">
                <div class="feature-icon">
                    <svg width="30" height="30" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 15V17M6 21H18C19.1046 21 20 20.1046 20 19V13C20 11.8954 19.1046 11 18 11H6C4.89543 11 4 11.8954 4 13V19C4 20.1046 4.89543 21 6 21ZM16 11V7C16 4.79086 14.2091 3 12 3C9.79086 3 8 4.79086 8 7V11H16Z" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </div>
                <h3 class="feature-title">Bank-Grade Security</h3>
                <p class="feature-description">
                    Your data is protected with enterprise-grade encryption, multi-factor authentication, and regular security audits.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Stats section
    st.markdown("""
    <div class="stats">
        <div class="stats-container">
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number" id="count1">0</div>
                    <div class="stat-label">Entities Analyzed</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="count2">0</div>
                    <div class="stat-label">Deals Verified</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="count3">0</div>
                    <div class="stat-label">Total Value Screened</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="count4">0</div>
                    <div class="stat-label">Happy Clients</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        function animateCounter(id, target, duration, prefix = '', suffix = '') {
            const element = document.getElementById(id);
            let count = 0;
            const increment = target / (duration / 16);
            
            const updateCounter = () => {
                count += increment;
                if (count >= target) {
                    count = target;
                    element.textContent = prefix + Math.floor(count).toLocaleString() + suffix;
                    return;
                }
                element.textContent = prefix + Math.floor(count).toLocaleString() + suffix;
                requestAnimationFrame(updateCounter);
            };
            
            updateCounter();
        }
        
        // Start counters when they come into view
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    animateCounter('count1', 1280, 2000);
                    animateCounter('count2', 347, 2000);
                    animateCounter('count3', 1500, 2000, '$', 'M');
                    animateCounter('count4', 289, 2000);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(document.querySelector('.stats'));
    </script>
    """, unsafe_allow_html=True)

    # Testimonials section
    st.markdown("""
    <div class="testimonials">
        <h2 class="section-title">Trusted by Industry Leaders</h2>
        <p class="section-subtitle">
            Don't just take our word for it. Here's what our clients say about our platform.
        </p>
        <div class="testimonials-grid">
            <div class="testimonial-card">
                <p class="testimonial-content">
                    The DueDiligence platform has transformed our investment process. What used to take weeks now takes days, with even better results. The AI risk detection has saved us from two bad investments already this year.
                </p>
                <div class="testimonial-author">
                    <img src="https://randomuser.me/api/portraits/women/43.jpg" alt="Sarah Johnson" class="testimonial-avatar">
                    <div class="testimonial-author-info">
                        <div class="testimonial-name">Sarah Johnson</div>
                        <div class="testimonial-role">Partner, Vertex Capital</div>
                    </div>
                </div>
            </div>
            <div class="testimonial-card">
                <p class="testimonial-content">
                    As a startup founder, I was amazed at how thorough the automated due diligence was. It helped us identify gaps in our financial reporting before our Series B, allowing us to address them proactively.
                </p>
                <div class="testimonial-author">
                    <img src="https://randomuser.me/api/portraits/men/32.jpg" alt="Michael Chen" class="testimonial-avatar">
                    <div class="testimonial-author-info">
                        <div class="testimonial-name">Michael Chen</div>
                        <div class="testimonial-role">CEO, TechNova</div>
                    </div>
                </div>
            </div>
            <div class="testimonial-card">
                <p class="testimonial-content">
                    The compliance monitoring feature alone is worth the subscription. We've reduced our regulatory risk exposure by 40% since implementing DueDiligence across our M&A practice.
                </p>
                <div class="testimonial-author">
                    <img src="https://randomuser.me/api/portraits/women/65.jpg" alt="Emily Rodriguez" class="testimonial-avatar">
                    <div class="testimonial-author-info">
                        <div class="testimonial-name">Emily Rodriguez</div>
                        <div class="testimonial-role">General Counsel, Stonebridge Partners</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA section
    st.markdown("""
    <div class="cta">
        <div class="cta-container">
            <h2 class="cta-title">Ready to Transform Your Due Diligence?</h2>
            <p class="cta-description">
                Join hundreds of financial professionals who trust our platform for smarter, faster investment decisions. 
                Get started with a free 14-day trial - no credit card required.
            </p>
            <div class="cta-actions">
                <button class="btn btn-primary" onclick="window.location.href='?page=signup'">
                    Start Free Trial
                </button>
                <button class="btn btn-outline" style="color: white; border-color: white;" onclick="window.location.href='?page=contact'">
                    Contact Sales
                </button>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <div class="footer">
        <div class="footer-container">
            <div>
                <a href="/" class="footer-logo">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L3 7L12 12L21 7L12 2Z" fill="#2563eb"/>
                        <path d="M3 12L12 17L21 12" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
                        <path d="M3 17L12 22L21 17" stroke="#2563eb" stroke-width="2" stroke-linecap="round"/>
                    </svg>
                    Due<span>Diligence</span>
                </a>
                <p class="footer-description">
                    The most advanced AI-powered due diligence platform for investors, advisors, and enterprises.
                </p>
                <div class="footer-social">
                    <a href="#" class="social-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M18 2H15C13.6739 2 12.4021 2.52678 11.4645 3.46447C10.5268 4.40215 10 5.67392 10 7V10H7V14H10V22H14V14H17L18 10H14V7C14 6.73478 14.1054 6.48043 14.2929 6.29289C14.4804 6.10536 14.7348 6 15 6H18V2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </a>
                    <a href="#" class="social-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M23 3C22.0424 3.67548 20.9821 4.19211 19.86 4.53C19.2577 3.83751 18.4573 3.34669 17.567 3.12393C16.6767 2.90116 15.7395 2.9572 14.8821 3.28445C14.0247 3.61171 13.2884 4.1944 12.773 4.95372C12.2575 5.71303 11.9877 6.61234 12 7.53V8.53C10.2426 8.57557 8.50127 8.18581 6.93101 7.39545C5.36074 6.60508 4.01032 5.43864 3 4C3 4 -1 13 8 17C5.94053 18.398 3.48716 19.0989 1 19C10 24 21 19 21 7.5C20.9991 7.22145 20.9723 6.94359 20.92 6.67C21.9406 5.66349 22.6608 4.39271 23 3V3Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </a>
                    <a href="#" class="social-icon">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M16 8C17.5913 8 19.1174 8.63214 20.2426 9.75736C21.3679 10.8826 22 12.4087 22 14V21H18V14C18 13.4696 17.7893 12.9609 17.4142 12.5858C17.0391 12.2107 16.5304 12 16 12C15.4696 12 14.9609 12.2107 14.5858 12.5858C14.2107 12.9609 14 13.4696 14 14V21H10V14C10 12.4087 10.6321 10.8826 11.7574 9.75736C12.8826 8.63214 14.4087 8 16 8Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M6 9H2V21H6V9Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <path d="M4 6C5.10457 6 6 5.10457 6 4C6 2.89543 5.10457 2 4 2C2.89543 2 2 2.89543 2 4C2 5.10457 2.89543 6 4 6Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </a>
                </div>
            </div>
            <div>
                <h3 class="footer-title">Product</h3>
                <ul class="footer-links">
                    <li><a href="#" class="footer-link">Features</a></li>
                    <li><a href="#" class="footer-link">Pricing</a></li>
                    <li><a href="#" class="footer-link">API</a></li>
                    <li><a href="#" class="footer-link">Integrations</a></li>
                    <li><a href="#" class="footer-link">Changelog</a></li>
                </ul>
            </div>
            <div>
                <h3 class="footer-title">Company</h3>
                <ul class="footer-links">
                    <li><a href="#" class="footer-link">About Us</a></li>
                    <li><a href="#" class="footer-link">Careers</a></li>
                    <li><a href="#" class="footer-link">Press</a></li>
                    <li><a href="#" class="footer-link">Blog</a></li>
                    <li><a href="#" class="footer-link">Contact</a></li>
                </ul>
            </div>
            <div>
                <h3 class="footer-title">Resources</h3>
                <ul class="footer-links">
                    <li><a href="#" class="footer-link">Documentation</a></li>
                    <li><a href="#" class="footer-link">Guides</a></li>
                    <li><a href="#" class="footer-link">Webinars</a></li>
                    <li><a href="#" class="footer-link">Community</a></li>
                    <li><a href="#" class="footer-link">Status</a></li>
                </ul>
            </div>
        </div>
        <div class="footer-bottom">
            <div>© 2023 DueDiligence AI. All rights reserved.</div>
            <div>
                <a href="#" style="color: rgba(255, 255, 255, 0.7); text-decoration: none; margin-left: 1.5rem;">Privacy Policy</a>
                <a href="#" style="color: rgba(255, 255, 255, 0.7); text-decoration: none; margin-left: 1.5rem;">Terms of Service</a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add smooth scroll behavior
    components.html("""
    <script>
        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
        
        // Navbar scroll effect
        window.addEventListener('scroll', function() {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.1)';
                navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            } else {
                navbar.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.05)';
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            }
        });
    </script>
    """)