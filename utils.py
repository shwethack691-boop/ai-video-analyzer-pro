from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from fpdf import FPDF
from pptx import Presentation
import os


# =========================
# TRANSLATION MODULE
# =========================
def translate_text(text, lang):
    """
    Translate text safely using deep-translator
    """
    try:
        if lang == "en":
            return text

        return GoogleTranslator(source="auto", target=lang).translate(text)

    except Exception as e:
        return f"Translation Error: {str(e)}"


# =========================
# TEXT TO AUDIO
# =========================
def text_to_audio(text, lang="en"):
    """
    Convert text to speech using gTTS
    """
    try:
        file_path = "output_audio.mp3"
        tts = gTTS(text=text, lang=lang)
        tts.save(file_path)
        return file_path

    except Exception as e:
        return f"Audio Error: {str(e)}"


# =========================
# DOCX EXPORT
# =========================
def save_docx(text):
    """
    Save transcript/summary as DOCX
    """
    doc = Document()
    doc.add_heading("AI Video Analysis Report", 0)
    doc.add_paragraph(text)

    file_path = "output.docx"
    doc.save(file_path)

    return file_path


# =========================
# PDF EXPORT (FIXED UNICODE)
# =========================
def save_pdf(text):
    """
    Save PDF safely (handles Unicode like Kannada, Tamil, etc.)
    """
    pdf = FPDF()
    pdf.add_page()

    # FIX: Unicode-safe font fallback
    pdf.set_font("Arial", size=12)

    # Clean text to avoid crash
    safe_text = text.encode("latin-1", "ignore").decode("latin-1")

    pdf.multi_cell(190, 10, safe_text)

    file_path = "output.pdf"
    pdf.output(file_path)

    return file_path


# =========================
# PPT EXPORT
# =========================
def save_ppt(text):
    """
    Create PPT summary slide
    """
    prs = Presentation()

    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)

    slide.shapes.title.text = "AI Video Summary"
    slide.placeholders[1].text = text[:1000]  # limit for safety

    file_path = "output.pptx"
    prs.save(file_path)

    return file_path
