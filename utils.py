import requests
import streamlit as st
import time
import uuid
from gtts import gTTS
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from pptx import Presentation
from deep_translator import GoogleTranslator

# ---------------- YOUTUBE TRANSCRIPTION ----------------
def get_youtube_text(url):
    headers = {
        "authorization": st.secrets.get("ASSEMBLYAI_API_KEY", "")
    }

    if not headers["authorization"]:
        return "❌ API key missing", []

    res = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json={"audio_url": url},
        headers=headers
    )

    data = res.json()

    if "id" not in data:
        return f"❌ API Error: {data}", []

    transcript_id = data["id"]

    polling_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    while True:
        poll = requests.get(polling_url, headers=headers).json()

        if poll["status"] == "completed":
            return poll["text"], []

        elif poll["status"] == "error":
            return f"❌ Transcription failed: {poll}", []

        time.sleep(3)

# ---------------- SUMMARY ----------------
def summarize_text(text, mode="Medium"):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

    headers = {
        "Authorization": f"Bearer {st.secrets.get('HF_TOKEN','')}"
    }

    if mode == "Short":
        max_len = 80
    elif mode == "Long":
        max_len = 200
    else:
        max_len = 120

    payload = {
        "inputs": text[:1000],
        "parameters": {
            "max_length": max_len,
            "min_length": 30
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()[0]["summary_text"]
    except:
        return "⚠️ Summary failed"

# ---------------- TRANSLATE ----------------
def translate_text(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return text

# ---------------- HIGHLIGHTS ----------------
def highlight_text(text):
    sentences = text.split(".")
    return [s.strip() for s in sentences if len(s) > 60][:8]

# ---------------- AUDIO ----------------
def text_to_audio(text, lang="en"):
    file = f"audio_{uuid.uuid4()}.mp3"
    gTTS(text=text, lang=lang).save(file)
    return file

# ---------------- PDF ----------------
def create_pdf(text):
    file = "output.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    content = []

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    return file

# ---------------- DOCX ----------------
def create_docx(text):
    file = "output.docx"
    doc = Document()
    doc.add_heading("AI Report", 0)

    for line in text.split("\n"):
        doc.add_paragraph(line)

    doc.save(file)
    return file

# ---------------- PPT ----------------
def create_ppt(text):
    file = "output.pptx"
    prs = Presentation()

    for part in text.split("\n"):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = "AI Slide"
        slide.placeholders[1].text = part[:200]

    prs.save(file)
    return file
