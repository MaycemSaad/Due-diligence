import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud
import spacy
import nltk
import numpy as np
from nltk.corpus import stopwords
from collections import Counter
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from datetime import datetime
from pymongo import MongoClient
from textblob import TextBlob
import time

# 🎨 Configuration de la page
st.set_page_config(page_title="📊 Admin Dashboard - AI Chatbot Analytics", page_icon="🤖", layout="wide")

# Sidebar Navigation with smaller logo
st.sidebar.image("logo.png", width=120) 
# 🌗 Light/Dark Mode Toggle
theme_mode = st.sidebar.radio("Choose Theme", ["Light", "Dark"], index=1)

def apply_theme(theme):
    if theme == "Dark":
        return """
            <style>
                body { background-color: #0F172A; color: white; }
                .stApp { background-color: #0F172A; }
                h2 { color: #C09B3E !important; } /* gold for subheaders only */

                h1, h3, h4, h5, h6, p, label { color: white !important; }
            </style>
        """
    else:
        return """
            <style>
                body { background-color: white; color: black; }
                .stApp { background-color: white; }
                h2 { color: #C09B3E !important; }
                h1, h2, h3, h4, h5, h6, p, label { color: black !important; }
            </style>
        """
st.markdown(apply_theme(theme_mode), unsafe_allow_html=True)

# 🛠️ Connexion à MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["due_diligence"]
collection = db["qa"]

# 🔹 Chargement des données MongoDB
data = list(collection.find().sort("timestamp", -1))
df = pd.DataFrame(data)

if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce', utc=True)
    df.dropna(subset=["timestamp"], inplace=True)
    df["response_length"] = df["answer"].apply(lambda x: len(x.split()) if isinstance(x, str) else 0)

    # Ensure sentiment analysis columns exist
    if "sentiment_label" not in df.columns:
        df["sentiment"] = df["answer"].apply(lambda x: TextBlob(x).sentiment.polarity if isinstance(x, str) else 0)
        df["sentiment_label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))



# 📊 Sidebar Navigation
st.sidebar.header("🔍 Dashboard Navigation")
page = st.sidebar.radio("Select a Page", ["Overview", "Q&A Data", "Engagement Analysis", "Sentiment Analysis", "NER & Topics", "Data Export", "Statistics", "Trending Topics", "Advanced Sentiment Analysis", "Data Export",  "User Interaction Trends"])

# 📊 Sidebar Filters
st.sidebar.header("🔍 Filters")
if not df.empty:
    date_range = st.sidebar.date_input("Select Date Range", [df["timestamp"].min().date(), df["timestamp"].max().date()])
    sentiment_options = ["All", "Positive", "Neutral", "Negative"]
    sentiment_filter = st.sidebar.selectbox("Filter by Sentiment", sentiment_options)
    keyword = st.sidebar.text_input("Search Keyword")

    if len(date_range) == 2:
        start_date = pd.to_datetime(date_range[0]).tz_localize('UTC')
        end_date = (pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)).tz_localize('UTC')
        df = df[(df["timestamp"] >= start_date) & (df["timestamp"] < end_date)]
    if sentiment_filter != "All":
        df = df[df["sentiment_label"] == sentiment_filter]
    if keyword:
        df = df[df["question"].str.contains(keyword, case=False, na=False)]

