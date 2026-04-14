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
    generate_chapters,
    extract_highlights
)

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="AI Video Analyzer Pro", layout="wide")

# =========================
# SESSION STATE INIT
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "users" not in st.session_state:
    st.session_state.users = {}

if "user" not in st.session_state:
    st.session_state.user = ""

if "text" not in st.session_state:
    st.session_state.text = ""

if "translated" not in st.session_state:
    st.session_state.translated = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "chapters" not in st.session_state:
    st.session_state.chapters = ""

if "highlights" not in st.session_state:
    st.session_state.highlights = []

if "lang" not in st.session_state:
    st.session_state.lang = "en"

if "summary_level" not in st.session_state:
    st.session_state.summary_level = "medium"

if "history" not in st.session_state:
    st.session_state.history = []

# =========================
# LOGIN + REGISTER PAGE
# =========================
if not st.session_state.logged_in:

    st.title("🔐 AI Video Analyzer Pro")

    mode = st.radio("Select Option", ["Login", "Register"])

    # ---------------- REGISTER ----------------
    if mode == "Register":
        st.subheader("📝 Register")

        new_user = st.text_input("Username")
        new_pass = st.text_input("Password", type="password")

        if st.button("Register"):
            if new_user in st.session_state.users:
                st.error("User already exists ❌")
            else:
                st.session_state.users[new_user] = new_pass
                st.success("Registered Successfully ✅ Please Login")

    # ---------------- LOGIN ----------------
    if mode == "Login":
        st.subheader("🔑 Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid Credentials ❌")

    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title(f"👤 Welcome {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["🏠 Dashboard", "📜 History"])

# =========================
# HISTORY PAGE
# =========================
if menu == "📜 History":
    st.title("📜 History")
    for i, h in enumerate(st.session_state.history):
        st.write(f"{i+1}. {h}")
    st.stop()

# =========================
# DOWNLOAD YOUTUBE
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
# TRANSCRIBE
# =========================
def transcribe(file):
    model = whisper.load_model("base")
    result = model.transcribe(file)
    return result["text"]

# =========================
# DASHBOARD
# =========================
st.title("🎬 AI Video Analyzer Pro (Industry SaaS)")

input_type = st.radio("Input Type", ["YouTube URL", "Upload File"])

text = ""

# =========================
# YOUTUBE INPUT
# =========================
if input_type == "YouTube URL":
    url = st.text_input("Enter YouTube URL")

    if st.button("Process"):
        file = download_audio(url)
        text = transcribe(file)

        st.session_state.text = text
        st.session_state.history.append(text)

# =========================
# FILE UPLOAD
# =========================
if input_type == "Upload File":
    file = st.file_uploader("Upload Video/Audio")

    if file and st.button("Process"):
        with open("temp.mp4", "wb") as f:
            f.write(file.read())

        text = transcribe("temp.mp4")

        st.session_state.text = text
        st.session_state.history.append(text)

# =========================
# OUTPUT SECTION
# =========================
if st.session_state.text:

    st.subheader("📄 Transcript")
    st.write(st.session_state.text)

    # =========================
    # TRANSLATION (NO RESET BUG FIX)
    # =========================
    st.session_state.lang = st.selectbox(
        "🌍 Language",
        ["en", "hi", "kn", "ta", "te", "ml", "fr", "de", "es"],
        index=["en", "hi", "kn", "ta", "te", "ml", "fr", "de", "es"].index(st.session_state.lang)
    )

    if st.button("Translate"):
        st.session_state.translated = translate_text(
            st.session_state.text,
            st.session_state.lang
        )

    if st.session_state.translated:
        st.subheader("🌍 Translation")
        st.write(st.session_state.translated)

    final_text = st.session_state.translated or st.session_state.text

    # =========================
    # 🧠 AI SUMMARY
    # =========================
    st.subheader("🧠 AI Summary")

    st.session_state.summary_level = st.radio(
        "Summary Level",
        ["short", "medium", "long"],
        horizontal=True
    )

    if st.button("Generate Summary"):
        st.session_state.summary = generate_summary(
            final_text,
            st.session_state.summary_level
        )

    if st.session_state.summary:
        st.success(st.session_state.summary)

    # =========================
    # 📌 HIGHLIGHTS
    # =========================
    if st.button("Extract Highlights"):
        st.session_state.highlights = extract_highlights(final_text)

    if st.session_state.highlights:
        st.subheader("📌 Highlights")
        for h in st.session_state.highlights:
            st.markdown(f"✔ {h}")

    # =========================
    # ⏱ CHAPTERS
    # =========================
    if st.button("Generate Chapters"):
        st.session_state.chapters = generate_chapters(final_text)

    if st.session_state.chapters:
        st.subheader("⏱ Timeline Chapters")
        st.write(st.session_state.chapters)

    # =========================
    # 📤 EXPORT
    # =========================
    st.subheader("📤 Export")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("PDF"):
            file = save_pdf(final_text)
            st.download_button("Download PDF", open(file, "rb"), file_name="report.pdf")

    with col2:
        if st.button("DOCX"):
            file = save_docx(final_text)
            st.download_button("Download DOCX", open(file, "rb"), file_name="report.docx")

    with col3:
        if st.button("PPT"):
            file = save_ppt(final_text)
            st.download_button("Download PPT", open(file, "rb"), file_name="report.pptx")

    # =========================
    # AUDIO
    # =========================
    if st.button("Generate Audio"):
        audio = text_to_audio(final_text)
        st.audio(audio)
        st.download_button("Download MP3", open(audio, "rb"), file_name="audio.mp3")