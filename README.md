# 🤖 Smartin AI — Document & Image Chatbot

Smartin AI is an intelligent **ChatGPT-style chatbot** built with **Streamlit** that allows users to **upload PDFs, Word documents, and images** and ask questions about their content in natural language.

It combines **LLM-powered reasoning** with **document understanding** and **OCR**, delivering fast, accurate answers through a clean chat interface.


# 📌 Live Demo :
👉 [https://smartin-assistant.streamlit.app/]
---

## 🚀 Features

✅ ChatGPT-like UI (chat bubbles + input at bottom)
✅ Upload and chat with **PDF files**
✅ Upload and chat with **Word (.docx) documents**
✅ Upload images and extract text using **OCR**
✅ Persistent chat history
✅ Cloud-deployable (Streamlit Cloud)
✅ Fast responses using **Groq LLaMA models**

---

## 🛠️ Tech Stack

### Frontend

* **Streamlit**
* Chat UI (`st.chat_message`, `st.chat_input`)

### Backend / AI

* **Groq API** (LLaMA 3.1)
* **OCR.Space API** (Image text extraction)

### File Processing

* `PyPDF2` – PDF text extraction
* `python-docx` – Word document parsing

---

## 📁 Supported File Types

| File Type                  | Supported |
| -------------------------- | --------- |
| PDF (.pdf)                 | ✅         |
| Word (.docx)               | ✅         |
| Images (.png, .jpg, .jpeg) | ✅ (OCR)   |

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/SanthoshU16/Smartin.git
cd smartin-ai
```

### 2️⃣ Create Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 API Keys Setup (IMPORTANT)

Create a folder called `.streamlit` and add a file named `secrets.toml`.

```toml
GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxx"
OCR_API_KEY = "xxxxxxxxxxxxxxxxxxxxx"
```

### 🔑 Get API Keys

* **Groq API** → [https://console.groq.com](https://console.groq.com)
* **OCR.Space API** → [https://ocr.space/ocrapi](https://ocr.space/ocrapi)

---

## ▶️ Run the App Locally

```bash
streamlit run app.py
```

The app will open at:

```
http://localhost:8501
```

---

## ☁️ Deploy on Streamlit Cloud

1. Push code to GitHub
2. Go to [https://share.streamlit.io](https://share.streamlit.io)
3. Select repository & branch
4. Add secrets in **App Settings → Secrets**
5. Deploy 🎉

---

## 🧠 How It Works

1. User uploads a document or image
2. Text is extracted (PDF / DOCX / OCR)
3. Extracted content is passed as context to LLM
4. User asks questions in chat
5. AI responds using document-aware reasoning

---

## 🧩 Future Enhancements

* 🔍 Vector search with FAISS (for large documents)
* 🧠 Multi-model selector (Groq / OpenAI)
* 📄 Chat export (PDF / TXT)
* 🔐 User authentication
* 🌍 Multi-language OCR support

---

## 👨‍💻 Author

**Santhosh**
AI / ML Enthusiast | B.Tech Student
📌 Passionate about building intelligent AI products

---

## ⭐ Support

If you like this project, please ⭐ star the repository
and share it on LinkedIn 🚀

---
