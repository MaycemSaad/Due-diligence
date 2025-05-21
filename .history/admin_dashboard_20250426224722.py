import streamlit as st
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone

def show_admin_dashboard():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]

    st.title("👑 User Management Panel")

    # CSS Styling PRO
    st.markdown("""
    <style>
    .user-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background-color: #1f1f1f;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .user-info {
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .user-email {
        color: #4fa3f7;
        font-weight: bold;
    }
    .user-role {
        background-color: #333;
        padding: 5px 10px;
        border-radius: 10px;
        font-size: 12px;
        color: #aaa;
    }
    .action-btn {
        background-color: #444;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 12px;
        margin-right: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .action-btn:hover {
        background-color: #0066ff;
    }
    .danger-btn {
        background-color: #b00020;
    }
    .danger-btn:hover {
        background-color: #ff1744;
    }
    </style>
    """, unsafe_allow_html=True)

    # Ajouter utilisateur
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

    # Recherche
    st.subheader("🔎 Search Users")
    search_query = st.text_input("Search by First Name, Last Name, or Email").lower()

    users = list(users_col.find({}, {"password": 0}))

    if not users:
        st.warning("No users found.")
        return

    if search_query:
        users = [
            u for u in users if
            search_query in u.get('first_name', '').lower() or
            search_query in u.get('last_name', '').lower() or
            search_query in u.get('email', '').lower()
        ]

    users_per_page = 8
    total_pages = (len(users) - 1) // users_per_page + 1

    if "admin_page" not in st.session_state:
        st.session_state.admin_page = 1

    start_idx = (st.session_state.admin_page - 1) * users_per_page
    end_idx = start_idx + users_per_page

    # Liste propre
    st.subheader("👥 Manage Users")
    for user in users[start_idx:end_idx]:
        st.markdown(f"""
        <div class="user-row">
            <div class="user-info">
                <span>👤 {user.get('first_name', '')} {user.get('last_name', '')}</span>
                <span class="user-email">{user['email']}</span>
                <span class="user-role">{user.get('role', 'user')}</span>
            </div>
            <div>
                <form method="POST">
                    <button class="action-btn" type="submit" name="action" value="promote_{user['_id']}">🚀 Promote</button>
                    <button class="action-btn" type="submit" name="action" value="demote_{user['_id']}">⬇️ Demote</button>
                    <button class="action-btn danger-btn" type="submit" name="action" value="delete_{user['_id']}">🗑️ Delete</button>
                </form>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Actions
        action = st.session_state.get('action')
        if action == f"promote_{user['_id']}":
            users_col.update_one({"_id": user["_id"]}, {"$set": {"role": "admin"}})
            st.success(f"✅ Promoted {user['email']} to Admin.")
            st.session_state.pop('action')
            st.experimental_rerun()
        elif action == f"demote_{user['_id']}":
            users_col.update_one({"_id": user["_id"]}, {"$set": {"role": "user"}})
            st.warning(f"⬇️ Demoted {user['email']} to User.")
            st.session_state.pop('action')
            st.experimental_rerun()
        elif action == f"delete_{user['_id']}":
            users_col.delete_one({"_id": user["_id"]})
            st.error(f"🗑️ Deleted {user['email']}.")
            st.session_state.pop('action')
            st.experimental_rerun()

    # Pagination
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous"):
            if st.session_state.admin_page > 1:
                st.session_state.admin_page -= 1
                st.experimental_rerun()
    with col2:
        st.markdown(f"<p style='text-align:center;'>Page {st.session_state.admin_page} / {total_pages}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("➡️ Next"):
            if st.session_state.admin_page < total_pages:
                st.session_state.admin_page += 1
                st.experimental_rerun()

show_admin_dashboard()