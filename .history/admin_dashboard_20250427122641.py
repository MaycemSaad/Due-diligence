import streamlit as st
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone
from Questions_Bank import Questions_bank

def show_admin_dashboard():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]

    # === Global CSS Professional Mode ===
    st.markdown("""
    <style>
    /* General Background + Typography */
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        background-color: #0f172a;
        color: #e2e8f0;
    }
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
        padding: 2rem 1rem;
    }
    section[data-testid="stSidebar"] .block-container {
        padding: 0;
    }
    /* Sidebar Title */
    .sidebar-title {
        font-size: 24px;
        color: #38bdf8;
        text-align: center;
        margin-bottom: 1rem;
    }
    /* Sidebar Radio Buttons */
    [role="radiogroup"] > label {
        background-color: #1e293b;
        color: #cbd5e1;
        margin-bottom: 10px;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        transition: 0.3s;
    }
    [role="radiogroup"] > label:hover {
        background-color: #0ea5e9;
        color: white;
        transform: scale(1.05);
    }
    /* Headers */
    h1, h2, h3 {
        color: #38bdf8;
    }
    /* User Card */
    .user-card {
        background: #1e293b;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.2);
        transition: 0.3s ease;
    }
    .user-card:hover {
        background: #273549;
        transform: scale(1.02);
    }
    /* Avatar */
    .avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background-color: #0ea5e9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 18px;
        color: white;
        margin-right: 10px;
    }
    /* Buttons */
    button {
        border-radius: 12px !important;
        font-weight: bold !important;
        background: linear-gradient(135deg, #38bdf8, #0ea5e9) !important;
        color: white !important;
        transition: 0.3s ease;
    }
    button:hover {
        transform: translateY(-3px);
        box-shadow: 0px 8px 16px rgba(56,189,248,0.4);
    }
    /* Toast Notification */
    .toast {
        position: fixed;
        top: 20px;
        right: 20px;
        background: #38bdf8;
        padding: 10px 20px;
        border-radius: 12px;
        color: white;
        font-weight: bold;
        box-shadow: 0px 4px 20px rgba(0,0,0,0.2);
        z-index: 9999;
    }
    </style>
    """, unsafe_allow_html=True)

    # === Sidebar ===
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Streamlit_logo_vertical_primary_light.svg/512px-Streamlit_logo_vertical_primary_light.svg.png", width=150)
    st.markdown('<div class="sidebar-title">Due Diligence AI</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Manage Users", "Chatbot"],
        index=0,
        key="page_radio"
    )
    
    # Beautiful separation line
    st.markdown('<hr style="border: 1px solid #334155;">', unsafe_allow_html=True)
    if page == "👥 Manage Users":
        st.title("👥 User Management Panel")

        # ➕ Add User
        with st.expander("➕ Add New User", expanded=False):
            with st.form(key="create_user_form", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("First Name")
                    email = st.text_input("Email")
                with col2:
                    last_name = st.text_input("Last Name")
                    password = st.text_input("Password", type="password")

                role = st.selectbox("Role", ["user", "admin"])
                submit_create = st.form_submit_button("Create User 🚀")

            if submit_create:
                with st.spinner("Creating user..."):
                    if not all([first_name, last_name, email, password]):
                        st.error("❌ Please fill all fields.")
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
                        st.success(f"✅ {first_name} added successfully!")
                        st.markdown('<div class="toast">✅ User Created!</div>', unsafe_allow_html=True)
                        st.rerun()

        st.divider()

        # 🔎 Search Users
        st.subheader("🔎 Search Users")
        search_query = st.text_input("Search by Name or Email").lower()
        users = list(users_col.find({}, {"password": 0}))

        if not users:
            st.warning("⚠️ No users found.")
            return

        if search_query:
            users = [
                u for u in users if
                search_query in u.get('first_name', '').lower() or
                search_query in u.get('last_name', '').lower() or
                search_query in u.get('email', '').lower()
            ]

        users_per_page = 6
        total_pages = (len(users) - 1) // users_per_page + 1

        if "admin_page" not in st.session_state:
            st.session_state.admin_page = 1

        start_idx = (st.session_state.admin_page - 1) * users_per_page
        end_idx = start_idx + users_per_page

        # Display Users
        st.subheader("👤 Users List")
        for user in users[start_idx:end_idx]:
            initials = (user.get('first_name', '')[:1] + user.get('last_name', '')[:1]).upper()
            with st.container():
                st.markdown(f"""
                    <div class="user-card" style="display: flex; align-items: center;">
                        <div class="avatar">{initials}</div>
                        <div>
                            <div class="user-name">{user.get('first_name', '')} {user.get('last_name', '')}</div>
                            <div class="user-email">{user['email']}</div>
                            <div class="badge">{user.get('role', 'user').capitalize()}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                with st.form(key=f"user_edit_form_{str(user['_id'])}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_role = st.selectbox(
                            "Change Role",
                            options=["user", "admin"],
                            index=0 if user.get("role") == "user" else 1,
                            key=f"role_select_{str(user['_id'])}"
                        )
                    with col2:
                        update_role = st.form_submit_button("💾 Update Role")
                        delete_user = st.form_submit_button("🗑️ Delete User")

                    if update_role:
                        with st.spinner("Updating role..."):
                            users_col.update_one({"_id": user["_id"]}, {"$set": {"role": new_role}})
                            st.success(f"✅ {user['email']}'s role updated.")
                            st.markdown('<div class="toast">✅ Role Updated!</div>', unsafe_allow_html=True)
                            st.rerun()

                    if delete_user:
                        with st.spinner("Deleting user..."):
                            users_col.delete_one({"_id": user["_id"]})
                            st.error(f"🗑️ {user['email']} deleted.")
                            st.markdown('<div class="toast" style="background:#f43f5e;">🗑️ User Deleted!</div>', unsafe_allow_html=True)
                            st.rerun()

        # ➡️ Pagination
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

    elif page == "🤖 Chatbot":
        st.title("🤖 Due Diligence Chatbot")
        Questions_bank()
