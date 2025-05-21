def show_due_diligence_app():
    from gridfs import GridFS    
    import os
    import streamlit as st
    import ollama
    import glob
    from pptx.enum.shapes import MSO_SHAPE
    from pptx.enum.text import PP_ALIGN
    import re
    import bcrypt
    import pdfplumber
    import PyPDF2
    import speech_recognition as sr
    from io import BytesIO
    from pymongo import MongoClient
    from datetime import datetime, timezone
    from sklearn.feature_extraction.text import TfidfVectorizer
    import numpy as np
    import pandas as pd
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    import pyttsx3
    import tempfile
    import pyttsx3
    import tempfile
    import time
    from fpdf import FPDF
    import os
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN
    from pptx.enum.shapes import MSO_SHAPE
    from datetime import datetime, timezone
    from ExtractionNLP import extract_text_from_pdf, clean_text, summarize_text
    from user_Profile import show_user_profile
    from Compliance_and_risk_tools import show_Tools
    from Contrat import show_generated_contrat
        # ... (keep all your existing imports)
    import speech_recognition as sr
    from gtts import gTTS
    import pygame
    import tempfile
    import time

    # ... (keep all your existing code until the MODEL_NAME definition)

    MODEL_NAME = "mistral:latest"


    # ⛓️ Environnement & DB
    os.environ["OLLAMA_NUM_GPU_LAYERS"] = "100"
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    collection = db["qa_sessions"]

    if "history" not in st.session_state:
        st.session_state.history = []

    if "chat_context" not in st.session_state:
        cleaned_texts_dir = "cleaned_texts"
        cleaned_texts = {
            txt_file: open(txt_file, "r", encoding="utf-8").read()
            for txt_file in glob.glob(f"{cleaned_texts_dir}/*.txt")
        }
        st.session_state.chat_context = dict(cleaned_texts)

    if "session_name" not in st.session_state:
        st.session_state.session_name = f"Session-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

        # === PAGE SWITCHER ===
    if "page" not in st.session_state:
        st.session_state.page = "main"  # page par défaut

    if st.session_state.page == "profile":
        show_user_profile()  # 🔥 tu appelles ici la page de profil
        st.stop()  # ❗ On arrête tout après l'affichage du profil

    if st.session_state.page == "Generate Contrat":
        show_generated_contrat()
        st.stop()
        

    if st.session_state.page == "Compliance & Risk Tools":
        show_Tools()  # 🔥 tu appelles ici la page de profil
        st.stop()     
    
    def force_question_output(doc_text, max_retries=3):
        base_prompt = f"""
    You are NOT allowed to summarize this document.

    Your task is to ONLY generate exactly 3 due diligence questions based on the document below.

    ❌ Do NOT write an intro or summary.  
    ✅ Each line must start with a number and end with a question mark.

    EXAMPLE FORMAT (and nothing else):
    1. What are the company’s internal controls for AML compliance?
    2. How does the business mitigate regulatory risk across jurisdictions?
    3. What client onboarding procedures are in place to detect fraud?

    📄 DOCUMENT START:
    {doc_text}
    📄 DOCUMENT END.
    """
        for attempt in range(max_retries):
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": base_prompt}],
                options={"num_predict": 200}
            )
            raw_output = response["message"]["content"].strip()
            questions = re.findall(r"\d\.\s+(.*?\?)", raw_output)

            if len(questions) == 3:
                return questions

        return []

    # === Charger les textes nettoyés disponibles ===
    cleaned_texts_dir = "cleaned_texts"
    cleaned_texts = {
        txt_file: open(txt_file, "r", encoding="utf-8").read()
        for txt_file in glob.glob(f"{cleaned_texts_dir}/*.txt")
    }




    def log_event(user_email, event, details=""):
        db["audit_logs"].insert_one({
            "user": user_email,
            "event": event,
            "details": details,
            "timestamp": datetime.now(timezone.utc)
        })

    def generate_compliance_pdf(session_name, summary, history, red_flags=None, reviewer="Due Diligence Bot"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # --- Title ---
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Compliance Audit Report", ln=True, align='C')

        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Session: {session_name}", ln=True)
        pdf.cell(0, 10, f"Date: {datetime.today().strftime('%Y-%m-%d')}", ln=True)
        pdf.cell(0, 10, f"Reviewer: {reviewer}", ln=True)
        pdf.ln(10)

        # --- Executive Summary ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Executive Summary", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, summary)
        pdf.ln(5)

        # --- Red Flags ---
        if red_flags:
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "Red Flags Detected", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 10, ", ".join(red_flags))
            pdf.ln(5)

        # --- Q&A ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Questions & Answers", ln=True)

        for i in range(0, len(history), 2):
            user_msg = history[i]
            bot_msg = history[i+1] if i+1 < len(history) else {"content": "", "tags": []}

            if user_msg["role"] != "user":
                continue

            pdf.set_font("Arial", 'B', 12)
            pdf.multi_cell(0, 10, f"{i//2 + 1}. {user_msg['content']}")
            pdf.set_font("Arial", '', 12)
            pdf.multi_cell(0, 10, bot_msg["content"])

            if bot_msg.get("tags"):
                pdf.set_font("Arial", 'I', 10)
                pdf.cell(0, 8, f"Tags: {', '.join(bot_msg['tags'])}", ln=True)

            pdf.ln(5)

        # --- Signature Section ---
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Validation & Signature", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, "Signature: ____________________________", ln=True)
        pdf.cell(0, 10, "Date: _________________________________", ln=True)

        # ✅ Export en mémoire compatible Streamlit
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        pdf_output = BytesIO(pdf_bytes)
        return pdf_output



    # 🔊 Enhanced Audio Initialization with device selection
    def init_audio():
        try:
            # Get available audio devices
            pygame.mixer.quit()
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
            pygame.mixer.init()
            
            # Try to find the best microphone
            mic_list = sr.Microphone.list_microphone_names()
            st.session_state.mic_list = mic_list
            
            if not hasattr(st.session_state, 'selected_mic_index'):
                # Try to find a good default microphone
                default_mic_index = None
                for i, name in enumerate(mic_list):
                    if 'microphone' in name.lower() or 'mic' in name.lower():
                        default_mic_index = i
                        break
                st.session_state.selected_mic_index = default_mic_index if default_mic_index else 0
            
            return True
        except Exception as e:
            st.error(f"❌ Audio init failed: {str(e)}")
            return False

    # 🔊 Advanced Voice Listening with adaptive thresholds
    def listen_to_user():
        """Enhanced voice capture with better recognition"""
        if not init_audio():
            return None
            
        r = sr.Recognizer()
        # Dynamic configuration based on environment
        r.energy_threshold = 300  # Start with sensitive setting
        r.dynamic_energy_threshold = True
        r.dynamic_energy_adjustment_damping = 0.15
        r.dynamic_energy_ratio = 1.5
        r.pause_threshold = 0.8
        r.phrase_threshold = 0.3
        r.non_speaking_duration = 0.5
        
        selected_mic = sr.Microphone(device_index=st.session_state.selected_mic_index)
        
        try:
            with selected_mic as source:
                # Visual feedback during calibration
                calibration_status = st.empty()
                calibration_status.info("🔊 Calibrating microphone... (Please stay silent)")
                
                # More thorough calibration
                r.adjust_for_ambient_noise(source, duration=3)
                current_threshold = r.energy_threshold
                
                
                # Listen with visual feedback
                listening_status = st.empty()
                
                
                audio = r.listen(source, timeout=6, phrase_time_limit=12)
                listening_status.empty()
                
                # Save audio for debugging
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    tmp.write(audio.get_wav_data())
                    st.session_state.last_audio = tmp.name
                
                # Try multiple recognition services as fallback
                try:
                    text = r.recognize_google(audio, language="en-US")
                    st.session_state.last_recognition_service = "Google"
                except sr.UnknownValueError:
                    try:
                        text = r.recognize_whisper(audio, language="english")
                        st.session_state.last_recognition_service = "Whisper"
                    except:
                        raise sr.UnknownValueError("All recognition methods failed")
                
                st.success(f"🎤 You said: {text} (via {st.session_state.last_recognition_service})")
                return text
                
        except sr.WaitTimeoutError:
            st.warning("⏱️ No speech detected. Try speaking louder or check microphone")
        except sr.UnknownValueError:
            st.error("🔇 Could not understand audio. Try speaking more clearly")
        except sr.RequestError as e:
            st.error(f"🌐 API Error: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            
        return None

    # 🔊 Robust Speech Synthesis
    def speak_response(text):
        """Improved text-to-speech with better error handling"""
        if not text:
            return False
            
        max_retries = 2
        temp_path = None
        
        for attempt in range(max_retries):
            try:
                # Create temp file with unique name
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                    temp_path = tmp.name
                
                # Generate speech with careful settings
                tts = gTTS(
                    text=text,
                    lang='en',
                    slow=False,
                    lang_check=False  # More permissive language handling
                )
                tts.save(temp_path)
                
                # Ensure file is fully written
                time.sleep(0.3)
                
                # Initialize audio if needed
                if not pygame.mixer.get_init():
                    if not init_audio():
                        raise Exception("Audio system not available")
                
                # Play with careful resource management
                pygame.mixer.music.load(temp_path)
                pygame.mixer.music.play()
                
                # Visual feedback during playback
                with st.spinner("🔊 Playing response..."):
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                
                break  # Success - exit retry loop
                
            except Exception as e:
                if attempt == max_retries - 1:  # Last attempt failed
                    st.error(f"🔇 Speech failed: {str(e)}")
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except:
                            pass
                    return False
                time.sleep(0.5)  # Wait before retry
                
        # Cleanup
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        except:
            pass
            
        return True

    # 🎙️ Professional Voice Chat Interface
    def voice_chat_loop():
        """Enhanced voice conversation with better UX"""
        st.header("🎙️ Voice Assistant Mode")
        
        # Microphone selection dropdown
        if hasattr(st.session_state, 'mic_list'):
            new_mic = st.selectbox(
                "Select Microphone",
                st.session_state.mic_list,
                index=st.session_state.selected_mic_index
            )
            st.session_state.selected_mic_index = st.session_state.mic_list.index(new_mic)
        
        # Initialize audio system
        if not init_audio():
            st.session_state.voice_mode = False
            st.error("Audio system unavailable - exiting voice mode")
            st.rerun()
        
        # Display conversation history with avatars
        chat_container = st.container()
        with chat_container:
            for i in range(0, len(st.session_state.history), 2):
                if i+1 < len(st.session_state.history):
                    user_msg = st.session_state.history[i]
                    assistant_msg = st.session_state.history[i+1]
                    
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(user_msg["content"])
                    
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(assistant_msg["content"])
                        if assistant_msg.get("tags"):
                            render_tags(assistant_msg["tags"])
        
        # Listen phase with visual feedback
        listen_container = st.empty()
        with listen_container.container():
            st.markdown("### Speak your question")
            st.write("Waiting for your voice input...")
            
            question = None
            with st.spinner("🔊 Initializing microphone..."):
                question = listen_to_user()
            
            if not question:
                # Show enhanced retry options
                cols = st.columns(3)
                with cols[0]:
                    if st.button("🔄 Retry Listening", help="Try listening again"):
                        st.rerun()
                with cols[1]:
                    if st.button("🎙️ Change Mic", help="Select different microphone"):
                        st.session_state.selected_mic_index = None
                        st.rerun()
                with cols[2]:
                    if st.button("❌ Exit Voice", help="Return to text mode"):
                        st.session_state.voice_mode = False
                        st.rerun()
                return
                    
        # Processing phase with progress
        with st.spinner("🤖 Analyzing your question..."):
            progress_bar = st.progress(0)
            
            # Simulate processing steps
            for i in range(3):
                time.sleep(0.3)
                progress_bar.progress((i + 1) * 25)
                
            context = find_relevant_context(question, st.session_state.chat_context)
            progress_bar.progress(75)
            
            answer = generate_answer_with_ollama(question, context)
            tags = classify_answer_tags(answer)
            progress_bar.progress(100)
            
            # Save conversation
            st.session_state.history.extend([
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer, "tags": tags}
            ])
            save_conversation(st.session_state.session_name, st.session_state.history)
            
        # Display response
        with chat_container:
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(answer)
                if tags:
                    render_tags(tags)
            
        # Play audio response
        speak_response(answer)
            
        cols = st.columns(3)
        with cols[0]:
            if st.button("🎤 Ask Another", key="continue", help="Ask another question"):
                st.rerun()
        with cols[1]:
            if st.button("🔊 Replay Answer", key="replay", help="Hear the last answer again"):
                speak_response(answer)
        with cols[2]:
            if st.button("❌ Exit Voice", key="exit", help="Return to text mode"):
                st.session_state.voice_mode = False
                st.rerun()


    import speech_recognition as sr
    import streamlit as st
    from pydub import AudioSegment

    # 🔎 Calibration et enregistrement du microphone
