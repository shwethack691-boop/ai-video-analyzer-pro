from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from pptx import Presentation
from fpdf import FPDF
import re
import os

# =========================
# TRANSLATION (MULTI LANGUAGE FIX)
# =========================
def translate_text(text, lang):
    if lang == "en":
        return text

    try:
        return GoogleTranslator(source="auto", target=lang).translate(text)
    except:
        return "Translation Error"


# =========================
# AI SUMMARY ENGINE (SIMPLE NLP STYLE)
# =========================
def generate_summary(text, level="medium"):
    sentences = re.split(r'(?<=[.!?]) +', text)

    if level == "short":
        return " ".join(sentences[:3])

    elif level == "medium":
        return " ".join(sentences[:8])

    elif level == "long":
        return " ".join(sentences[:15])

    return text


# =========================
# HIGHLIGHTS EXTRACTOR (BULLETS)
# =========================
def extract_highlights(text):
    sentences = re.split(r'(?<=[.!?]) +', text)

    keywords = [
        "important", "key", "main", "significant", "AI",
        "machine", "learning", "data", "model", "system"
    ]

    highlights = []

    for s in sentences:
        if any(k.lower() in s.lower() for k in keywords):
            highlights.append(s.strip())

    # fallback if nothing found
    if not highlights:
        highlights = sentences[:5]

    return highlights[:8]


# =========================
# TIMELINE CHAPTERS (SMART SEGMENTATION)
# =========================
def generate_chapters(text):
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunk_size = 5
    chapters = []

    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i+chunk_size])
        chapters.append(f"Chapter {i//chunk_size + 1}: {chunk}")

    return "\n\n".join(chapters)


# =========================
# AUDIO GENERATION
# =========================
def text_to_audio(text):
    file = "output.mp3"
    tts = gTTS(text=text, lang="en")
    tts.save(file)
    return file


# =========================
# SAFE PDF (UNICODE FIX)
# =========================
class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", size=12)

def save_pdf(text):
    pdf = PDF()
    pdf.add_page()

    # FIX: avoid Unicode crash
    safe_text = text.encode("latin-1", "ignore").decode("latin-1")

    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 10, safe_text)

    file = "output.pdf"
    pdf.output(file)
    return file


# =========================
# DOCX EXPORT
# =========================
def save_docx(text):
    doc = Document()
    doc.add_heading("AI Video Report", 0)
    doc.add_paragraph(text)

    file = "output.docx"
    doc.save(file)
    return file


# =========================
# PPT EXPORT (INDUSTRY STYLE SLIDES)
# =========================
def save_ppt(text):
    prs = Presentation()

    sentences = re.split(r'(?<=[.!?]) +', text)

    for i in range(0, len(sentences), 3):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = f"Slide {i//3 + 1}"
        slide.placeholders[1].text = " ".join(sentences[i:i+3])

    file = "output.pptx"
    prs.save(file)
    return file