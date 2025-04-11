import streamlit as st
import ollama
import pyttsx3
import speech_recognition as sr
import tempfile
from streamlit_audio_recorder import audio_recorder

# Setup basic Streamlit config
st.set_page_config(page_title="AI Chat - Voice", layout="centered")

# Text-to-speech engine (offline)
tts = pyttsx3.init()
tts.setProperty("rate", 160)

# ChatGPT-style UI
st.markdown("""
    <style>
    body { background-color: #121212; color: white; }
    .stChatBubble {
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 10px;
        max-width: 80%;
    }
    .user {
        background-color: #0B5ED7;
        color: white;
        margin-left: auto;
        text-align: right;
    }
    .bot {
        background-color: #2F2F2F;
        color: white;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗣️ ChatBot Voice Assistant")

# Use session state to store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Audio Recorder (User Input)
audio_bytes = audio_recorder(text="🎤 Click to speak", icon_size="2x")

if audio_bytes:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name

    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_path) as source:
        audio_data = recognizer.record(source)
        try:
            question = recognizer.recognize_google(audio_data)
            st.session_state.messages.append({"role": "user", "text": question})
        except sr.UnknownValueError:
            st.warning("Speech not recognized. Try again.")
            question = ""

    if question:
        # 🔍 Generate Answer
        prompt = f"You are a helpful AI assistant. Answer clearly and politely.\n\nQ: {question}\nA:"
        response = ollama.chat(
            model="mistral:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["message"]["content"]
        st.session_state.messages.append({"role": "bot", "text": answer})
        
        # 🗣️ Speak the answer
        tts.say(answer)
        tts.runAndWait()

# Display Chat Bubbles
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="stChatBubble {role_class}">{msg["text"]}</div>', unsafe_allow_html=True)
