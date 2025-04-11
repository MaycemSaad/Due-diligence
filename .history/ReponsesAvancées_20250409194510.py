import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import tempfile
import sounddevice as sd
import scipy.io.wavfile as wav
import ollama

# --- CONFIG STREAMLIT ---
st.set_page_config(page_title="Assistant Vocal", layout="centered")
st.markdown("<h1 style='text-align: center;'>🎤 Assistant vocal IA</h1>", unsafe_allow_html=True)

# --- STYLES CHATGPT ---
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

# --- TEXT TO SPEECH ---
def speak_text(text):
    tts = gTTS(text=text, lang='fr')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")

# --- ENREGISTRER VOIX ---
def record_voice(duration=5, fs=44100):
    st.info("🎙️ Enregistrement en cours... Parlez maintenant.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    path = tempfile.NamedTemporaryFile(delete=False, suffix=".wav").name
    wav.write(path, fs, recording)
    return path

# --- RECONNAISSANCE VOCALE ---
def process_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            question = recognizer.recognize_google(audio, language="fr-FR")
            return question
        except sr.UnknownValueError:
            st.warning("❌ Voix non reconnue.")
            return None

# --- CONVERSATION AVEC CONTEXTE ---
def get_response_with_context(question):
    # Ajout de la question à l’historique
    st.session_state.messages.append({"role": "user", "text": question})

    # Construction du contexte
    messages = [{"role": "system", "content": "Tu es un assistant vocal intelligent et empathique, qui répond de manière claire et concise."}]
    for msg in st.session_state.messages:
        role = msg["role"]
        if role == "bot":  # Sécurité si l'ancien rôle a été utilisé
            role = "assistant"
        messages.append({"role": role, "content": msg["text"]})

    try:
        response = ollama.chat(
            model="mistral:latest",
            messages=messages
        )
        answer = response["message"]["content"]
        # Ajoute la réponse avec le bon rôle
        st.session_state.messages.append({"role": "assistant", "text": answer})
        speak_text(answer)
    except Exception as e:
        st.error(f"Erreur lors de l'appel IA : {e}")

# --- UI ---
st.markdown('<div class="centered-button">', unsafe_allow_html=True)
if st.button("🎙️ Appuyer pour parler", use_container_width=True):
    audio_path = record_voice()
    question = process_audio(audio_path)
    if question:
        get_response_with_context(question)
st.markdown('</div>', unsafe_allow_html=True)

# --- AFFICHAGE HISTORIQUE ---
for msg in st.session_state.messages:
    role_css = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="stChatBubble {role_css}">{msg["text"]}</div>', unsafe_allow_html=True)
