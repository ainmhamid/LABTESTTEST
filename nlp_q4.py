# app.py
import streamlit as st
from PyPDF2 import PdfReader
import nltk
from nltk.tokenize import sent_tokenize

# -----------------------------
# Download required NLTK data
# -----------------------------
nltk.download('punkt')
nltk.download('punkt_tab')

# -----------------------------
# Streamlit Page Config
# -----------------------------
st.set_page_config(
    page_title="Text Chunking with NLTK",
    layout="wide"
)

st.title("📄 Text Chunking Web App (NLTK Sentence Tokenizer)")
st.write(
    "This application extracts text from a PDF file and performs "
    "**semantic sentence chunking** using NLTK."
)

# -----------------------------
# Step 1: Upload PDF
# -----------------------------
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:

    # -----------------------------
    # Step 2: Extract text from PDF
    # -----------------------------
    reader = PdfReader(uploaded_file)
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + " "

    st.success("PDF text extracted successfully.")

    # -----------------------------
    # Step 3: Sentence Tokenization
    # -----------------------------
    sentences = sent_tokenize(full_text)

    st.subheader("📌 Sample Extracted Sentences (Index 58–68)")

    if len(sentences) >= 69:
        sample_sentences = sentences[58:69]

        for i, sentence in enumerate(sample_sentences, start=58):
            st.markdown(f"**Sentence {i}:** {sentence}")
    else:
        st.warning("The document does not contain enough sentences.")

    # -----------------------------
    # Step 4: Semantic Sentence Chunking
    # -----------------------------
    st.subheader("🧠 Semantic Sentence Chunking Output")

    if len(sentences) >= 69:
        for idx, chunk in enumerate(sample_sentences, start=1):
            st.markdown(f"**Chunk {idx}**")
            st.write(chunk)
            st.markdown("---")

else:
    st.info("Please upload a PDF file to begin.")
