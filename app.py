import streamlit as st
import json
import os
from utils import (
    get_youtube_text,
    transcribe_audio,
    summarize_text,
    translate_text
)

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
    with open(USER_FILE) as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

def register(username, password):
    users = load_users()
    for u in users:
        if u["username"] == username:
            return False
    users.append({"username": username, "password": password})
    save_users(users)
    return True

def login(username, password):
    users = load_users()
    for u in users:
        if u["username"] == username and u["password"] == password:
            return True
    return False

# ---------------- HISTORY FUNCTIONS ----------------
def load_history():
    try:
        with open(HISTORY_FILE) as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except:
        return []

def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_history(user, text):
    data = load_history()
    data.append({"user": user, "text": text})
    save_history(data)

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- AUTH UI ----------------
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
            st.info("Processing YouTube...")

            text = get_youtube_text(url)

            if not text:
                st.error("⚠ Cannot process this video. Try upload.")
            else:
                st.success("Done")

                st.subheader("Transcript")
                st.write(text)

                summary = summarize_text(text)
                st.subheader("Summary")
                st.write(summary)

                translation = translate_text(summary)
                st.subheader("Translation")
                st.write(translation)

                add_history(st.session_state.user, summary)

    # -------- UPLOAD --------
    if option == "Upload File":
        file = st.file_uploader("Upload video/audio", type=["mp4", "mp3", "wav"])

        if file:
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())

            if st.button("Process File"):
                st.info("Transcribing...")

                text = transcribe_audio(file.name)

                st.subheader("Transcript")
                st.write(text)

                summary = summarize_text(text)
                st.subheader("Summary")
                st.write(summary)

                translation = translate_text(summary)
                st.subheader("Translation")
                st.write(translation)

                add_history(st.session_state.user, summary)

                os.remove(file.name)

# ---------------- HISTORY ----------------
if menu == "History":
    st.title("📜 History")

    data = load_history()

    user_data = [d for d in data if isinstance(d, dict) and d.get("user") == st.session_state.user]

    if not user_data:
        st.info("No history found")
    else:
        for item in user_data[::-1]:
            st.write(item.get("text", ""))
            st.markdown("---")
