import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
import ollama
import tempfile
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

# --- CONFIG ---
st.set_page_config(page_title="Assistant Vocal", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎤 Assistant vocal IA</h1>", unsafe_allow_html=True)

# --- STYLE CHATGPT ---
st.markdown("""
<style>
.stChatBubble {
    padding: 15px;
    border-radius: 20px;
    margin: 10px;
    max-width: 80%;
    word-wrap: break-word;
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
.centered-button {
    display: flex;
    justify-content: center;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TTS ---
def speak_text(text):
    tts = gTTS(text=text, lang='fr')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")

# --- ENREGISTRER AUDIO ---
def record_voice(duration=5, fs=44100):
    st.info("🎙️ Enregistrement en cours... Parlez maintenant.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    wav.write(path, fs, recording)
    return path

# --- CONVERSATION ---
def process_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            question = recognizer.recognize_google(audio, language="fr-FR")
            st.session_state.messages.append({"role": "user", "text": question})
            return question
        except sr.UnknownValueError:
            st.warning("❌ Voix non reconnue.")
            return None

def get_response(prompt):
    try:
        response = ollama.chat(
            model="mistral:latest",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["message"]["content"]
        st.session_state.messages.append({"role": "bot", "text": answer})
        speak_text(answer)
    except Exception as e:
        st.error(f"Erreur lors de l'appel IA : {e}")

# --- UI ---

st.markdown('<div class="centered-button">', unsafe_allow_html=True)
if st.button("🎙️ Appuyer pour parler", use_container_width=True):
    audio_path = record_voice()
    question = process_audio(audio_path)
    if question:
        prompt = f"Tu es un assistant vocal. Réponds de manière claire et utile : {question}"
        get_response(prompt)
st.markdown('</div>', unsafe_allow_html=True)

# --- HISTORIQUE ---
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="stChatBubble {role}">{msg["text"]}</div>', unsafe_allow_html=True)
