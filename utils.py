import whisper
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from deep_translator import GoogleTranslator
from gtts import gTTS
from fpdf import FPDF
from docx import Document
import os

# Load models once
model = whisper.load_model("base")
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# -------------------------
# TRANSCRIPTION
# -------------------------
def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]

# -------------------------
# YOUTUBE TRANSCRIPT
# -------------------------
def get_youtube_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t['text'] for t in transcript])
        return text
    except:
        return None

# -------------------------
# SUMMARY
# -------------------------
def summarize_text(text):
    if len(text) < 100:
        return text
    summary = summarizer(text[:1000], max_length=150, min_length=40, do_sample=False)
    return summary[0]['summary_text']

# -------------------------
# TRANSLATION
# -------------------------
def translate_text(text, lang):
    return GoogleTranslator(source='auto', target=lang).translate(text)

# -------------------------
# TEXT TO SPEECH
# -------------------------
def text_to_speech(text, filename="output.mp3"):
    tts = gTTS(text)
    tts.save(filename)
    return filename

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
