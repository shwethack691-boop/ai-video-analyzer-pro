from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from fpdf import FPDF
from pptx import Presentation
import os

# =========================
# TRANSLATION
# =========================
def translate_text(text, lang):
    try:
        if lang == "en":
            return text
        return GoogleTranslator(source="auto", target=lang).translate(text)
    except:
        return "Translation Error"

# =========================
# PDF EXPORT
# =========================
def save_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    file = "output.pdf"
    pdf.output(file)
    return file

# =========================
# DOCX EXPORT
# =========================
def save_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    file = "output.docx"
    doc.save(file)
    return file

# =========================
# PPT EXPORT
# =========================
def save_ppt(text):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "AI Summary"
    slide.placeholders[1].text = text
    file = "output.pptx"
    prs.save(file)
    return file

# =========================
# TEXT TO SPEECH
# =========================
def text_to_audio(text):
    file = "output.mp3"
    tts = gTTS(text)
    tts.save(file)
    return file

# =========================
# AI SUMMARY (SIMPLE VERSION)
# =========================
def generate_summary(text, level="Short"):
    words = text.split()

    if level == "Short":
        return " ".join(words[:80])
    elif level == "Medium":
        return " ".join(words[:200])
    else:
        return " ".join(words[:400])

# =========================
# HIGHLIGHTS
# =========================
def extract_highlights(text):
    sentences = text.split(".")
    return "\n".join(["⭐ " + s.strip() for s in sentences[:5] if s.strip()])

# =========================
# CHAPTERS (SIMPLE TIMELINE)
# =========================
def generate_chapters(text):
    sentences = text.split(".")
    chapters = []

    step = max(1, len(sentences)//5)

    for i in range(0, len(sentences), step):
        chapters.append(f"⏱ Chapter {len(chapters)+1}: {sentences[i].strip()}")

    return "\n".join(chapters)
