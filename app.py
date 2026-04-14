import streamlit as st
import yt_dlp
import whisper
from utils import (
    save_docx,
    save_pdf,
    save_ppt,
    text_to_audio,
    translate_text,
    generate_summary,
    generate_chapters
)

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Video Analyzer Pro", layout="wide")

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "translated" not in st.session_state:
    st.session_state.translated = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "chapters" not in st.session_state:
    st.session_state.chapters = ""

# =========================
# LOGIN PAGE
# =========================
if not st.session_state.logged_in:
    st.title("🔐 AI Video Analyzer Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.rerun()
        else:
            st.error("Enter credentials")

    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title(f"👤 Welcome {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["🏠 Dashboard", "📜 History"])

# =========================
# HISTORY
# =========================
if menu == "📜 History":
    st.title("History")
    for i, h in enumerate(st.session_state.history):
        st.write(f"{i+1}. {h}")
    st.stop()

# =========================
# SAFE YOUTUBE DOWNLOAD
# =========================
def download_audio(url):
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "audio.%(ext)s",
            "quiet": True,
            "noplaylist": True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        return "audio.webm"

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
st.title("🎬 AI Video Analyzer Pro (SaaS Ready)")

input_type = st.radio("Input Type", ["Upload File", "YouTube URL"])

text = ""

# =========================
# UPLOAD FILE (BEST OPTION)
# =========================
if input_type == "Upload File":
    file = st.file_uploader("Upload Video/Audio")

    if file:
        path = "temp.mp4"
        with open(path, "wb") as f:
            f.write(file.read())

        text = transcribe(path)

# =========================
# YOUTUBE (FALLBACK)
# =========================
if input_type == "YouTube URL":
    url = st.text_input("Enter YouTube URL")

    if url:
        audio = download_audio(url)

        if audio is None:
            st.error("⚠ YouTube failed. Please upload file instead.")
            st.stop()

        text = transcribe(audio)

# =========================
# OUTPUT
# =========================
if text:
    st.subheader("📄 Transcript")
    st.write(text)

    st.session_state.history.append(text)

    # =========================
    # LANGUAGE FIX (NO RESET ISSUE)
    # =========================
    lang = st.selectbox(
        "🌍 Select Language",
        ["en", "hi", "kn", "ta", "te", "ml", "fr", "de", "es", "zh"],
        key="lang_select"
    )

    if st.button("Translate"):
        st.session_state.translated = translate_text(text, lang)

    if st.session_state.translated:
        st.subheader("🌍 Translation")
        st.write(st.session_state.translated)

    final_text = st.session_state.translated or text

    # =========================
    # AI SUMMARY
    # =========================
    st.subheader("🧠 AI Summary")

    level = st.radio("Summary Level", ["short", "medium", "long"])

    if st.button("Generate Summary"):
        st.session_state.summary = generate_summary(final_text, level)

    if st.session_state.summary:
        st.write(st.session_state.summary)

    # =========================
    # CHAPTERS
    # =========================
    if st.button("Generate Chapters"):
        st.session_state.chapters = generate_chapters(text)

    if st.session_state.chapters:
        st.subheader("⏱ Timeline Chapters")
        st.write(st.session_state.chapters)

    # =========================
    # EXPORT
    # =========================
    st.subheader("📤 Export")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("PDF"):
            save_pdf(final_text)
            st.success("PDF Saved")

    with col2:
        if st.button("DOCX"):
            save_docx(final_text)
            st.success("DOCX Saved")

    with col3:
        if st.button("PPT"):
            save_ppt(final_text)
            st.success("PPT Saved")

    with col4:
        if st.button("AUDIO"):
            text_to_audio(final_text)
            st.success("Audio Saved")
