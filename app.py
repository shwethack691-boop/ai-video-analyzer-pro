import streamlit as st
import os
import json
from utils import (
    transcribe_audio,
    get_youtube_transcript,
    summarize_text,
    translate_text,
    text_to_speech,
    create_pdf,
    create_docx
)

st.set_page_config(page_title="AI Video Summarizer", layout="wide")

# -------------------------
# FILES
# -------------------------
USER_FILE = "users.json"
HISTORY_FILE = "history.json"

# Create if not exists
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# -------------------------
# USER FUNCTIONS
# -------------------------
def load_users():
    return json.load(open(USER_FILE))

def save_users(users):
    json.dump(users, open(USER_FILE, "w"))

def register(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = password
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    return username in users and users[username] == password

# -------------------------
# HISTORY
# -------------------------
def save_history(user, text):
    data = json.load(open(HISTORY_FILE))
    data.append({"user": user, "text": text})
    json.dump(data, open(HISTORY_FILE, "w"))

def load_history(user):
    data = json.load(open(HISTORY_FILE))
    return [d["text"] for d in data if d["user"] == user]

# -------------------------
# SESSION
# -------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------
# LOGIN / REGISTER
# -------------------------
if not st.session_state.user:
    st.title("🔐 AI Video Summarizer & Translator")

    menu = st.selectbox("Choose Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if menu == "Register":
        if st.button("Register"):
            if register(username, password):
                st.success("✅ Registered successfully! Please login.")
            else:
                st.error("❌ Username already exists")

    if menu == "Login":
        if st.button("Login"):
            if login(username, password):
                st.session_state.user = username
                st.rerun()
            else:
                st.error("❌ Invalid username or password")

    st.stop()

# -------------------------
# MAIN APP
# -------------------------
st.sidebar.write(f"👤 {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Tool", "History", "Logout"])

# Logout
if menu == "Logout":
    st.session_state.user = None
    st.rerun()

# -------------------------
# TOOL PAGE
# -------------------------
if menu == "Tool":
    st.title("🎬 AI Video Analyzer PRO")

    option = st.radio("Input Type", ["Upload", "YouTube Link"])
    text = ""

    # -------------------------
    # UPLOAD (LOCAL ONLY)
    # -------------------------
    if option == "Upload":
        file = st.file_uploader("Upload video/audio")

        if file:
            path = file.name
            with open(path, "wb") as f:
                f.write(file.read())

            st.info("Processing file...")

            text = transcribe_audio(path)

            if "⚠" in text:
                st.warning(text)

    # -------------------------
    # YOUTUBE (CLOUD SAFE)
    # -------------------------
    if option == "YouTube Link":
        url = st.text_input("Enter YouTube URL")

        if st.button("Fetch"):
            try:
                if "v=" in url:
                    video_id = url.split("v=")[-1].split("&")[0]
                else:
                    video_id = url.split("/")[-1]

                text = get_youtube_transcript(video_id)

                if not text:
                    st.error("❌ No captions available for this video")
            except:
                st.error("❌ Invalid YouTube URL")

    # -------------------------
    # PROCESS OUTPUT
    # -------------------------
    if text:
        st.subheader("📄 Transcript")
        st.write(text)

        # Summary
        summary = summarize_text(text)
        st.subheader("🧠 Summary")
        st.write(summary)

        # Translation
        lang = st.selectbox("🌍 Translate to", ["hi", "kn", "ta", "fr"])
        translated = translate_text(summary, lang)

        st.subheader("🌐 Translation")
        st.write(translated)

        # Audio
        audio_file = text_to_speech(summary)
        if audio_file:
            st.audio(audio_file)

        # Downloads
        pdf = create_pdf(summary)
        docx = create_docx(summary)

        if pdf:
            with open(pdf, "rb") as f:
                st.download_button("📄 Download PDF", f, file_name="summary.pdf")

        if docx:
            with open(docx, "rb") as f:
                st.download_button("📝 Download DOCX", f, file_name="summary.docx")

        # Save history
        save_history(st.session_state.user, summary)

# -------------------------
# HISTORY PAGE
# -------------------------
if menu == "History":
    st.title("📜 History")

    history = load_history(st.session_state.user)

    if not history:
        st.info("No history yet")
    else:
        for item in history[::-1]:
            st.write(item)
            st.markdown("---")
