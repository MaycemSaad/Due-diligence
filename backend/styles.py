import streamlit as st

def set_custom_styles():
    st.markdown("""
    <style>
    html, body, .stApp {
        background-color: #0d0d0d;
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
