import streamlit as st
import yt_dlp
import os
from utils import transcribe_audio

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Video Summarizer & Translator",
    layout="wide"
)

# ---------------- SESSION STATE ----------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "1234"}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- LOGIN / REGISTER ----------------
if not st.session_state.logged_in:

    st.title("🔐 AI Video SaaS Login")

    option = st.radio("Choose Option", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    # REGISTER
    if option == "Register":
        if st.button("Create Account"):
            if username in st.session_state.users:
                st.error("User already exists")
            else:
                st.session_state.users[username] = password
                st.success("Account created! Now login.")

    # LOGIN
    if option == "Login":
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Invalid credentials")

    st.stop()

# ---------------- HEADER ----------------
st.title("🎬 AI Video Summarizer & Translator (SaaS Mode)")

st.sidebar.success(f"👤 Welcome {st.session_state.user}")
menu = st.sidebar.radio("Menu", ["Dashboard", "History"])

# ---------------- HISTORY ----------------
if menu == "History":
    st.subheader("📜 History")
    for i, h in enumerate(st.session_state.history):
        st.write(f"{i+1}. {h[:200]}...")
    st.stop()

# ---------------- DASHBOARD ----------------
st.subheader("Input Source")

input_type = st.radio("Select Input Type", ["Upload File", "YouTube Link"])

text = ""

# ---------------- FILE UPLOAD ----------------
if input_type == "Upload File":
    file = st.file_uploader("Upload Video / Audio")

    if file:
        ext = file.name.split(".")[-1]
        path = f"temp.{ext}"

        with open(path, "wb") as f:
            f.write(file.read())

        st.info("Processing file...")

        text = transcribe_audio(path)

# ---------------- YOUTUBE ----------------
if input_type == "YouTube Link":
    url = st.text_input("Paste YouTube URL")

    if url:
        st.info("Processing YouTube video...")

        try:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "video.mp4",
                "quiet": True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            text = transcribe_audio("video.mp4")

        except Exception:
            st.error("⚠ YouTube blocked or restricted.")
            st.info("👉 Please try Upload File option for this video.")

# ---------------- OUTPUT ----------------
if text:
    st.success("Processing Complete")

    st.subheader("📄 Transcript")
    st.write(text)

    st.session_state.history.append(text)
