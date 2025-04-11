import streamlit as st
import PyPDF2
import re
import os
import spacy
import pandas as pd
import matplotlib.pyplot as plt
from transformers import pipeline
from fpdf import FPDF
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# 📂 Storage Directories
output_dir = "resumes"
clean_text_dir = "cleaned_texts"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(clean_text_dir, exist_ok=True)

# 📊 Summarization Model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# 📜 List of PDF Files
new_pdf_files = [
    "108364 PLE_Digital Assets_Deck 290724.pdf",
    "1110830.1.0 Introduction to Digital Assets for Institutional Investors_FINAL_0.pdf",
    "cravath-bringing-blockchain-due-diligence-into-focus-102024_vb-002.pdf",
    "DASCPWhitePaper.pdf",
    "Digital_Assets_Legal_Regulation_and_Estimation_of_.pdf"
]

# 📝 Extract & Clean Text
def extract_text_from_pdf(pdf_file):
    try:
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text.strip()
    except Exception:
        return ""

def clean_text(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[^\w\s.,;!?]', '', text)
    text = re.sub(r'\bPage \d+\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'http\S+', '', text)
    text = text.strip()
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 5]
    return " ".join(sentences)

def summarize_text(text):
    text = text[:1024]
    summary = summarizer(text, max_length=250, min_length=50, length_penalty=3.5, num_beams=6, do_sample=False)
    return summary[0]['summary_text']

# 📊 Word Search & Related Words
def count_word_occurrences(text, word):
    words = re.findall(r'\b' + re.escape(word) + r'\b', text, re.IGNORECASE)
    return len(words)

def get_related_words(text, word, top_n=5):
    doc = nlp(text)
    word_freq = Counter(token.text.lower() for token in doc if token.is_alpha)
    
    related_words = {}
    for token in doc:
        if token.text.lower() != word.lower() and token.has_vector and nlp(word).has_vector:
            similarity = token.similarity(nlp(word))
            related_words[token.text.lower()] = similarity

    sorted_words = sorted(related_words.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]

# 📊 Data Visualization
def visualize_data(df):
    st.subheader("📈 Data Visualization")
    
    if df.empty:
        st.warning("⚠️ No data available to display!")
        return
    
    st.write("### 📊 Word Count per Document")
    fig1 = px.bar(df, x="PDF Name", y="Word Count", title="Word Count per Document", color="Word Count", height=500)
    st.plotly_chart(fig1, use_container_width=True)
    
    st.write("### ☁️ Word Cloud of Extracted Texts")
    text_corpus = " ".join(df["Cleaned Text"])
    if text_corpus:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_corpus)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt)

    st.write("### 🥧 Proportion of Words per Document")
    fig2 = px.pie(df, names="PDF Name", values="Word Count", title="Proportion of Words per Document")
    st.plotly_chart(fig2, use_container_width=True)

# 📄 Generate PDF Report
def generate_pdf_report(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "AI Due Diligence Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(200, 10, f"Document: {row['PDF Name']}", ln=True)
        pdf.multi_cell(0, 10, f"Résumé: {row['Summary']}\n")
        pdf.ln(5)
    pdf_file = "due_diligence_report.pdf"
    pdf.output(pdf_file)
    return pdf_file

def process_pdfs():
    pdf_data = []
    for pdf_file in new_pdf_files:
        extracted_text = extract_text_from_pdf(pdf_file)
        if not extracted_text:
            continue
        cleaned_text = clean_text(extracted_text)
        summary = summarize_text(cleaned_text)
        pdf_data.append({"PDF Name": os.path.basename(pdf_file), "Word Count": len(cleaned_text.split()), "Cleaned Text": cleaned_text, "Summary": summary})
    return pd.DataFrame(pdf_data) if pdf_data else None

# 🆕 Search Word in PDFs
def search_word_in_pdfs(df, search_word):
    if df is None or search_word == "":
        return None
    
    results = []
    for _, row in df.iterrows():
        count = count_word_occurrences(row["Cleaned Text"], search_word)
        related_words = get_related_words(row["Cleaned Text"], search_word)
        results.append({"PDF Name": row["PDF Name"], "Occurrences": count, "Related Words": ", ".join(related_words)})

    return pd.DataFrame(results)

# 🎨 Streamlit UI
st.set_page_config(page_title="AI Due Diligence Platform", page_icon="🌍", layout="wide")

st.markdown('<div style="text-align: center;"><h1>🌍 AI Due Diligence Platform</h1></div>', unsafe_allow_html=True)

# 📜 Sidebar
with st.sidebar:
    st.title("🔍 Search & Reports")
    search_word = st.text_input("Enter a word to search:")
    
    if st.button("🔎 Search Word"):
        df_result = process_pdfs()
        if df_result is not None:
            search_results = search_word_in_pdfs(df_result, search_word)
            if search_results is not None:
                st.subheader(f"🔍 Search Results for '{search_word}'")
                st.dataframe(search_results)
                st.write("### 📊 Word Occurrences per Document")
                fig = px.bar(search_results, x="PDF Name", y="Occurrences", title=f"Occurrences of '{search_word}'", color="Occurrences", height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ No results found.")

# 📈 Data Visualization
st.write("## 📈 Comprehensive Data Insights")
if st.button("📊 Generate Full Analysis"):
    df_result = process_pdfs()
    if df_result is not None:
        visualize_data(df_result)
        st.success("✅ Full report generated successfully!")
    else:
        st.warning("⚠️ No data available.")
