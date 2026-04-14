import streamlit as st
import yt_dlp
import whisper
from utils import (
    translate_text,
    save_pdf,
    save_docx,
    save_ppt,
    text_to_audio,
    generate_summary,
    generate_chapters,
    extract_highlights
)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Video Analyzer SaaS", layout="wide")

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:
    st.title("🔐 AI Video Analyzer Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user and pwd:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Enter credentials")

    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title(f"👤 Welcome {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard", "History"])

# =========================
# HISTORY
# =========================
if menu == "History":
    st.title("📜 History")

    for i, h in enumerate(st.session_state.history):
        st.write(f"{i+1}. {h}")

    st.stop()

# =========================
# YT DOWNLOAD FIXED FUNCTION
# =========================
def download_audio(url):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)

    except Exception:
        return None

# =========================
# TRANSCRIBE
# =========================
def transcribe(file):
    model = whisper.load_model("base")
    result = model.transcribe(file)
    return result["text"]

# =========================
# DASHBOARD
# =========================
st.title("🎬 AI Video Analyzer SaaS")

input_type = st.radio("Input Type", ["YouTube URL", "Upload File"])

text = ""

# =========================
# YOUTUBE
# =========================
if input_type == "YouTube URL":
    url = st.text_input("Enter YouTube URL")

    if url and st.button("Process"):
        audio_file = download_audio(url)

        if audio_file:
            text = transcribe(audio_file)
            st.session_state.transcript = text
        else:
            st.error("YouTube blocked download. Please upload file.")
            st.stop()

# =========================
# UPLOAD
# =========================
if input_type == "Upload File":
    file = st.file_uploader("Upload Video / Audio")

    if file:
        with open("temp.mp4", "wb") as f:
            f.write(file.read())

        text = transcribe("temp.mp4")
        st.session_state.transcript = text

# =========================
# OUTPUT SECTION
# =========================
if st.session_state.transcript:

    st.subheader("📄 Transcript")
    st.write(st.session_state.transcript)

    st.session_state.history.append(st.session_state.transcript)

    # =========================
    # LANGUAGE
    # =========================
    lang = st.selectbox("🌍 Language", ["en", "hi", "kn", "ta", "te", "fr", "de", "es"])

    translated = translate_text(st.session_state.transcript, lang)

    st.subheader("🌍 Translation")
    st.write(translated)

    # =========================
    # AI FEATURES
    # =========================
    st.subheader("🧠 AI Summary")

    level = st.radio("Summary Type", ["Short", "Medium", "Long"])

    summary = generate_summary(translated, level)
    st.write(summary)

    # =========================
    # HIGHLIGHTS
    # =========================
    st.subheader("⭐ Highlights")
    highlights = extract_highlights(translated)
    st.write(highlights)

    # =========================
    # CHAPTERS
    # =========================
    st.subheader("⏱ Timeline Chapters")
    chapters = generate_chapters(translated)
    st.write(chapters)

    # =========================
    # EXPORT
    # =========================
    st.subheader("📤 Export")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("PDF"):
            file = save_pdf(summary)
            st.download_button("Download PDF", open(file, "rb"), file_name="report.pdf")

    with col2:
        if st.button("DOCX"):
            file = save_docx(summary)
            st.download_button("Download DOCX", open(file, "rb"), file_name="report.docx")

    with col3:
        if st.button("PPT"):
            file = save_ppt(summary)
            st.download_button("Download PPT", open(file, "rb"), file_name="report.pptx")

    with col4:
        if st.button("Audio"):
            file = text_to_audio(summary)
            st.audio(file)
            st.download_button("Download MP3", open(file, "rb"), file_name="audio.mp3")
