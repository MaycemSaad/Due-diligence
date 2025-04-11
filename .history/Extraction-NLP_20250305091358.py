import PyPDF2
import re
import os
import spacy
from transformers import pipeline

# Charger le modèle NLP pour le nettoyage
nlp = spacy.load("en_core_web_sm")  # Si tes textes sont en anglais


# Liste des fichiers PDF
new_pdf_files = [
    "108364 PLE_Digital Assets_Deck 290724.pdf",
    "1110830.1.0 Introduction to Digital Assets for Institutional Investors_FINAL_0.pdf",
    "cravath-bringing-blockchain-due-diligence-into-focus-102024_vb-002.pdf",
    "DASCPWhitePaper.pdf",
    "Digital_Assets_Legal_Regulation_and_Estimation_of_.pdf",
    "ey-token-due-diligence-a-structured-approach-to-evaluate-digital-asset-risk (1).pdf",
    "ey-token-due-diligence-a-structured-approach-to-evaluate-digital-asset-risk.pdf",
    "FATF-Booklet_VA.pdf",
    "FTI+Technology+-+Decentralized+Due+Diligence.pdf",
    "guide-to-regulation-on-cryptocurrency-and-digital-token.pdf",
    "guide-to-the-vetting-of-digital-asset-and-digital-asset-exchanges.pdf",
    "mpdf.pdf",
    "Operational-Due-Diligence-on-Digital-Assets.pdf",
    "SSRN-id4594467.pdf",
    "us-crypto-regulatory-whitepaper.pdf",
    "WEF_Digital_Assets_Regulation_2024.pdf"
]

# Création des dossiers de stockage
output_dir = "resumes"
clean_text_dir = "cleaned_texts"
os.makedirs(output_dir, exist_ok=True)
os.makedirs(clean_text_dir, exist_ok=True)

# Chargement du modèle de résumé
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def extract_text_from_pdf(pdf_file):
    """Extrait tout le texte d'un PDF."""
    try:
        with open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text.strip()
    except Exception as e:
        print(f"❌ Erreur d'extraction pour {pdf_file}: {e}")
        return ""

def clean_text(text):
    """Nettoie le texte extrait du PDF pour améliorer la qualité du résumé."""
    # Suppression des caractères spéciaux inutiles
    text = re.sub(r'\n+', '\n', text)  # Supprime les sauts de ligne excessifs
    text = re.sub(r'[^\w\s.,;!?]', '', text)  # Supprime caractères spéciaux sauf ponctuation
    text = re.sub(r'\bPage \d+\b', '', text, flags=re.IGNORECASE)  # Supprime les numéros de page
    text = re.sub(r'http\S+', '', text)  # Supprime les URL
    text = text.strip()

    # Segmentation en phrases avec spaCy
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 5]  # Supprime les phrases trop courtes

    return " ".join(sentences)  # Reconstruit le texte propre

def summarize_text(text):
    """Utilise le modèle NLP pour résumer un texte."""
    text = text[:1024]  # Limite à 1024 tokens pour éviter les erreurs de BART

    input_length = len(text.split())  # Nombre de tokens dans le texte d'entrée

    # Ajustement dynamique
    max_length = min(350, int(input_length * 0.8))  # max = 80% de l'entrée
    min_length = max(50, int(input_length * 0.4))  # min = 40% de l'entrée

    summary = summarizer(
        text,
        max_length=max_length,
        min_length=min_length,
        length_penalty=3.5,
        num_beams=6,
        do_sample=False
    )
    return summary[0]['summary_text']

def process_pdfs():
    """Extrait, nettoie et résume chaque PDF, puis enregistre le texte propre et le résumé."""
    for pdf_file in new_pdf_files:
        print(f"\n📄 Traitement du fichier : {pdf_file}")

        # Étape 1 : Extraction
        extracted_text = extract_text_from_pdf(pdf_file)
        if not extracted_text:
            print(f"❌ Aucun texte extrait pour {pdf_file}, passage au suivant.")
            continue

        print(f"🔎 Longueur du texte brut : {len(extracted_text.split())} mots")

        # Étape 2 : Nettoyage du texte
        cleaned_text = clean_text(extracted_text)
        print(f"✅ Texte nettoyé ({len(cleaned_text.split())} mots)")

        # Sauvegarde du texte nettoyé
        pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
        cleaned_text_file = os.path.join(clean_text_dir, f"cleaned_{pdf_name}.txt")
        with open(cleaned_text_file, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        # Étape 3 : Résumé du texte propre
        summary = summarize_text(cleaned_text)

        # Sauvegarde du résumé
        output_file = os.path.join(output_dir, f"resume_{pdf_name}.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(summary)

        print(f"✅ Résumé sauvegardé dans {output_file}")

if __name__ == "__main__":
    process_pdfs()
