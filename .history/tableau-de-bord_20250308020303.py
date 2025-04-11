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

# Initial configurations
nltk.download('stopwords')
nlp = spacy.load("en_core_web_sm")
st.set_page_config(page_title="📊 AI Chatbot Analytics", page_icon="🤖", layout="wide")

# ------------------------
# 🛠 CORE FUNCTIONS
# ------------------------

@st.cache_data(ttl=300)
def load_mongodb_data():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    return pd.DataFrame(list(db["qa"].find().sort("timestamp", -1)))

@st.cache_data
def load_text_files(directory="cleaned_texts"):
    texts = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            with open(os.path.join(directory, filename), "r", encoding="utf-8") as f:
                texts.append((filename, f.read()))
    return pd.DataFrame(texts, columns=["filename", "text"])

def apply_filters(df, date_range, sentiment_filter, length_range):
    filtered = df[
        (df["timestamp"].between(*date_range)) &
        (df["sentiment_label"].isin(sentiment_filter)) &
        (df["doc_length"].between(*length_range))
    ]
    return filtered

# ------------------------
# 📊 VISUALIZATION COMPONENTS
# ------------------------

def create_entity_cloud(entities):
    wordcloud = WordCloud(width=800, height=400, 
                         background_color="#0F172A", colormap="viridis").generate(" ".join(entities))
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    return fig

def create_sentiment_gauge(sentiment_score):
    fig = px.indicator(
        mode="gauge+number",
        value=sentiment_score,
        title="Overall Sentiment Score",
        range=[-1,1],
        number={'font':{'color':"white"}},
        gauge={'axis': {'tickcolor': "white"},
               'bar': {'color': "#25D366"}}
    )
    fig.update_layout(paper_bgcolor="#1E293B")
    return fig

# ------------------------
# 🎨 PAGE LAYOUT
# ------------------------

def main():
    # Custom theme
    st.markdown("""
        <style>
            :root { --primary: #25D366; --secondary: #2ECC71; 
                    --background: #0F172A; --surface: #1E293B; }
            .metric-box { padding: 1.5rem; border-radius: 10px; 
                        background: var(--surface); margin: 0.5rem; }
        </style>
    """, unsafe_allow_html=True)

    # ------------------------
    # 📌 HEADER & FILTERS
    # ------------------------
    st.title("📑 AI Document Analysis Dashboard")
    
    # Real-time toggle
    real_time = st.sidebar.checkbox("Live Data Mode", True)
    refresh_btn = st.sidebar.button("Refresh Data" if not real_time else "Live Updating")
    
    # Date filter
    min_date = datetime(2023,1,1)
    max_date = datetime.now()
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
    
    # Sentiment filter
    sentiment_filter = st.sidebar.multiselect("Sentiment", 
        options=["Positive", "Neutral", "Negative"], default=["Positive", "Neutral", "Negative"])
    
    # Document length filter
    length_range = st.sidebar.slider("Document Length (words)", 0, 1000, (50, 500))

    # ------------------------
    # 📥 DATA LOADING
    # ------------------------
    qa_df = load_mongodb_data()
    text_df = load_text_files()
    
    if not qa_df.empty:
        qa_df["timestamp"] = pd.to_datetime(qa_df["timestamp"])
        qa_df["response_length"] = qa_df["answer"].str.split().str.len()
    
    text_df["sentiment"] = text_df["text"].apply(lambda x: TextBlob(x).sentiment.polarity)
    text_df["sentiment_label"] = text_df["sentiment"].apply(
        lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))
    text_df["doc_length"] = text_df["text"].str.split().str.len()

    # Apply filters
    filtered_df = apply_filters(text_df, date_range, sentiment_filter, length_range)

    # ------------------------
    # 📈 KEY METRICS
    # ------------------------
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-box">📄 Total Documents<br><h2>{}</h2></div>'.format(
            len(filtered_df)), unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-box">💬 Avg Sentiment<br><h2>{:.2f}</h2></div>'.format(
            filtered_df["sentiment"].mean()), unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-box">📏 Avg Length<br><h2>{:.0f}</h2></div>'.format(
            filtered_df["doc_length"].mean()), unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-box">🔥 Top Entity<br><h2>{}</h2></div>'.format(
            max(Counter([ent.text for ent in nlp(" ".join(filtered_df["text"])).ents]), key=len)),
            unsafe_allow_html=True)

    # ------------------------
    # 📊 MAIN VISUALIZATIONS
    # ------------------------
    tab1, tab2, tab3 = st.tabs(["📌 Text Analysis", "📈 Trends", "🔍 Entities"])
    
    with tab1:
        c1, c2 = st.columns([1,2])
        with c1:
            st.plotly_chart(create_sentiment_gauge(filtered_df["sentiment"].mean()), 
                          use_container_width=True)
        with c2:
            fig = px.histogram(filtered_df, x="doc_length", nbins=20, 
                             title="Document Length Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.line(qa_df.groupby(pd.Grouper(key='timestamp', freq='D')).size(),
                     title="Daily Question Volume", labels={'value':'Questions'})
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        entities = [ent.text for ent in nlp(" ".join(filtered_df["text"])).ents if len(ent.text) > 2]
        st.pyplot(create_entity_cloud(entities))

    # ------------------------
    # 🎯 ADVANCED FEATURES
    # ------------------------
    with st.expander("🔍 Deep Document Analysis"):
        selected_doc = st.selectbox("Select Document", filtered_df["filename"])
        doc_text = filtered_df[filtered_df["filename"] == selected_doc]["text"].iloc[0]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Key Statistics**")
            st.metric("Sentiment Score", 
                     f"{TextBlob(doc_text).sentiment.polarity:.2f}")
            st.metric("Readability Score", 
                     f"{len(doc_text.split())/len(doc_text.split('.')):.1f}")
        with col2:
            st.markdown("**Entities Found**")
            entities = list(set([ent.text for ent in nlp(doc_text).ents]))
            st.write(", ".join(entities[:5]))

    # ------------------------
    # 📥 DATA EXPORT
    # ------------------------
    st.sidebar.download_button("Export Filtered Data",
                              filtered_df.to_csv().encode('utf-8'),
                              "filtered_data.csv",
                              "text/csv")

if __name__ == "__main__":
    main()