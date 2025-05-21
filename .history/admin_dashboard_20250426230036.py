import streamlit as st
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone

def show_admin_dashboard():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]

    st.title("👑 User Management Panel")

    # CSS Styling
    st.markdown("""
    <style>
    .user-row {
        background-color: #1f1f1f;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .user-name {
        color: white;
        font-weight: bold;
        font-size: 16px;
    }
    .user-email {
        color: #4fa3f7;
        font-size: 14px;
    }
    .user-role {
        background-color: #333;
        padding: 5px 10px;
        border-radius: 10px;
        font-size: 12px;
        color: #aaa;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ➕ Add New User
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

    # 🔎 Search
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

    # 👥 Manage Users
    st.subheader("👥 Manage Users")
    for user in users[start_idx:end_idx]:
        with st.container():
            st.markdown(f"""
            <div class="user-row">
            👤 <span class="user-name">{user.get('first_name', '')} {user.get('last_name', '')}</span><br>
            📧 <span class="user-email">{user['email']}</span><br>
            </div>
            """, unsafe_allow_html=True)

            # Form for editing role or deleting user
            with st.form(key=f"user_edit_form_{str(user['_id'])}"):
                col1, col2 = st.columns(2)

                # Select role
                with col1:
                    new_role = st.selectbox(
                        "Role",
                        options=["user", "admin"],
                        index=0 if user.get("role") == "user" else 1,
                        key=f"role_select_{str(user['_id'])}"
                    )

                # Buttons
                with col2:
                    update_role = st.form_submit_button("💾 Save Role")
                    delete_user = st.form_submit_button("🗑️ Delete User")

                # Action handling
                if update_role:
                    users_col.update_one({"_id": user["_id"]}, {"$set": {"role": new_role}})
                    st.success(f"✅ Updated {user['email']}'s role to {new_role}.")
                    st.rerun()

                if delete_user:
                    users_col.delete_one({"_id": user["_id"]})
                    st.error(f"🗑️ Deleted {user['email']}.")
                    st.rerun()

    # ➡️ Pagination
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous"):
            if st.session_state.admin_page > 1:
                st.session_state.admin_page -= 1
                st.rerun()
    with col2:
        st.markdown(f"<p style='text-align:center;'>Page {st.session_state.admin_page} / {total_pages}</p>", unsafe_allow_html=True)
    with col3:
        if st.button("➡️ Next"):
            if st.session_state.admin_page < total_pages:
                st.session_state.admin_page += 1
                st.rerun()

show_admin_dashboard()
