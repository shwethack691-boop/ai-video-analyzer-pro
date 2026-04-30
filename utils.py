import os
import uuid
import whisper
import yt_dlp
import requests
import streamlit as st

from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from docx import Document
from pptx import Presentation
from deep_translator import GoogleTranslator

# ---------------- LOAD MODEL ----------------
whisper_model = whisper.load_model("base")

# ---------------- YOUTUBE TEXT ----------------
def get_youtube_text(url):
    try:
        video_id = url.split("v=")[1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        timestamps = [(t["start"], t["text"]) for t in transcript]
        return text, timestamps
    except:
        return None, None

# ---------------- DOWNLOAD AUDIO ----------------
def download_audio(url):
    filename = f"audio_{uuid.uuid4()}.mp3"

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'quiet': True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename

# ---------------- TRANSCRIBE ----------------
def transcribe_audio(path):
    result = whisper_model.transcribe(path)
    text = result["text"]

    timestamps = []
    for seg in result.get("segments", []):
        timestamps.append((seg["start"], seg["text"]))

    return text, timestamps

# ---------------- AI SUMMARY (HF API) ----------------
def summarize_text(text, mode="Medium"):
    API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"

    headers = {
        "Authorization": f"Bearer {st.secrets['HF_TOKEN']}"
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

    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        return response.json()[0]["summary_text"]
    except:
        return "⚠️ Summary failed. Try shorter text."

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

# ---------------- AUTO CHAPTERS ----------------
def generate_chapters(timestamps):
    chapters = []
    step = max(1, len(timestamps)//5)

    for i in range(0, len(timestamps), step):
        start, text = timestamps[i]
        chapters.append(f"{round(start)}s - {text[:50]}")

    return chapters

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
