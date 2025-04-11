import streamlit as st
import PyPDF2
import re
import os
import spacy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import pipeline
from fpdf import FPDF
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go

# Charger le modèle NLP
nlp = spacy.load("en_core_web_sm")

# 📂 Dossiers de stockage
output_dir = "resumes"
clean_text_dir = "cleaned_texts"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(clean_text_dir, exist_ok=True)

# 📊 Modèle de résumé
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# 📜 Liste des fichiers PDF
new_pdf_files = [
    "108364 PLE_Digital Assets_Deck 290724.pdf",
    "1110830.1.0 Introduction to Digital Assets for Institutional Investors_FINAL_0.pdf",
    "cravath-bringing-blockchain-due-diligence-into-focus-102024_vb-002.pdf",
    "DASCPWhitePaper.pdf",
    "Digital_Assets_Legal_Regulation_and_Estimation_of_.pdf"
]

# 📝 Extraction et Nettoyage
def extract_text_from_pdf(pdf_file):
    try:
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text.strip()
    except Exception as e:
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

# 📊 Visualisation avancée
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
    
    st.write("### 📈 Word Count Evolution Over Time")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=df["PDF Name"], y=df["Word Count"], mode='lines+markers', name='Word Count'))
    fig3.update_layout(title="Word Count Evolution", xaxis_title="Documents", yaxis_title="Word Count")
    st.plotly_chart(fig3, use_container_width=True)

# 📄 Génération du Rapport PDF
def generate_pdf_report(df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, "AI Due Diligence Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for index, row in df.iterrows():
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
    df = pd.DataFrame(pdf_data)
    return df if not df.empty else None

# 🎨 Interface Streamlit améliorée
st.set_page_config(page_title="AI Due Diligence Platform", page_icon="🌍", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #F0F2F6; color: #333; }
        .header { text-align: center; padding: 30px; background: linear-gradient(90deg, #4A90E2, #145DA0); color: white; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🌍 AI Due Diligence Platform</h1><p>AI-powered document analysis and visualization</p></div>', unsafe_allow_html=True)

# 📜 Sidebar avec de nouvelles fonctionnalités
with st.sidebar:
    st.title("📊 Advanced Tools & Reports")
    if st.button("🔍 Start Full Analysis"):
        df_result = process_pdfs()
        if df_result is not None:
            pdf_file = generate_pdf_report(df_result)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Download Full Report", f, file_name=pdf_file, mime="application/pdf")

# 📈 Data Visualization améliorée
st.write("## 📈 Comprehensive Data Insights")
if st.button("📊 Generate Full Analysis"):
    st.write("🚀 Processing PDFs... Please wait!")
    df_result = process_pdfs()
    if df_result is not None:
        visualize_data(df_result)
        generate_pdf_report(df_result)
        st.success("✅ Full report generated successfully!")
    else:
        st.warning("⚠️ No data available.")