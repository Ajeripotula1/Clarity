# 🧠 Clarity

> “Turn messy notes into flashcards, crisp summaries, and instant answers. Clarity grows as you do.”

**Clarity** is an AI-powered second brain. Upload your notes — Clarity will read them, understand your style, and help you study smarter by generating summaries, flashcards, and personalized answers.

Built with LLMs, RAG, and modern AI tooling.

---

## ✨ Features

- 📝 **Upload Notes** — Supports `.txt`, `.md`, and `.pdf`
- 🔍 **Searchable Memory** — Uses embeddings + vector search for retrieval
- 💬 **Chat with Your Notes** — LLM chatbot that cites your uploaded content
- 🧠 **Smart Summaries** — TL;DR-style summaries per note
- 🎓 **Flashcard Generator** — Q&A note cards from your uploads
- 🧬 **Style Adaptation** — Mirrors your writing style over time (prototype)
- 🌐 **Frontend UI** — Streamlit or minimal React for quick interaction

---

## 🏗️ Tech Stack

| Area | Tools |
|------|-------|
| **Backend** | Python, FastAPI |
| **LLM APIs** | OpenAI GPT-4 / Claude / Hugging Face |
| **RAG** | LangChain |
| **Embeddings** | OpenAI Embeddings / SentenceTransformers |
| **Vector Store** | FAISS / Chroma |
| **Frontend** | Streamlit or basic React (TBD) |
| **Storage** | Local filesystem / S3 (optional) |
| **Deployment** | Docker, EC2 / Render / Vercel (optional) |
| **Authentication** | Token-based / Firebase (optional) |

---

## 🛠️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/clarity-ai.git
cd clarity-ai
