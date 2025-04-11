import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud
import spacy
import nltk
from nltk.corpus import stopwords
from collections import Counter
import string
from datetime import datetime
from pymongo import MongoClient
from textblob import TextBlob

# 🎨 Configuration de la page
st.set_page_config(page_title="📊 AI Chatbot Analytics", page_icon="🤖", layout="wide")

# 🛠️ Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

# 🔹 Chargement des données MongoDB
data = list(collection.find().sort("timestamp", -1))
df = pd.DataFrame(data)

# 📥 Chargement des textes nettoyés
def load_cleaned_texts(directory):
    texts, filenames = [], []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as file:
                texts.append(file.read())
                filenames.append(filename)
    return pd.DataFrame({"filename": filenames, "text": texts})

cleaned_texts_dir = "cleaned_texts"
df_texts = load_cleaned_texts(cleaned_texts_dir)

# 🎨 Amélioration du design
st.markdown("""
    <style>
        :root {
            --primary: #25D366;
            --secondary: #2ECC71;
            --background: #0F172A;
            --surface: #1E293B;
        }
        .chart-container {
            background: var(--surface);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            border: 1px solid rgba(255,255,255,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# 🔥 Trending Questions
if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["response_length"] = df["answer"].apply(lambda x: len(x.split()))
    
    st.markdown("<h3 style='color: var(--primary);'>🔥 Trending Questions</h3>", unsafe_allow_html=True)
    most_frequent_questions = df["question"].value_counts().head(5).reset_index()
    most_frequent_questions.columns = ["Question", "Count"]
    st.dataframe(most_frequent_questions, use_container_width=True)

    # 📈 Engagement Timeline
    fig = px.area(df, x="timestamp", y="response_length", title="Engagement Timeline",
                  template="plotly_dark", color_discrete_sequence=["#25D366"],
                  labels={"response_length": "Response Complexity"})
    st.plotly_chart(fig, use_container_width=True)

# 📌 Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_sm")
if not df_texts.empty:
    all_text = " ".join(df_texts["text"])
    doc = nlp(all_text)
    entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
    
    wordcloud = WordCloud(width=800, height=400, background_color="#0F172A", colormap="viridis").generate(" ".join(entities))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

# 📊 Sentiment Analysis
df_texts["sentiment"] = df_texts["text"].apply(lambda x: TextBlob(x).sentiment.polarity)
df_texts["sentiment_label"] = df_texts["sentiment"].apply(lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))
sentiment_counts = df_texts["sentiment_label"].value_counts()
fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, 
             title="Sentiment Distribution", color_discrete_sequence=["#2ECC71", "#E74C3C", "#F1C40F"])
st.plotly_chart(fig, use_container_width=True)

# 📄 Document Length Distribution
df_texts["doc_length"] = df_texts["text"].apply(lambda x: len(x.split()))
fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df_texts["doc_length"], bins=20, kde=True, color="#25D366", edgecolor="white")
st.pyplot(fig)

# 📌 Footer
st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #64748B; font-size: 0.9rem;">
        AI Document Analysis Dashboard v2.0 • Powered by Streamlit • Updated: {datetime.now().strftime("%Y-%m-%d")}
    </div>
""", unsafe_allow_html=True)
