import streamlit as st
import ollama
import glob
import os
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

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
cleaned_texts = {txt_file: open(txt_file, "r", encoding="utf-8").read() for txt_file in glob.glob(f"{cleaned_texts_dir}/*.txt")}

def find_relevant_context(question, texts, max_words=250):
    """🔍 Selects the most relevant text segments for the question."""
    question_words = set(question.lower().split())
    relevant_parts = [content[:max_words] for content in texts.values() if sum(1 for word in content.lower().split() if word in question_words) > 2]
    return " ".join(relevant_parts) if relevant_parts else list(texts.values())[0][:max_words] if texts else ""

def generate_answer_with_ollama(question, context):
    """🤖 Generates an AI-powered answer."""
    prompt = f"""
    You are an expert in digital finance and due diligence. Answer the question strictly based on the provided context.
    
    [CONTEXT]: {context}
    
    [QUESTION]: {question}
    
    [INSTRUCTIONS]:
    - Be precise and factual.
    - Do not provide information that is not present in the context.
    - Structure your answer clearly.
    
    [ANSWER]:
    """
    
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": min(120, len(question.split()) * 5)}
    )
    return response["message"]["content"].strip()

def save_to_mongodb(question, answer):
    """💾 Saves Q&A in MongoDB."""
    collection.insert_one({"question": question, "answer": answer, "timestamp": datetime.utcnow()})

def get_previous_questions(limit=5):
    """🔄 Fetch last 5 questions from MongoDB."""
    return list(collection.find().sort("timestamp", -1).limit(limit))

# 🎨 Streamlit UI Redesign
st.set_page_config(page_title="AI Due Diligence Assistant", page_icon="🧠", layout="wide")

st.markdown("""
    <style>
        body { font-family: 'Roboto', sans-serif; }
        .stApp { background-color: #F4F4F4; color: #333; }
        .header { text-align: center; padding: 20px; background: linear-gradient(90deg, #4A90E2, #145DA0); color: white; border-radius: 10px; }
        .question-box { background: white; padding: 15px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); }
        .response-box { background: #E3F2FD; padding: 15px; border-radius: 8px; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1); }
        .stButton>button { background-color: #145DA0 !important; color: white !important; border-radius: 8px; padding: 12px; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🧠 AI Due Diligence Assistant</h1><p>Get instant insights into financial and due diligence queries</p></div>', unsafe_allow_html=True)

# 📜 Sidebar for Advanced Features
with st.sidebar:
    st.title("📊 Insights & Tools")
    previous_qas = get_previous_questions()
    selected_past_question = st.selectbox("🔄 Select a past question:", [qa['question'] for qa in previous_qas]) if previous_qas else None
    st.write("📊 **Total Questions Asked:**", collection.count_documents({}))
    if st.button("📥 Download Q&A History (CSV)"):
        df = pd.DataFrame(previous_qas)
        df.to_csv("qa_history.csv", index=False)
        st.download_button("Download File", "qa_history.csv", file_name="qa_history.csv")

# 📝 User Input Section
st.markdown('<div class="question-box">', unsafe_allow_html=True)
question = st.text_input("💬 Enter your question:", value=selected_past_question or "")
st.markdown('</div>', unsafe_allow_html=True)

# 📥 File Upload Feature
txt_file = st.file_uploader("📂 Upload a text file to analyze", type=["txt"])
if txt_file:
    file_content = txt_file.read().decode("utf-8")
    st.text_area("📜 File Content", file_content, height=150)
    if st.button("📊 Summarize File"):
        summary = generate_answer_with_ollama("Summarize the key points:", file_content)
        st.markdown(f'<div class="response-box"><p>{summary}</p></div>', unsafe_allow_html=True)

# 🔘 Buttons Section
col1, col2 = st.columns([1, 1])
with col1:
    get_answer_btn = st.button("🔍 Get Answer")
with col2:
    regenerate_answer_btn = st.button("♻️ Regenerate Answer")

# 📢 Answer Processing & Display
if (get_answer_btn or regenerate_answer_btn) and question.strip():
    context = find_relevant_context(question, cleaned_texts)
    with st.spinner("💡 AI is generating your answer..."):
        answer = generate_answer_with_ollama(question, context)
    st.markdown('<div class="response-box">', unsafe_allow_html=True)
    st.subheader("📢 AI Response:")
    st.markdown(f'<p>{answer}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if get_answer_btn:
        save_to_mongodb(question, answer)
else:
    if get_answer_btn or regenerate_answer_btn:
        st.warning("⚠️ Please enter a valid question.")