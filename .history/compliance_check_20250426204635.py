# --- compliance_analyzer.py ---

import streamlit as st
import base64
import fitz  # PyMuPDF
import re
import io
import tempfile

# --- COMPLIANCE RULES ---
COMPLIANCE_RULES = [ 
        # ========= HIGH RISK (FRAUD/AML) =========
    {
        "pattern": r"\(No\s+KYC\)|investments?\s+under\s+\$?1M?\b",
        "regulation": "FATF Recommendation 10 + FinCEN $3K Rule",
        "risk": "Critical",
        "recommendation": "Implement KYC for ALL transactions regardless of amount"
    },
    {
        "pattern": r"simplified\s+onboarding|express\s+verification",
        "regulation": "5AMLD Article 13",
        "risk": "High",
        "recommendation": "Require full identity documents for all customers"
    },

    # ===== OFFSHORE ACCOUNT ENHANCEMENTS =====
    {
        "pattern": r"Cayman\s+Islands.*no\s+tax\s+reporting",
        "regulation": "CRS (Common Reporting Standard)",
        "risk": "Critical",
        "recommendation": "Register for automatic tax information exchange"
    },
    {
        "pattern": r"shielded\s+banking\s+relationships",
        "regulation": "EU Tax Haven Blacklist",
        "risk": "High",
        "recommendation": "Disclose all banking partners to regulators"
    },

    # ===== AUDIT & FINANCIAL CONTROLS =====
    {
        "pattern": r"no\s+audit\s+since\s+\d{4}",
        "regulation": "PCAOB AS 3101",
        "risk": "High",
        "recommendation": "Conduct back-audits for missing years + current audit"
    },
    {
        "pattern": r"internal\s+controls\s+only",
        "regulation": "SOX 404",
        "risk": "Medium",
        "recommendation": "Implement external control testing framework"
    },

    # ===== GDPR/PRIVACY ENHANCEMENTS =====
    {
        "pattern": r"reserve\s+the\s+right\s+to\s+sell\s+data",
        "regulation": "GDPR Article 7/CCPA 1798.120",
        "risk": "Critical",
        "recommendation": "Rewrite privacy policy to require explicit opt-in consent"
    },
    {
        "pattern": r"gdpr\s+not\s+applicable",
        "regulation": "GDPR Article 3 (Extra-Territoriality)",
        "risk": "High",
        "recommendation": "Appoint EU representative if processing any EU data"
    },

    # ===== SEC REGISTRATION ENHANCEMENTS =====
    {
        "pattern": r"not\s+registered\s+with\s+SEC.*no\s+plans\s+to\s+register",
        "regulation": "Securities Act Section 5 + Rule 506(c)",
        "risk": "Critical",
        "recommendation": "Immediately file Form D or cease offerings"
    },

    # ===== GUARANTEED RETURNS ENHANCEMENTS =====
    {
        "pattern": r"25%\s+monthly.*no\s+risk",
        "regulation": "SEC Rule 10b-5 + FINRA 2210",
        "risk": "Critical",
        "recommendation": """
            1. Remove all return claims
            2. Add: "Hypothetical returns, risk of total loss"
            3. SEC pre-approve all marketing materials"""
    },

    # ===== COOLING-OFF PERIOD RULES =====
    {
        "pattern": r"no\s+cooling\-off.*binding\s+commitment",
        "regulation": "FTC Rule 16 CFR §429.1",
        "risk": "Medium",
        "recommendation": "Implement 14-day cancellation right for all contracts"
    },

    # ===== NEW: WHISTLEBLOWER PROTECTIONS =====
    {
        "pattern": r"confidentiality\s+agreement.*report",
        "regulation": "Dodd-Frank §922",
        "risk": "High",
        "recommendation": "Add whistleblower carve-out to all NDAs"
    },

    # ===== NEW: CRYPTO-SPECIFIC RISKS =====
    {
        "pattern": r"non\-custodial\s+wallets.*no\s+tracking",
        "regulation": "FATF Travel Rule (2021)",
        "risk": "High",
        "recommendation": "Implement VASP protocols for all crypto transfers"
    },
    {
        "pattern": r"defi\s+platform.*no\s+kyc",
        "regulation": "FinCEN 2019 Guidance",
        "risk": "Critical",
        "recommendation": "Register as MSB and implement chainalysis"
    },

    # ===== NEW: SANCTIONS SCREENING =====
    {
        "pattern": r"global\s+clients.*no\s+screening",
        "regulation": "OFAC 50% Rule",
        "risk": "Critical",
        "recommendation": "Implement real-time sanctions screening (e.g., Refinitiv)"
    },
    {
        "pattern": r"\b(no\s+(id|kyc|paperwork|documents?)|without\s+verification)\b",
        "regulation": "AML/KYC Requirements",
        "risk": "High",
        "recommendation": "Implement full identity verification for all investors"
    },
    {
        "pattern": r"\b(anonymous|numbered)\s+(accounts?|wallets?)\b",
        "regulation": "FATF Recommendation 10",
        "risk": "Critical",
        "recommendation": "Disclose all beneficial ownership information"
    },
    
    # ========= TAX EVASION =========
    {
        "pattern": r"\b(offshore|tax\s+haven|cayman|bvi|panama)\b.*?\b(account|fund|entity)\b",
        "regulation": "IRS Foreign Account Compliance",
        "risk": "High",
        "recommendation": "File FBAR and FATCA disclosures"
    },
    {
        "pattern": r"\b(untraceable|unreported)\s+(income|assets)\b",
        "regulation": "IRC §7201 (Tax Evasion)",
        "risk": "Critical",
        "recommendation": "Amend tax filings with proper disclosures"
    },
    
    # ========= SECURITIES VIOLATIONS =========
    {
        "pattern": r"\b(unregistered)\s+(security|offering)\b",
        "regulation": "Securities Act §5",
        "risk": "High",
        "recommendation": "File Form D or register with SEC"
    },
    {
        "pattern": r"\b(secret|proprietary)\s+(algorithm|strategy|formula)\b",
        "regulation": "SEC Marketing Rule",
        "risk": "Medium",
        "recommendation": "Disclose all material facts and risks"
    },
    
    # ========= CRYPTO RISKS =========
    {
        "pattern": r"\b(unlicensed)\s+(crypto|digital\s+asset)\s+(exchange|platform)\b",
        "regulation": "FinCEN MSB Requirements",
        "risk": "High",
        "recommendation": "Register as Money Services Business"
    },
    {
        "pattern": r"\b(mixing|tumbling)\s+services?\b",
        "regulation": "Anti-Money Laundering Act",
        "risk": "Critical",
        "recommendation": "Cease operations and file SAR"
    },
    
    # ========= INVESTOR PROTECTION =========
    
    {
        "pattern": r"\b(instant|immediate)\s+(returns|profits)\b",
        "regulation": "CFTC Anti-Fraud Provisions",
        "risk": "High",
        "recommendation": "Remove unrealistic timeframes"
    },
    
    # ========= SANCTIONS RISKS =========
    {
        "pattern": r"\b(russia|iran|north korea)\s+(investments?|clients?)\b",
        "regulation": "OFAC Sanctions",
        "risk": "Critical",
        "recommendation": "Block transactions and file report"
    },
    
    # ========= PRIVACY VIOLATIONS =========
    {
        "pattern": r"\b(share|sell)\s+client\s+data\b",
        "regulation": "GDPR/CCPA",
        "risk": "High",
        "recommendation": "Implement data protection measures"
    },
    
    # ========= OPERATIONAL RISKS =========
    {
        "pattern": r"\b(no\s+audit|unaudited)\b",
        "regulation": "AICPA Standards",
        "risk": "Medium",
        "recommendation": "Conduct annual third-party audits"
    },
    {
        "pattern": r"\b(manual\s+processes|spreadsheets?)\s+for\s+accounting\b",
        "regulation": "SOX Compliance",
        "risk": "Medium",
        "recommendation": "Implement proper accounting systems"
    },
    {
        "pattern": r"no\s+(paperwork|documentation|id|kyc)\s+required",
        "regulation": "AML/KYC Regulations",
        "risk": "High",
        "recommendation": "Implement full KYC procedures for all investors"
    },
    {
        "pattern": r"anonymous\s+(numbered\s+)?accounts?",
        "regulation": "Tax Evasion Risk",
        "risk": "Critical",
        "recommendation": "Disclose all account information to regulators"
    },
    {
        "pattern": r"untraceable\s+cryptocurrency",
        "regulation": "FinCEN Travel Rule",
        "risk": "High",
        "recommendation": "Implement cryptocurrency transaction monitoring"
    },
    {
        "pattern": r"operate\s+outside\s+financial\s+authorities",
        "regulation": "Regulatory Circumvention",
        "risk": "Critical",
        "recommendation": "Register with appropriate financial regulators"
    },
    {
    "pattern": r"\b(swift|wire)\s+transfers?\s+without\s+questions\b",
    "regulation": "FATF Recommendation 16",
    "risk": "High",
    "recommendation": "Implement wire transfer due diligence"
    },
    {
    "pattern": r"\b(limited\s+time|act\s+now)\b.*?\b(offer|discount)\b",
    "regulation": "FTC Cooling-Off Rule",
    "risk": "Medium",
    "recommendation": "Remove high-pressure sales tactics"
    },
    {
    "pattern": r"\b(ai\-generated|chatgpt)\s+investment\s+advice\b",
    "regulation": "SEC Reg BI",
    "risk": "Medium",
    "recommendation": "Disclose AI usage and limitations"
    },
    {
    "pattern": r"\b(privacy\s+coin|monero|zcash)\b",
    "regulation": "Travel Rule Compliance",
    "risk": "High",
    "recommendation": "Implement blockchain analytics tools"
    }
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