# 📊 Page Navigation
if page == "Overview":
    st.header("📊 AI Chatbot Overview")
    
    # 🔹 Introduction Section
    st.subheader("💡 Dashboard Insights")
    st.write(
        "Welcome to the AI Chatbot Analytics Dashboard! This platform provides an in-depth analysis of chatbot interactions, user engagement, sentiment trends, and topic recognition. Use the sidebar filters to refine your analysis and gain valuable insights."
    )
    
    # 🔹 Key Metrics
    st.subheader("📊 Key Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="💬 Total Interactions", value=len(df))
    
    with col2:
        avg_response_length = round(df["response_length"].mean(), 2)
        st.metric(label="📝 Avg. Response Length", value=f"{avg_response_length} words")
    
    with col3:
        unique_users = df["question"].nunique()
        st.metric(label="👥 Unique Questions", value=unique_users)
    

    

    
    # 🔹 Most Asked Questions
    st.subheader("📌 Most Frequent Questions")
    most_asked_questions = df["question"].value_counts().head(5).reset_index()
    most_asked_questions.columns = ["Question", "Count"]
    st.dataframe(most_asked_questions, use_container_width=True)

    # 🔹 Active Users Trend
    st.subheader("🚀 User Activity Over Time")
    df["date"] = df["timestamp"].dt.date
    daily_activity = df.groupby("date").size().reset_index(name="Interactions")

    # Customized plot aligned with your logo color
    fig_activity = px.bar(
        daily_activity,
        x="date",
        y="Interactions",
        title="User Activity Over Time",
        color_discrete_sequence=["#C09B3E"]  # Gold inspired by your logo
    )
    st.plotly_chart(fig_activity, use_container_width=True)
    

    
    st.markdown(
        """
        <div style="background-color:#C09B3E;padding:10px;border-radius:8px;color:black;">
            📢 Stay updated with your chatbot’s analytics and optimize interactions for better engagement!
        </div>
        """,
        unsafe_allow_html=True
    )


elif page == "Q&A Data":
    st.header("📊 Chatbot Q&A Data")
    if not df.empty:
        st.dataframe(df[['_id', 'question', 'answer', 'timestamp', 'response_length']], use_container_width=True)
    else:
        st.warning("⚠️ No data available for the selected filters.")

elif page == "Engagement Analysis":
    st.header("📈 Engagement Over Time")
    if not df.empty:
        # Make sure your timestamp column is parsed as datetime
        df["date"] = df["timestamp"].dt.date

        # Group by date
        engagement_over_time = df.groupby("date").size().reset_index(name="Interactions")

        # Create line chart with gold color from your logo
        fig = px.line(
            engagement_over_time, 
            x="date", 
            y="Interactions", 
            title="Engagement Over Time",
            markers=True,
            color_discrete_sequence=["#C09B3E"]
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("⚠️ No data available for the selected filters.")



elif page == "Sentiment Analysis":
    st.header("📈 Sentiment Analysis")
    if not df.empty:
        sentiment_counts = df["sentiment_label"].value_counts()

        fig = px.pie(
            values=sentiment_counts.values,
            names=sentiment_counts.index,
            title="Sentiment Distribution",
            color_discrete_sequence=["#C09B3E", "#F1C40F", "#6E260E"]  # Always gold-inspired colors
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No sentiment data available.")





elif page == "NER & Topics": 
    st.header("🔍 Named Entity Recognition (NER) & Topics")
    if not df.empty:
        nlp = spacy.load("en_core_web_sm")
        all_text = " ".join(df["answer"].dropna())
        doc = nlp(all_text)
        entities = [ent.text for ent in doc.ents if len(ent.text) > 2]
        entity_counts = Counter(entities)

        if entities:
            # Get the most frequent word
            most_frequent_word, most_frequent_count = entity_counts.most_common(1)[0]
            
            # Dynamic Animated Word Cloud Alternative
            st.subheader("🌍 Named Entities Word Cloud")
            wordcloud_placeholder = st.empty()
            
            for _ in range(10):  # Run animation for 10 iterations
                sampled_entities = np.random.choice(entities, min(len(entities), 100), replace=False)
                wordcloud = WordCloud(
                    width=800, height=400, background_color="white" if theme_mode == "Light" else "#0F172A", 
                    colormap="viridis", max_font_size=150
                ).generate(" ".join(sampled_entities))
                
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.imshow(wordcloud, interpolation="bilinear")
                ax.axis("off")
                
              
                
                wordcloud_placeholder.pyplot(fig)
                time.sleep(2)
            
            # Animated Bar Chart for Top Entities
            st.subheader("📊 Top Named Entities Over Time")
            entity_df = pd.DataFrame(entity_counts.most_common(10), columns=["Entity", "Count"])
            fig_bar = px.bar(
                entity_df, x="Count", y="Entity", orientation='h',
                title="Top Named Entities", animation_frame="Entity", range_x=[0, max(entity_df["Count"]) + 2],
                color_discrete_sequence=["#2ECC71"], text_auto=True
            )
            fig_bar.update_traces(textfont_size=12, textposition="outside")
            st.plotly_chart(fig_bar, use_container_width=True)

        else:
            st.warning("⚠️ No named entities found in the selected dataset.")
    else:
        st.warning("⚠️ No data available for the selected filters.")
 
elif page == "Data Export":
    st.header("📥 Export Data")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download Data as CSV", data=csv, file_name="chatbot_data.csv", mime="text/csv")

elif page == "Statistics":
    st.header("📊 Data Statistics")
    st.write(df.describe())

elif page == "Trending Topics":
    st.header("📈 Trending Topics Analysis")
    if not df.empty:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=20)
        tfidf_matrix = vectorizer.fit_transform(df["question"].dropna())
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
        top_keywords = tfidf_df.mean().sort_values(ascending=False).reset_index()
        top_keywords.columns = ["Keyword", "Importance"]
        fig_keywords = px.bar(top_keywords, x="Importance", y="Keyword", orientation='h', title="Trending Keywords")
        st.plotly_chart(fig_keywords, use_container_width=True)
    else:
        st.warning("No data available for trending topics analysis.")


elif page == "User Interaction Trends":
    st.header("📊 User Interaction Trends")
    if not df.empty:
        interaction_counts = df["question"].value_counts().reset_index()
        interaction_counts.columns = ["Question", "Count"]
        fig = px.bar(
            interaction_counts.head(10), 
            x="Count", 
            y="Question", 
            orientation='h', 
            title="Top User Questions", 
            text_auto=True,
            color_discrete_sequence=["#D4AF37"]  # Gold color matching the logo
        )
        fig.update_layout(
            plot_bgcolor="black",  # Black background for contrast
            paper_bgcolor="black",
            font=dict(color="white")  # White text for readability
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No user interaction data available.")

# 📌 Footer
st.markdown(f"""
    <div style="text-align: center; margin-top: 3rem; color: #64748B; font-size: 0.9rem;">
        AI Chatbot Admin Dashboard v2.0 • Powered by Streamlit • Updated: {datetime.now().strftime("%Y-%m-%d")}
    </div>
""", unsafe_allow_html=True)
