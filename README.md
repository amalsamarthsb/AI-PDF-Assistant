# 📄 AI PDF Assistant Pro

An AI-powered Retrieval-Augmented Generation (RAG) application that allows users to upload one or multiple PDF documents and ask natural language questions about their contents.

Built with **Google Gemini**, **LangChain**, **FAISS**, **Hybrid Retrieval (Semantic + BM25)**, and **Streamlit**.

---

## 🚀 Features

- 📄 Multiple PDF Upload
- 🤖 Gemini 2.5 Flash LLM
- 🔍 Hybrid Retrieval (FAISS + BM25)
- ⚡ Streaming Responses
- 📚 Source Citations
- 💬 Persistent Chat History
- 📊 RAG Evaluation Dashboard
- 🔎 Retrieval Inspector
- 🐳 Docker Support
- ☁️ Streamlit Ready

---

## 🏗 Architecture

```text
          PDFs
            │
            ▼
   PyPDFLoader
            │
            ▼
 RecursiveCharacterTextSplitter
            │
     ┌──────┴─────────┐
     ▼                ▼
FAISS Vector DB    BM25 Index
     │                │
     └──────┬─────────┘
            ▼
     Hybrid Retriever
            │
            ▼
      Gemini 2.5 Flash
            │
            ▼
      Streamlit Interface
```

---

## 📂 Project Structure

```
AI-PDF-Assistant/
│
├── app.py
├── config.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
├── services/
│   ├── ingest.py
│   ├── retriever.py
│   ├── hybrid_retriever.py
│   ├── llm.py
│   ├── logger.py
│   └── chat_history.py
│
├── database/
├── vectorstore/
├── assets/
├── data/
├── tests/
└── utils/
```

---

## 🛠 Tech Stack

- Python
- Streamlit
- Google Gemini
- LangChain
- FAISS
- HuggingFace Embeddings
- BM25
- SQLite
- Docker

---

## ⚙ Installation

Clone the repository

```bash
git clone https://github.com/amalsamarthsb/AI-PDF-Assistant.git
```

Navigate to the project

```bash
cd AI-PDF-Assistant
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env`

```
GOOGLE_API_KEY=YOUR_KEY
```

Run

```bash
streamlit run app.py
```

---

## 🐳 Docker

Build

```bash
docker build -t ai-pdf-assistant .
```

Run

```bash
docker run -p 8501:8501 ai-pdf-assistant
```

---

## 📸 Screenshots

(Add screenshots here)

---

## 🎥 Demo

(Add demo GIF here)

---

## 🔮 Future Improvements

- User Authentication
- Cloud Database
- OCR Support
- Image Understanding
- Citation Highlighting
- Conversation Memory
- Azure/OpenAI Support

---

## 📄 License

MIT License