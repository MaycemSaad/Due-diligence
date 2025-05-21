# --- scam_detector.py ---

import re

# Red flags list
SCAM_KEYWORDS = [
    r"guaranteed\s+returns",
    r"no\s+risk",
    r"instant\s+profits",
    r"anonymous\s+wallet",
    r"hidden\s+fees",
    r"unregulated\s+platform",
    r"double\s+your\s+money",
    r"no\s+identification\s+required",
    r"exclusive\s+investment\s+opportunity"
]

def detect_scam_signals(text):
    scam_signals = []
    for pattern in SCAM_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            scam_signals.append(pattern)
    return scam_signals

def show_scam_detector():
    st.title("🛡️ Crypto Scam Detector")

    uploaded_file = st.file_uploader("Upload Project Document or Paste Text", type=["txt", "pdf"])

    if uploaded_file:
        try:
            if uploaded_file.type == "application/pdf":
                import fitz
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = ""
                for page in doc:
                    text += page.get_text()
            else:
                text = uploaded_file.read().decode()

            st.subheader("Scanning for scam patterns...")

            detected = detect_scam_signals(text)
            if detected:
                st.error("⚠️ Potential Scam Indicators Detected:")
                for signal in detected:
                    st.write(f"- {signal}")
            else:
                st.success("✅ No obvious scam indicators found.")
        except Exception as e:
            st.error(f"Error analyzing file: {e}")
