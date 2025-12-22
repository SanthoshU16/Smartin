import streamlit as st
import requests
import PyPDF2
from docx import Document
import json
import os

# ================= CONFIG =================

OPENROUTER_MODELS = [
    "meta-llama/llama-3.1-8b-instruct:free",
    "mistralai/mistral-7b-instruct:free",
    "google/gemma-2-9b-it:free"
]

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

OCR_API_KEY = st.secrets["OCR_API_KEY"]
OCR_URL = "https://api.ocr.space/parse/image"

HISTORY_FILE = "chat_history.json"


# ================= HELPERS =================

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(chats):
    with open(HISTORY_FILE, "w") as f:
        json.dump(chats, f, indent=2)

def extract_text_from_file(uploaded_file):
    try:
        # PDF
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            return "\n".join(
                page.extract_text()
                for page in reader.pages
                if page.extract_text()
            )

        # Word
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            return "\n".join(p.text for p in doc.paragraphs)

        # Image (OCR)
        elif uploaded_file.type.startswith("image/"):
            files = {"file": uploaded_file}
            data = {"apikey": OCR_API_KEY, "language": "eng"}
            res = requests.post(OCR_URL, files=files, data=data, timeout=40)
            parsed = res.json().get("ParsedResults")
            return parsed[0]["ParsedText"] if parsed else "⚠️ OCR failed."

    except Exception as e:
        return f"⚠️ File processing error: {e}"

    return "❌ Unsupported file type"

def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Smartin AI"
    }

    for model in OPENROUTER_MODELS:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant. Use uploaded documents if provided."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1500,
            "temperature": 0.7
        }

        try:
            response = requests.post(
                OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=40
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

        except Exception:
            continue

    return "⚠️ All models failed. Please try again later."


# ================= UI SETUP =================

st.set_page_config(page_title="Smartin", layout="wide")

if "chats" not in st.session_state:
    st.session_state.chats = load_history()

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""


# ================= SIDEBAR =================

with st.sidebar:
    st.header("📚 Chats")

    if st.button("➕ New chat"):
        cid = f"chat_{len(st.session_state.chats) + 1}"
        st.session_state.chats[cid] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat = cid
        save_history(st.session_state.chats)
        st.rerun()

    search = st.text_input("🔍 Search chats")

    for cid, chat in list(st.session_state.chats.items()):
        if search.lower() in chat["title"].lower():
            col1, col2 = st.columns([4, 1])

            with col1:
                if st.button(chat["title"], key=f"open_{cid}"):
                    st.session_state.current_chat = cid
                    st.rerun()

            with col2:
                if st.button("🗑️", key=f"del_{cid}"):
                    del st.session_state.chats[cid]
                    save_history(st.session_state.chats)
                    st.session_state.current_chat = None
                    st.rerun()


# ================= INIT CHAT =================

if not st.session_state.chats:
    st.session_state.chats["chat_1"] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat = "chat_1"
    save_history(st.session_state.chats)

if not st.session_state.current_chat:
    st.session_state.current_chat = next(iter(st.session_state.chats))

current_chat = st.session_state.chats[st.session_state.current_chat]


# ================= FILE UPLOAD =================

uploaded_file = st.file_uploader(
    "📁 Upload PDF, Word, or Image",
    type=["pdf", "docx", "png", "jpg", "jpeg"]
)

if uploaded_file:
    st.session_state.doc_text = extract_text_from_file(uploaded_file)
    st.success("✅ File processed successfully!")


# ================= CHAT UI =================

st.title(current_chat["title"])

for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your file or general..."):
    current_chat["messages"].append({"role": "user", "content": prompt})

    context = ""
    if st.session_state.doc_text:
        context = f"Document content:\n{st.session_state.doc_text[:4000]}"

    final_prompt = f"{context}\n\nQuestion: {prompt}"

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = call_openrouter(final_prompt)
            st.markdown(answer)

    current_chat["messages"].append({"role": "assistant", "content": answer})

    if current_chat["title"] == "New Chat":
        current_chat["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")

    save_history(st.session_state.chats)
    st.rerun()
