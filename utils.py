import os
import yt_dlp
import whisper
from transformers import pipeline

# ---------------- LOAD MODELS ----------------
whisper_model = whisper.load_model("base")

# Summarizer model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Translator model (multi-language)
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")  
# 👉 You can change 'en-hi' to:
# en-fr (French), en-es (Spanish), en-de (German), etc.

# ---------------- DOWNLOAD AUDIO ----------------
def download_audio(url):
    output_path = "downloads"
    os.makedirs(output_path, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            audio_file = os.path.splitext(filename)[0] + ".mp3"
            return audio_file
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- TRANSCRIBE WITH TIMESTAMPS ----------------
def transcribe_audio(file_path):
    try:
        result = whisper_model.transcribe(file_path)

        text = result["text"]

        # Extract timestamps
        timestamps = []
        for segment in result["segments"]:
            start = round(segment["start"], 2)
            end = round(segment["end"], 2)
            content = segment["text"]
            timestamps.append(f"[{start}s - {end}s] {content}")

        return text, timestamps

    except Exception as e:
        return f"Error: {str(e)}", []

# ---------------- SUMMARIZE TEXT ----------------
def summarize_text(text):
    try:
        if len(text) < 50:
            return "Text too short to summarize."

        summary = summarizer(
            text,
            max_length=150,
            min_length=50,
            do_sample=False
        )

        return summary[0]['summary_text']

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- TRANSLATE TEXT ----------------
def translate_text(text):
    try:
        translated = translator(text, max_length=512)
        return translated[0]['translation_text']
    except Exception as e:
        return f"Error: {str(e)}"
