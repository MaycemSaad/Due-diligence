import streamlit as st
import ollama
import pyttsx3
import speech_recognition as sr
import tempfile
import av
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, ClientSettings

# Config
st.set_page_config(page_title="AI Voice Chat", layout="centered")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# TTS engine
tts = pyttsx3.init()
tts.setProperty("rate", 160)

# UI styling
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

st.title("🎙️ Voice ChatBot")

# Audio Processor for capturing speech
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.recorder = sr.Recognizer()
        self.buffer = b""
        self.audio_received = False

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm_data = frame.to_ndarray().tobytes()
        self.buffer += pcm_data
        self.audio_received = True
        return frame

    def get_audio(self):
        return self.buffer if self.audio_received else None

audio_ctx = webrtc_streamer(
    key="speech",
    mode="SENDRECV",
    audio_receiver_size=1024,
    client_settings=ClientSettings(
        media_stream_constraints={"video": False, "audio": True},
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
    ),
    audio_processor_factory=AudioProcessor,
)

if audio_ctx and audio_ctx.audio_processor and st.button("🎤 Envoyer la voix"):
    audio_data = audio_ctx.audio_processor.get_audio()
    if audio_data:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_data)
            temp_path = temp_audio.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio = recognizer.record(source)
            try:
                question = recognizer.recognize_google(audio, language="fr-FR")
                st.session_state.messages.append({"role": "user", "text": question})
            except sr.UnknownValueError:
                st.warning("🤷 Voix non reconnue.")
                question = ""

        if question:
            # 🧠 Appel au modèle
            prompt = f"Tu es un assistant intelligent et bienveillant. Réponds clairement et poliment.\n\nQuestion : {question}\nRéponse :"
            response = ollama.chat(
                model="mistral:latest",
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response["message"]["content"]
            st.session_state.messages.append({"role": "bot", "text": answer})

            # 🔊 Lecture vocale
            tts.say(answer)
            tts.runAndWait()

# Affichage style chat
for msg in st.session_state.messages:
    role_class = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="stChatBubble {role_class}">{msg["text"]}</div>', unsafe_allow_html=True)
