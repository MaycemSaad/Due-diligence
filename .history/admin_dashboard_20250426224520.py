import streamlit as st
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone

def show_admin_dashboard():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]

    st.title("👑 Admin Dashboard - User Management")

    # ================== Formulaire d'ajout utilisateur ==================
    with st.expander("➕ Add New User"):
        with st.form("create_user_form", clear_on_submit=True):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["user", "admin"])
            submit_create = st.form_submit_button("Create User")

        if submit_create:
            if not all([first_name, last_name, email, password]):
                st.error("❌ All fields are required.")
            elif users_col.find_one({"email": email}):
                st.error("❌ Email already exists.")
            else:
                hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
                users_col.insert_one({
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "password": hashed_pw,
                    "role": role,
                    "created_at": datetime.now(timezone.utc)
                })
                st.success(f"✅ User {first_name} created successfully.")
                st.experimental_rerun()

    st.divider()

    # ================== Barre de recherche ==================
    st.subheader("🔎 Search Users")
    search_query = st.text_input("Search by First Name, Last Name, or Email").lower()

    # ================== Pagination ==================
    users = list(users_col.find({}, {"password": 0}))
    if not users:
        st.warning("No users found.")
        return

    # Filtrer
    if search_query:
        users = [
            u for u in users if
            search_query in u.get('first_name', '').lower() or
            search_query in u.get('last_name', '').lower() or
            search_query in u.get('email', '').lower()
        ]

    users_per_page = 10
    total_pages = (len(users) - 1) // users_per_page + 1

    if "admin_page" not in st.session_state:
        st.session_state.admin_page = 1

    start_idx = (st.session_state.admin_page - 1) * users_per_page
    end_idx = start_idx + users_per_page

    # ================== Tableau avec promote/demote ==================
    st.subheader("👥 Manage Users")
    for user in users[start_idx:end_idx]:
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1])

        with col1:
            st.markdown(f"👤 **{user.get('first_name', '')} {user.get('last_name', '')}**")
        with col2:
            st.markdown(f"📧 {user['email']}")
        with col3:
            st.markdown(f"🏷️ `{user.get('role', 'user')}`")
        with col4:
            if user.get('role') == "user":
                if st.button("🚀 Promote", key=f"promote_{user['_id']}"):
                    users_col.update_one({"_id": user["_id"]}, {"$set": {"role": "admin"}})
                    st.success(f"✅ Promoted {user['email']} to Admin.")
                    st.experimental_rerun()
            else:
                if st.button("⬇️ Demote", key=f"demote_{user['_id']}"):
                    users_col.update_one({"_id": user["_id"]}, {"$set": {"role": "user"}})
                    st.warning(f"⚠️ Demoted {user['email']} to User.")
                    st.experimental_rerun()
        with col5:
            if st.button("🗑️ Delete", key=f"delete_{user['_id']}"):
                users_col.delete_one({"_id": user["_id"]})
                st.error(f"🗑️ Deleted {user['email']}.")
                st.experimental_rerun()

    # ================== Contrôle de pagination ==================
    st.divider()
    col_prev, col_page, col_next = st.columns([1, 2, 1])

    with col_prev:
        if st.button("⬅️ Previous"):
            if st.session_state.admin_page > 1:
                st.session_state.admin_page -= 1
                st.experimental_rerun()
    with col_page:
        st.markdown(f"**Page {st.session_state.admin_page} / {total_pages}**", unsafe_allow_html=True)
    with col_next:
        if st.button("➡️ Next"):
            if st.session_state.admin_page < total_pages:
                st.session_state.admin_page += 1
                st.experimental_rerun()

show_admin_dashboard()
