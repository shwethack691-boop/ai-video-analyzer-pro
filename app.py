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
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "history" not in st.session_state:
    st.session_state.history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

# =========================
# AUTH SYSTEM (LOGIN + REGISTER)
# =========================
if not st.session_state.logged_in:

    st.title("🔐 AI Video Analyzer - Login System")

    menu = st.radio("Choose Option", ["Login", "Register"])

    # ================= REGISTER =================
    if menu == "Register":
        st.subheader("📝 Create New Account")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Register"):
            if new_user in st.session_state.users:
                st.error("User already exists")
            elif new_user == "" or new_pass == "":
                st.error("Fill all fields")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("Registered successfully! Go to Login")

    # ================= LOGIN =================
    if menu == "Login":
        st.subheader("🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title(f"👤 Welcome {st.session_state.user}")

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
# YOUTUBE DOWNLOAD (SAFE)
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
# YOUTUBE INPUT
# =========================
if input_type == "YouTube URL":
    url = st.text_input("Enter YouTube URL")

    if url and st.button("Process"):
        audio_file = download_audio(url)

        if audio_file:
            text = transcribe(audio_file)
        else:
            st.error("YouTube blocked download. Please upload file instead.")
            st.stop()

# =========================
# FILE UPLOAD
# =========================
if input_type == "Upload File":
    file = st.file_uploader("Upload Video / Audio")

    if file:
        with open("temp.mp4", "wb") as f:
            f.write(file.read())

        text = transcribe("temp.mp4")

# =========================
# OUTPUT SECTION
# =========================
if text:
    st.subheader("📄 Transcript")
    st.write(text)

    st.session_state.history.append(text)

    # ================= TRANSLATION =================
    lang = st.selectbox("🌍 Language", ["en", "hi", "kn", "ta", "te", "fr", "de", "es"])

    translated = translate_text(text, lang)

    st.subheader("🌍 Translation")
    st.write(translated)

    # ================= AI SUMMARY =================
    st.subheader("🧠 AI Summary")

    level = st.radio("Summary Level", ["Short", "Medium", "Long"])

    summary = generate_summary(translated, level)
    st.write(summary)

    # ================= HIGHLIGHTS =================
    st.subheader("⭐ Highlights")
    highlights = extract_highlights(translated)
    st.write(highlights)

    # ================= CHAPTERS =================
    st.subheader("⏱ Timeline Chapters")
    chapters = generate_chapters(translated)
    st.write(chapters)

    # ================= EXPORT =================
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
        if st.button("AUDIO"):
            file = text_to_audio(summary)
            st.audio(file)
            st.download_button("Download MP3", open(file, "rb"), file_name="audio.mp3")
