import streamlit as st
from pymongo import MongoClient
import bcrypt
from datetime import datetime

def show_user_profile():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]

    st.sidebar.title("🔙 Menu")
    if st.sidebar.button("🏠 Back to App"):
        st.session_state.page = "main"
        st.rerun()

    # 🌟 Professional Styling
    st.markdown("""
    <style>
    .profile-container {
        display: flex;
        flex-wrap: wrap;
        gap: 2rem;
        justify-content: center;
        margin-top: 2rem;
    }
    .profile-card, .password-card {
        background: rgba(30, 41, 59, 0.8);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        flex: 1 1 400px;
        color: white;
        transition: transform 0.3s ease;
    }
    .profile-card:hover, .password-card:hover {
        transform: translateY(-5px);
    }
    .profile-title {
        font-size: 2.5rem;
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
    .info-icon {
        font-size: 1.6rem;
    }
    .avatar {
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        color: white;
        font-weight: bold;
        border-radius: 50%;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        margin: auto;
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .avatar:hover {
        transform: scale(1.1);
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 0.7rem;
        background-color: #38bdf8;
        color: black;
        font-weight: bold;
        margin-left: 0.5rem;
        font-size: 1rem;
    }
    .password-title {
        font-size: 2rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1.5rem;
        color: #38bdf8;
    }
    .stButton>button {
        width: 100%;
        height: 50px;
        font-weight: bold;
        border-radius: 10px;
        background: linear-gradient(90deg, #0ea5e9, #38bdf8);
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #38bdf8, #0ea5e9);
    }
    </style>
    """, unsafe_allow_html=True)

    # === Container Layout
    st.markdown("<div class='profile-container'>", unsafe_allow_html=True)

    # === Profile Card
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)

    if "user" not in st.session_state or not st.session_state.user:
        st.error("❌ Unable to retrieve user information.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    user = st.session_state.user
    initials = (user.get('first_name', '')[:1] + user.get('last_name', '')[:1]).upper() if user.get('first_name') and user.get('last_name') else "👤"

    st.markdown(f"<div class='avatar'>{initials}</div>", unsafe_allow_html=True)
    st.markdown("<div class='profile-title'>My Profile</div>", unsafe_allow_html=True)

    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False

    if st.session_state.edit_mode:
        with st.form("edit_profile_form"):
            new_first_name = st.text_input("First Name", value=user.get('first_name', ''))
            new_last_name = st.text_input("Last Name", value=user.get('last_name', ''))
            save_changes = st.form_submit_button("💾 Save Changes")

            if save_changes:
                db["users"].update_one(
                    {"email": user["email"]},
                    {"$set": {"first_name": new_first_name, "last_name": new_last_name}}
                )
                st.session_state.user['first_name'] = new_first_name
                st.session_state.user['last_name'] = new_last_name
                st.success("✅ Profile updated successfully!")
                st.session_state.edit_mode = False
                st.rerun()
    else:
        st.markdown(f"<div class='profile-info'><span class='info-icon'>🧑</span><b>First Name:</b> {user.get('first_name', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><span class='info-icon'>👨‍🦰</span><b>Last Name:</b> {user.get('last_name', 'N/A')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-info'><span class='info-icon'>📧</span><b>Email:</b> {user.get('email', 'N/A')}</div>", unsafe_allow_html=True)

        role_badge = f"<span class='badge'>{user.get('role', 'User').capitalize()}</span>"
        st.markdown(f"<div class='profile-info'><span class='info-icon'>🛡️</span><b>Role:</b> {role_badge}</div>", unsafe_allow_html=True)

        if st.button("🖊️ Edit Profile"):
            st.session_state.edit_mode = True
            st.rerun()

    fields = [user.get('first_name'), user.get('last_name'), user.get('email')]
    completion = (sum(1 for f in fields if f and f != 'N/A') / 3) * 100
    st.markdown(f"<div class='profile-info'><span class='info-icon'>📈</span><b>Profile Completion:</b> {int(completion)}%</div>", unsafe_allow_html=True)
    st.progress(int(completion))

    st.markdown("</div>", unsafe_allow_html=True)

    # === Password Card
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
    st.markdown("</div>", unsafe_allow_html=True)
