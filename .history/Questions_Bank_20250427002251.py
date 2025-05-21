def Questions_bank():
    import os
    os.environ["OLLAMA_NUM_GPU_LAYERS"] = "100"  # ✅ Force l'utilisation GPU pour 100 couches

    import streamlit as st
    import faiss
    import numpy as np
    import json
    import re
    import datetime
    import io
    import base64
    import PyPDF2
    import docx
    import ollama  # ✅ Ajout direct de ollama
    from sentence_transformers import SentenceTransformer
    from pymongo import MongoClient

    # === Initialization ===
    theme_color = "#00eaff"
    model_name = "mistral:latest"  # ✅ Ton modèle utilisé dans Ollama

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
        "You are a professional Due Diligence assistant specialized in ESG, Compliance, and Legal audits.\n"
        "Your task is to read the following document and generate exactly two (2) specific, clear, and realistic questions for each of the three categories (ESG, Compliance, Legal).\n\n"
        "Document content:\n"
        f"{context}\n\n"
        "Output format strictly:\n"
        "ESG:\n- [Question 1]\n- [Question 2]\nCompliance:\n- [Question 1]\n- [Question 2]\nLegal:\n- [Question 1]\n- [Question 2]\n"
        "Only output the questions. Do not add explanations."
    )
    return generate_response(prompt)

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
        return generate_response(prompt).strip()

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
            decoded = generate_response(prompt)

            issues_parsed = parse_and_classify_questions(decoded)
            for category, detected in issues_parsed.items():
                issues[category].extend(detected)

        return issues

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

            # Rebuild FAISS index
            st.session_state.index = create_faiss_index(st.session_state.new_chunks)
            st.success(f"✅ {len(uploaded_files)} documents processed successfully.")

    st.divider()

    # Buttons
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
