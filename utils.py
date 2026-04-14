import whisper
import yt_dlp
import json
import os
from deep_translator import GoogleTranslator
from gtts import gTTS
from docx import Document
from fpdf import FPDF
from pptx import Presentation

# =========================
# USER DATABASE
# =========================
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

# =========================
# AUTH
# =========================
def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == password

# =========================
# TRANSCRIPTION
# =========================
def transcribe_audio(file_path):
    model = whisper.load_model("base")
    result = model.transcribe(file_path)
    return result["text"]

# =========================
# YOUTUBE AUDIO
# =========================
def download_audio_from_youtube(url):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for f in os.listdir():
            if f.startswith("audio"):
                return f
        return None

    except:
        return None

# =========================
# NLP FEATURES
# =========================
def summarize_text(text, level):
    sentences = text.split(". ")

    if level == "Short":
        return ". ".join(sentences[:3])
    elif level == "Medium":
        return ". ".join(sentences[:7])
    else:
        return text

def extract_chapters(text):
    sentences = text.split(". ")
    chapters = []

    step = max(1, len(sentences)//5)
    time = 0

    for i in range(0, len(sentences), step):
        chunk = sentences[i:i+step]
        if chunk:
            chapters.append({
                "time": f"{time:02d}:00",
                "title": chunk[0][:50]
            })
            time += 1

    return chapters

def translate_text(text, lang):
    if lang == "en":
        return text
    return GoogleTranslator(source="auto", target=lang).translate(text)

# =========================
# EXPORT FUNCTIONS
# =========================
def save_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    safe = text.encode("latin-1", "ignore").decode("latin-1")
    pdf.multi_cell(0, 8, safe)
    file = "output.pdf"
    pdf.output(file)
    return file

def save_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    file = "output.docx"
    doc.save(file)
    return file

def save_ppt(text):
    prs = Presentation()
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "AI Summary"
    slide.placeholders[1].text = text
    file = "output.pptx"
    prs.save(file)
    return file

def text_to_audio(text):
    tts = gTTS(text)
    file = "output.mp3"
    tts.save(file)
    return file
