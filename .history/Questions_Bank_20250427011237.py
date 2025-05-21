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
            "Your task is to generate exactly two short, precise, due diligence questions for each of these categories:\n"
            "- ESG\n- Compliance\n- Legal\n"
            "Use strictly this format:\n"
            "ESG:\n- [Question 1]\n- [Question 2]\nCompliance:\n- [Question 1]\n- [Question 2]\nLegal:\n- [Question 1]\n- [Question 2]\n\n"
            f"Document content:\n{context}\n\n"
            "⚠️ Only output in this format. No comments, no titles."
        )
        return generate_response(prompt)

    def parse_and_classify_questions(response_text):
        question_bank = {"ESG": [], "Compliance": [], "Legal": []}
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
            elif line.startswith("- [") and current_category:
                question = re.search(r"\[(.*?)\]", line)
                if question:
                    question_text = question.group(1).strip()
                    question_bank[current_category].append(question_text)
        return question_bank

    def generate_question_bank():
        if not st.session_state.new_chunks:
            return {}

        question_bank = {"ESG": [], "Compliance": [], "Legal": []}

        for chunk in st.session_state.new_chunks[:1]:
            response = generate_questions_from_document(chunk)
            st.write("🧠 Raw model output:", response)  # Debugging: see the raw response
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

            st.success("✅ Questions generated successfully!")
            for category, questions in results.items():
                if questions:
                    with st.expander(f"📂 {category} ({len(questions)} questions)"):
                        for q in questions:
                            st.markdown(f"📋 **{q}**")
                else:
                    st.info(f"No questions generated for {category}.")

    if verify:
        with st.spinner("Verifying documents..."):
            verifications = verify_all_documents()
            st.json(verifications)

    if reset:
        st.session_state.new_chunks = []
        st.session_state.index = None
        st.success("Session reset successfully.")
