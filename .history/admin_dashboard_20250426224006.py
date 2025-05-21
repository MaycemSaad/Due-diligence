import streamlit as st
from pymongo import MongoClient

def show_admin_dashboard():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]

    st.title("👑 Admin Dashboard")

    users = list(users_col.find({}, {"password": 0}))  # Ne pas afficher le mot de passe

    if not users:
        st.warning("No users found.")
        return

    for user in users:
        st.markdown(f"""
        - 👤 **{user.get('first_name', '')} {user.get('last_name', '')}**  
        📧 {user['email']}  
        🏷️ Role: `{user.get('role', 'user')}`
        ---
        """)
