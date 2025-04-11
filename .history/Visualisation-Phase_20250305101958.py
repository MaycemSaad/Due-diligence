import streamlit as st
import PyPDF2
import os
import re
import spacy
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from transformers import pipeline
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Load NLP Model
nlp = spacy.load("en_core_web_sm")

# Summarization Pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Storage Directories
output_dir = "resumes"
os.makedirs(output_dir, exist_ok=True)

# Session State Initialization
if 'df_result' not in st.session_state:
    st.session_state.df_result = None

# Function to Extract and Clean Text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return re.sub(r'[^\w\s.,;!?]', '', text.strip())

# Text Cleaning Function
def clean_text(text):
    doc = nlp(text)
    return " ".join([sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 5])

# Summarization Function
def summarize_text(text):
    text = text[:1024]  # Truncate for summarization model
    summary = summarizer(text, max_length=250, min_length=50, num_beams=6, do_sample=False)
    return summary[0]['summary_text']

# Processing Uploaded PDFs
def process_uploaded_pdfs(uploaded_files):
    pdf_data = []
    for file in uploaded_files:
        text = extract_text_from_pdf(file)
        cleaned_text = clean_text(text)
        summary = summarize_text(cleaned_text)
        pdf_data.append({
            "PDF Name": file.name,
            "Word Count": len(cleaned_text.split()),
            "Summary": summary,
            "Cleaned Text": cleaned_text
        })
    return pd.DataFrame(pdf_data)

# Real-time Processing
def real_time_processing(uploaded_files):
    while True:
        time.sleep(5)  # Update every 5 seconds
        if uploaded_files:
            df = process_uploaded_pdfs(uploaded_files)
            st.session_state.df_result = df
            st.experimental_rerun()

# Visualization Function
def visualize_data(df):
    if df.empty:
        st.warning("⚠️ No data available!")
        return
    
    st.write("### Word Count per Document")
    st.plotly_chart(px.bar(df, x="PDF Name", y="Word Count", color="Word Count"))
    
    st.write("### Word Cloud")
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(df["Cleaned Text"]))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    st.pyplot(plt)

# Streamlit UI
st.set_page_config(page_title="Real-Time AI Due Diligence", layout="wide")
st.title("📜 AI Due Diligence Analyzer")

uploaded_files = st.file_uploader("📂 Upload PDFs", type=['pdf'], accept_multiple_files=True)
if uploaded_files:
    df_result = process_uploaded_pdfs(uploaded_files)
    st.session_state.df_result = df_result

# Display Processed Data & Visualizations
if st.session_state.df_result is not None:
    visualize_data(st.session_state.df_result)

# Start Real-Time Processing
if st.button("🔄 Enable Real-Time Processing"):
    real_time_processing(uploaded_files)
