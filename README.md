# 🧠 Clarity

> “Turn dense notes into flashcards, crisp summaries, and instant answers. Clarity grows as you do.”

**Clarity** is an AI-powered second brain. Upload your notes — Clarity will read them, understand your style, and help you study smarter by generating summaries, flashcards, and personalized answers to your questions. Clarity gives you the tools to turn passive notes into active learning.

Clarity stands out from other document summarization apps by thinking with your material. It blends contextual awareness with AI reasoning te deliver relevant, thoughtful answers. 

Built with OpenAI LLM, RAG, and LangChain.

---

## ✨ Features

- 📂 **Upload Files** — Add `.txt` and `.pdf` files to your knowledge base
- 🔍 **Searchable Memory** — Uses embeddings + vector search for retrieval
- 💬 **Chat with Your Notes** — Ask anything. Clarity will prioritize your uploaded notes, but if it finds gaps, it fills them using reliable general knowledge — just like a great tutor would.
- 🧠 **Smart Summaries** — Tired of reading dense paragraphs? Get clean concise summaries outlining Big Ideas, Key terms, and TL;DR-style takeaways.
- 🎓 **Flashcard Generator** — Turn any document into interactive flashcards with one click — perfect for spaced repetition and active recall.
- 🌐 **Frontend UI** — Clean, minimal, and modularized UI for quick interactions

---

### 🤖 How It Works

Clarity uses:

- **LLMs (via LangChain)** to interpret user queries and generate responses
- **ChromaDB** for vector-based semantic search across uploaded notes
- **FastAPI** to handle backend logic and file processing
- **Streamlit** for a focused, responsive user interface

> Answers are grounded in your uploaded material. When needed, Clarity enhances them with general knowledge — like a smart, personalized tutor.

---


## 🏗️ Tech Stack

| Area | Tools |
|------|-------|
| **Backend** | Python, FastAPI |
| **LLM APIs** | OpenAI GPT-4 |
| **RAG** | LangChain |
| **Embeddings** | OpenAI Embeddings |
| **Vector Store** |Chroma |
| **Frontend** | Streamlit |

---

### 🚀 Try It Out
1. Clone the repo

### 🚀 Try It Out

1. Clone the repo and set up the project:

```bash
# Clone the repository
git clone https://github.com/yourusername/clarity
cd clarity

# Create and set up your virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env example and add your OpenAI API key
cp .env.example .env
# Then edit the .env file to insert your key

# Start backend
uvicorn app.main:app --reload

# In a new terminal, run frontend
streamlit run app/ui.py
