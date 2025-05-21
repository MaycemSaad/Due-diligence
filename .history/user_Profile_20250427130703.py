import streamlit as st
import bcrypt
from pymongo import MongoClient

# Connexion MongoDB (à réutiliser ici si nécessaire)
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def show_user_profile():
    st.title("👤 My Profile")

    user_email = st.session_state.user
    user = db["users"].find_one({"first_name": user_email})

    if not user:
        st.error("❌ Unable to retrieve user information.")
        return

    st.subheader("📄 Personal Information")
    st.markdown(f"**First Name:** {user.get('first_name', 'N/A')}")
    st.markdown(f"**Last Name:** {user.get('last_name', 'N/A')}")
    st.markdown(f"**Email:** {user.get('email', 'N/A')}")
    st.markdown(f"**Role:** {user.get('role', 'user').capitalize()}")
    st.markdown(f"**Created At:** {user.get('created_at', 'N/A')}")

    st.divider()

    st.subheader("🔒 Change Password")

    with st.form(key="change_password_form"):
        current_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        submit_change = st.form_submit_button("Update Password")

    if submit_change:
        if not all([current_pw, new_pw, confirm_pw]):
            st.error("❌ Please fill all fields.")
        elif new_pw != confirm_pw:
            st.error("❌ New passwords do not match.")
        elif not verify_password(current_pw, user["password"]):
            st.error("❌ Current password is incorrect.")
        else:
            new_hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt())
            db["users"].update_one({"_id": user["_id"]}, {"$set": {"password": new_hashed}})
            st.success("✅ Password updated successfully!")
            st.balloons()

    st.divider()

    if st.button("⬅️ Back to App"):
        st.session_state.page = "chat"
        st.rerun()
