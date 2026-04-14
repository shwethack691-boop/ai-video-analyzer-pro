import streamlit as st
import yt_dlp
import whisper
from utils import (
    translate_text,
    save_docx,
    save_pdf,
    save_ppt,
    text_to_audio
)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Video Analyzer Pro", layout="wide")

# =========================
# SESSION STATE INIT
# =========================
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = ""

if "history" not in st.session_state:
    st.session_state.history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""


# =========================
# AUTH SYSTEM (LOGIN + REGISTER)
# =========================
if not st.session_state.logged_in:

    st.title("🔐 AI Video Analyzer Login")

    menu = st.radio("Select Option", ["Login", "Register"])

    # ---------------- LOGIN ----------------
    if menu == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    # ---------------- REGISTER ----------------
    elif menu == "Register":
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Register"):
            if new_user in st.session_state.users:
                st.error("User already exists")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("Registered successfully! Now login.")

    st.stop()


# =========================
# SIDEBAR
# =========================
st.sidebar.title(f"👤 {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard", "History"])

# =========================
# HISTORY PAGE
# =========================
if menu == "History":
    st.title("📜 History")

    if len(st.session_state.history) == 0:
        st.info("No history yet")
    else:
        for i, h in enumerate(st.session_state.history):
            st.write(f"{i+1}. {h}")

    st.stop()


# =========================
# DOWNLOAD YOUTUBE AUDIO
# =========================
def download_audio(url):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "video.mp4",
        "quiet": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return "video.mp4"


# =========================
# WHISPER TRANSCRIPTION
# =========================
@st.cache_resource
def load_model():
    return whisper.load_model("base")


def transcribe_audio(file):
    model = load_model()
    result = model.transcribe(file)
    return result["text"]


# =========================
# SIMPLE AI SUMMARY
# =========================
def generate_summary(text):
    sentences = text.split(".")
    return ". ".join(sentences[:5])  # simple smart summary


# =========================
# TIMELINE CHAPTERS
# =========================
def generate_chapters(text):
    words = text.split()
    chunk_size = 80
    chapters = []

    for i in range(0, len(words), chunk_size):
        chapters.append(" ".join(words[i:i+chunk_size]))

    return chapters


# =========================
# DASHBOARD
# =========================
st.title("🎬 AI Video Analyzer Pro (SaaS Version)")

input_type = st.radio("Input Type", ["YouTube URL", "Upload File"])

text = ""

# ---------------- YOUTUBE ----------------
if input_type == "YouTube URL":
    url = st.text_input("Enter YouTube URL")

    if st.button("Process YouTube"):
        try:
            file = download_audio(url)
            text = transcribe_audio(file)

            st.session_state.transcript = text
            st.session_state.history.append(text)

        except Exception as e:
            st.error("YouTube download failed. Please upload file instead.")
            st.write(str(e))


# ---------------- FILE UPLOAD ----------------
if input_type == "Upload File":
    file = st.file_uploader("Upload Video/Audio")

    if file and st.button("Process File"):
        with open("temp.mp4", "wb") as f:
            f.write(file.read())

        text = transcribe_audio("temp.mp4")

        st.session_state.transcript = text
        st.session_state.history.append(text)


# =========================
# OUTPUT SECTION
# =========================
if st.session_state.transcript:

    st.subheader("📄 Transcript")
    st.write(st.session_state.transcript)

    # ---------------- SUMMARY ----------------
    st.subheader("🧠 AI Summary")

    summary_level = st.radio("Summary Level", ["Short", "Medium", "Long"])

    if summary_level == "Short":
        summary = generate_summary(st.session_state.transcript)
    elif summary_level == "Medium":
        summary = st.session_state.transcript[:800]
    else:
        summary = st.session_state.transcript

    st.write(summary)

    st.session_state.summary = summary

    # ---------------- TRANSLATION ----------------
    st.subheader("🌍 Translation")

    lang = st.selectbox(
        "Select Language",
        ["en", "hi", "kn", "ta", "te", "ml", "fr", "de", "es"]
    )

    translated = translate_text(summary, lang)
    st.write(translated)

    # ---------------- CHAPTERS ----------------
    st.subheader("⏱ Timeline Chapters")

    chapters = generate_chapters(st.session_state.transcript)

    for i, ch in enumerate(chapters):
        st.write(f"**Chapter {i+1}:** {ch[:200]}...")

    # ---------------- EXPORT ----------------
    st.subheader("📤 Export")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("DOCX"):
            file = save_docx(summary)
            st.download_button("Download DOCX", open(file, "rb"), file_name=file)

    with col2:
        if st.button("PDF"):
            file = save_pdf(summary)
            st.download_button("Download PDF", open(file, "rb"), file_name=file)

    with col3:
        if st.button("PPT"):
            file = save_ppt(summary)
            st.download_button("Download PPT", open(file, "rb"), file_name=file)

    with col4:
        if st.button("AUDIO"):
            audio = text_to_audio(summary)
            st.audio(audio)
            st.download_button("Download MP3", open(audio, "rb"), file_name=audio)
