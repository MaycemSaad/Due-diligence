def Questions_bank():
    import os
    os.environ["OLLAMA_NUM_GPU_LAYERS"] = "100"

    import streamlit as st
    import faiss
    import numpy as np
    import re
    import datetime
    import PyPDF2
    import docx
    import pandas as pd
    import ollama
    from sentence_transformers import SentenceTransformer
    from pymongo import MongoClient

    # === Initialization ===
    model_name = "mistral:latest"

    # MongoDB connection
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence_db"]
    collection = db["questions"]

    # Load existing chunks
    try:
        existing_chunks = np.load("text_chunks.npy", allow_pickle=True).tolist()
    except:
        existing_chunks = []

    try:
        index = faiss.read_index("faiss_index.bin")
    except:
        index = None

    # Embedding model
    embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Session state
    if "new_chunks" not in st.session_state:
        st.session_state.new_chunks = []
    if "index" not in st.session_state:
        st.session_state.index = index
    if "questions_bank" not in st.session_state:
        st.session_state.questions_bank = {}

    st.markdown("""
    <style>
    .card {
        background-color: #1f2937;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
        color: white;
    }
    .category-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #3b82f6;
        margin-bottom: 1rem;
    }
    .question-text {
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }
    .search-bar input {
        width: 100%;
        padding: 0.7rem;
        border-radius: 8px;
        border: 1px solid #ccc;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

    def display_questions(questions_bank):
        st.markdown("<h2 style='text-align: center;'>📋 Question Bank</h2>", unsafe_allow_html=True)
        
        # Choix catégorie
        categories = ["All"] + list(questions_bank.keys())
        selected_category = st.selectbox("Filter by Category:", categories)

        # Search bar
        search_query = st.text_input("🔎 Search Questions...").lower()

        for category, questions in questions_bank.items():
            if selected_category != "All" and category != selected_category:
                continue

            filtered_questions = [q for q in questions if search_query in q.lower()]

            if filtered_questions:
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='category-title'>{category}</div>", unsafe_allow_html=True)
                for q in filtered_questions:
                    st.markdown(f"<div class='question-text'>📋 {q}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

    

    # === Helper Functions ===
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

    def generate_response(prompt):
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return response['message']['content']

    def generate_questions_from_document(context):
        prompt = (
            "You are a professional Due Diligence assistant.\n"
            "Your task is to generate exactly five short, precise due diligence questions for each category:\n"
            "- ESG\n- Compliance\n- Legal\n- Risque\n\n"
            "Strictly use this format without any explanation:\n"
            "ESG:\n- Question 1\n- Question 2\n- Question 3\n- Question 4\n- Question 5\n"
            "Compliance:\n- Question 1\n- Question 2\n- Question 3\n- Question 4\n- Question 5\n"
            "Legal:\n- Question 1\n- Question 2\n- Question 3\n- Question 4\n- Question 5\n"
            "Risque:\n- Question 1\n- Question 2\n- Question 3\n- Question 4\n- Question 5\n\n"
            f"Document:\n{context}\n\n"
            "⚠️ Output ONLY using the above format. No comments, no extra text."
        )
        return generate_response(prompt)

    def parse_and_classify_questions(response_text):
        question_bank = {"ESG": [], "Compliance": [], "Legal": [], "Risque": []}
        current_category = None
        lines = response_text.split("\n")

        for line in lines:
            line = line.strip()
            if line.lower().startswith("esg"):
                current_category = "ESG"
            elif line.lower().startswith("compliance"):
                current_category = "Compliance"
            elif line.lower().startswith("legal"):
                current_category = "Legal"
            elif line.lower().startswith("risque"):
                current_category = "Risque"
            elif line.startswith("-") and current_category:
                question_text = line.lstrip("-").strip()
                if question_text:
                    question_bank[current_category].append(question_text)

        return question_bank

    def generate_question_bank():
        if not st.session_state.new_chunks:
            return {}

        question_bank = {"ESG": [], "Compliance": [], "Legal": [], "Risque": []}

        for chunk in st.session_state.new_chunks[:1]:
            response = generate_questions_from_document(chunk)
            parsed_questions = parse_and_classify_questions(response)

            for category, questions in parsed_questions.items():
                for q in questions:
                    question_bank[category].append(q)
                    collection.insert_one({
                        "category": category,
                        "question": q,
                        "created_at": datetime.datetime.utcnow()
                    })

        return question_bank

    def verify_all_documents():
        if not st.session_state.new_chunks:
            return {}

        issues = {"ESG": [], "Compliance": [], "Legal": []}

        for chunk in st.session_state.new_chunks[:1]:
            prompt = (
                "Review the following document. List 2 issues for ESG, Compliance, and Legal separately.\n\n"
                f"{chunk}\n"
            )
            decoded = generate_response(prompt)
            parsed_issues = parse_and_classify_questions(decoded)

            for category, issues_list in parsed_issues.items():
                issues[category].extend(issues_list)

        return issues

    def download_csv(data):
        df = pd.DataFrame([(cat, q) for cat, qs in data.items() for q in qs], columns=["Category", "Question"])
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Questions as CSV",
            data=csv,
            file_name='questions_bank.csv',
            mime='text/csv',
        )

    # === UI ===
    st.title("📚 Due Diligence Chatbot")

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
            st.session_state.index = create_faiss_index(st.session_state.new_chunks)
            st.success(f"✅ {len(uploaded_files)} documents processed successfully.")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        generate = st.button("🧠 Generate Question Bank")
    with col2:
        verify = st.button("🛡️ Verify Documents")
    with col3:
        reset = st.button("♻️ Reset Session")

if generate:
    with st.spinner("Generating questions..."):
        results = generate_question_bank()
        st.session_state.questions_bank = results

        if results:
            st.success("✅ Questions generated successfully!")
            display_questions(results)  # <=== appel de la fonction moderne
            download_csv(results)
        else:
            st.warning("⚠️ No questions generated. Check your document or model response.")


    if verify:
        with st.spinner("Verifying documents..."):
            verifications = verify_all_documents()
            st.json(verifications)

    if reset:
        st.session_state.new_chunks = []
        st.session_state.index = None
        st.session_state.questions_bank = {}
        st.success("Session reset successfully.")
