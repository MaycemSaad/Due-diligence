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

# Setup
os.environ["OLLAMA_NUM_GPU_LAYERS"] = "100"
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

MODEL_NAME = "mistral:latest"
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
searcher = SemanticSearch()
searcher.load_index()

st.set_page_config(page_title="RAG Due Diligence Assistant", layout="wide")

# --- Custom Styles (ChatGPT Look) ---
st.markdown("""
    <style>
        .stApp { background-color: #101010; color: white; }
        .chat-box { max-height: 70vh; overflow-y: auto; display: flex; flex-direction: column; padding: 1rem; }
        .user-msg, .bot-msg { max-width: 75%; padding: 12px 18px; border-radius: 18px; margin: 8px 0; }
        .user-msg { background-color: #1a73e8; color: white; align-self: flex-end; }
        .bot-msg { background-color: #2c2c2c; color: white; align-self: flex-start; }
        .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; background-color: #111; padding: 1rem; border-top: 1px solid #333; }
    </style>
""", unsafe_allow_html=True)

# Sidebar: Conversation History
with st.sidebar:
    st.title("🧠 History")
    past_qas = list(collection.find().sort("timestamp", -1).limit(10))
    for qa in past_qas:
        with st.expander(qa["question"][:60]):
            st.markdown(f"**A:** {qa['answer']}")

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PDF Upload Handler ---
def extract_text_from_uploaded_pdf(file) -> str:
    text = ""
    with pdfplumber.open(BytesIO(file.read())) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

def create_temp_faiss_index(text):
    paragraphs = [p for p in text.split("\n\n") if len(p.strip()) > 40]
    embeddings = EMBED_MODEL.encode(paragraphs)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index, paragraphs

# --- Display Chat History ---
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    role = msg["role"]
    content = msg["content"]
    class_name = "user-msg" if role == "user" else "bot-msg"
    st.markdown(f'<div class="{class_name}">{content}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- Prompt Input and File Upload ---
with st.container():
    st.markdown('<div class="bottom-bar">', unsafe_allow_html=True)
    col1, col2 = st.columns([7, 2])
    with col1:
        question = st.text_input("💬 Ask something...", key="input")
    with col2:
        uploaded_file = st.file_uploader("📎 Upload", type=["pdf"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

# --- If PDF Uploaded, Process and Store in Session ---
if uploaded_file and "custom_index" not in st.session_state:
    st.toast(f"📄 Using: {uploaded_file.name}")
    doc_text = extract_text_from_uploaded_pdf(uploaded_file)
    index, chunks = create_temp_faiss_index(doc_text)
    st.session_state.custom_index = index
    st.session_state.custom_chunks = chunks

# --- Your Prompt Logic (Preserved Exactly) ---
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

def get_context(q):
    results = searcher.search(q, top_k=3)
    relevant = [r[0] for r in results if r[1] < 0.65]
    return "\n\n".join(relevant) if relevant else "There is no technical or financial context found."

def get_custom_context(q):
    if "custom_index" not in st.session_state:
        return ""
    query_vec = EMBED_MODEL.encode([q])
    D, I = st.session_state.custom_index.search(query_vec, k=3)
    return "\n\n".join([st.session_state.custom_chunks[i] for i in I[0] if i < len(st.session_state.custom_chunks)])

def generate_answer(prompt):
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": 350},
        stream=False
    )
    return response['message']['content'].strip()

def save_to_db(q, a):
    collection.insert_one({"question": q, "answer": a, "timestamp": datetime.utcnow()})

# --- Handle Message Submission ---
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    context = get_custom_context(question) if uploaded_file else get_context(question)
    prompt = generate_prompt(question, context)

    with st.spinner("🧠 Thinking..."):
        answer = generate_answer(prompt)

    st.session_state.messages.append({"role": "bot", "content": answer})
    save_to_db(question, answer)
    st.session_state.input = ""  # clear prompt
