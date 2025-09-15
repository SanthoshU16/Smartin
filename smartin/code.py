import streamlit as st
import requests
import PyPDF2
from docx import Document
from PIL import Image
import json
import os
import io

# ========== CONFIG ==========
OPENROUTER_MODEL = "meta-llama/llama-3.3-8b-instruct:free"
OPENROUTER_API_KEY = "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"  # ⬅️ Enter your OpenRouter API key here
OPENROUTER_URL = "https://openrouter.ai/api/v1/completions"

OCR_API_KEY = "K82144717888957"  # ⬅️ Enter your OCR.Space API key here
OCR_URL = "https://api.ocr.space/parse/image"

HISTORY_FILE = "chat_history.json"


# ========== HELPERS ==========

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(chats):
    with open(HISTORY_FILE, "w") as f:
        json.dump(chats, f, indent=2)


def extract_text_from_file(uploaded_file):
    # --- PDF ---
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([p.extract_text() for p in pdf_reader.pages if p.extract_text()])

    # --- Word ---
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])

    # --- Image (OCR.Space API) ---
    elif uploaded_file.type.startswith("image/"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        data = {"apikey": OCR_API_KEY, "language": "eng"}
        try:
            res = requests.post(OCR_URL, files=files, data=data, timeout=40)
            result = res.json()
            parsed = result.get("ParsedResults")
            if parsed:
                return parsed[0].get("ParsedText", "").strip()
            else:
                return "⚠️ OCR failed to extract text."
        except Exception as e:
            return f"⚠️ OCR request failed: {e}"

    else:
        return "❌ Unsupported file type"


def call_openrouter_api(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "prompt": prompt,
        "max_tokens": 2000
    }
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        if response.status_code != 200:
            return f"⚠️ API error {response.status_code}: {response.text[:200]}"
        try:
            data = response.json()
            return data.get("choices", [{}])[0].get("text", "⚠️ No text in response")
        except ValueError:
            return f"⚠️ Non-JSON response: {response.text[:200]}"
    except requests.exceptions.ConnectionError:
        return "⚠️ Could not connect to OpenRouter API. Check API key and URL"

# ========== UI SETUP ==========
st.set_page_config(page_title="Smartin", layout="wide")

if "chats" not in st.session_state:
    st.session_state.chats = load_history()
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""


# ========== SIDEBAR ==========
with st.sidebar:
    st.header("📚 Chats")

    if st.button("➕ New chat"):
        new_id = f"chat_{len(st.session_state.chats)+1}"
        st.session_state.chats[new_id] = {"title": "New Chat", "messages": []}
        st.session_state.current_chat = new_id
        save_history(st.session_state.chats)

    search = st.text_input("🔍 Search chats")

    for chat_id, chat in list(st.session_state.chats.items()):
        if search.lower() in chat["title"].lower():
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(chat["title"], key=f"select_{chat_id}"):
                    st.session_state.current_chat = chat_id
            with col2:
                if st.button("🗑️", key=f"delete_{chat_id}"):
                    del st.session_state.chats[chat_id]
                    save_history(st.session_state.chats)
                    if st.session_state.current_chat == chat_id:
                        if st.session_state.chats:
                            st.session_state.current_chat = next(iter(st.session_state.chats))
                        else:
                            st.session_state.current_chat = None
                    st.rerun()


# ========== INIT CHAT ==========
if not st.session_state.chats:
    st.session_state.chats["chat_1"] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat = "chat_1"
    save_history(st.session_state.chats)
elif not st.session_state.current_chat or st.session_state.current_chat not in st.session_state.chats:
    st.session_state.current_chat = next(iter(st.session_state.chats))

current_chat = st.session_state.chats[st.session_state.current_chat]


# ========== FILE UPLOAD ==========
uploaded_file = st.file_uploader("📁 Upload PDF, Word, or Image", type=["pdf", "docx", "png", "jpg", "jpeg"])
if uploaded_file:
    extracted_text = extract_text_from_file(uploaded_file)
    st.session_state.doc_text = extracted_text
    st.success("✅ File uploaded and processed!")


# ========== CHAT UI ==========
st.title(current_chat["title"])

for msg in current_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your file or general..."):
    current_chat["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    context = ""
    if st.session_state.doc_text:
        context = f"The following is the uploaded file content:\n{st.session_state.doc_text[:4000]}"

    final_prompt = f"{context}\n\nQuestion: {prompt}"
    answer = call_openrouter_api(final_prompt)

    current_chat["messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

    if current_chat["title"] == "New Chat":
        current_chat["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")

    save_history(st.session_state.chats)
