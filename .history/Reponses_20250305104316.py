import streamlit as st
import ollama
import glob
import os
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

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
    """🔍 Finds the most relevant text segment based on TF-IDF similarity."""
    if not texts:
        return ""
    
    vectorizer = TfidfVectorizer(stop_words="english")
    corpus = list(texts.values()) + [question]
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    # Compute similarity between question and all texts
    similarity_scores = (tfidf_matrix[-1] @ tfidf_matrix[:-1].T).toarray()[0]
    best_match_idx = np.argmax(similarity_scores)

    # Select the most relevant text
    return list(texts.values())[best_match_idx][:max_words] if similarity_scores[best_match_idx] > 0 else ""

def generate_answer_with_ollama(question, context):
    """🤖 Generates an AI-powered answer with fallback and educated guessing."""
    
    # If no context is found, guide the AI to infer an answer
    if not context.strip():
        context = """
        No specific context is available. However, you are an expert in digital finance and due diligence.
        If relevant information is missing, provide an educated answer based on general industry knowledge.
        Additionally, suggest what details would be needed to answer accurately.
        """

    prompt = f"""
    You are an expert in digital finance and due diligence. Answer the question strictly based on the provided context.
    
    [CONTEXT]: {context}
    
    [QUESTION]: {question}
    
    [INSTRUCTIONS]:
    - If the context provides relevant information, answer directly.
    - If the context is missing or insufficient, make an educated guess based on industry standards.
    - Suggest what details would be needed for a more precise answer.
    - Structure your answer clearly and avoid stating "no information available."

    [ANSWER]:
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        options={"num_predict": min(150, len(question.split()) * 5)}
    )
    
    answer = response["message"]["content"].strip()

    # Ensure a valid response is always returned
    if not answer or "no information" in answer.lower():
        answer = ("The provided context does not explicitly state the licensing details. However, in general, projects in this domain "
                  "typically require regulatory approvals such as [mention typical licenses in the industry]. If you can provide more specifics "
                  "about the project's nature and jurisdiction, I can offer a more tailored response.")

    return answer

def save_to_mongodb(question, answer):
    """💾 Saves Q&A in MongoDB."""
    collection.insert_one({"question": question, "answer": answer, "timestamp": datetime.utcnow()})

def get_previous_questions(limit=5):
    """🔄 Fetch last 5 questions from MongoDB."""
    return list(collection.find().sort("timestamp", -1).limit(limit))

# 🎨 Streamlit UI Redesign
st.set_page_config(page_title="AI Due Diligence Dashboard", page_icon="💼", layout="wide")

st.markdown("""
    <style>
        body { font-family: 'Arial', sans-serif; }
        .stApp { background-color: #F8F9FA; color: #333; }
        .header { text-align: center; padding: 30px; background: linear-gradient(90deg, #6A11CB, #2575FC); color: white; border-radius: 12px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
        .stButton>button { background-color: #2575FC !important; color: white !important; border-radius: 8px; padding: 12px; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>💼 AI Due Diligence Dashboard</h1><p>Advanced AI-powered insights for financial analysis</p></div>', unsafe_allow_html=True)

# 📜 Sidebar for Insights & Analytics
with st.sidebar:
    st.title("📊 Dashboard & Tools")
    previous_qas = get_previous_questions()
    selected_past_question = st.selectbox("🔄 Recent Queries", [qa['question'] for qa in previous_qas]) if previous_qas else None
    st.write("📊 **Total Questions Analyzed:**", collection.count_documents({}))
    if st.button("📥 Export Data (CSV)"):
        df = pd.DataFrame(previous_qas)
        df.to_csv("qa_data.csv", index=False)
        st.download_button("Download CSV", "qa_data.csv", file_name="qa_data.csv")

# 📝 Question Input Section
st.markdown('<div class="card">', unsafe_allow_html=True)
question = st.text_input("💬 Ask a question:", value=selected_past_question or "")
st.markdown('</div>', unsafe_allow_html=True)

# 📂 File Upload Feature
txt_file = st.file_uploader("📂 Upload a document for analysis", type=["txt"])
if txt_file:
    file_content = txt_file.read().decode("utf-8")
    st.text_area("📜 Document Preview", file_content, height=150)
    if st.button("📊 Generate Summary"):
        summary = generate_answer_with_ollama("Summarize this document:", file_content)
        st.markdown(f'<div class="card"><h3>📌 Summary</h3><p>{summary}</p></div>', unsafe_allow_html=True)

# 🔘 Action Buttons
col1, col2 = st.columns([1, 1])
with col1:
    get_answer_btn = st.button("🔍 Analyze")
with col2:
    regenerate_answer_btn = st.button("♻️ Reanalyze")

# 📢 Answer Processing & Display
if (get_answer_btn or regenerate_answer_btn) and question.strip():
    context = find_relevant_context(question, cleaned_texts)
    with st.spinner("💡 AI is analyzing..."):
        answer = generate_answer_with_ollama(question, context)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📢 AI Response:")
    st.markdown(f'<p>{answer}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if get_answer_btn:
        save_to_mongodb(question, answer)
else:
    if get_answer_btn or regenerate_answer_btn:
        st.warning("⚠️ Please enter a valid question.")
