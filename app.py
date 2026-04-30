import streamlit as st
import json
import os
from utils import *

USER_FILE = "users.json"
HISTORY_FILE = "history.json"

# ---------------- INIT FILES ----------------
for f in [USER_FILE, HISTORY_FILE]:
    if not os.path.exists(f):
        json.dump([], open(f, "w"))

# ---------------- USER SYSTEM ----------------
def load_users():
    return json.load(open(USER_FILE))

def save_users(data):
    json.dump(data, open(USER_FILE, "w"))

def register(u, p):
    users = load_users()
    if any(x["username"] == u for x in users):
        return False
    users.append({"username": u, "password": p})
    save_users(users)
    return True

def login(u, p):
    return any(x["username"] == u and x["password"] == p for x in load_users())

# ---------------- HISTORY ----------------
def save_history(data):
    old = json.load(open(HISTORY_FILE))
    old.append(data)
    json.dump(old, open(HISTORY_FILE, "w"))

def get_history(user):
    return [x for x in json.load(open(HISTORY_FILE)) if x["user"] == user]

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

# ---------------- AUTH ----------------
def auth():
    st.title("🔐 AI Video Analyzer Pro")

    mode = st.radio("Select Mode", ["Login", "Register"])
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button(mode):
        if mode == "Login" and login(u, p):
            st.session_state.user = u
            st.rerun()
        elif mode == "Register" and register(u, p):
            st.success("Registered successfully")
        else:
            st.error("Invalid credentials")

# ---------------- MAIN ----------------
if not st.session_state.user:
    auth()
    st.stop()

st.sidebar.success(f"👤 {st.session_state.user}")
menu = st.sidebar.selectbox("Menu", ["Tool", "History", "Logout"])

if menu == "Logout":
    st.session_state.user = None
    st.rerun()

# ---------------- TOOL ----------------
if menu == "Tool":
    st.title("🎬 AI Video Analyzer Pro")

    url = st.text_input("Enter YouTube URL")

    if st.button("🚀 Process Video"):
        if not url:
            st.warning("Please enter URL")
            st.stop()

        with st.spinner("Processing video..."):
            text, timestamps = get_youtube_text(url)

        # ❗ ERROR HANDLING
        if not text or text.startswith("❌"):
            st.error(text if text else "❌ Failed to extract text")
            st.stop()

        st.subheader("📜 Transcript")
        st.write(text)

        # ---------------- SUMMARY ----------------
        mode = st.selectbox("Summary Type", ["Short", "Medium", "Long"])
        summary = summarize_text(text, mode)

        st.subheader("🧠 Summary")
        st.write(summary)

        # ---------------- HIGHLIGHTS ----------------
        st.subheader("✨ Highlights")
        st.write(highlight_text(text))

        # ---------------- LANGUAGE ----------------
        st.markdown("---")
        language_options = {
            "English": "en",
            "Hindi": "hi",
            "Kannada": "kn",
            "Tamil": "ta",
            "Telugu": "te",
            "French": "fr",
            "German": "de",
            "Spanish": "es",
            "Chinese": "zh-cn",
            "Japanese": "ja"
        }

        lang_name = st.selectbox("Select Language", list(language_options.keys()))
        lang_code = language_options[lang_name]

        translated = translate_text(summary, lang_code)

        st.subheader(f"🌍 Translated ({lang_name})")
        st.write(translated)

        # ---------------- AUDIO ----------------
        audio_file = text_to_audio(translated, lang_code)
        st.audio(audio_file)

        with open(audio_file, "rb") as f:
            st.download_button("⬇️ Download Audio", f, "audio.mp3")

        # ---------------- EXPORT ----------------
        pdf = create_pdf(translated)
        docx = create_docx(translated)
        ppt = create_ppt(translated)

        with open(pdf, "rb") as f:
            st.download_button("⬇️ Download PDF", f)

        with open(docx, "rb") as f:
            st.download_button("⬇️ Download DOCX", f)

        with open(ppt, "rb") as f:
            st.download_button("⬇️ Download PPT", f)

        # ---------------- SAVE HISTORY ----------------
        save_history({
            "user": st.session_state.user,
            "text": summary
        })

# ---------------- HISTORY ----------------
if menu == "History":
    st.title("📜 History")

    history = get_history(st.session_state.user)

    if not history:
        st.info("No history found")

    for h in history:
        st.write(h["text"])
        st.markdown("---")
