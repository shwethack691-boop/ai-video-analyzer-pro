import streamlit as st
import json
import os
from utils import (
    download_audio,
    transcribe_audio,
    summarize_text,
    translate_text
)
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# ---------------- FILES ----------------
USER_FILE = "users.json"
HISTORY_FILE = "history.json"

# ---------------- INIT FILES ----------------
if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

# ---------------- USER FUNCTIONS ----------------
def load_users():
    try:
        with open(USER_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except:
        return []

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)

def register(username, password):
    users = load_users()

    for u in users:
        if isinstance(u, dict) and u.get("username") == username:
            return False

    users.append({"username": username, "password": password})
    save_users(users)
    return True

def login(username, password):
    users = load_users()

    for u in users:
        if isinstance(u, dict):
            if u.get("username") == username and u.get("password") == password:
                return True
    return False

# ---------------- HISTORY ----------------
def load_history():
    try:
        with open(HISTORY_FILE) as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_history(user, text):
    data = load_history()
    data.append({"user": user, "text": text})
    save_history(data)

# ---------------- PDF GENERATION ----------------
def create_pdf(text, filename="summary.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    content = []

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))

    doc.build(content)
    return filename

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- AUTH ----------------
def auth():
    st.title("🔐 AI Video Summarizer & Translator")

    choice = st.radio("Select", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Register"):
            if register(username, password):
                st.success("Registered successfully")
            else:
                st.error("User already exists")

    if choice == "Login":
        if st.button("Login"):
            if login(username, password):
                st.session_state.user = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

# ---------------- MAIN ----------------
if not st.session_state.user:
    auth()
    st.stop()

st.sidebar.write(f"👤 {st.session_state.user}")
menu = st.sidebar.selectbox("Menu", ["Tool", "History", "Logout"])

# ---------------- LOGOUT ----------------
if menu == "Logout":
    st.session_state.user = None
    st.rerun()

# ---------------- TOOL ----------------
if menu == "Tool":
    st.title("🎬 AI Video Analyzer Pro")

    option = st.radio("Input Type", ["YouTube URL", "Upload File"])

    # -------- YOUTUBE --------
    if option == "YouTube URL":
        url = st.text_input("Enter YouTube URL")

        if st.button("Process YouTube"):
            if not url:
                st.warning("Enter a URL")
                st.stop()

            st.info("Downloading audio...")
            audio_path = download_audio(url)

            if not os.path.exists(audio_path):
                st.error("Download failed")
                st.stop()

            st.success("Download complete")

            st.info("Transcribing...")
            text, timestamps = transcribe_audio(audio_path)

            st.subheader("Transcript")
            st.write(text)

            st.subheader("Timestamps")
            for t in timestamps:
                st.write(t)

            summary = summarize_text(text)
            st.subheader("Summary")
            st.write(summary)

            translation = translate_text(summary)
            st.subheader("Translation")
            st.write(translation)

            # PDF
            pdf_file = create_pdf(summary)
            with open(pdf_file, "rb") as f:
                st.download_button("Download PDF", f, file_name="summary.pdf")

            add_history(st.session_state.user, summary)

    # -------- FILE UPLOAD --------
    if option == "Upload File":
        file = st.file_uploader("Upload video/audio", type=["mp4", "mp3", "wav"])

        if file:
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())

            if st.button("Process File"):
                st.info("Transcribing...")

                text, timestamps = transcribe_audio(file.name)

                st.subheader("Transcript")
                st.write(text)

                st.subheader("Timestamps")
                for t in timestamps:
                    st.write(t)

                summary = summarize_text(text)
                st.subheader("Summary")
                st.write(summary)

                translation = translate_text(summary)
                st.subheader("Translation")
                st.write(translation)

                pdf_file = create_pdf(summary)
                with open(pdf_file, "rb") as f:
                    st.download_button("Download PDF", f, file_name="summary.pdf")

                add_history(st.session_state.user, summary)

                os.remove(file.name)

# ---------------- HISTORY ----------------
if menu == "History":
    st.title("📜 History")

    data = load_history()

    user_data = [
        d for d in data
        if isinstance(d, dict) and d.get("user") == st.session_state.user
    ]

    if not user_data:
        st.info("No history found")
    else:
        for item in user_data[::-1]:
            st.write(item.get("text", ""))
            st.markdown("---")
