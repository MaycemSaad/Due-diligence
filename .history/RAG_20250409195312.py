import streamlit as st
from datetime import datetime
from pymongo import MongoClient
from vector_store import SemanticSearch
import ollama
import os
import pdfplumber
import faiss
from io import BytesIO
from sentence_transformers import SentenceTransformer

# --- Environnement GPU pour Ollama
os.environ["OLLAMA_NUM_GPU_LAYERS"] = "100"

# --- Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
conversations = db["conversations"]
qa_collection = db["qa"]

# --- Modèles
MODEL_NAME = "mistral:latest"
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# --- Index FAISS (pré-chargé)
searcher = SemanticSearch()
searcher.load_index()

# --- Configuration UI
st.set_page_config(page_title="RAG Due Diligence Chatbot", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #111; color: white; }
        .chat-message { padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
        .user-message { background-color: #2d2d2d; margin-left: 30%; }
        .bot-message { background-color: #1e1e1e; margin-right: 30%; }
        .stTextInput textarea { color: white !important; }
    </style>
""", unsafe_allow_html=True)

# --- State initial
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_convo" not in st.session_state:
    st.session_state.current_convo = None
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
if "custom_index" not in st.session_state:
    st.session_state.custom_index = None
    st.session_state.custom_chunks = []

# --- Sidebar : historique
with st.sidebar:
    st.title("🧠 Conversations")
    if st.button("🆕 New Chat"):
        st.session_state.messages = []
        st.session_state.current_convo = None
        st.session_state.uploaded_file = None
        st.session_state.custom_index = None
        st.session_state.custom_chunks = []

    all_convos = list(conversations.find().sort("last_modified", -1))
    for convo in all_convos:
        if st.button(convo.get("title", "Untitled")):
            st.session_state.current_convo = convo["_id"]
            st.session_state.messages = convo["messages"]

# --- Affichage des messages
st.title("🤖 RAG Due Diligence Assistant")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Traitement PDF Upload (si demandé via /upload)
def handle_pdf_upload():
    uploaded_file = st.file_uploader("Upload your PDF", type=["pdf"], key="pdf_upload")
    if uploaded_file:
        text = ""
        with pdfplumber.open(BytesIO(uploaded_file.read())) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"

        paragraphs = [p for p in text.split("\n\n") if len(p.strip()) > 40]
        embeddings = EMBED_MODEL.encode(paragraphs)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(embeddings)

        st.session_state.uploaded_file = uploaded_file.name
        st.session_state.custom_index = index
        st.session_state.custom_chunks = paragraphs
        st.success(f"PDF {uploaded_file.name} uploaded and indexed.")
        st.rerun()

# --- Gestion du contexte (conserve ta logique d'origine)
def get_context(q):
    if st.session_state.custom_index:
        query_vec = EMBED_MODEL.encode([q])
        _, I = st.session_state.custom_index.search(query_vec, k=3)
        return "\n\n".join([st.session_state.custom_chunks[i] for i in I[0] if i < len(st.session_state.custom_chunks)])
    else:
        results = searcher.search(q, top_k=3)
        relevant = [r[0] for r in results if r[1] < 0.65]
        return "\n\n".join(relevant) if relevant else "No context found."

# --- Génération de prompt (inchangé)
def generate_prompt(question, context):
    return f"""
You are a helpful and knowledgeable assistant specializing in finance and digital asset due diligence.

[CONTEXT START]
{context}
[CONTEXT END]

Instructions:
- If the question is general (e.g., greetings, casual inquiry), respond naturally and politely.
- If the question relates to digital assets, finance, compliance, or due diligence, answer precisely using only the context.
- If context is insufficient, clearly state it and guide the user.

Question: {question}

Answer:
"""

# --- Appel modèle
def generate_answer(prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 350},
        stream=False
    )
    return response['message']['content'].strip()

# --- Chat Input
if prompt := st.chat_input("Type your question or `/upload` to load a PDF..."):
    if prompt.lower().startswith("/upload"):
        handle_pdf_upload()
    else:
        # Afficher question
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Construire contexte + prompt
        context = get_context(prompt)
        full_prompt = generate_prompt(prompt, context)

        # Réponse IA
        with st.spinner("Generating answer..."):
            answer = generate_answer(full_prompt)

        # Afficher réponse
        st.session_state.messages.append({"role": "assistant", "content": answer})

        # Enregistrer QA
        qa_collection.insert_one({
            "question": prompt,
            "answer": answer,
            "timestamp": datetime.utcnow()
        })

        # Enregistrer conversation
        if st.session_state.current_convo:
            conversations.update_one(
                {"_id": st.session_state.current_convo},
                {"$set": {
                    "messages": st.session_state.messages,
                    "last_modified": datetime.utcnow()
                }}
            )
        else:
            new_convo = conversations.insert_one({
                "title": prompt[:50],
                "messages": st.session_state.messages,
                "created": datetime.utcnow(),
                "last_modified": datetime.utcnow()
            })
            st.session_state.current_convo = new_convo.inserted_id

        st.rerun()