# 🔎 Calibration et enregistrement du microphone
    def test_microphone():
        """Test le microphone et affiche l'audio capturé"""

        # ✅ Import forcé de streamlit pour éviter les erreurs
        try:
            import streamlit as st
        except ImportError:
            print("❌ Erreur : Streamlit n'est pas importé correctement.")
            return
        
        import speech_recognition as sr
        r = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                st.info("🔎 Calibration du microphone...")
                r.adjust_for_ambient_noise(source, duration=2)
                st.info(f"🔈 Niveau de bruit détecté : {r.energy_threshold}")
                st.info("🎤 Parlez maintenant... (10 secondes max)")
                
                # ✅ Écoute de l'audio
                audio = r.listen(source, timeout=10, phrase_time_limit=15)

                # 📝 Sauvegarde temporaire de l'audio pour vérification
                with open("test_audio.wav", "wb") as f:
                    f.write(audio.get_wav_data())
                
                st.success("✅ Audio capturé. Vérifiez le fichier ci-dessous pour l'écouter.")
                st.audio("test_audio.wav", format="audio/wav")

        except Exception as e:
            # ➡️ Correction : ajout explicite de st.error
            st.error(f"❌ Erreur lors de l'initialisation du microphone : {e}")
            return None

    # --- Auth utils ---
    def hash_password(password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def verify_password(password, hashed):
        return bcrypt.checkpw(password.encode(), hashed)

    # --- Auth & Session ---
    if "user" not in st.session_state:
        st.session_state.user = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = {}  # Initialize user_info    

    if not st.session_state.user:
        st.subheader("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = db["users"].find_one({"email": email})


            if user and verify_password(password, user["password"]):
                st.session_state.user = user 
                st.session_state.user_email = user["email"]  # ➔ 🔥 juste email
                st.session_state.user_info = user  # 🔥 en bonus on garde tout le profil
                st.success(f"✅ Logged in as: {user['email']}")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        st.stop()

    MODEL_NAME = "mistral:latest"

    # 📜 Préchargement de textes si dispos
    cleaned_texts_dir = "cleaned_texts"
    cleaned_texts = {txt_file: open(txt_file, "r", encoding="utf-8").read() for txt_file in glob.glob(f"{cleaned_texts_dir}/*.txt")}

    # 🔍 Recherche de contexte
    def find_relevant_context(question, texts, max_words=300):
        if not texts: return ""
        vectorizer = TfidfVectorizer(stop_words="english")
        corpus = list(texts.values()) + [question]
        tfidf_matrix = vectorizer.fit_transform(corpus)
        similarity_scores = (tfidf_matrix[-1] @ tfidf_matrix[:-1].T).toarray()[0]
        best_match_idx = np.argmax(similarity_scores)
        return list(texts.values())[best_match_idx][:max_words]


    # 🤖 Appel Ollama
    def generate_answer_with_ollama(question, context):
        if not context.strip():
            context = "No specific context available. Please answer based on your digital finance expertise."
        prompt = f"""
        You are a due diligence expert. Answer the question below using only this context if possible:

        CONTEXT:
        {context}

        QUESTION:
        {question}

        INSTRUCTIONS:
        - Be complete, minimum 4 sentences.
        - If context is insufficient, answer with industry knowledge and suggest additional details needed.

        ANSWER:
        """
        response = ollama.chat(model=MODEL_NAME, messages=[{"role": "user", "content": prompt}], options={"num_predict": 250})
        return response['message']['content'].strip()

    # 📄 Lecture fichier
    def extract_text_from_file(uploaded_file):
        ext = uploaded_file.name.lower()
        text = ""
        if ext.endswith(".txt"):
            text = uploaded_file.read().decode("utf-8")
        elif ext.endswith(".pdf"):
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    content = page.extract_text()
                    if content:
                        text += content + "\n"
        return text

    def classify_answer_tags(answer_text):
            prompt = f"""
        You are an AI assistant analyzing answers in a due diligence assistant.

        Based on the following answer, extract **3 to 5 relevant tags** that summarize the key topics or themes discussed.

        🔹 The tags must:
        - Be concise (1–3 words each)
        - Be meaningful (e.g. "KYC", "Digital Assets", "Blockchain Strategy")
        - Not generic ("text", "document", etc.)
        - Not come from a predefined list — generate them based on the content.

        Return in this format only:
        Tags: [tag1, tag2, tag3, ...]


        ANSWER:
        {answer_text}
        """
            response = ollama.chat(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                options={"num_predict": 150}
            )
            raw = response["message"]["content"].strip()

            # Extraction des tags sous forme de liste
            match = re.search(r"\[([^\]]+)\]", raw)
            if match:
                return [tag.strip() for tag in match.group(1).split(",")]
            return []


    def speak_text(text):
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        
        # Créer un fichier temporaire pour stocker l'audio
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        temp_path = temp_file.name
        temp_file.close()

        engine.save_to_file(text, temp_path)
        engine.runAndWait()

        # 🔁 Attendre un peu que le fichier soit écrit (important pour certains systèmes)
        time.sleep(1)

        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
            st.audio(temp_path, format='audio/mp3')
        else:
            st.error("⚠️ Audio file was not generated correctly.")

    # 🔎 Red Flags à surveiller
    def detect_red_flags_with_highlight(text):
        red_flags = [
            "ponzi", "scam", "non audited", "data breach",
            "offshore", "non compliant", "no license",
            "sanction", "money laundering", "anonymous",
            "rug pull", "fraud", "suspicious"
        ]
        
        # Découper le texte en phrases
        sentences = re.split(r'(?<=[.?!])\s+', text)

        matched_flags = set()
        highlighted_sentences = []

        for sentence in sentences:
            original_sentence = sentence
            for flag in red_flags:
                pattern = re.compile(rf'\b({re.escape(flag)})\b', re.IGNORECASE)
                if pattern.search(sentence):
                    sentence = pattern.sub(r'<mark>\1</mark>', sentence)
                    matched_flags.add(flag.lower())
            if sentence != original_sentence:
                highlighted_sentences.append(sentence.strip())

        return sorted(matched_flags), highlighted_sentences

    def evaluate_answer_with_ollama(question, answer):
        prompt = f"""
    You are a senior due diligence reviewer.

    Evaluate the following answer to the question based on:
    - Relevance
    - Completeness
    - Usefulness in due diligence

    Format your response exactly like this:
    Score: X/10  
    Comment: <Your feedback>

    QUESTION:
    {question}

    ANSWER:
    {answer}
    """
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 200}
        )
        result = response["message"]["content"].strip()

        # Extraction du score et du commentaire
        score_match = re.search(r"Score:\s*(\d+)/10", result)
        comment_match = re.search(r"Comment:\s*(.*)", result, re.DOTALL)

        score = int(score_match.group(1)) if score_match else 0
        comment = comment_match.group(1).strip() if comment_match else "No comment."

        return score, comment
    # 📤 PowerPoint Générateur

    def generate_pptx(session_name, summary_text, history=None, logo_path="logo.png"):
        from pptx import Presentation
        from pptx.util import Inches, Pt
        from pptx.dml.color import RGBColor
        from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.enum.dml import MSO_THEME_COLOR
        from io import BytesIO
        from datetime import datetime
        import os
        import tempfile
        from PIL import Image
        import requests
        from io import BytesIO as BIO

        # Configuration de base
        prs = Presentation()
        prs.slide_width = Inches(13.333)  # Format 16:9
        prs.slide_height = Inches(7.5)

        # Couleurs professionnelles
        COLORS = {
            "primary": RGBColor(0, 32, 96),       # Bleu foncé corporate
            "secondary": RGBColor(0, 84, 159),     # Bleu moyen
            "accent": RGBColor(227, 114, 34),      # Orange vif
            "light": RGBColor(235, 241, 247),      # Bleu très clair
            "dark": RGBColor(51, 51, 51),          # Gris foncé
            "white": RGBColor(255, 255, 255),
            "success": RGBColor(40, 167, 69),      # Vert
            "warning": RGBColor(255, 193, 7),      # Jaune
            "danger": RGBColor(220, 53, 69)        # Rouge
        }

        # Styles de police
        TITLE_FONT = {"name": "Arial", "size": Pt(36), "bold": True, "color": COLORS["white"]}
        SUBTITLE_FONT = {"name": "Arial", "size": Pt(24), "color": COLORS["white"]}
        SECTION_FONT = {"name": "Arial", "size": Pt(28), "bold": True, "color": COLORS["primary"]}
        BODY_FONT = {"name": "Arial", "size": Pt(14), "color": COLORS["dark"]}
        BULLET_FONT = {"name": "Arial", "size": Pt(18), "color": COLORS["dark"]}
        CAPTION_FONT = {"name": "Arial", "size": Pt(12), "italic": True, "color": COLORS["secondary"]}

        # Télécharger des icônes depuis Flaticon (exemples)
        ICON_URLS = {
            "risk": "https://cdn-icons-png.flaticon.com/512/2889/2889676.png",
            "compliance": "https://cdn-icons-png.flaticon.com/512/1570/1570887.png",
            "summary": "https://cdn-icons-png.flaticon.com/512/3652/3652191.png",
            "qa": "https://cdn-icons-png.flaticon.com/512/711/711319.png",
            "recommendation": "https://cdn-icons-png.flaticon.com/512/3281/3281289.png"
        }

        def download_icon(url, size=(100, 100)):
            try:
                response = requests.get(url)
                img = Image.open(BIO(response.content))
                img.thumbnail(size)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
                img.save(temp_file.name)
                return temp_file.name
            except:
                return None

        def add_slide_with_layout(layout_idx=6):
            return prs.slides.add_slide(prs.slide_layouts[layout_idx])

        # In your generate_pptx function
        def add_title_slide():
            slide = add_slide_with_layout()
            
            # Background with gradient
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.gradient()
            bg.fill.gradient_angle = 45
            bg.fill.gradient_stops[0].color.rgb = COLORS["primary"]
            bg.fill.gradient_stops[1].color.rgb = COLORS["secondary"]
            
            # Logo
            if logo_path and os.path.exists(logo_path):
                slide.shapes.add_picture(logo_path, Inches(10), Inches(0.5), height=Inches(0.8))
            
            # Title
            title = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(8), Inches(2))
            tf = title.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "DUE DILIGENCE REPORT"
            run.font.size = TITLE_FONT["size"]
            run.font.bold = TITLE_FONT["bold"]
            run.font.color.rgb = TITLE_FONT["color"]
            run.font.name = TITLE_FONT["name"]
            p.alignment = PP_ALIGN.LEFT
            
            # Subtitle
            subtitle = slide.shapes.add_textbox(Inches(1), Inches(3.5), Inches(8), Inches(1))
            tf = subtitle.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "Detailed Analysis & Recommendations"
            run.font.size = SUBTITLE_FONT["size"]
            run.font.color.rgb = SUBTITLE_FONT["color"]
            run.font.name = SUBTITLE_FONT["name"]
            
            # Session information
            info = slide.shapes.add_textbox(Inches(1), Inches(5), Inches(8), Inches(1.5))
            tf = info.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = f"Client: {st.session_state.user_info.get('company', 'N/A')}\n"  # Safely access user_info
            run.text += f"Session: {session_name}\n"
            run.text += f"Date: {datetime.today().strftime('%B %d, %Y')}"
            run.font.size = Pt(16)
            run.font.color.rgb = COLORS["white"]
            
            # Decorative line
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(6.8), Inches(3), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS["accent"]



        def add_summary_slide():
            slide = add_slide_with_layout()
            
            # Background
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLORS["light"]
            
            # Icône
            icon_path = download_icon(ICON_URLS["summary"])
            if icon_path:
                slide.shapes.add_picture(icon_path, Inches(10.5), Inches(0.5), height=Inches(1))
            
            # Titre de section
            title = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(8), Inches(1))
            tf = title.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "EXECUTIVE SUMMARY"
            run.font.size = SECTION_FONT["size"]
            run.font.bold = SECTION_FONT["bold"]
            run.font.color.rgb = SECTION_FONT["color"]
            
            # Ligne de séparation
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.2), Inches(4), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS["accent"]
            
            # Contenu du résumé
            content = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(11), Inches(4.5))
            tf = content.text_frame
            tf.word_wrap = True
            
            # Formatage du texte avec des puces
            paragraphs = summary_text.split('\n')
            for para in paragraphs[:10]:  # Limiter à 10 paragraphes max
                if para.strip():
                    p = tf.add_paragraph()
                    p.text = para.strip()
                    p.font.size = BODY_FONT["size"]
                    p.font.color.rgb = BODY_FONT["color"]
                    p.level = 0
                    p.space_after = Pt(12)
            
            # Note en bas de page
            footer = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12), Inches(0.8))
            tf = footer.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "Confidential - For internal use only"
            run.font.size = CAPTION_FONT["size"]
            run.font.italic = CAPTION_FONT["italic"]
            run.font.color.rgb = CAPTION_FONT["color"]

        def add_qa_slides():
            if not history or len(history) < 2:
                return
                
            slide = add_slide_with_layout()
            
            # Background
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLORS["light"]
            
            # Icône
            icon_path = download_icon(ICON_URLS["qa"])
            if icon_path:
                slide.shapes.add_picture(icon_path, Inches(10.5), Inches(0.5), height=Inches(1))
            
            # Titre de section
            title = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(8), Inches(1))
            tf = title.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "KEY QUESTIONS & ANSWERS"
            run.font.size = SECTION_FONT["size"]
            run.font.bold = SECTION_FONT["bold"]
            run.font.color.rgb = SECTION_FONT["color"]
            
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.2), Inches(4), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS["accent"]
            
            # Contenu Q&A
            y_pos = Inches(1.6)
            qa_count = 0
            
            for i in range(0, len(history), 2):
                if qa_count >= 3:  # 3 Q&A par slide max
                    slide = add_slide_with_layout()
                    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
                    bg.fill.solid()
                    bg.fill.fore_color.rgb = COLORS["light"]
                    y_pos = Inches(1.6)
                    qa_count = 0
                
                user_msg = history[i]
                assistant_msg = history[i+1] if (i+1) < len(history) else None
                
                # Question
                q_box = slide.shapes.add_textbox(Inches(0.7), y_pos, Inches(11), Inches(0.8))
                tf = q_box.text_frame
                p = tf.paragraphs[0]
                run = p.add_run()
                run.text = f"Q: {user_msg['content']}"
                run.font.size = Pt(16)
                run.font.bold = True
                run.font.color.rgb = COLORS["primary"]
                y_pos += Inches(0.9)
                
                # Réponse
                if assistant_msg:
                    a_box = slide.shapes.add_textbox(Inches(1), y_pos, Inches(10.5), Inches(1.2))
                    tf = a_box.text_frame
                    p = tf.paragraphs[0]
                    run = p.add_run()
                    run.text = f"A: {assistant_msg['content'][:500]}"  # Limiter la longueur
                    run.font.size = Pt(14)
                    run.font.color.rgb = COLORS["dark"]
                    
                    # Tags
                    if assistant_msg.get("tags"):
                        tag_box = slide.shapes.add_textbox(Inches(1), y_pos + Inches(1.1), Inches(10.5), Inches(0.5))
                        tf = tag_box.text_frame
                        p = tf.paragraphs[0]
                        run = p.add_run()
                        run.text = "Tags: " + ", ".join(assistant_msg["tags"])
                        run.font.size = Pt(12)
                        run.font.italic = True
                        run.font.color.rgb = COLORS["secondary"]
                    
                    y_pos += Inches(1.7)
                    qa_count += 1

        def add_risk_analysis_slide():
            slide = add_slide_with_layout()
            
            # Background
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLORS["light"]
            
            # Icône
            icon_path = download_icon(ICON_URLS["risk"])
            if icon_path:
                slide.shapes.add_picture(icon_path, Inches(10.5), Inches(0.5), height=Inches(1))
            
            # Titre
            title = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(8), Inches(1))
            tf = title.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "RISK ANALYSIS"
            run.font.size = SECTION_FONT["size"]
            run.font.bold = SECTION_FONT["bold"]
            run.font.color.rgb = SECTION_FONT["color"]
            
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.2), Inches(3), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS["danger"]
            
            # Matrice de risque (exemple)
            risk_matrix = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(1.6), Inches(5), Inches(3.5))
            risk_matrix.fill.solid()
            risk_matrix.fill.fore_color.rgb = COLORS["white"]
            risk_matrix.line.color.rgb = COLORS["dark"]
            risk_matrix.line.width = Pt(1)
            
            # Ajouter des éléments à la matrice
            risks = [
                ("Regulatory", "High", COLORS["danger"]),
                ("Operational", "Medium", COLORS["warning"]),
                ("Financial", "Low", COLORS["success"]),
                ("Reputational", "Medium", COLORS["warning"])
            ]
            
            y_pos = Inches(1.8)
            for risk, level, color in risks:
                # Bullet point
                bullet = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), y_pos, Inches(0.3), Inches(0.3))
                bullet.fill.solid()
                bullet.fill.fore_color.rgb = color
                
                # Texte du risque
                risk_text = slide.shapes.add_textbox(Inches(1.2), y_pos, Inches(2), Inches(0.3))
                tf = risk_text.text_frame
                p = tf.paragraphs[0]
                run = p.add_run()
                run.text = risk
                run.font.size = Pt(14)
                run.font.bold = True
                
                # Niveau de risque
                level_text = slide.shapes.add_textbox(Inches(3.5), y_pos, Inches(1.5), Inches(0.3))
                tf = level_text.text_frame
                p = tf.paragraphs[0]
                run = p.add_run()
                run.text = level
                run.font.size = Pt(14)
                run.font.color.rgb = color
                
                y_pos += Inches(0.5)
            
            # Légende
            legend = slide.shapes.add_textbox(Inches(6), Inches(1.6), Inches(4), Inches(1))
            tf = legend.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "Risk Assessment Legend:"
            run.font.size = Pt(12)
            run.font.bold = True
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "High: Immediate action required"
            run.font.size = Pt(10)
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Medium: Monitor closely"
            run.font.size = Pt(10)
            p = tf.add_paragraph()
            run = p.add_run()
            run.text = "Low: Acceptable risk"
            run.font.size = Pt(10)

        def add_recommendations_slide():
            slide = add_slide_with_layout()
            
            # Background
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.solid()
            bg.fill.fore_color.rgb = COLORS["light"]
            
            # Icône
            icon_path = download_icon(ICON_URLS["recommendation"])
            if icon_path:
                slide.shapes.add_picture(icon_path, Inches(10.5), Inches(0.5), height=Inches(1))
            
            # Titre
            title = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(8), Inches(1))
            tf = title.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "RECOMMENDATIONS & NEXT STEPS"
            run.font.size = SECTION_FONT["size"]
            run.font.bold = SECTION_FONT["bold"]
            run.font.color.rgb = SECTION_FONT["color"]
            
            line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.2), Inches(5), Inches(0.1))
            line.fill.solid()
            line.fill.fore_color.rgb = COLORS["accent"]
            
            # Recommandations
            recommendations = [
                "Implement enhanced KYC procedures for all new clients",
                "Conduct a full audit of compliance controls within 30 days",
                "Develop a risk mitigation plan for regulatory changes",
                "Train staff on updated AML policies quarterly",
                "Establish a compliance task force with monthly reporting"
            ]
            
            y_pos = Inches(1.6)
            for i, rec in enumerate(recommendations, 1):
                # Numéro
                num = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.7), y_pos, Inches(0.4), Inches(0.4))
                num.fill.solid()
                num.fill.fore_color.rgb = COLORS["accent"]
                num.line.color.rgb = COLORS["white"]
                num.line.width = Pt(1)
                num_text = slide.shapes.add_textbox(Inches(0.7), y_pos, Inches(0.4), Inches(0.4))
                tf = num_text.text_frame
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                run = p.add_run()
                run.text = str(i)
                run.font.size = Pt(14)
                run.font.bold = True
                run.font.color.rgb = COLORS["white"]
                
                # Texte de recommandation
                rec_text = slide.shapes.add_textbox(Inches(1.2), y_pos, Inches(8), Inches(0.6))
                tf = rec_text.text_frame
                p = tf.paragraphs[0]
                run = p.add_run()
                run.text = rec
                run.font.size = BULLET_FONT["size"]
                run.font.color.rgb = BULLET_FONT["color"]
                
                y_pos += Inches(0.7)
            
            # Timeline
            timeline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6), Inches(1.6), Inches(4), Inches(2.5))
            timeline.fill.solid()
            timeline.fill.fore_color.rgb = COLORS["white"]
            timeline.line.color.rgb = COLORS["secondary"]
            timeline.line.width = Pt(2)
            
            # Titre timeline
            timeline_title = slide.shapes.add_textbox(Inches(6.2), Inches(1.7), Inches(3.6), Inches(0.4))
            tf = timeline_title.text_frame
            p = tf.paragraphs[0]
            run = p.add_run()
            run.text = "Implementation Timeline"
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = COLORS["primary"]
            
            # Étapes timeline
            steps = [
                ("Immediate", "KYC Update"),
                ("30 Days", "Compliance Audit"),
                ("60 Days", "Risk Plan"),
                ("Ongoing", "Training")
            ]
            
            y_pos_t = Inches(2.2)
            for when, what in steps:
                step = slide.shapes.add_textbox(Inches(6.2), y_pos_t, Inches(3.6), Inches(0.4))
                tf = step.text_frame
                p = tf.paragraphs[0]
                run = p.add_run()
                run.text = f"• {when}: {what}"
                run.font.size = Pt(12)
                y_pos_t += Inches(0.4)

        def add_closing_slide():
            slide = add_slide_with_layout()
            
            # Background avec dégradé
            bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
            bg.fill.gradient()
            bg.fill.gradient_angle = 315
            bg.fill.gradient_stops[0].color.rgb = COLORS["primary"]
            bg.fill.gradient_stops[1].color.rgb = COLORS["secondary"]
            
            # Message de clôture
            closing = slide.shapes.add_textbox(Inches(2), Inches(3), Inches(8), Inches(1.5))
            tf = closing.text_frame
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = "Thank You"
            run.font.size = Pt(48)
            run.font.bold = True
            run.font.color.rgb = COLORS["white"]
            
            # Coordonnées
            contact = slide.shapes.add_textbox(Inches(4), Inches(4.5), Inches(4), Inches(1))
            tf = contact.text_frame
            p = tf.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            run = p.add_run()
            run.text = "Contact: compliance@yourcompany.com"
            run.font.size = Pt(18)
            run.font.color.rgb = COLORS["light"]
            
            # Logo en bas
            if logo_path and os.path.exists(logo_path):
                slide.shapes.add_picture(logo_path, Inches(5.5), Inches(6), height=Inches(0.8))

        # Construction de la présentation
        add_title_slide()
        add_summary_slide()
        add_qa_slides()
        add_risk_analysis_slide()
        add_recommendations_slide()
        add_closing_slide()

        # Enregistrement en mémoire
        pptx_io = BytesIO()
        prs.save(pptx_io)
        pptx_io.seek(0)
        
        # Nettoyage des fichiers temporaires
        for icon in ICON_URLS.values():
            temp_path = download_icon(icon)
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
        
        return pptx_io
    def render_tags(tags):
        tag_html = ' '.join([
            f'<span style="background-color:#343541;padding:5px 10px;border-radius:12px;color:white;font-size:12px;margin-right:5px;">{tag}</span>'
            for tag in tags
        ])
        st.markdown(tag_html, unsafe_allow_html=True)
    # 💾 Sauvegarde MongoDB

    def save_conversation(session_name, history):
        for msg in history:
            if "tags" not in msg:
                msg["tags"] = []

        collection.update_one(
            {"session": session_name, "user_email": st.session_state.user},
            {
                "$set": {
                    "messages": history,
                    "timestamp": datetime.now(timezone.utc),
                    "user_email": st.session_state.user,
                    "session_title": st.session_state.session_title if "session_title" in st.session_state else session_name
                }
            },
            upsert=True
        )


    def chunk_text(text, max_chars=3000):
        return [text[i:i+max_chars] for i in range(0, len(text), max_chars)]



    # 🔐 INIT SESSION STATE - Avant tout usage
    timestamp_now = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    if "history" not in st.session_state:
        st.session_state.history = []
    if "chat_context" not in st.session_state:
        st.session_state.chat_context = dict(cleaned_texts)
    if "session_name" not in st.session_state:
        st.session_state.session_name = f"Session-{timestamp_now}"

    st.markdown("<h1 style='text-align: center;'>💼 TawaCheck Chatbot </h1>", unsafe_allow_html=True)
    if "just_reset" in st.session_state:
        st.toast("🆕 Nouvelle session démarrée.")
        del st.session_state["just_reset"]

   


    # 📎 Upload document
    st.sidebar.title("📎 Document Context")
    st.markdown("""
    <style>
        section[data-testid="stSidebar"] button {
            width: 100% !important;
            max-width: 300px;
            min-height: 50px;
            font-weight: 600;
            border-radius: 10px;
            margin-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

    # 📎 Upload multiple documents
    uploaded_files = st.sidebar.file_uploader("Upload .pdf or .txt files", type=["pdf", "txt"], accept_multiple_files=True)
    if uploaded_files:
        st.session_state.chat_context = {}
        for uploaded_file in uploaded_files:
            # ⏱️ Timestamp
            upload_timestamp = datetime.now(timezone.utc)

            # 📥 Sauvegarder temporairement le fichier
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = tmp.name

            # 📄 NLP Pipeline
            raw_text = extract_text_from_pdf(tmp_path)
            cleaned_text = clean_text(raw_text)
            summary = summarize_text(cleaned_text)

            # 💾 Sauvegarde MongoDB
            db["documents"].insert_one({
                "filename": uploaded_file.name,
                "user_email": st.session_state.user,
                "timestamp": upload_timestamp,
                "raw_text": raw_text,
                "cleaned_text": cleaned_text,
                "summary": summary
            })

            log_event(st.session_state.user, "document_upload", f"Parsed and saved {uploaded_file.name}")

            # ➕ Ajouter au contexte de chat
            st.session_state.chat_context[uploaded_file.name] = cleaned_text

            # 🔹 Découpage du document pour questions
            chunks = chunk_text(cleaned_text)

            st.sidebar.subheader(f"💡 Suggested Questions for {uploaded_file.name}")
            for idx, chunk in enumerate(chunks[:1]):  # 1 seul chunk
                with st.spinner(f"Generating questions from chunk {idx+1}..."):
                    result = force_question_output(chunk)

                if not result:
                    st.sidebar.warning(f"❌ No valid questions for {uploaded_file.name}")
                else:
                    for i, question in enumerate(result):
                        if st.sidebar.button(f"❓ {question}", key=f"{uploaded_file.name}_q{i}"):
                            st.session_state["pending_question"] = question
                            st.rerun()

            # 🔍 Analyse red flags
            detected_flags, flagged_sentences = detect_red_flags_with_highlight(cleaned_text)

            if detected_flags:
                st.sidebar.error(f"⚠️ Red flags in {uploaded_file.name}: {', '.join(detected_flags)}")
                with st.sidebar.expander(f"🔍 Sentences in {uploaded_file.name}", expanded=False):
                    for sentence in flagged_sentences:
                        st.sidebar.markdown(f"• {sentence}", unsafe_allow_html=True)
            else:
                st.sidebar.success(f"✅ {uploaded_file.name} loaded without detected risks.")

                        # ➕ Ajouter au contexte de chat
            st.session_state.chat_context[uploaded_file.name] = cleaned_text

            # 💾 Sauvegarder pour Agentic AI
            st.session_state["agentic_file_name"] = uploaded_file.name
            st.session_state["agentic_cleaned_text"] = cleaned_text    
        # Check for the New Chat button and handle session reset
    if st.sidebar.button("➕ New Chat"):
        st.session_state.history = []
        st.session_state.session_name = f"Session-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        st.session_state.chat_context = {
            txt_file: open(txt_file, "r", encoding="utf-8").read()
            for txt_file in glob.glob("cleaned_texts/*.txt")
        }
        st.session_state.selected_session = None  # <=== Important !
        st.session_state["just_reset"] = True
        st.rerun()
    # 💡 Toujours en dehors du bouton
    if "session_title" not in st.session_state:
        st.session_state.session_title = f"My Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"
          

    # 📌 Récupérer tous les tags utilisés
    # 📌 Récupérer tous les tags utilisés par l'utilisateur dans TOUTES les sessions
    all_tags = sorted(set(
        tag
        for session in collection.find({"user_email": st.session_state.user}, {"messages": 1})
        for msg in session.get("messages", [])
        for tag in msg.get("tags", [])
    ))


    st.sidebar.title("🗂️ Filter by Tag")
    selected_tag = st.sidebar.selectbox("Select a tag to filter answers", ["All"] + all_tags)


    # Ensure session state is set up correctly for the first load
    if "history" not in st.session_state:
        st.session_state.history = []
    if "chat_context" not in st.session_state:
        cleaned_texts_dir = "cleaned_texts"
        cleaned_texts = {
            txt_file: open(txt_file, "r", encoding="utf-8").read()
            for txt_file in glob.glob(f"{cleaned_texts_dir}/*.txt")
        }
        st.session_state.chat_context = dict(cleaned_texts)
    if "session_name" not in st.session_state:
        st.session_state.session_name = f"Session-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"








    # 🔄 Chargement des 10 dernières sessions avec titres personnalisés
    chat_sessions = list(
        collection.find(
            {"user_email": st.session_state.user},
            {"session": 1, "session_title": 1, "timestamp": 1}
        ).sort("timestamp", -1).limit(10)
    )

    # 🧠 Mapping session_id → titre (ou session_id si pas de titre)
    session_map = {
        s["session"]: s.get("session_title", s["session"]) for s in chat_sessions
    }

    session_ids = list(session_map.keys())
    session_titles = list(session_map.values())

    # 🧠 Historique des sessions (valeur sélectionnée actuelle)
    if "selected_session" not in st.session_state:
        st.session_state.selected_session = None

    # 📋 Affichage dropdown avec titres
    selected_display = st.sidebar.selectbox(
        "📚 Load a past chat",
        ["Choose an option"] + session_titles,
        index=0 if not st.session_state.selected_session else session_ids.index(st.session_state.selected_session) + 1,
        key="selected_session_display"
    )

    # ✅ Rechargement si changement
    if selected_display != "Choose an option":
        selected_session_id = session_ids[session_titles.index(selected_display)]
        if selected_session_id != st.session_state.session_name:
            doc = collection.find_one({"session": selected_session_id, "user_email": st.session_state.user})
            if doc:
                st.session_state.session_name = selected_session_id
                st.session_state.session_title = doc.get("session_title", selected_session_id)  # Pour affichage cohérent
                st.session_state.history = doc["messages"]
                st.session_state.selected_session = selected_session_id
                st.rerun()



            
       
    # ✅ Handle pending suggested question
    # ✅ Handle pending suggested question
    if "pending_question" in st.session_state and st.session_state.pending_question:
        question = st.session_state.pending_question
        st.session_state.pending_question = None  # Clear it after using
    else:
        question = st.chat_input("Ask a due diligence question...")

    if question:
        log_event(st.session_state.user, "login")
        log_event(st.session_state.user, "ask_question", question)
        log_event(st.session_state.user, "download_csv", f"session={st.session_state.session_name}")

        # 🔐 Définir automatiquement un titre de session
        if len(st.session_state.history) == 0:
            simplified_title = question.strip().capitalize()
            simplified_title = re.sub(r'[^\w\s-]', '', simplified_title)
            if len(simplified_title) > 40:
                simplified_title = simplified_title[:40].rsplit(' ', 1)[0] + "..."
            st.session_state.session_title = simplified_title

        # ➡️ Ajouter la question dans l'historique
        st.session_state.history.append({"role": "user", "content": question})

        # ⏳ Pendant génération de réponse
        with st.spinner("⏳ Thinking..."):
            context = find_relevant_context(question, st.session_state.chat_context)
            answer = generate_answer_with_ollama(question, context)
            tags = classify_answer_tags(answer)

        # ➡️ Ajouter la réponse dans l'historique
        st.session_state.history.append({
            "role": "assistant",
            "content": answer,
            "tags": tags
        })

        # 💾 Sauvegarder
        save_conversation(st.session_state.session_name, st.session_state.history)

        # 🔄 Redessiner toute la page (automatique)
        st.rerun()



    import streamlit as st






    def improve_answer_with_ollama(question, old_answer, context):
        prompt = f"""
    You are an expert in Due Diligence.

    The user asked:
    {question}

    An AI assistant gave the following answer:
    "{old_answer}"

    The answer is OK but incomplete. Based on the question and the following CONTEXT, improve and rewrite the answer:
    - Add any missing important points.
    - Be clearer and more actionable.
    - Use complete, professional English.

    CONTEXT:
    {context}

    Now give the improved answer:
    """
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            options={"num_predict": 250}
        )
        return response['message']['content'].strip()
    
    import speech_recognition as sr

    # 🔊 Amélioration du volume sonore
    def increase_volume(file_path, db=10):
        """Augmente le volume de l'audio de +10dB"""
        try:
            sound = AudioSegment.from_wav(file_path)
            sound = sound + db
            new_file_path = "test_audio_boosted.wav"
            sound.export(new_file_path, format="wav")
            return new_file_path
        except Exception as e:
            st.error(f"❌ Erreur lors de l'augmentation du volume : {e}")
            return None

    # 🔍 Reconnaissance vocale depuis un fichier
    def recognize_from_file(file_path):
        """Teste la reconnaissance vocale sur un fichier .wav"""
        r = sr.Recognizer()
        try:
            with sr.AudioFile(file_path) as source:
                audio = r.record(source)  # Lecture du fichier
                try:
                    text = r.recognize_google(audio, language="fr-FR")
                    st.success(f"✅ Reconnaissance réussie : {text}")
                except sr.UnknownValueError:
                    st.error("❌ Impossible de comprendre le fichier audio.")
                except sr.RequestError as e:
                    st.error(f"❌ Erreur avec l'API Google : {e}")
        except FileNotFoundError:
            st.error("❌ Fichier audio non trouvé.")




    # 💬 Affichage messages + Lecture audio + Filtrage par tag (Q&A associés)
    # Dans la partie où vous gérez l'affichage des messages, remplacez le bloc actuel par ceci :

# 💬 Affichage messages + Lecture audio + Filtrage par tag (Q&A associés)
    i = 0
    while i < len(st.session_state.history):
        user_msg = st.session_state.history[i]

        # --- Affiche la question ---
        if user_msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(user_msg["content"])

        # Peut-être que l'assistant n'a pas encore répondu
        assistant_msg = st.session_state.history[i+1] if (i+1) < len(st.session_state.history) else None

        # --- Vérification filtrage actif ---
        if selected_tag != "All" and assistant_msg:
            if selected_tag not in assistant_msg.get("tags", []):
                i += 2
                continue

        # --- Affiche la réponse si disponible ---
        if assistant_msg and assistant_msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(assistant_msg["content"])

                # Afficher les tags s'ils existent
                if assistant_msg.get("tags"):
                    render_tags(assistant_msg["tags"])

                # Boutons d'actions
                col1, col2, col3 = st.columns([1,1,2])
                with col1:
                    if st.button(f"👍 Like", key=f"like_{i}"):
                        log_event(st.session_state.user, "feedback_like", assistant_msg["content"])
                with col2:
                    if st.button(f"🔊 Speak", key=f"speak_{i}"):
                        speak_text(assistant_msg["content"])
                with col3:
                    if st.button(f"📈 Evaluate & Improve", key=f"judge_{i}"):
                        user_question = user_msg["content"]
                        score, comment = evaluate_answer_with_ollama(user_question, assistant_msg["content"])
                        st.info(f"🧠 LLM Evaluation:\n\nScore: {score}/10\nComment: {comment}")

                        if score < 7:
                            st.warning("⚠️ The answer can be improved. Generating a refined version...")
                            context = find_relevant_context(user_question, st.session_state.chat_context)
                            improved = improve_answer_with_ollama(user_question, assistant_msg["content"], context)
                            st.markdown("🔁 **Improved Answer:**")
                            st.markdown(improved)

                            tags = classify_answer_tags(improved)
                            st.session_state.history.append({
                                "role": "assistant",
                                "content": improved,
                                "tags": tags
                            })
                            save_conversation(st.session_state.session_name, st.session_state.history)

        i += 2







    st.sidebar.title("🎙️ Voice Assistant")
    
    # Initialize session state if not exists
    if 'voice_mode' not in st.session_state:
        st.session_state.voice_mode = False
    
    # Toggle voice mode
    if st.sidebar.button("🗣️ Start Voice Chat" if not st.session_state.voice_mode else "🔇 Stop Voice Chat"):
        st.session_state.voice_mode = not st.session_state.voice_mode
        st.rerun()
    
    # Run voice chat if in voice mode
    if st.session_state.voice_mode:
        voice_chat_loop()
        # Add a button to continue without exiting voice mode
        if st.button("🎤 Ask another question"):
            st.rerun()

    # 📤 Export
    st.sidebar.title("📤 Export")

    if st.sidebar.button("📁 Export Conversation (.csv)"):
        df = pd.DataFrame(st.session_state.history)
        df.to_csv("conversation.csv", index=False)
        st.sidebar.download_button("⬇️ Download CSV", data=open("conversation.csv", "rb"), file_name="conversation.csv")

    if st.sidebar.button("📊 Export PowerPoint (.pptx)"):
        if st.session_state.chat_context and st.session_state.history:
            raw_doc_text = list(st.session_state.chat_context.values())[0]
            pptx_file = generate_pptx(
    session_name=st.session_state.session_name,
    summary_text=summary,
    history=st.session_state.history
)
            st.sidebar.download_button(
                label="⬇️ Download PPTX",
                data=pptx_file,
                file_name=f"{st.session_state.session_name}_report.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
        else:
            st.sidebar.warning("❗ Please upload a document and ask at least one question before exporting.")

    if st.sidebar.button("📄 Export PDF Report"):
        if st.session_state.chat_context and st.session_state.history:
            raw_doc_text = list(st.session_state.chat_context.values())[0]
            summary = summarize_text(raw_doc_text)
            red_flags, _ = detect_red_flags_with_highlight(raw_doc_text)

            pdf_file = generate_compliance_pdf(
                session_name=st.session_state.session_name,
                summary=summary,
                history=st.session_state.history,
                red_flags=red_flags
            )

            st.sidebar.download_button(
                label="⬇️ Télécharger le rapport PDF",
                data=pdf_file,
                file_name=f"{st.session_state.session_name}_rapport.pdf",
                mime="application/pdf"
            )

    
    st.sidebar.markdown("---")
    
    if st.sidebar.button("📄 Generate Official Contract"):
        st.session_state.page = "Generate Contrat"
        st.rerun()
     

    if st.sidebar.button("👤 Compliance & Risk Tools"):
        st.session_state.page = "Compliance & Risk Tools"
        st.rerun()          

    st.sidebar.markdown("---")
    if st.sidebar.button("👤 My Profile"):
        st.session_state.page = "profile"
        st.rerun() 
    email_username = st.session_state.user["email"].split("@")[0]
    st.sidebar.write(f"👤 Logged in as: **{email_username}** ")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user = None
        st.rerun()          
       
