import streamlit as st
import bcrypt
from pymongo import MongoClient
import re
from datetime import datetime, timezone
from PIL import Image



client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
users_col = db["users"]

# ---------- UTILS ----------
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed)

def is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

def is_valid_name(name):
    return re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\-'\s]+$", name)

# ---------- STYLES GLOBAUX ----------
def inject_form_style():
    st.markdown("""
        <style>
            .auth-container {
                background-color: transparent;
                padding: 2.5rem;
                border-radius: 16px;
                max-width: 500px;
                margin: 4rem auto;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
            }
            .auth-title {
                font-size: 2rem;
                font-weight: bold;
                text-align: center;
                color: #2E3B4E;
                margin-bottom: 1.5rem;
            }
            .stTextInput > div > div > input {
                font-size: 1rem;
                padding: 10px;
            }
            .stButton > button {
                font-size: 1rem;
                background-color: #0066ff;
                color: white;
                border-radius: 8px;
                padding: 0.7rem 1.2rem;
                width: 100%;
            }
            .stButton > button:hover {
                background-color: #004bcc;
            }
            .auth-footer {
                text-align: center;
                margin-top: 1rem;
                color: gray;
                font-size: 0.9rem;
            }
            .login-header {
                text-align: center;
                margin-bottom: 2rem;
                animation: fadeIn 1.2s ease-in;
            }

            .login-heading {
                font-size: 1.5rem;
                font-weight: bold;
                margin: 0;
                color: var(--text-color, #2E3B4E);
            }

            .login-subtext {
                font-size: 0.95rem;
                color: gray;
                margin-top: 0.4rem;
            }

            /* Optional dark/light support */
            @media (prefers-color-scheme: dark) {
                .login-heading {
                    color: #f0f0f0;
                }
                .login-subtext {
                    color: #aaa;
                }
            }

            /* Optional animation */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }

        </style>
    """, unsafe_allow_html=True)

# ---------- PAGE SIGNUP ----------
def show_signup_page():
    inject_form_style()

    # Bloc logo + titres dans le même container HTML + image encodée base64
    import base64
    from io import BytesIO

    import base64
    from io import BytesIO

    def get_base64_image(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
        encoded = base64.b64encode(data).decode()
        return f"data:image/png;base64,{encoded}"

    try:
        logo_base64 = get_base64_image("TawaCheck.png")
        st.markdown(f"""
            <div class="login-header">
                <img src="{logo_base64}" width="220" style="margin-bottom: 1.5rem;" />
                <h1 class="login-heading">Due Diligence AI</h1>
                <p class="login-subtext">Secure access to your intelligent audit platform</p>
            </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Logo TawaCheck.png introuvable.")


    
    st.markdown('<div class="auth-title">📝 Créer un compte</div>', unsafe_allow_html=True)

    # 🔐 Champs du formulaire
    first_name = st.text_input("👤 Prénom")
    last_name = st.text_input("👤 Nom de famille")
    email = st.text_input("📧 Email")
    password = st.text_input("🔒 Mot de passe", type="password")
    confirm = st.text_input("🔒 Confirmer le mot de passe", type="password")

    # ✅ Logique d'inscription
    if st.button("Créer mon compte"):
        if not first_name or not last_name or not email or not password or not confirm:
            st.error("❌ Tous les champs sont obligatoires.")
        elif not is_valid_name(first_name):
            st.error("❌ Le prénom ne doit contenir que des lettres.")
        elif not is_valid_name(last_name):
            st.error("❌ Le nom de famille ne doit contenir que des lettres.")
        elif not is_valid_email(email):
            st.error("❌ Format d'email invalide.")
        elif password != confirm:
            st.error("❌ Les mots de passe ne correspondent pas.")
        elif len(password) < 8:
            st.error("❌ Le mot de passe doit contenir au moins 8 caractères.")
        elif users_col.find_one({"email": email}):
            st.warning("⚠️ Un compte existe déjà avec cet email.")
        else:
            hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            users_col.insert_one({
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": hashed_pw,
                "role": "user" , # ➡️ Ajouter ici
                "created_at": datetime.now(timezone.utc)  
            })
            st.success(f"✅ Compte créé avec succès, {first_name} !")
            st.session_state.page = "login"
            st.rerun()

    # 🔁 Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔐 Déjà inscrit ? Se connecter"):
            st.session_state.page = "login"
            st.rerun()
    with col2:
        if st.button("🏠 Accueil"):
            st.session_state.page = "home"
            st.rerun()

    # ✅ Fermer .auth-container
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- PAGE LOGIN ----------
def show_login_page():
    inject_form_style()
    
    # Start container
    st.markdown("""
        <div class="auth-container">
            <div class="login-header">
                <img src="https://cdn-icons-png.flaticon.com/512/5956/5956597.png" alt="logo" width="80" style="margin-bottom: 1rem;"/>
                <h1 class="login-heading">Due Diligence AI</h1>
                <p class="login-subtext">Secure access to your intelligent audit platform</p>
            </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="auth-title">🔐 Connexion sécurisée</div>', unsafe_allow_html=True)

    email = st.text_input("📧 Email", key="login_email")
    password = st.text_input("🔒 Mot de passe", type="password", key="login_password")

    # ✅ Close the container BEFORE widgets like button/columns
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Se connecter"):
        user = users_col.find_one({"email": email})
        if user and verify_password(password, user["password"]):
            st.session_state.user = {
                "email": email,
                "role": user.get("role", "user")
            }

            # ✅ Redirect based on role
            if st.session_state.user["role"] == "admin":
                st.success("✅ Connexion réussie. Redirection vers le panneau Admin...")
                st.session_state.page = "admin_dashboard"  # ➡️ you must manage this page
                st.rerun()
            else:
                st.success("✅ Connexion réussie. Redirection vers l'application utilisateur...")
                st.session_state.page = "user_app"  # ➡️ you must manage this page too
                st.rerun()

        else:
            st.error("❌ Email ou mot de passe incorrect")


    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Créer un compte"):
            st.session_state.page = "signup"
            st.rerun()
    with col2:
        if st.button("🏠 Accueil"):
            st.session_state.page = "home"
            st.rerun()

    st.markdown('<div class="auth-footer">Mot de passe oublié ? Fonction à venir 💡</div>', unsafe_allow_html=True)
