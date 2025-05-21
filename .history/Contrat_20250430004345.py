import streamlit as st
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import os

def show_generated_contrat():
    st.title("📄 Generate Official Confirmation Contract")
    st.markdown("This contract certifies that all information provided to the user has been issued through ChainVestor Hub's Due Diligence Assistant.")

    with st.form("contract_form"):
        name = st.text_input("👤 Full Name")
        email = st.text_input("📧 Email Address")
        session_id = st.text_input("🗂️ Session ID")
        summary = st.text_area("🧠 Summary of the Recommendation", height=150)
        submitted = st.form_submit_button("✅ Generate Contract")

    if submitted:
        if not all([name, email, session_id, summary]):
            st.warning("⚠️ Please fill in all fields.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # === Logo (if exists) ===
        logo_path = "assets/chainvestor_logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=40)

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "ChainVestor Hub - Official Confirmation Contract", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"""
🧾 This document certifies that the user:

   👤 Name: {name}
   📧 Email: {email}
   🗂️ Session ID: {session_id}
   📅 Date: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}

has received the following insights and/or recommendations from ChainVestor Hub's Due Diligence Assistant:
""")
        pdf.set_font("Arial", 'I', 12)
        pdf.multi_cell(0, 10, f"\"{summary}\"")
        pdf.set_font("Arial", '', 12)

        pdf.ln(5)
        pdf.multi_cell(0, 10, """
✅ We confirm that all of the above information originates directly from our platform's AI-powered assistant and was based on the uploaded documents and contextual analysis.

⚠️ This contract is system-generated and holds traceable proof of issuance.

Signed digitally by:
ChainVestor Hub Compliance AI

""")

        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.success("✅ Contract generated successfully.")
        st.download_button(
            label="📥 Download Contract PDF",
            data=BytesIO(pdf_bytes),
            file_name=f"{session_id}_confirmation_contract.pdf",
            mime="application/pdf"
        )
