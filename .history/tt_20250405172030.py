import streamlit as st
import streamlit.components.v1 as components

# Page setup
st.set_page_config(page_title="Due Diligence Platform", layout="wide")

# Function to get the current page based on URL parameters
def get_page_from_url():
    query_params = st.experimental_get_query_params()
    if "page" in query_params:
        return query_params["page"][0]
    return "home"  # Default page

# Horizontal Navbar with clickable links
st.markdown("""
    <style>
        .navbar {
            background-color: #1a1a1a;
            overflow: hidden;
            display: flex;
            justify-content: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .navbar a {
            float: left;
            display: block;
            color: #f1f1f1;
            text-align: center;
            padding: 14px 20px;
            text-decoration: none;
            font-size: 17px;
        }
        .navbar a:hover {
            background-color: #ddd;
            color: black;
        }
        .navbar a.active {
            background-color: #06f;
            color: white;
        }
    </style>
    <div class="navbar">
        <a href="?page=home" class="navbar-link">Home</a>
        <a href="?page=about" class="navbar-link">About</a>
        <a href="?page=services" class="navbar-link">Services</a>
        <a href="?page=contact" class="navbar-link">Contact</a>
    </div>
""", unsafe_allow_html=True)

# Get current page based on the URL query parameter
page = get_page_from_url()

# Content based on the selected page
if page == "home":
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

elif page == "about":
    st.markdown("""
        <div style="padding: 4rem 2rem; background: #f4f4f4; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333;">About Us</h2>
            <p style="font-size: 1.1rem; color: #555;">
                We are a team of experts dedicated to simplifying the due diligence process. 
                Our platform uses advanced AI and machine learning to help companies and investors make well-informed decisions. 
                With years of experience in the field, we aim to make due diligence faster, easier, and more accurate.
            </p>
        </div>
    """, unsafe_allow_html=True)

elif page == "services":
    st.markdown("""
        <div style="padding: 4rem 2rem; background: #f4f4f4; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333;">Our Services</h2>
            <ul style="font-size: 1.1rem; color: #555;">
                <li>AI-powered Document Review</li>
                <li>Real-time Risk Analysis</li>
                <li>Background Checks & Financial Validation</li>
                <li>Customizable Workflows for Due Diligence</li>
                <li>Secure Data Rooms for Sensitive Information</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)

elif page == "contact":
    st.markdown("""
        <div style="padding: 4rem 2rem; background: #f4f4f4; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            <h2 style="color: #333;">Contact Us</h2>
            <p style="font-size: 1.1rem; color: #555;">
                For inquiries, feedback, or partnership opportunities, please reach out to us through the following methods:
            </p>
            <ul style="font-size: 1.1rem; color: #555;">
                <li>Email: <a href="mailto:info@duediligenceplatform.com" style="color: #06f;">info@duediligenceplatform.com</a></li>
                <li>Phone: +1 (800) 123-4567</li>
                <li>Address: 123 Business Avenue, Suite 456, New York, NY 10001</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
