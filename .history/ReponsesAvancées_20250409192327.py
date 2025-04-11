import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import tempfile
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
import ollama

# --- CONFIG ---
st.set_page_config(page_title="Assistant Vocal IA", layout="centered")
st.title("🎙️ Assistant vocal IA")

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
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AUDIO CAPTURE ---
class AudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.buffer = b""

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        self.buffer += frame.to_ndarray().tobytes()
        return frame

    def get_audio(self):
        return self.buffer

# --- FUNCTION : Text-to-Speech ---
def speak_text(text):
    tts = gTTS(text=text, lang='fr')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    st.audio(fp.read(), format="audio/mp3")

# --- STREAM ---
ctx = webrtc_streamer(
    key="speech",
    mode=WebRtcMode.SENDRECV,
    audio_receiver_size=1024,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"video": False, "audio": True},
    async_processing=True,
)

# --- TRAITEMENT DE L'AUDIO ---
if ctx and ctx.audio_processor:
    audio_data = ctx.audio_processor.get_audio()
    if audio_data and len(audio_data) > 10000:
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
            prompt = f"Tu es un assistant vocal intelligent. Réponds clairement et gentiment :\n\n{question}"
            try:
                response = ollama.chat(
                    model="mistral:latest",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response["message"]["content"]
                st.session_state.messages.append({"role": "bot", "text": answer})
                speak_text(answer)
            except Exception as e:
                st.error(f"Erreur IA : {e}")

# --- AFFICHAGE HISTORIQUE CONVERSATION ---
for msg in st.session_state.messages:
    role = "user" if msg["role"] == "user" else "bot"
    st.markdown(f'<div class="stChatBubble {role}">{msg["text"]}</div>', unsafe_allow_html=True)
