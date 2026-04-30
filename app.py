import streamlit as st
import json
import os
from utils import *

USER_FILE = "users.json"
HISTORY_FILE = "history.json"

# ---------------- INIT ----------------
for f in [USER_FILE, HISTORY_FILE]:
    if not os.path.exists(f):
        json.dump([], open(f, "w"))

# ---------------- USERS ----------------
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

if "chat" not in st.session_state:
    st.session_state.chat = []

if "context" not in st.session_state:
    st.session_state.context = ""

if "text" not in st.session_state:
    st.session_state.text = ""

if "timestamps" not in st.session_state:
    st.session_state.timestamps = []

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

# ---------------- AUTH ----------------
def auth():
    st.title("🔐 AI Video Analyzer Pro")
    mode = st.radio("Mode", ["Login", "Register"])
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")

    if st.button(mode):
        if mode == "Login" and login(u, p):
            st.session_state.user = u
            st.rerun()
        elif mode == "Register" and register(u, p):
            st.success("Registered successfully")
        else:
            st.error("Invalid credentials or user exists")

if not st.session_state.user:
    auth()
    st.stop()

st.sidebar.success(f"👤 {st.session_state.user}")
menu = st.sidebar.selectbox("Menu", ["Tool", "Chat", "History", "Logout"])

if menu == "Logout":
    st.session_state.user = None
    st.session_state.chat = []
    st.session_state.context = ""
    st.session_state.text = ""
    st.session_state.timestamps = []
    st.session_state.summary = ""
    st.session_state.translated_text = ""
    st.rerun()

# ---------------- TOOL ----------------
if menu == "Tool":
    st.title("🎬 AI Video Analyzer Pro")

    option = st.radio("Input Type", ["YouTube URL", "Upload File"])

    url = st.text_input("Enter YouTube URL") if option == "YouTube URL" else None
    file = st.file_uploader("Upload Audio/Video", type=["mp3", "wav", "mp4"]) if option == "Upload File" else None

    if st.button("🚀 Process"):

        if url:
            text, timestamps = get_youtube_text(url)

            if not text:
                st.warning("⚠️ No captions found. Using audio transcription...")
                audio_path = download_audio(url)
                text, timestamps = transcribe_audio(audio_path)

        elif file:
            with open(file.name, "wb") as f:
                f.write(file.getbuffer())
            text, timestamps = transcribe_audio(file.name)

        else:
            st.error("Please provide input")
            st.stop()

        # ✅ SAVE EVERYTHING
        st.session_state.text = text
        st.session_state.timestamps = timestamps
        st.session_state.summary = summarize_text(text, "Medium")
        st.session_state.context = text

    # -------- SHOW DATA (NO RESET) --------
    if st.session_state.text:

        st.subheader("📄 Transcript")
        st.write(st.session_state.text)

        st.subheader("📌 Auto Chapters")
        for ch in generate_chapters(st.session_state.timestamps):
            st.write(f"{ch['time']}s → {ch['title']}")

        st.subheader("📝 Summary")
        st.write(st.session_state.summary)

        st.subheader("✨ Highlights")
        st.write(highlight_text(st.session_state.text))

        # -------- LANGUAGES --------
        st.markdown("---")

        LANGUAGES = {
            "English": "en", "Hindi": "hi", "Kannada": "kn", "Tamil": "ta",
            "Telugu": "te", "Malayalam": "ml", "Marathi": "mr", "Gujarati": "gu",
            "Bengali": "bn", "Punjabi": "pa", "Urdu": "ur", "Spanish": "es",
            "French": "fr", "German": "de", "Italian": "it", "Portuguese": "pt",
            "Russian": "ru", "Chinese (Simplified)": "zh-cn", "Japanese": "ja",
            "Korean": "ko", "Arabic": "ar", "Turkish": "tr", "Dutch": "nl",
            "Polish": "pl", "Thai": "th", "Vietnamese": "vi",
            "Indonesian": "id", "Greek": "el"
        }

        lang_name = st.selectbox("🌍 Select Language", list(LANGUAGES.keys()))
        lang_code = LANGUAGES[lang_name]

        if st.button("🌐 Translate"):
            st.session_state.translated_text = translate_text(
                st.session_state.text, lang_code
            )

        st.subheader("🌐 Translated Text")
        st.write(st.session_state.translated_text)

        # -------- AUDIO --------
        if st.session_state.translated_text:
            audio = text_to_audio(st.session_state.translated_text, lang_code)
            st.audio(audio)

            with open(audio, "rb") as f:
                st.download_button("⬇️ Download Audio", f, "audio.mp3")

        # -------- EXPORT --------
        if st.session_state.translated_text:
            pdf = create_pdf(st.session_state.translated_text)
            docx = create_docx(st.session_state.translated_text)
            ppt = create_ppt(st.session_state.translated_text)

            with open(pdf, "rb") as f:
                st.download_button("Download PDF", f)

            with open(docx, "rb") as f:
                st.download_button("Download DOCX", f)

            with open(ppt, "rb") as f:
                st.download_button("Download PPT", f)

# ---------------- CHAT ----------------
if menu == "Chat":
    st.title("💬 Ask Questions from Video")

    if not st.session_state.context:
        st.warning("⚠️ Process a video first")
    else:
        q = st.text_input("Ask your question")

        if st.button("Ask"):
            ans = ask_question(st.session_state.context, q)
            st.session_state.chat.append((q, ans))

        for q, a in st.session_state.chat:
            st.markdown(f"**Q:** {q}")
            st.markdown(f"**A:** {a}")
            st.markdown("---")

# ---------------- HISTORY ----------------
if menu == "History":
    st.title("📜 History")

    for h in get_history(st.session_state.user):
        st.write(h["text"])
        st.markdown("---")
# restart
