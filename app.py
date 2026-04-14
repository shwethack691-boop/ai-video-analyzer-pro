import streamlit as st
import yt_dlp
import os

from utils import (
    transcribe_audio,
    generate_summary,
    extract_bullets,
    generate_chapters,
    translate_text,
    save_pdf,
    save_docx,
    save_ppt,
    text_to_audio
)

# -----------------------
# PAGE CONFIG (CLEAN SAAS)
# -----------------------
st.set_page_config(page_title="SaaS Tool", layout="wide")

# -----------------------
# SESSION STATE
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------
# LOGIN ONLY
# -----------------------
if not st.session_state.logged_in:
    st.markdown("### 🔐 Login")

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

# -----------------------
# SIDEBAR (MINIMAL)
# -----------------------
st.sidebar.write(f"👤 {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Tool", "History"])

# -----------------------
# HISTORY
# -----------------------
if menu == "History":
    for h in st.session_state.history:
        st.write(h)
    st.stop()

# -----------------------
# TOOL PAGE (NO BIG HEADINGS)
# -----------------------
input_type = st.radio("Input", ["Upload", "YouTube Link"])

text = ""

# -----------------------
# UPLOAD FILE
# -----------------------
if input_type == "Upload":
    file = st.file_uploader("Upload video/audio")

    if file:
        path = "temp.mp4"
        with open(path, "wb") as f:
            f.write(file.read())

        st.info("Processing...")
        text = transcribe_audio(path)

# -----------------------
# YOUTUBE LINK
# -----------------------
if input_type == "YouTube Link":
    url = st.text_input("Paste link")

    if url:
        st.info("Processing YouTube...")

        try:
            ydl_opts = {"format": "bestaudio/best", "outtmpl": "video.mp4"}

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            text = transcribe_audio("video.mp4")

        except:
            st.error("YouTube blocked. Use upload.")

# -----------------------
# OUTPUT (NO HEADINGS OVERLOAD)
# -----------------------
if text:
    st.session_state.history.append(text)

    st.text_area("Transcript", text, height=200)

    # SUMMARY LEVEL
    level = st.selectbox("Summary", ["short", "medium", "long"])
    summary = generate_summary(text, level)
    st.text_area("Summary", summary, height=150)

    # BULLETS
    st.write(extract_bullets(text))

    # CHAPTERS
    st.write(generate_chapters(text))

    # TRANSLATION
    lang = st.selectbox("Language", ["en", "hi", "kn", "ta", "te", "fr", "de"])
    translated = translate_text(summary, lang)

    st.text_area("Translated", translated, height=150)

    # EXPORT
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("PDF"):
            file = save_pdf(translated)
            st.download_button("Download PDF", open(file, "rb"), file_name=file)

    with col2:
        if st.button("DOC"):
            file = save_docx(translated)
            st.download_button("Download DOC", open(file, "rb"), file_name=file)

    with col3:
        if st.button("PPT"):
            file = save_ppt(translated)
            st.download_button("Download PPT", open(file, "rb"), file_name=file)

    if st.button("Audio"):
        audio = text_to_audio(translated)
        st.audio(audio)
        st.download_button("Download Audio", open(audio, "rb"), file_name=audio)
