import streamlit as st
import os

from utils import (
    register_user,
    login_user,
    transcribe_audio,
    download_audio_from_youtube,
    summarize_text,
    extract_chapters,
    translate_text,
    save_pdf,
    save_docx,
    save_ppt,
    text_to_audio
)

st.set_page_config(page_title="AI Video Analyzer Pro", layout="wide")

# =========================
# SESSION STATE
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

# =========================
# AUTH PAGE (LOGIN + REGISTER)
# =========================
if not st.session_state.logged_in:

    st.title("🔐 AI Video Analyzer - Auth System")

    choice = st.radio("Choose Option", ["Login", "Register"])

    # ================= REGISTER =================
    if choice == "Register":
        st.subheader("📝 Register")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Register"):
            if register_user(new_user, new_pass):
                st.success("Registered successfully! Now login.")
            else:
                st.error("User already exists")

    # ================= LOGIN =================
    if choice == "Login":
        st.subheader("🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# =========================
# DASHBOARD
# =========================
st.sidebar.title(f"👤 Welcome {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["🏠 Dashboard", "📜 History"])

st.title("🎬 AI Video Analyzer Pro (SaaS)")

# =========================
# INPUT
# =========================
input_type = st.radio("Input Type", ["Upload File", "YouTube URL"])

text = ""

# =========================
# UPLOAD
# =========================
if input_type == "Upload File":
    file = st.file_uploader("Upload Video/Audio", type=["mp4", "mp3", "wav", "m4a"])

    if file:
        path = "temp.mp4"
        with open(path, "wb") as f:
            f.write(file.read())

        st.info("Transcribing...")
        text = transcribe_audio(path)

# =========================
# YOUTUBE
# =========================
if input_type == "YouTube URL":
    url = st.text_input("Enter YouTube URL")

    if url:
        st.info("Processing YouTube...")

        audio = download_audio_from_youtube(url)

        if audio:
            text = transcribe_audio(audio)
        else:
            st.error("YouTube download failed. Please upload file.")

# =========================
# OUTPUT
# =========================
if text:
    st.subheader("📄 Transcript")
    st.write(text)

    # SAVE HISTORY
    st.session_state.setdefault("history", []).append(text)

    # ================= SUMMARY =================
    st.subheader("🧠 AI Summary")
    level = st.radio("Summary Level", ["Short", "Medium", "Long"])
    summary = summarize_text(text, level)
    st.write(summary)

    # ================= CHAPTERS =================
    st.subheader("⏱ Chapters")
    chapters = extract_chapters(text)
    for c in chapters:
        st.write(f"{c['time']} - {c['title']}")

    # ================= TRANSLATION =================
    lang = st.selectbox("🌍 Translate", ["en", "hi", "kn", "ta", "te", "fr", "de"])
    translated = translate_text(summary, lang)

    st.subheader("🌍 Translated")
    st.write(translated)

    # ================= EXPORT =================
    st.subheader("📤 Export")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("PDF"):
            file = save_pdf(translated)
            st.download_button("Download", open(file, "rb"), file_name="report.pdf")

    with col2:
        if st.button("DOCX"):
            file = save_docx(translated)
            st.download_button("Download", open(file, "rb"), file_name="report.docx")

    with col3:
        if st.button("PPT"):
            file = save_ppt(translated)
            st.download_button("Download", open(file, "rb"), file_name="report.pptx")

    with col4:
        if st.button("AUDIO"):
            audio = text_to_audio(translated)
            st.audio(audio)
            st.download_button("Download", open(audio, "rb"), file_name="audio.mp3")
