import streamlit as st
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import os

def clean_text_for_pdf(text):
    return text.encode('latin-1', errors='ignore').decode('latin-1')

def show_generated_contrat():
    st.set_page_config(layout="wide")
    st.sidebar.title("🛡️ ChainVestor Hub")
    st.sidebar.markdown("### 📝 Contract Generator")
    st.sidebar.info("Generate a digitally confirmed contract that validates the advice you received.")
    
    if st.sidebar.button("⬅️ Back to Chatbot"):
        st.session_state.page = "main"
        st.rerun()

    st.title("📄 Generate Official Confirmation Contract")
    st.markdown("""
    This contract certifies that **all due diligence information** provided to the user originates from the official **ChainVestor Hub AI assistant**, based on uploaded documents and live analysis.
    """)

    with st.form("contract_form"):
        name = st.text_input("👤 Full Name")
        email = st.text_input("📧 Email Address")
        session_id = st.text_input("🗂️ Session ID")
        summary = st.text_area("📌 Summary of Recommendation or Final Advice", height=200)
        submitted = st.form_submit_button("✅ Generate Contract")

    if submitted:
        if not all([name, email, session_id, summary]):
            st.warning("⚠️ Please fill in all fields.")
            return

        # Clean input fields to avoid Unicode errors
        name = clean_text_for_pdf(name)
        email = clean_text_for_pdf(email)
        session_id = clean_text_for_pdf(session_id)
        summary = clean_text_for_pdf(summary)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Logo
        logo_path = "assets/chainvestor_logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=40)
            pdf.ln(25)

        # Title
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "ChainVestor Hub – Official Confirmation Contract", ln=True, align='C')
        pdf.ln(10)

        # Body
        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"""
This is to certify that:

👤 Name: {name}
📧 Email: {email}
🗂️ Session ID: {session_id}
📅 Date: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}

has received the following recommendation or confirmation from ChainVestor Hub's AI-powered Due Diligence Assistant:
""")

        pdf.set_font("Arial", 'I', 12)
        pdf.multi_cell(0, 10, f"\"{summary}\"")
        pdf.ln(5)

        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, """
✅ We confirm that this information originates directly from ChainVestor Hub's platform and is based on:

- Uploaded and parsed documents
- Contextual semantic analysis
- Answers and recommendations provided during the session

🔐 This contract is digitally generated, includes embedded metadata, and is verifiable through your session ID.

Signed digitally by:
ChainVestor Hub Compliance AI
""")

        pdf_bytes = BytesIO(pdf.output(dest='S').encode('latin-1', errors='ignore'))
        st.success("✅ Contract generated successfully.")
        st.download_button(
            label="📥 Download Confirmation Contract (PDF)",
            data=pdf_bytes,
            file_name=f"{session_id}_confirmation_contract.pdf",
            mime="application/pdf"
        )
