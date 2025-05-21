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

    st.title("👤 My Profile")

    if "user" not in st.session_state or not st.session_state.user:
        st.error("❌ Unable to retrieve user information.")
        return

    user = st.session_state.user

    st.subheader("📝 Personal Information")
    st.text(f"First Name: {user.get('first_name', 'N/A')}")
    st.text(f"Last Name: {user.get('last_name', 'N/A')}")
    st.text(f"Email: {user.get('email', 'N/A')}")
    st.text(f"Role: {user.get('role', 'User')}")

    st.divider()

    st.subheader("🔒 Change Password")
    with st.form("change_password_form"):
        old_password = st.text_input("Old Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_new_password = st.text_input("Confirm New Password", type="password")
        submit = st.form_submit_button("Update Password")

        if submit:
            # Recheck in database (safer)
            db_user = db["users"].find_one({"email": user["email"]})
            if not db_user or not bcrypt.checkpw(old_password.encode(), db_user["password"]):
                st.error("❌ Old password incorrect.")
            elif new_password != confirm_new_password:
                st.error("❌ New passwords do not match.")
            else:
                hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                db["users"].update_one({"email": user["email"]}, {"$set": {"password": hashed_pw}})
                st.success("✅ Password updated successfully!")
