import streamlit as st
import requests
from PIL import Image
import tempfile
import base64

OCR_SPACE_API_KEY = st.secrets["OCR_API_KEY"]  # Stockée dans secrets.toml

st.title("📄 Compteur de lignes remplies via OCR.Space")

uploaded_file = st.file_uploader("Importer un PDF ou une image", type=["pdf", "jpg", "jpeg", "png"])

def ocr_space_file(file, overlay=False, language='eng'):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': OCR_SPACE_API_KEY,
        'language': language,
        'OCREngine': 2
    }
    r = requests.post('https://api.ocr.space/parse/image',
                      files={'filename': file},
                      data=payload,
                      )
    return r.json()

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    st.write("⏳ Traitement en cours...")
    result = ocr_space_file(open(tmp_file_path, 'rb'))

    if result["IsErroredOnProcessing"]:
        st.error("Erreur de traitement OCR.")
    else:
        parsed_text = result["ParsedResults"][0]["ParsedText"]
        lignes = [l.strip() for l in parsed_text.split("\n") if l.strip() != ""]
        st.write("📝 Lignes extraites :")
        for ligne in lignes:
            st.write("- " + ligne)
        st.success(f"✅ Total de lignes remplies : {len(lignes)}")
