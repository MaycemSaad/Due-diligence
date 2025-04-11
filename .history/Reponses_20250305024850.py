import streamlit as st
import ollama
import glob
import os
from pymongo import MongoClient
from datetime import datetime

# ⚡ Force GPU Acceleration for Ollama (if available)
os.environ["OLLAMA_NUM_GPU_LAYERS"] = "100"

# 🛠️ Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

# 🤖 Model Selection (Default: Mistral 7B)
MODEL_NAME = "mistral:latest"

# 📜 Load Cleaned PDF Texts
cleaned_texts_dir = "cleaned_texts"
cleaned_texts = {}

for txt_file in glob.glob(f"{cleaned_texts_dir}/*.txt"):
    with open(txt_file, "r", encoding="utf-8") as f:
        cleaned_texts[os.path.basename(txt_file)] = f.read()

def find_relevant_context(question, texts, max_words=250):
    """🔍 Selects the most relevant text segments for the question."""
    relevant_parts = []
    question_words = set(question.lower().split())

    for filename, content in texts.items():
        words = content.lower().split()
        match_count = sum(1 for word in words if word in question_words)

        if match_count > 2:
            relevant_parts.append(content[:max_words])

    if not relevant_parts and texts:
        return list(texts.values())[0][:max_words]

    return " ".join(relevant_parts)

def generate_answer_with_ollama(question, context):
    """🤖 Generates an AI-powered answer."""
    prompt = f"""
    You are an expert in digital finance and due diligence. 
    Answer the question strictly based on the provided context.

    [CONTEXT]:
    {context}

    [QUESTION]:
    {question}

    [INSTRUCTIONS]:
    - Be precise and factual.
    - Do not provide information that is not present in the context.
    - Structure your answer in a clear paragraph.

    [ANSWER]:
    """

    max_tokens = min(120, len(question.split()) * 5)  

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": max_tokens}  
    )

    return response["message"]["content"].strip()

def save_to_mongodb(question, answer):
    """💾 Saves Q&A in MongoDB."""
    with MongoClient("mongodb://localhost:27017/") as client:
        db = client["due_diligence"]
        collection = db["qa"]
        entry = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.utcnow()
        }
        collection.insert_one(entry)

def get_previous_questions(limit=5):
    """🔄 Fetch last 5 questions from MongoDB."""
    return list(collection.find().sort("timestamp", -1).limit(limit))

# 🎨 Streamlit UI
st.set_page_config(page_title="AI Due Diligence Chatbot", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            background-color: #1E1E1E;
            color: white;
        }
        .title {
            font-size: 48px;
            font-weight: bold;
            color: #FFD700;
            text-align: center;
        }
        .sub-title {
            font-size: 22px;
            text-align: center;
            color: #A9A9A9;
        }
        .response-box {
            background-color: #2C2F33;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 4px 4px 15px rgba(255, 215, 0, 0.5);
        }
        .response-text {
            font-size: 20px;
            color: #FFFFFF;
            font-weight: normal;
        }
        .stButton>button {
            font-size: 18px !important;
            border-radius: 12px;
            padding: 12px 25px;
            background-color: #FFD700 !important;
            color: black !important;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🤖 AI Due Diligence Chatbot</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Ask your finance or due diligence questions and get AI-powered answers instantly!</p>', unsafe_allow_html=True)

# 📜 Sidebar for Past Questions
with st.sidebar:
    st.title("📜 Past Questions")
    previous_qas = get_previous_questions()
    selected_past_question = None

    if previous_qas:
        selected_past_question = st.selectbox("🔄 Select a past question:", 
                                              [qa['question'] for qa in previous_qas])
    st.write("📊 **Analytics**")
    st.write("Total Questions Asked: ", collection.count_documents({}))

# 📝 User Input Field
question = st.text_input("💬 Type your question:", value=selected_past_question if selected_past_question else "")

# 📥 File Upload Feature
txt_file = st.file_uploader("📂 Upload a text file to analyze", type=["txt"])

if txt_file is not None:
    file_content = txt_file.read().decode("utf-8")
    st.text_area("📜 File Content", file_content, height=200)

# 🔘 Buttons Section
col1, col2 = st.columns([1, 1])
with col1:
    get_answer_btn = st.button("🔍 Get Answer", key="get_answer")
with col2:
    regenerate_answer_btn = st.button("♻️ Regenerate Answer", key="regenerate_answer")

# 📢 Answer Processing & Display
if get_answer_btn or regenerate_answer_btn:
    if question.strip():
        context = find_relevant_context(question, cleaned_texts)
        
        with st.spinner("💡 AI is generating your answer..."):
            answer = generate_answer_with_ollama(question, context)
        
        st.markdown('<div class="response-box">', unsafe_allow_html=True)
        st.subheader("📢 AI Response:")
        st.markdown(f'<p class="response-text">{answer}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if get_answer_btn:
            save_to_mongodb(question, answer)
    else:
        st.warning("⚠️ Please enter a valid question.")
