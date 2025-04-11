import streamlit as st
import PyPDF2
import re
import os
import spacy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import pipeline

# Charger le modèle NLP pour le nettoyage
nlp = spacy.load("en_core_web_sm")

# 📂 Création des dossiers de stockage
output_dir = "resumes"
clean_text_dir = "cleaned_texts"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(clean_text_dir, exist_ok=True)

# 📊 Chargement du modèle de résumé
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# 📜 Liste des fichiers PDF à traiter
new_pdf_files = [
    "108364 PLE_Digital Assets_Deck 290724.pdf",
    "1110830.1.0 Introduction to Digital Assets for Institutional Investors_FINAL_0.pdf",
    "cravath-bringing-blockchain-due-diligence-into-focus-102024_vb-002.pdf",
    "DASCPWhitePaper.pdf",
    "Digital_Assets_Legal_Regulation_and_Estimation_of_.pdf"
]

# 📝 Extraction et Nettoyage
def extract_text_from_pdf(pdf_file):
    """Extrait tout le texte d'un PDF."""
    try:
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text.strip()
    except Exception as e:
        print(f"❌ Erreur d'extraction pour {pdf_file}: {e}")
        return ""

def clean_text(text):
    """Nettoie le texte extrait du PDF."""
    text = re.sub(r'\n+', '\n', text)  # Supprime les sauts de ligne excessifs
    text = re.sub(r'[^\w\s.,;!?]', '', text)  # Supprime caractères spéciaux sauf ponctuation
    text = re.sub(r'\bPage \d+\b', '', text, flags=re.IGNORECASE)  # Supprime les numéros de page
    text = re.sub(r'http\S+', '', text)  # Supprime les URL
    text = text.strip()

    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 5]

    return " ".join(sentences)

def summarize_text(text):
    """Utilise le modèle NLP pour résumer un texte."""
    text = text[:1024]
    input_length = len(text.split())
    max_length = min(350, int(input_length * 0.8))
    min_length = max(50, int(input_length * 0.4))

    summary = summarizer(
        text,
        max_length=max_length,
        min_length=min_length,
        length_penalty=3.5,
        num_beams=6,
        do_sample=False
    )
    return summary[0]['summary_text']

# 📈 Visualisation des Données
def visualize_data(data):
    """Affiche des graphiques professionnels sur les données de tous les PDF."""
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="PDF Name", y="Word Count", data=data, palette="coolwarm", ax=ax)
    plt.xticks(rotation=45, ha="right")
    plt.title("Nombre de mots extraits par document")
    plt.xlabel("Documents PDF")
    plt.ylabel("Nombre de mots")
    st.pyplot(fig)

def process_pdfs():
    """Extrait, nettoie, résume et visualise tous les PDF."""
    pdf_data = []

    for pdf_file in new_pdf_files:
        extracted_text = extract_text_from_pdf(pdf_file)
        if not extracted_text:
            continue

        cleaned_text = clean_text(extracted_text)
        pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
        cleaned_text_file = os.path.join(clean_text_dir, f"cleaned_{pdf_name}.txt")
        with open(cleaned_text_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        summary = summarize_text(cleaned_text)
        output_file = os.path.join(output_dir, f"resume_{pdf_name}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary)

        pdf_data.append({"PDF Name": pdf_name, "Word Count": len(cleaned_text.split())})

    df = pd.DataFrame(pdf_data)
    if not df.empty:
        visualize_data(df)

# 🎨 Interface Streamlit Redesign
st.set_page_config(page_title="AI Due Diligence Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #F8F9FA; color: #333; }
        .header { text-align: center; padding: 30px; background: linear-gradient(90deg, #6A11CB, #2575FC); color: white; border-radius: 12px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 2px 4px 10px rgba(0, 0, 0, 0.1); margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>📊 AI Due Diligence Dashboard</h1><p>Professional AI-driven insights for document analysis</p></div>', unsafe_allow_html=True)

# 📜 Sidebar & Controls
with st.sidebar:
    st.title("📊 Analysis & Tools")
    if st.button("🔍 Start Full Analysis"):
        process_pdfs()

# 📈 Data Visualization
st.write("## 📈 Data Visualization for All PDFs")
if st.button("📊 Generate Full Report"):
    process_pdfs()import streamlit as st
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
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x="PDF Name", y="Word Count", data=df, palette="coolwarm", ax=ax)
    plt.xticks(rotation=45, ha="right")
    plt.title("Nombre de mots extraits par document")
    plt.xlabel("Documents PDF")
    plt.ylabel("Nombre de mots")
    st.pyplot(fig)
    
    # Nuage de mots
    text_corpus = " ".join(df["Cleaned Text"])
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_corpus)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)

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
        pdf.multi_cell(0, 10, f"Résumé: {row['Summary']}")
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
        pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
        pdf_data.append({"PDF Name": pdf_name, "Word Count": len(cleaned_text.split()), "Cleaned Text": cleaned_text, "Summary": summary})
    df = pd.DataFrame(pdf_data)
    if not df.empty:
        visualize_data(df)
        return df
    return None

# 🎨 Interface Streamlit
st.set_page_config(page_title="AI Due Diligence Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #F8F9FA; color: #333; }
        .header { text-align: center; padding: 30px; background: linear-gradient(90deg, #6A11CB, #2575FC); color: white; border-radius: 12px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>📊 AI Due Diligence Dashboard</h1><p>Comprehensive AI-powered insights</p></div>', unsafe_allow_html=True)

# 📜 Sidebar
with st.sidebar:
    st.title("📊 Tools & Reports")
    if st.button("🔍 Run Full Analysis"):
        df_result = process_pdfs()
        if df_result is not None:
            pdf_file = generate_pdf_report(df_result)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 Download Full Report", f, file_name=pdf_file, mime="application/pdf")

# 📈 Data Visualization
st.write("## 📈 Comprehensive Analysis Report")
if st.button("📊 Generate Interactive Report"):
    df_result = process_pdfs()
    if df_result is not None:
        generate_pdf_report(df_result)