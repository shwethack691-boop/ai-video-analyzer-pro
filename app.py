import streamlit as st
import yt_dlp
from utils import (
    transcribe_audio,
    translate_text,
    generate_summary,
    extract_bullets,
    generate_chapters,
    save_docx,
    save_pdf,
    save_ppt,
    text_to_audio
)
import os

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(page_title="AI Video Analyzer SaaS", layout="wide")

# -----------------------
# SESSION STATE
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------
# LOGIN
# -----------------------
if not st.session_state.logged_in:
    st.title("🔐 SaaS Login")

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user and pwd:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.rerun()

    st.stop()

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title(f"👤 {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard", "History"])

# -----------------------
# HISTORY
# -----------------------
if menu == "History":
    st.title("📜 History")
    for h in st.session_state.history:
        st.write(h)
    st.stop()

# -----------------------
# DASHBOARD
# -----------------------
st.title("🎬 AI Video Analyzer Pro (SaaS)")

input_type = st.radio("Input Type", ["Upload File", "YouTube URL"])

text = ""

# -----------------------
# FILE UPLOAD
# -----------------------
if input_type == "Upload File":
    file = st.file_uploader("Upload Video/Audio")

    if file:
        path = "temp.mp4"
        with open(path, "wb") as f:
            f.write(file.read())

        st.info("Transcribing...")
        text = transcribe_audio(path)

# -----------------------
# YOUTUBE (SAFE MODE)
# -----------------------
if input_type == "YouTube URL":
    url = st.text_input("Enter YouTube URL")

    if url:
        st.warning("⚠ YouTube may fail on cloud. If error, upload file instead.")

        try:
            ydl_opts = {"format": "bestaudio/best", "outtmpl": "video.mp4"}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            text = transcribe_audio("video.mp4")

        except:
            st.error("YouTube blocked. Please upload file.")

# -----------------------
# OUTPUT SECTION
# -----------------------
if text:
    st.subheader("📄 Transcript")
    st.write(text)

    st.session_state.history.append(text)

    # SUMMARY
    mode = st.selectbox("AI Summary Level", ["short", "medium", "long"])
    summary = generate_summary(text, mode)

    st.subheader("🧠 AI Summary")
    st.write(summary)

    # BULLETS
    st.subheader("📌 Key Highlights")
    st.write(extract_bullets(text))

    # CHAPTERS
    st.subheader("⏱ Timeline Chapters")
    st.write(generate_chapters(text))

    # TRANSLATION
    lang = st.selectbox("🌍 Language", ["en", "hi", "kn", "ta", "te", "fr", "de"])
    translated = translate_text(summary, lang)

    st.subheader("🌍 Translated Summary")
    st.write(translated)

    # EXPORT
    st.subheader("📤 Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("PDF"):
            file = save_pdf(translated)
            st.download_button("Download", open(file, "rb"), file_name=file)

    with col2:
        if st.button("DOCX"):
            file = save_docx(translated)
            st.download_button("Download", open(file, "rb"), file_name=file)

    with col3:
        if st.button("PPT"):
            file = save_ppt(translated)
            st.download_button("Download", open(file, "rb"), file_name=file)

    # AUDIO
    if st.button("Generate Audio"):
        audio = text_to_audio(translated, lang)
        st.audio(audio)
        st.download_button("Download MP3", open(audio, "rb"), file_name=audio)
