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

# 🎨 Configuration de la page
st.set_page_config(page_title="📊 AI Chatbot Analytics", page_icon="🤖", layout="wide")

from textblob import TextBlob

# 📂 Dossier contenant les textes nettoyés
cleaned_texts_dir = "cleaned_texts"

# 🛠️ Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]



# 🔹 Chargement des données MongoDB
data = list(collection.find().sort("timestamp", -1))
df = pd.DataFrame(data)

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["response_length"] = df["answer"].apply(lambda x: len(x.split()))

    # 🔥 MODERN QUESTION ANALYSIS SECTION
    with st.container():
        st.markdown('<div style="margin-bottom: 10px;"><h3 style="color: var(--primary);">🔥 Trending Questions</h3></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1.5, 2.5])  # Ajustement des colonnes pour agrandir les questions

        with col1:
            # 📌 Affichage des questions agrandies
            most_frequent_questions = df["question"].value_counts().head(5).reset_index()
            most_frequent_questions.columns = ["Question", "Count"]

            st.dataframe(
                most_frequent_questions.style.set_table_styles([
                    {'selector': 'th', 'props': [('font-size', '18px'), ('text-align', 'left')]},
                    {'selector': 'td', 'props': [('font-size', '16px'), ('text-align', 'left')]}
                ]),
                use_container_width=True
            )

        with col2:
            # 📈 Graphique "Engagement Timeline"
            fig = px.area(df, x="timestamp", y="response_length",
                          title="Engagement Timeline",
                          template="plotly_dark",
                          color_discrete_sequence=["#25D366"],
                          labels={"response_length": "Response Complexity"})
            fig.update_layout(
                paper_bgcolor="var(--background)",
                plot_bgcolor="var(--surface)",
                xaxis_title="",
                yaxis_title="Response Length (words)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

# 📥 Charger les textes sans vérification
def load_cleaned_texts(directory):
    texts = []
    filenames = []
    
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):  # 🔍 Vérifie si c'est un fichier texte
            file_path = os.path.join(directory, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                text = file.read()
                texts.append(text)
                filenames.append(filename)

    return pd.DataFrame({"filename": filenames, "text": texts})

# 🛠️ Chargement des textes directement
df = load_cleaned_texts(cleaned_texts_dir)


# 🎨 PRO-GRADE CUSTOM THEME
st.markdown("""
    <style>
        :root {
            --primary: #25D366;
            --secondary: #2ECC71;
            --background: #0F172A;
            --surface: #1E293B;
        }
        
        body { 
            background-color: var(--background); 
            color: white; 
            font-family: 'Poppins', sans-serif;
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

st.markdown('<div class="gradient-header">📑 AI Document Analysis Dashboard</div>', unsafe_allow_html=True)

### 🔍 **1. Named Entity Recognition (NER)**
nlp = spacy.load("en_core_web_sm")

st.markdown('<div class="chart-container"><h3 style="color: var(--primary);">🔍 Named Entity Recognition (NER)</h3></div>', unsafe_allow_html=True)
st.markdown('<p style="color: lightgrey; font-size:14px;">📌 This word cloud highlights the most common named entities (companies, places, people, etc.).</p>', unsafe_allow_html=True)

all_text = " ".join(df["text"])
doc = nlp(all_text)
entities = [ent.text for ent in doc.ents if len(ent.text) > 2]

wordcloud = WordCloud(width=800, height=400, background_color="#0F172A", colormap="viridis").generate(" ".join(entities))

fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)


### 🔥 **2. Most Relevant Topics**
st.markdown('<div class="chart-container"><h3 style="color: var(--primary);">📌 Most Relevant Topics</h3></div>', unsafe_allow_html=True)
st.markdown('<p style="color: lightgrey; font-size:14px;">🔥 This bar chart shows the most relevant topics based on keyword frequency.</p>', unsafe_allow_html=True)

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
text_cleaned = all_text.lower().translate(str.maketrans('', '', string.punctuation))
words = [word for word in text_cleaned.split() if word not in stop_words and len(word) > 2]

word_counts = Counter(words)
top_words = pd.DataFrame(word_counts.most_common(10), columns=["Word", "Count"]).sort_values("Count", ascending=True)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(x="Count", y="Word", data=top_words, palette="rocket_r", ax=ax, edgecolor="white", linewidth=1)

for i, (count, word) in enumerate(zip(top_words["Count"], top_words["Word"])):
    ax.text(count + max(top_words["Count"])*0.02, i, f"{count}", color="white", va="center", fontsize=10)

ax.set_title("Most Relevant Topics", fontsize=14, color="white", pad=20)
ax.set_xlabel("Occurrences", color="white", fontsize=12, labelpad=15)
ax.set_ylabel(None)
ax.tick_params(axis='both', colors='white', labelsize=10)
ax.grid(axis='x', linestyle='--', alpha=0.3, color="white")

fig.patch.set_facecolor('#1E293B')
ax.set_facecolor('#1E293B')

st.pyplot(fig)


### 📈 **3. Sentiment Analysis**
st.markdown('<div class="chart-container"><h3 style="color: var(--primary);">📈 Sentiment Analysis</h3></div>', unsafe_allow_html=True)
st.markdown('<p style="color: lightgrey; font-size:14px;">📌 This pie chart shows the distribution of positive, negative, and neutral documents based on sentiment analysis.</p>', unsafe_allow_html=True)

df["sentiment"] = df["text"].apply(lambda x: TextBlob(x).sentiment.polarity)
df["sentiment_label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))

sentiment_counts = df["sentiment_label"].value_counts()

fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, 
             title="Sentiment Distribution", color_discrete_sequence=["#2ECC71", "#E74C3C", "#F1C40F"])
st.plotly_chart(fig, use_container_width=True)


### 🌍 **4. Word Cloud of Key Terms**
st.markdown('<div class="chart-container"><h3 style="color: var(--primary);">🌍 Word Cloud</h3></div>', unsafe_allow_html=True)
st.markdown('<p style="color: lightgrey; font-size:14px;">📌 This word cloud represents the most frequent words used in documents.</p>', unsafe_allow_html=True)

wordcloud = WordCloud(width=800, height=400, background_color="#0F172A", colormap="viridis").generate(" ".join(words))

fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)


### 🔹 **5. Document Length Distribution**
st.markdown('<div class="chart-container"><h3 style="color: var(--primary);">📄 Document Length Distribution</h3></div>', unsafe_allow_html=True)
st.markdown('<p style="color: lightgrey; font-size:14px;">📌 This histogram shows the distribution of document lengths.</p>', unsafe_allow_html=True)

df["doc_length"] = df["text"].apply(lambda x: len(x.split()))

fig, ax = plt.subplots(figsize=(10, 5))
sns.histplot(df["doc_length"], bins=20, kde=True, color="#25D366", edgecolor="white")

ax.set_title("Document Length Distribution", fontsize=14, color="white", pad=20)
ax.set_xlabel("Number of Words", color="white", fontsize=12, labelpad=15)
ax.set_ylabel("Count", color="white", fontsize=12)
ax.tick_params(axis='both', colors='white', labelsize=10)
ax.grid(axis='y', linestyle='--', alpha=0.3, color="white")

fig.patch.set_facecolor('#1E293B')
ax.set_facecolor('#1E293B')

st.pyplot(fig)

# FOOTER
st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #64748B; font-size: 0.9rem;">
        AI Document Analysis Dashboard v2.0 • Powered by Streamlit • Updated: {datetime.now().strftime("%Y-%m-%d")}
    </div>
""", unsafe_allow_html=True)
