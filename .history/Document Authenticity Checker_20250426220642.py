# --- document_authenticity_pro.py ---

import streamlit as st
import fitz  # PyMuPDF
import datetime
import re
import requests
import tempfile

# --- Helper Functions ---

def extract_metadata(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return doc.metadata, doc.page_count

def analyze_metadata(metadata, page_count):
    issues = []

    creation_date = metadata.get("creationDate", "")
    mod_date = metadata.get("modDate", "")
    producer = metadata.get("producer", "")
    author = metadata.get("author", "")
    title = metadata.get("title", "")

    # --- Date Checks ---
    if creation_date:
        try:
            create_datetime = datetime.datetime.strptime(creation_date[2:16], "%Y%m%d%H%M%S")
            if (datetime.datetime.now() - create_datetime).days < 30:
                issues.append("⚠️ Very recent creation date (less than 30 days ago).")
        except:
            issues.append("⚠️ Could not parse creation date properly.")

    if mod_date:
        try:
            mod_datetime = datetime.datetime.strptime(mod_date[2:16], "%Y%m%d%H%M%S")
            if (datetime.datetime.now() - mod_datetime).days < 10:
                issues.append("⚠️ Very recent modification date (less than 10 days ago).")
        except:
            issues.append("⚠️ Could not parse modification date properly.")

    # --- Producer Software Checks ---
    if producer and any(x in producer.lower() for x in ["word", "photoshop", "unknown", "openoffice"]):
        issues.append(f"⚠️ Suspicious document producer: {producer}")

    # --- Author Checks ---
    if not author:
        issues.append("⚠️ No author information found.")
    elif author.lower() in ["anonymous", "user", "admin"]:
        issues.append(f"⚠️ Suspicious author name: {author}")

    # --- Title Missing ---
    if not title:
        issues.append("⚠️ No document title specified.")

    # --- Page Count Checks ---
    if page_count < 2:
        issues.append("⚠️ Document has only 1 page - suspiciously short for an official document.")

    return issues

def analyze_text_content(text):
    issues = []
    if len(text.strip()) < 300:
        issues.append("⚠️ Very small amount of text - possible fake document or scan.")

    if "lorem ipsum" in text.lower():
        issues.append("⚠️ Lorem Ipsum placeholder text detected.")

    if re.search(r"(scan|photo|image only)", text, re.IGNORECASE):
        issues.append("⚠️ Document mentions being a scan or photo.")

    return issues

def detect_fonts_and_layout(doc):
    issues = []
    fonts = set()

    for page in doc:
        for font in page.get_fonts():
            fonts.add(font[3])  # font name

    if len(fonts) > 4:
        issues.append("⚠️ Multiple different fonts detected (>4) — inconsistent formatting.")

    return issues

def detect_signatures_stamps(text):
    issues = []

    if not re.search(r"(signed|signature|seal|stamp)", text, re.IGNORECASE):
        issues.append("⚠️ No mention of signature or stamp found in document.")

    return issues

def cross_check_company_names(text):
    companies_found = []
    issues = []

    # Simple heuristic to find capitalized words that look like company names
    candidates = re.findall(r"\b([A-Z][A-Za-z&,\s]{2,})\b", text)

    for company in set(candidates):
        try:
            query = f"{company} site:linkedin.com OR site:bloomberg.com"
            url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
            response = requests.get(url)
            if "No results found" in response.text:
                issues.append(f"⚠️ Could not validate existence of company: {company}")
            else:
                companies_found.append(company)
        except:
            issues.append("⚠️ Cross-verification failed (connectivity issue).")

    return issues, companies_found

# --- Main App ---

def show_document_authenticity_pro():
    st.title("🔍 Document Authenticity Checker PRO")
    st.subheader("Advanced AI-Based PDF Authenticity and Fraud Detection")

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file:
        pdf_bytes = uploaded_file.read()

        with st.spinner("Analyzing document..."):
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                metadata, page_count = extract_metadata(pdf_bytes)
                text = ""
                for page in doc:
                    text += page.get_text()

                metadata_issues = analyze_metadata(metadata, page_count)
                text_issues = analyze_text_content(text)
                font_issues = detect_fonts_and_layout(doc)
                signature_issues = detect_signatures_stamps(text)
                cross_issues, companies_found = cross_check_company_names(text)

                total_issues = metadata_issues + text_issues + font_issues + signature_issues + cross_issues

                # Display Metadata
                st.subheader("📄 Extracted Metadata")
                st.json(metadata)

                # Display Companies
                if companies_found:
                    st.subheader("🏢 Companies Mentioned")
                    for company in companies_found:
                        st.info(company)

                # Display Issues
                st.subheader("⚠️ Detected Issues")
                if total_issues:
                    for issue in total_issues:
                        st.error(issue)
                else:
                    st.success("✅ No obvious authenticity problems detected!")

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
