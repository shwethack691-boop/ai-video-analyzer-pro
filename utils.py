import os

# -------------------------
# SAFE IMPORTS (Cloud-friendly)
# -------------------------
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
from gtts import gTTS
from fpdf import FPDF
from docx import Document

# -------------------------
# OPTIONAL HEAVY IMPORT (LOCAL ONLY)
# -------------------------
try:
    import whisper
    model = whisper.load_model("base")
    WHISPER_AVAILABLE = True
except:
    WHISPER_AVAILABLE = False


# -------------------------
# TRANSCRIPTION (LOCAL ONLY)
# -------------------------
def transcribe_audio(file_path):
    if not WHISPER_AVAILABLE:
        return "⚠ Upload transcription works only on local system (not Streamlit Cloud)"

    try:
        result = model.transcribe(file_path)
        return result["text"]
    except Exception as e:
        return f"Transcription failed: {str(e)}"


# -------------------------
# YOUTUBE TRANSCRIPT (CLOUD SAFE)
# -------------------------
def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except:
        return None


# -------------------------
# FAST SUMMARY (NO AI MODEL)
# -------------------------
def summarize_text(text):
    try:
        sentences = text.split(".")
        return ".".join(sentences[:5])
    except:
        return text


# -------------------------
# TRANSLATION
# -------------------------
def translate_text(text, lang):
    try:
        return GoogleTranslator(source='auto', target=lang).translate(text)
    except:
        return "Translation failed"


# -------------------------
# TEXT TO SPEECH
# -------------------------
def text_to_speech(text, filename="output.mp3"):
    try:
        tts = gTTS(text)
        tts.save(filename)
        return filename
    except:
        return None


# -------------------------
# PDF
# -------------------------
def create_pdf(text, filename="output.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 8, line)

    pdf.output(filename)
    return filename


# -------------------------
# DOCX
# -------------------------
def create_docx(text, filename="output.docx"):
    doc = Document()
    doc.add_paragraph(text)
    doc.save(filename)
    return filename
