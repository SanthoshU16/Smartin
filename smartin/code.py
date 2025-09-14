import streamlit as st
import requests
import PyPDF2
from docx import Document
from PIL import Image
import tempfile
import os
import json


HISTORY_FILE = "chat_history.json"
OPENROUTER_MODEL = "meta-llama/llama-3.3-8b-instruct:free"


OPENROUTER_API_KEY ="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"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_history(chats):
    with open(HISTORY_FILE, "w") as f:
        json.dump(chats, f, indent=2)

def ocr_space_file(file_path, api_key):
    """Call OCR.Space API and return extracted text."""
    payload = {'apikey':'K82144717888957', 'language': 'eng'}
    with open(file_path, 'rb') as f:
        response = requests.post('https://api.ocr.space/parse/image', data=payload, files={'file': f})
    result = response.json()
    text = result['ParsedResults'][0]['ParsedText'] if result.get('ParsedResults') else ''
    return text

def extract_text_from_file(uploaded_file, ocr_api_key=None):
    """Extract text from PDF, Word, or Image (using OCR API)."""
    if uploaded_file.type == "application/pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        return "".join([p.extract_text() for p in pdf_reader.pages if p.extract_text()])

    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join([para.text for para in doc.paragraphs])

    elif uploaded_file.type.startswith("image/"):
        if ocr_api_key:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_file_path = tmp_file.name
            return ocr_space_file(tmp_file_path, ocr_api_key)
        else:
            return "❌ OCR API key not provided"

    else:
        return "❌ Unsupported file type"

st.set_page_config(page_title="Smartin", layout="wide")

if "chats" not in st.session_state:
    st.session_state.chats = load_history()
if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""


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
                        st.session_state.current_chat = next(iter(st.session_state.chats), None)
                    st.experimental_rerun()

    st.header("⚙️ Settings")
    ocr_api_key = st.text_input("OCR API Key", type="password")


if not st.session_state.chats:
    st.session_state.chats["chat_1"] = {"title": "New Chat", "messages": []}
    st.session_state.current_chat = "chat_1"
    save_history(st.session_state.chats)
elif not st.session_state.current_chat or st.session_state.current_chat not in st.session_state.chats:
    st.session_state.current_chat = next(iter(st.session_state.chats))

current_chat = st.session_state.chats[st.session_state.current_chat]


uploaded_file = st.file_uploader("Upload a PDF, Word doc, or Image", type=["pdf", "docx", "png", "jpg", "jpeg"])
if uploaded_file:
    extracted_text = extract_text_from_file(uploaded_file, ocr_api_key)
    st.session_state.doc_text = extracted_text
    st.success("✅ File uploaded and processed!")


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

    payload = {"model": OLLAMA_MODEL, "prompt": final_prompt, "stream": False}
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        if response.status_code == 200:
            answer = response.json().get("response", "").strip()
        else:
            answer = f"❌ Error {response.status_code}: {response.text}"
    except Exception as e:
        answer = f"⚠️ Request failed: {e}"

    current_chat["messages"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

    if current_chat["title"] == "New Chat":
        current_chat["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")

    save_history(st.session_state.chats)
