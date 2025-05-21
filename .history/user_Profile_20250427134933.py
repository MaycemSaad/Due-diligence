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

    st.markdown("""
    <style>
        .profile-card {
            background-color: #1f2937;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .profile-title {
            font-size: 2.2rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .profile-info {
            font-size: 1.1rem;
            margin: 0.5rem 0;
        }
        .password-form {
            background-color: #374151;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
            color: white;
        }
        .password-form-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 1rem;
            text-align: center;
        }
        .stTextInput > label {
            color: white;
        }
        .stButton button {
            width: 100%;
            height: 50px;
            font-size: 1.1rem;
            font-weight: bold;
            background-color: #2563eb;
            color: white;
            border-radius: 12px;
            margin-top: 1rem;
        }
        .stButton button:hover {
            background-color: #1d4ed8;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)

    st.markdown("<div class='profile-title'>👤 My Profile</div>", unsafe_allow_html=True)

    if "user" not in st.session_state or not st.session_state.user:
        st.error("❌ Unable to retrieve user information.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    user = st.session_state.user

    st.markdown(f"<div class='profile-info'><b>First Name:</b> {user.get('first_name', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-info'><b>Last Name:</b> {user.get('last_name', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-info'><b>Email:</b> {user.get('email', 'N/A')}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='profile-info'><b>Role:</b> {user.get('role', 'User').capitalize()}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # === Password Change Section ===
    st.markdown("<div class='password-form'>", unsafe_allow_html=True)
    st.markdown("<div class='password-form-title'>🔒 Change Password</div>", unsafe_allow_html=True)

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
