import re
import os
import whisper
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline

# Load models once
model = whisper.load_model("base")
summarizer = pipeline("summarization")
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")

# -------- EXTRACT VIDEO ID --------
def extract_video_id(url):
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    return match.group(1) if match else None

# -------- YOUTUBE PROCESS --------
def get_youtube_text(url):
    video_id = extract_video_id(url)

    if not video_id:
        return None

    # STEP 1: captions
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t["text"] for t in transcript])
        if text.strip():
            return text
    except:
        pass

    # STEP 2: download audio
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'yt_audio.%(ext)s',
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for file in os.listdir():
            if file.startswith("yt_audio"):
                text = transcribe_audio(file)
                os.remove(file)
                return text
    except:
        pass

    return None

# -------- TRANSCRIBE --------
def transcribe_audio(file_path):
    result = model.transcribe(file_path)
    return result["text"]

# -------- SUMMARY --------
def summarize_text(text):
    if len(text) < 50:
        return text
    return summarizer(text[:1000])[0]["summary_text"]

# -------- TRANSLATION --------
def translate_text(text):
    return translator(text)[0]["translation_text"]
