import streamlit as st
from pymongo import MongoClient

def show_admin_dashboard():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]

    st.title("👑 Admin Dashboard - Manage Users")

    users = list(users_col.find({}, {"password": 0}))  # Masquer les mots de passe

    if not users:
        st.warning("No users found.")
        return

    st.markdown("""
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #ddd;
        }
    </style>
    """, unsafe_allow_html=True)

    # 🧹 Tableau
    for user in users:
        col1, col2, col3, col4 = st.columns([3, 3, 2, 2])

        with col1:
            st.markdown(f"**👤 {user.get('first_name', '')} {user.get('last_name', '')}**")
        with col2:
            st.markdown(f"📧 {user['email']}")
        with col3:
            current_role = user.get('role', 'user')
            new_role = st.selectbox(
                "Role",
                options=["user", "admin"],
                index=0 if current_role == "user" else 1,
                key=f"role_select_{user['_id']}"
            )
        with col4:
            if st.button("💾 Save", key=f"save_button_{user['_id']}"):
                if new_role != current_role:
                    users_col.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"role": new_role}}
                    )
                    st.success(f"✅ Role updated to '{new_role}' for {user['email']}")
                    st.experimental_rerun()  # Refresh dashboard immediately


show_admin_dashboard()