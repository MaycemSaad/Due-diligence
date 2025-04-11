import streamlit as st
import ollama
import pyttsx3
import speech_recognition as sr
import tempfile
import av
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

# Config Streamlit
st.set_page_config(page_title="Voice Assistant", layout="centered")

# Initialiser TTS
tts = pyttsx3.init()
tts.setProperty("rate", 160)

# Session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Styles
st.markdown("""
<style>
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

st.title("🎙️ Assistant vocal IA")

# AudioProcessor personnalisé
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.buffer += frame.to_ndarray().tobytes()
        return frame

    def get_audio(self):
        return self.buffer

# Lancer enregistrement audio
ctx = webrtc_streamer(
    key="audio",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=1024,
    audio_processor_factory=AudioProcessor,
)

if ctx and ctx.audio_processor:
    audio_data = ctx.audio_processor.get_audio()
    if audio_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_data)
            tmp_path = tmp_file.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
            try:
                question = recognizer.recognize_google(audio, language="fr-FR")
                st.session_state.messages.append({"role": "user", "text": question})
            except sr.UnknownValueError:
                st.warning("🤷 Voix non reconnue.")
                question = ""

        if question:
            # Appel modèle IA
            prompt = f"Tu es un assistant intelligent. Réponds clairement :\n\n{question}"
            try:
                response = ollama.chat(
                    model="mistral:latest",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response["message"]["content"]
                st.session_state.messages.append({"role": "bot", "text": answer})
                tts.say(answer)
                tts.runAndWait()
            except Exception as e:
                st.error(f"Erreur lors de l'appel au modèle IA: {e}")

# Affichage de l'historique
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="stChatBubble {role}">{msg["text"]}</div>', unsafe_allow_html=True)
