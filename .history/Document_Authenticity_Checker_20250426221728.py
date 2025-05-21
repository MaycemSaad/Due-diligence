# --- document_authenticity_pro_ultimate.py ---

import streamlit as st
import fitz  # PyMuPDF
import datetime
import re
import requests
import json
import io
import tempfile

# --- OpenCorporates API ---
OPENCORPORATES_API_KEY = ""  # Optional: You can register and get an API key for more precise company verification

# --- Helper Functions ---

def extract_metadata_and_xmp(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    return doc.metadata, doc.page_count, doc.xref_length()

def analyze_metadata(metadata, page_count):
    issues = []

    creation_date = metadata.get("creationDate", "")
    mod_date = metadata.get("modDate", "")
    producer = metadata.get("producer", "")
    author = metadata.get("author", "")
    title = metadata.get("title", "")

    if creation_date:
        try:
            create_datetime = datetime.datetime.strptime(creation_date[2:16], "%Y%m%d%H%M%S")
            if (datetime.datetime.now() - create_datetime).days < 30:
                issues.append("⚠️ Very recent creation date (under 30 days).")
        except:
            issues.append("⚠️ Cannot parse creation date properly.")

    if mod_date:
        try:
            mod_datetime = datetime.datetime.strptime(mod_date[2:16], "%Y%m%d%H%M%S")
            if (datetime.datetime.now() - mod_datetime).days < 10:
                issues.append("⚠️ Very recent modification date (under 10 days).")
        except:
            issues.append("⚠️ Cannot parse modification date properly.")

    if producer and any(x in producer.lower() for x in ["photoshop", "word", "openoffice", "unknown"]):
        issues.append(f"⚠️ Suspicious producer software: {producer}")

    if not author or author.lower() in ["anonymous", "user", "admin"]:
        issues.append(f"⚠️ Suspicious or missing author: {author or 'None'}")

    if not title:
        issues.append("⚠️ No title found.")

    if page_count < 2:
        issues.append("⚠️ Document is only 1 page — uncommon for serious documents.")

    return issues

def analyze_text(text):
    issues = []
    if len(text.strip()) < 300:
        issues.append("⚠️ Very small amount of text — possible scan or dummy document.")

    if "lorem ipsum" in text.lower():
        issues.append("⚠️ Lorem Ipsum detected — placeholder content.")

    if re.search(r"(scan|photo|image only)", text, re.IGNORECASE):
        issues.append("⚠️ Document mentions being a scan/photo.")

    return issues

def detect_fonts(doc):
    fonts = set()
    for page in doc:
        for font in page.get_fonts():
            fonts.add(font[3])
    if len(fonts) > 5:
        return ["⚠️ More than 5 fonts detected — suspicious formatting."]
    return []

def detect_signatures(text):
    if not re.search(r"(signed|signature|seal|stamp)", text, re.IGNORECASE):
        return ["⚠️ No mentions of signature or seal detected."]
    return []

def detect_xmp_suspicion(xmp_streams_count):
    issues = []
    if xmp_streams_count > 30:
        issues.append(f"⚠️ Unusually high number of XMP streams ({xmp_streams_count}) — possible tampering or multiple edits.")
    return issues

def cross_verify_company_opencorporates(text):
    companies_found = []
    issues = []

    # Find likely company names (simplified)
    candidates = re.findall(r"\b([A-Z][A-Za-z&,\s]{2,})\b", text)

    for company in set(candidates):
        query = f"https://api.opencorporates.com/v0.4/companies/search?q={company}&api_token={OPENCORPORATES_API_KEY}"
        try:
            response = requests.get(query)
            if response.status_code == 200:
                results = response.json()
                if results["results"]["total_count"] == 0:
                    issues.append(f"⚠️ Company '{company}' not found in business registry.")
                else:
                    companies_found.append(company)
        except Exception:
            issues.append("⚠️ Company verification failed (no API or network issue).")
            break

    return issues, companies_found

def generate_plain_language_summary(total_issues):
    if not total_issues:
        return "✅ Document appears authentic with no significant red flags."
    elif len(total_issues) <= 3:
        return "⚠️ Minor inconsistencies detected. Manual review recommended."
    else:
        return "🚨 Significant authenticity risks detected. Document could be forged or manipulated."

# --- Main App ---

def show_document_authenticity_pro_ultimate():
    st.title("🔍 Document Authenticity Checker PRO+")
    st.subheader("Full metadata, text, layout, company, and editing validation.")

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file:
        pdf_bytes = uploaded_file.read()

        with st.spinner("Analyzing deeply..."):
            try:
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                metadata, page_count, xmp_streams = extract_metadata_and_xmp(pdf_bytes)
                text = ""
                for page in doc:
                    text += page.get_text()

                metadata_issues = analyze_metadata(metadata, page_count)
                text_issues = analyze_text(text)
                font_issues = detect_fonts(doc)
                signature_issues = detect_signatures(text)
                xmp_issues = detect_xmp_suspicion(xmp_streams)
                cross_issues, companies_found = cross_verify_company_opencorporates(text)

                total_issues = metadata_issues + text_issues + font_issues + signature_issues + xmp_issues + cross_issues

                # Display Sections
                st.subheader("📄 Metadata Extracted")
                st.json(metadata)

                st.subheader("🏢 Companies Mentioned")
                if companies_found:
                    for company in companies_found:
                        st.info(company)
                else:
                    st.warning("No verified companies detected.")

                st.subheader("⚠️ Detected Issues")
                if total_issues:
                    for issue in total_issues:
                        st.error(issue)
                else:
                    st.success("✅ No critical issues found.")

                st.subheader("🤖 Authenticity Summary")
                summary = generate_plain_language_summary(total_issues)
                st.info(summary)

            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
