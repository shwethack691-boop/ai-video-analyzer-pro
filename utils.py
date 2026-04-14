import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from fpdf import FPDF
from pptx import Presentation
import os

# -------------------------
# TRANSCRIPTION (FIXED)
# -------------------------
def transcribe_audio(file_path):
    model = whisper.load_model("base")

    file_path = os.path.abspath(file_path)

    if not os.path.exists(file_path):
        return "File not found"

    result = model.transcribe(file_path)
    return result["text"]

# -------------------------
# TRANSLATION
# -------------------------
def translate_text(text, lang):
    try:
        if lang == "en":
            return text
        return GoogleTranslator(source="auto", target=lang).translate(text)
    except:
        return text

# -------------------------
# AI SUMMARY (SIMULATED SMART NLP)
# -------------------------
def generate_summary(text, mode="medium"):
    sentences = text.split(".")
    sentences = [s.strip() for s in sentences if s.strip()]

    if mode == "short":
        return ". ".join(sentences[:3])

    if mode == "medium":
        return ". ".join(sentences[:7])

    return ". ".join(sentences)

# -------------------------
# BULLET HIGHLIGHTS
# -------------------------
def extract_bullets(text):
    sentences = text.split(".")
    return ["✔ " + s.strip() for s in sentences[:10] if s.strip()]

# -------------------------
# TIMELINE CHAPTERS
# -------------------------
def generate_chapters(text):
    sentences = text.split(".")
    chapters = []

    step = max(1, len(sentences)//5)

    for i in range(0, len(sentences), step):
        chapters.append(f"⏱ {i}–{i+step} sec: {sentences[i][:60]}")

    return chapters

# -------------------------
# EXPORT DOCX
# -------------------------
def save_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    file = "output.docx"
    doc.save(file)
    return file

# -------------------------
# EXPORT PDF
# -------------------------
def save_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text)
    file = "output.pdf"
    pdf.output(file)
    return file

# -------------------------
# EXPORT PPT (SaaS STYLE)
# -------------------------
def save_ppt(text):
    prs = Presentation()

    slides = text.split(".")[:6]

    for i, s in enumerate(slides):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = f"Slide {i+1}"
        slide.placeholders[1].text = s

    file = "output.pptx"
    prs.save(file)
    return file

# -------------------------
# TEXT TO AUDIO
# -------------------------
def text_to_audio(text, lang="en"):
    tts = gTTS(text=text, lang=lang)
    file = "output.mp3"
    tts.save(file)
    return file
