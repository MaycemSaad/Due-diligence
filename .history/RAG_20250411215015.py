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
import speech_recognition as sr
from gtts import gTTS
import tempfile
import pygame


# GPU acceleration for Ollama
os.environ["OLLAMA_NUM_GPU_LAYERS"] = "100"

# MongoDB Setup
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

# LLM Model
MODEL_NAME = "mistral:latest"
EMBED_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

# Load FAISS index
searcher = SemanticSearch()
searcher.load_index()

# Streamlit UI config
st.set_page_config(page_title="RAG Due Diligence Chatbot", layout="wide")



# --- Styles ---
st.markdown("""
    <style>
        .stApp { background-color: #121212; color: white; }
        .chat-container { padding: 10px; max-height: 70vh; overflow-y: auto; }
        .user-msg, .bot-msg { padding: 10px 15px; border-radius: 15px; margin: 10px 0; max-width: 70%; }
        .user-msg { background-color: #2f80ed; color: white; align-self: flex-end; margin-left: auto; }
        .bot-msg { background-color: #333; color: white; align-self: flex-start; margin-right: auto; }
        .chat-box { display: flex; flex-direction: column; }
        .bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; padding: 1rem; background-color: #111; }
    </style>
""", unsafe_allow_html=True)

# --- UI Header ---
st.markdown('<div class="title">🤖 RAG-Powered Due Diligence Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask about your documents. Powered by FAISS + Ollama</div>', unsafe_allow_html=True)

# --- Sidebar History ---
with st.sidebar:
    st.title("📜 Past Questions")
    past_qas = list(collection.find().sort("timestamp", -1).limit(5))
    selected_q = st.selectbox("Choose a previous question", [""] + [qa["question"] for qa in past_qas])

# --- File Upload ---
uploaded_file = st.file_uploader("📄 Upload a PDF to ask questions about it", type=["pdf"])
custom_index = None
custom_chunks = []

if uploaded_file:
    st.success(f"✅ Using uploaded file: {uploaded_file.name}")

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

    doc_text = extract_text_from_uploaded_pdf(uploaded_file)
    custom_index, custom_chunks = create_temp_faiss_index(doc_text)

# --- Input Section ---
question = st.text_input("Ask your question:", value=selected_q if selected_q else "")

col1, col2 = st.columns([1, 1])
with col1:
    get_answer = st.button("🔍 Get Answer")
with col2:
    regen_answer = st.button("♻️ Regenerate")

col3, col4 = st.columns([1, 1])
with col3:
    voice_input = st.button("🎤 Speak")

# --- Voice Input + Output Functions ---
def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Speak now...")
        audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Sorry, I could not understand your voice."
        except sr.RequestError:
            return "API unavailable. Please try again."

def speak_text(text):
    tts = gTTS(text=text, lang='en')

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        temp_path = fp.name

    tts.save(temp_path)

    # Jouer audio
    pygame.mixer.quit()
    pygame.mixer.init(frequency=52000)
    pygame.mixer.music.load(temp_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Arrêter et libérer le fichier avant suppression
    pygame.mixer.music.stop()
    pygame.mixer.quit()  # libère l'accès au fichier mp3

    try:
        os.remove(temp_path)
    except PermissionError:
        st.warning("⚠️ Could not delete temp audio file. It might still be in use.")


from_voice = False
# --- Use voice if clicked ---
if voice_input:
    transcribed_text = record_and_transcribe()
    st.success(f"🗣️ You said: {transcribed_text}")
    question = transcribed_text
    get_answer = True
    from_voice = True  # 👈 active la lecture audio

# --- Prompt & Answer Functions ---
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
    if not custom_index:
        return ""
    query_vec = EMBED_MODEL.encode([q])
    D, I = custom_index.search(query_vec, k=3)
    return "\n\n".join([custom_chunks[i] for i in I[0] if i < len(custom_chunks)])

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

# --- Trigger QA ---
triggered = get_answer or regen_answer
if triggered:
    user_input = question.strip()
    if user_input:
        st.info("Retrieving context and generating response... ⏳")
        ctx = get_custom_context(user_input) if uploaded_file else get_context(user_input)
        prompt = generate_prompt(user_input, ctx)

        with st.spinner("Generating answer..."):
            final_answer = generate_answer(prompt)

        st.markdown('<div class="response-box">', unsafe_allow_html=True)
        st.subheader("📢 AI Response:")
        st.markdown(f'<div class="response-text">{final_answer}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if get_answer:
            save_to_db(user_input, final_answer)

        if from_voice:  # 👈 lire uniquement si vocal
            speak_text(final_answer)
    else:
        st.warning("Please enter a valid question.")
"