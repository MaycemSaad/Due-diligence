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
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Initialize NLP Model
nlp = spacy.load("en_core_web_sm")
nltk.download('stopwords')

# Page Configuration
st.set_page_config(page_title="📊 AI Chatbot Analytics", page_icon="🤖", layout="wide")

# Database Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

# Load Data from MongoDB
data = list(collection.find().sort("timestamp", -1))
df = pd.DataFrame(data)

# Vérification si la base est vide
if df.empty:
    st.warning("🚨 Aucune donnée trouvée dans la base MongoDB.")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"])
df["response_length"] = df["answer"].apply(lambda x: len(x.split()))

# Sidebar Filters
st.sidebar.header("🔍 Filters")
date_range = st.sidebar.date_input("Select Date Range", [df["timestamp"].min(), df["timestamp"].max()])
sentiment_filter = st.sidebar.multiselect("Filter by Sentiment", ["Positive", "Neutral", "Negative"], default=[])

# Filtered Data
if sentiment_filter:
    df = df[df["sentiment_label"].isin(sentiment_filter)]
df = df[(df["timestamp"] >= pd.to_datetime(date_range[0])) & (df["timestamp"] <= pd.to_datetime(date_range[1]))]

# Search Functionality
search_query = st.sidebar.text_input("Search Keyword")
if search_query:
    df = df[df["question"].str.contains(search_query, case=False, na=False)]

# Display Data
st.markdown("### 📊 Chatbot Q&A Data")
gb = GridOptionsBuilder.from_dataframe(df)
gb.configure_pagination()
AgGrid(df, gridOptions=gb.build(), height=300, fit_columns_on_grid_load=True)

# Engagement Timeline
st.markdown("### 📈 Engagement Over Time")
fig = px.area(df, x="timestamp", y="response_length", title="Engagement Timeline", template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Named Entity Recognition
st.markdown("### 🔍 Named Entity Recognition (NER)")
all_text = " ".join(df["question"].astype(str))
doc = nlp(all_text)
entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(entities))
fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)

# Sentiment Analysis
st.markdown("### 📈 Sentiment Analysis")
df["sentiment"] = df["question"].apply(lambda x: TextBlob(x).sentiment.polarity)
df["sentiment_label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))
sentiment_counts = df["sentiment_label"].value_counts()
fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Sentiment Distribution")
st.plotly_chart(fig, use_container_width=True)

# Document Length Distribution
st.markdown("### 📄 Document Length Distribution")
df["doc_length"] = df["question"].apply(lambda x: len(x.split()))
fig, ax = plt.subplots()
sns.histplot(df["doc_length"], bins=20, kde=True, color="blue")
st.pyplot(fig)

# Topic Modeling
st.markdown("### 📌 Topic Modeling")
top_words = Counter(" ".join(df["question"].dropna()).split()).most_common(10)
top_words_df = pd.DataFrame(top_words, columns=["Word", "Count"])
st.bar_chart(top_words_df.set_index("Word"))

# Text Summarization with Sumy
st.markdown("### 📄 Automatic Text Summarization")
def summarize_text(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)  # Nombre de phrases résumées
    return " ".join(str(sentence) for sentence in summary)

if not df.empty:
    long_text = " ".join(df["question"].dropna())
    summary = summarize_text(long_text)
    st.text_area("Summary of Questions", summary, height=200)

# Download Processed Data
st.markdown("### 📥 Download Processed Data")
st.download_button(label="Download CSV", data=df.to_csv(index=False), file_name="chatbot_analytics.csv", mime="text/csv")

# Footer
st.markdown(f"<div style='text-align: center;'>AI Chatbot Analytics v3.0 | Enhanced with NLP Features | Updated: {datetime.now().strftime('%Y-%m-%d')}</div>", unsafe_allow_html=True)
