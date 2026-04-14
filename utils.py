import whisper
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
from gtts import gTTS
from fpdf import FPDF
from docx import Document
import os

# -------------------------
# LOAD WHISPER MODEL (ONCE)
# -------------------------
model = whisper.load_model("base")

# -------------------------
# TRANSCRIPTION
# -------------------------
def transcribe_audio(file_path):
    try:
        if not os.path.exists(file_path):
            return "File not found"

        result = model.transcribe(file_path)
        return result["text"]

    except Exception as e:
        return f"Transcription failed: {str(e)}"


# -------------------------
# YOUTUBE TRANSCRIPT
# -------------------------
def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        return text
    except Exception:
        return None


# -------------------------
# SUMMARY (SAFE VERSION)
# -------------------------
def summarize_text(text):
    try:
        from transformers import pipeline

        # Load only when needed (prevents crash)
        summarizer = pipeline(
            "summarization",
            model="facebook/bart-large-cnn"
        )

        if not text or len(text) < 100:
            return text

        summary = summarizer(
            text[:1000],
            max_length=150,
            min_length=40,
            do_sample=False
        )

        return summary[0]["summary_text"]

    except Exception as e:
        return f"Summary failed: {str(e)}"


# -------------------------
# TRANSLATION
# -------------------------
def translate_text(text, lang):
    try:
        return GoogleTranslator(source="auto", target=lang).translate(text)
    except Exception as e:
        return f"Translation failed: {str(e)}"


# -------------------------
# TEXT TO SPEECH
# -------------------------
def text_to_speech(text, filename="output.mp3"):
    try:
        tts = gTTS(text)
        tts.save(filename)
        return filename
    except Exception as e:
        return None


# -------------------------
# PDF GENERATION
# -------------------------
def create_pdf(text, filename="output.pdf"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        for line in text.split("\n"):
            pdf.multi_cell(0, 8, line)

        pdf.output(filename)
        return filename
    except Exception as e:
        return None


# -------------------------
# DOCX GENERATION
# -------------------------
def create_docx(text, filename="output.docx"):
    try:
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filename)
        return filename
    except Exception as e:
        return None
