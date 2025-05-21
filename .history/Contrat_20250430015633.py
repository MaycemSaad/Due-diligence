import streamlit as st
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import os

def clean_text_for_pdf(text):
    return text.encode('latin-1', errors='ignore').decode('latin-1')

def show_generated_contrat():
    # Mongo setup
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/")
    db = client["due_diligence"]
    collection = db["qa_sessions"]

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

    # 🔍 Load sessions
    # 🛡️ Secure retrieval of email
    user_info = st.session_state.get("user", {})
    user_email = user_info.get("email")

    if not user_email:
        st.warning("⚠️ User not logged in. Please log in again.")
        st.stop()

    # 🔍 Retrieve sessions
    sessions = list(collection.find({"user_email": user_email}).sort("timestamp", -1))

    if not sessions:
        st.warning("⚠️ No sessions found for this user. Please use the chatbot before generating a contract.")
        return


    if not sessions:
        st.warning("⚠️ No sessions found for this user. Please chat with the assistant before generating a contract.")
        return

    # Dropdown for session selection
    session_options = [s.get("session_title", s["session"]) for s in sessions]
    selected_session_label = st.selectbox("🗂️ Select Session", session_options)

    selected_doc = sessions[session_options.index(selected_session_label)]
    default_summary = ""
    # Get the latest assistant message
    for msg in reversed(selected_doc.get("messages", [])):
        if msg.get("role") == "assistant":
            default_summary = msg.get("content", "")
            break

    # Form with auto-filled summary
    with st.form("contract_form"):
        name = st.text_input("👤 Full Name")
        email = st.text_input("📧 Email Address", user_email)
        session_id = st.text_input("🆔 Session ID", value=selected_doc["session"])
        summary = st.text_area("📌 Summary of Recommendation", height=200, value=default_summary)
        submitted = st.form_submit_button("✅ Generate Contract")

    if submitted:
        if not all([name, email, session_id, summary]):
            st.warning("⚠️ Please fill in all fields.")
            return

        # Clean input
        name = clean_text_for_pdf(name)
        email = clean_text_for_pdf(email)
        session_id = clean_text_for_pdf(session_id)
        summary = clean_text_for_pdf(summary)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        logo_path = "assets/chainvestor_logo.png"
        if os.path.exists(logo_path):
            pdf.image(logo_path, x=10, y=8, w=40)
            pdf.ln(25)

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "ChainVestor Hub – Official Confirmation Contract", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, f"""
This is to certify that:

👤 Name: {name}
📧 Email: {email}
🆔 Session ID: {session_id}
📅 Date: {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}

has received the following insights from ChainVestor Hub's AI-powered Due Diligence Assistant:
""")

        pdf.set_font("Arial", 'I', 12)
        pdf.multi_cell(0, 10, f"\"{summary}\"")
        pdf.ln(5)

        pdf.set_font("Arial", '', 12)
        pdf.multi_cell(0, 10, """
✅ We confirm that this information originates directly from ChainVestor Hub's platform and is based on:

- Uploaded documents and semantic analysis
- Answers and recommendations from the assistant
- Interactive contextual evaluation

🔐 This contract is digitally generated and verifiable through your session ID.

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
