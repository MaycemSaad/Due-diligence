import streamlit as st
from pymongo import MongoClient
import bcrypt

def show_user_profile():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]

    st.sidebar.title("🔙 Menu")
    if st.sidebar.button("🏠 Back to App"):
        st.session_state.page = "main"
        st.rerun()

    # === CSS Modernized ===
    st.markdown("""
    <style>
        .profile-container {
            display: flex;
            gap: 2rem;
            justify-content: center;
            margin-top: 2rem;
        }
        .profile-card, .password-card {
            background-color: #1e293b;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            flex: 1;
            color: white;
        }
        .profile-title {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: center;
            color: #38bdf8;
        }
        .profile-info {
            font-size: 1.1rem;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }
        .avatar {
            background: linear-gradient(135deg, #38bdf8, #0ea5e9);
            color: white;
            font-weight: bold;
            border-radius: 50%;
            width: 80px;
            height: 80px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            margin: auto;
            margin-bottom: 1rem;
        }

        .info-icon {
            font-size: 1.4rem;
        }
        .password-title {
            font-size: 1.6rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #38bdf8;
        }
        .stTextInput>div>div>input {
            background-color: #334155;
            color: white;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(90deg, #38bdf8, #0ea5e9);
            color: white;
            border: none;
            height: 50px;
            font-size: 1.1rem;
            font-weight: bold;
            border-radius: 10px;
            margin-top: 1rem;
        }
        .stButton>button:hover {
            background: #0ea5e9;
        }
    </style>
    """, unsafe_allow_html=True)

    # === Layout ===
    st.markdown("<div class='profile-container'>", unsafe_allow_html=True)

    # === Left: Profile Info ===
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.markdown("<div class='profile-title'>👤 My Profile</div>", unsafe_allow_html=True)

    if "user" not in st.session_state or not st.session_state.user:
        st.error("❌ Unable to retrieve user information.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    user = st.session_state.user

    st.markdown(f"<div class='profile-info'><span class='info-icon'>🧑</span><b>First Name:</b> {user.get('first_name', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-info'><span class='info-icon'>👨‍🦰</span><b>Last Name:</b> {user.get('last_name', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-info'><span class='info-icon'>📧</span><b>Email:</b> {user.get('email', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-info'><span class='info-icon'>🛡️</span><b>Role:</b> {user.get('role', 'User').capitalize()}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # === Right: Change Password ===
    st.markdown("<div class='password-card'>", unsafe_allow_html=True)
    st.markdown("<div class='password-title'>🔒 Change Password</div>", unsafe_allow_html=True)

    with st.form("change_password_form"):
        old_password = st.text_input("Old Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Update Password")

        if submit:
            db_user = db["users"].find_one({"email": user["email"]})
            if not db_user or not bcrypt.checkpw(old_password.encode(), db_user["password"]):
                st.error("❌ Old password incorrect.")
            elif new_password != confirm_new_password:
                st.error("❌ New passwords do not match.")
            else:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                db["users"].update_one({"email": user["email"]}, {"$set": {"password": hashed_pw}})
                st.success("✅ Password updated successfully!")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # Close container
