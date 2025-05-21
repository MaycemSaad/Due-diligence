import streamlit as st
from pymongo import MongoClient
import bcrypt
from datetime import datetime, timezone


def show_admin_dashboard():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    users_col = db["users"]

    # === Sidebar ===
    st.sidebar.title("📋 Admin Dashboard")
    page = st.sidebar.radio("Select Page", ["Manage Users", "Chatbot"])

    if page == "Manage Users":
        st.title("👑 User Management Panel")

        # --- Styling ---
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
        with st.expander("➕ Add New User", expanded=False):
            create_user_form = st.form(key="create_user_form", clear_on_submit=True)

            with create_user_form:
                first_name = st.text_input("First Name", key="first_name_input")
                last_name = st.text_input("Last Name", key="last_name_input")
                email = st.text_input("Email", key="email_input")
                password = st.text_input("Password", type="password", key="password_input")
                role = st.selectbox("Role", ["user", "admin"], key="role_select")
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
                    st.rerun()

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

                with st.form(key=f"user_edit_form_{str(user['_id'])}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        new_role = st.selectbox(
                            "Role",
                            options=["user", "admin"],
                            index=0 if user.get("role") == "user" else 1,
                            key=f"role_select_{str(user['_id'])}"
                        )

                    with col2:
                        update_role = st.form_submit_button("💾 Save Role")
                        delete_user = st.form_submit_button("🗑️ Delete User")

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

    elif page == "Chatbot":
        st.title("💬 Question Bank Chatbot")

        import faiss
        import numpy as np
        import json
        import re
        import datetime
        import io
        import base64
        import PyPDF2
        import docx
        import torch
        from sentence_transformers import SentenceTransformer
        from model import model, tokenizer

        # Setup MongoDB and embed model (you can move these imports up if you want cleaner)
        client = MongoClient("mongodb://localhost:27017/")
        db = client["due_diligence_db"]
        collection = db["questions"]

        theme_color = "#00eaff"
        
        try:
            existing_chunks = np.load("text_chunks.npy", allow_pickle=True).tolist()
        except:
            existing_chunks = []

        try:
            index = faiss.read_index("faiss_index.bin")
        except:
            index = None

        embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        if "new_chunks" not in st.session_state:
            st.session_state.new_chunks = []
        if "index" not in st.session_state:
            st.session_state.index = index

        # Helper functions
        def create_faiss_index(chunks):
            if not chunks:
                return None
            embeddings = embed_model.encode(chunks, convert_to_numpy=True)
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            faiss.write_index(index, "faiss_index.bin")
            return index

        def extract_text(file):
            if file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(file)
                return "".join([page.extract_text() for page in pdf_reader.pages])
            elif file.name.endswith('.docx'):
                doc = docx.Document(file)
                return "\n".join([para.text for para in doc.paragraphs])
            elif file.name.endswith('.txt'):
                return str(file.read(), "utf-8")
            else:
                return ""

        def chunk_text(text, chunk_size=500):
            words = text.split()
            return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

        def generate_questions_from_document(context):
            prompt = (
                "You are an expert in Due Diligence Reports. Based on the following document, generate specific questions for ESG, Compliance, and Legal.\n\n"
                f"Document: {context}\n"
                "ESG:\n- [Question 1]\n- [Question 2]\nCompliance:\n- [Question 1]\n- [Question 2]\nLegal:\n- [Question 1]\n- [Question 2]"
            )
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to("cuda" if torch.cuda.is_available() else "cpu")
            output = model.generate(**inputs, max_new_tokens=300)
            decoded = tokenizer.decode(output[0], skip_special_tokens=True)
            return decoded

        def parse_and_classify_questions(response_text):
            question_bank = {"ESG": [], "Compliance": [], "Legal": []}
            current_category = None
            lines = response_text.split("\n")

            for line in lines:
                line = line.strip()
                if line.startswith("ESG:"):
                    current_category = "ESG"
                elif line.startswith("Compliance:"):
                    current_category = "Compliance"
                elif line.startswith("Legal:"):
                    current_category = "Legal"
                elif line.startswith("- [") and current_category:
                    question = re.search(r"\[(.*?)\]", line)
                    if question:
                        question_text = question.group(1).strip()
                        question_bank[current_category].append(question_text)
            return question_bank

        def generate_question_bank():
            if not st.session_state.new_chunks:
                return "❌ No chunks uploaded yet."

            question_bank = {"ESG": [], "Compliance": [], "Legal": []}

            for chunk in st.session_state.new_chunks[:1]:  # Only process 1 chunk
                response = generate_questions_from_document(chunk)
                parsed_questions = parse_and_classify_questions(response)

                for category, questions in parsed_questions.items():
                    for q in questions:
                        answer = generate_answer_for_question(q)
                        question_bank[category].append({"question": q, "answer": answer})

                        # Save to MongoDB
                        collection.insert_one({
                            "category": category,
                            "question": q,
                            "answer": answer,
                            "created_at": datetime.datetime.utcnow()
                        })

            return question_bank

        def retrieve_text(query):
            chunks_to_use = st.session_state.new_chunks if st.session_state.new_chunks else existing_chunks
            if not st.session_state.index or not chunks_to_use:
                return ""

            query_embedding = embed_model.encode([query], convert_to_numpy=True)
            distances, indices = st.session_state.index.search(query_embedding, 3)
            valid_indices = [i for i in indices[0] if 0 <= i < len(chunks_to_use)]
            retrieved_chunks = [chunks_to_use[i] for i in valid_indices]
            return "\n".join(retrieved_chunks)

        def generate_answer_for_question(question):
            context = retrieve_text(question)
            if not context:
                return "No relevant context found."

            prompt = (
                f"Context: {context}\n\n"
                f"Question: {question}\n\n"
                "Answer the question based on the context. If context is missing, say 'No specific information available.'"
            )
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to("cuda" if torch.cuda.is_available() else "cpu")
            output = model.generate(**inputs, max_new_tokens=150)
            decoded = tokenizer.decode(output[0], skip_special_tokens=True).strip()
            return decoded

        def verify_all_documents():
            if not st.session_state.new_chunks:
                return "❌ No documents to verify."

            issues = {"ESG": [], "Compliance": [], "Legal": []}

            for chunk in st.session_state.new_chunks[:1]:
                prompt = (
                    "Review the document for ESG, Compliance, and Legal issues:\n\n"
                    f"Document: {chunk}\n"
                    "List 2-3 issues for each category."
                )
                inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048).to("cuda" if torch.cuda.is_available() else "cpu")
                output = model.generate(**inputs, max_new_tokens=300)
                decoded = tokenizer.decode(output[0], skip_special_tokens=True)
                issues_parsed = parse_and_classify_questions(decoded)
                for category, detected in issues_parsed.items():
                    issues[category].extend(detected)

            return issues

        # === UI Chatbot ===

        uploaded_files = st.file_uploader(
            "Upload your documents (PDF, DOCX, TXT)", 
            type=["pdf", "docx", "txt"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            with st.spinner("Processing uploaded files..."):
                for file in uploaded_files:
                    text = extract_text(file)
                    if text:
                        chunks = chunk_text(text)
                        st.session_state.new_chunks.extend(chunks)

                # Rebuild FAISS index
                st.session_state.index = create_faiss_index(st.session_state.new_chunks)
                st.success(f"✅ {len(uploaded_files)} documents processed successfully.")

        st.divider()

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            generate = st.button("🧠 Generate Question Bank")
        with col2:
            verify = st.button("🛡️ Verify Documents")
        with col3:
            reset = st.button("♻️ Reset Session")

        # Outputs
        if generate:
            with st.spinner("Generating questions and answers..."):
                results = generate_question_bank()
                st.json(results)

        if verify:
            with st.spinner("Verifying documents..."):
                verifications = verify_all_documents()
                st.json(verifications)

        if reset:
            st.session_state.new_chunks = []
            st.session_state.index = None
            st.success("Session reset successfully.")

