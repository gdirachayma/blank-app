import streamlit as st
from PIL import Image
import pytesseract
import tempfile
import os
import cv2
import numpy as np
from pdf2image import convert_from_bytes

st.title("🧾 Compteur de lignes remplies dans un tableau scanné")

uploaded_file = st.file_uploader("📤 Importer un fichier PDF ou image", type=["pdf", "png", "jpg", "jpeg"])

def process_image(img):
    # Convert to OpenCV format
    open_cv_image = np.array(img.convert('RGB'))
    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, 15, 4)

    # Detect horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))

    detect_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    detect_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    table_mask = cv2.add(detect_horizontal, detect_vertical)

    contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    filled_rows = 0
    st.write(f"🗂️ Nombre de tableaux détectés : {len(contours)}")

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        roi = open_cv_image[y:y+h, x:x+w]
        text = pytesseract.image_to_string(roi)

        lines = [line for line in text.split('\n') if line.strip() != '']
        st.write(f"- 📄 Lignes remplies dans ce tableau : {len(lines)}")
        filled_rows += len(lines)

    return filled_rows

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        images = convert_from_bytes(uploaded_file.read())
        total = 0
        for i, img in enumerate(images):
            st.image(img, caption=f"📄 Page {i+1}")
            filled = process_image(img)
            total += filled
        st.success(f"✅ Total de lignes remplies : {total}")
    else:
        img = Image.open(uploaded_file)
        st.image(img, caption="🖼️ Image importée")
        total = process_image(img)
        st.success(f"✅ Total de lignes remplies : {total}")
