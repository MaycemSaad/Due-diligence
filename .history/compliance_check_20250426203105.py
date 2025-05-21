# --- compliance_analyzer.py ---

import streamlit as st
import base64
import fitz  # PyMuPDF
import re
import io
import tempfile

# --- COMPLIANCE RULES ---
COMPLIANCE_RULES = [ 
    # (You can paste your full big COMPLIANCE_RULES list here directly)
]

# --- Functions ---

def extract_text_from_pdf(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc[:3]:  # Only first 3 pages
        text += page.get_text()
        if len(text) > 2000:
            break
    return text[:2000]

def analyze_text(text):
    issues = []
    for rule in COMPLIANCE_RULES:
        matches = re.finditer(rule["pattern"], text, re.IGNORECASE)
        for match in matches:
            issues.append({
                "text": match.group(),
                "regulation": rule["regulation"],
                "risk": rule["risk"],
                "recommendation": rule["recommendation"],
                "start": match.start(),
                "end": match.end()
            })

    score = max(1, 10 - len(issues))
    recommendations = list({issue["recommendation"] for issue in issues})
    
    return {
        "issues": issues,
        "score": f"{score}/10",
        "recommendations": recommendations if recommendations else ["No specific recommendations needed"]
    }

def highlight_pdf(pdf_bytes, issues):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page in doc:
        for issue in issues:
            text_instances = page.search_for(issue["text"])
            for inst in text_instances:
                highlight = page.add_highlight_annot(inst)
                highlight.set_colors({"stroke": (1, 0, 0)})  # Red color
                highlight.update()
    return doc.tobytes()

# --- Streamlit App ---

def show_compliance_analyzer():
    st.title("📜 Compliance Analyzer PRO")
    st.subheader("Upload investment documents to detect regulatory compliance risks.")

    uploaded_file = st.file_uploader("Upload your PDF file", type=["pdf"])
    
    if uploaded_file:
        with st.spinner('Analyzing document...'):
            try:
                pdf_bytes = uploaded_file.read()
                text = extract_text_from_pdf(io.BytesIO(pdf_bytes))
                analysis = analyze_text(text)
                highlighted_pdf = highlight_pdf(pdf_bytes, analysis["issues"])

                # Display the PDF viewer
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
                    tmpfile.write(highlighted_pdf)
                    tmpfilepath = tmpfile.name

                pdf_display = f'<iframe src="data:application/pdf;base64,{base64.b64encode(highlighted_pdf).decode()}" width="100%" height="600px" type="application/pdf"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)

                st.markdown("---")

                # Display compliance results
                st.header("🧠 Compliance Analysis Report")

                st.subheader("Compliance Status")
                score_color = "#4CAF50" if int(analysis["score"].split("/")[0]) > 5 else "#F44336"
                st.markdown(f"<h2 style='color:{score_color}; text-align:center;'>{analysis['score']}</h2>", unsafe_allow_html=True)

                st.subheader("🔎 Identified Issues")
                if analysis["issues"]:
                    for issue in analysis["issues"]:
                        st.warning(f'"{issue["text"]}" ➔ {issue["regulation"]} (Risk: {issue["risk"]})')
                else:
                    st.success("No major issues found.")

                st.subheader("✅ Recommendations")
                for rec in analysis["recommendations"]:
                    st.info(rec)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")